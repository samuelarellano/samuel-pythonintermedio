export interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  categoria: string;
  precio_centavos: number;
  proveedor_id: number;
}

export interface ProductoCrear {
  codigo: string;
  nombre: string;
  categoria: string;
  precio_centavos: number;
  proveedor_id: number;
}

export interface ProductoActualizar {
  codigo?: string;
  nombre?: string;
  categoria?: string;
  precio_centavos?: number;
  proveedor_id?: number;
}
