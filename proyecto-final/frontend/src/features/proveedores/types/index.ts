export interface Proveedor {
  id: number;
  nombre: string;
  contacto: string;
  telefono: string;
}

export interface ProveedorCrear {
  nombre: string;
  contacto: string;
  telefono: string;
}

export interface ProveedorActualizar {
  nombre?: string;
  contacto?: string;
  telefono?: string;
}
