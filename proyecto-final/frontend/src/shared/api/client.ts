/**
 * Cliente HTTP centralizado con token en memoria y manejo unificado de errores.
 */
import { API_BASE_URL } from './config';

let memoryToken: string | null = null;
let unauthorizedHandler: (() => void) | null = null;

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export function setMemoryToken(token: string | null): void {
  memoryToken = token;
}

export function getMemoryToken(): string | null {
  return memoryToken;
}

export function registerUnauthorizedHandler(handler: () => void): void {
  unauthorizedHandler = handler;
}

interface FetchOptions extends RequestInit {
  isFormUrlEncoded?: boolean;
}

export async function apiFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { isFormUrlEncoded = false, headers = {}, ...rest } = options;

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const requestHeaders = new Headers(headers);

  // Inyección de token en memoria
  if (memoryToken && !requestHeaders.has('Authorization')) {
    requestHeaders.set('Authorization', `Bearer ${memoryToken}`);
  }

  if (isFormUrlEncoded) {
    if (!requestHeaders.has('Content-Type')) {
      requestHeaders.set('Content-Type', 'application/x-www-form-urlencoded');
    }
  } else if (!requestHeaders.has('Content-Type') && rest.body) {
    requestHeaders.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...rest,
    headers: requestHeaders,
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (unauthorizedHandler) {
        unauthorizedHandler();
      }
    }

    let errorDetail = `Error ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (typeof errorJson.detail === 'string') {
        errorDetail = errorJson.detail;
      } else if (Array.isArray(errorJson.detail)) {
        errorDetail = errorJson.detail
          .map((err: { msg?: string; loc?: string[] }) => err.msg || JSON.stringify(err))
          .join(', ');
      }
    } catch {
      // Si no es JSON, conservar el mensaje estándar de error HTTP
    }

    throw new ApiError(response.status, errorDetail);
  }

  if (response.status === 204) {
    return null as unknown as T;
  }

  return response.json() as Promise<T>;
}
