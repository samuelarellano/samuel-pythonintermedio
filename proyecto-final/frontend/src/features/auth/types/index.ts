export interface Usuario {
  id: number;
  username: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Credentials {
  username: string;
  password: string;
}
