/**
 * Utilidades para manejo monetario seguro evitando imprecisiones de punto flotante.
 */

/**
 * Convierte un entero en centavos a una cadena formateada en pesos mexicanos (MXN).
 * Ejemplo: 14550 -> "$145.50 MXN"
 */
export function centavosAPesosFormateado(centavos: number): string {
  const pesos = (centavos / 100).toFixed(2);
  return `$${pesos} MXN`;
}

/**
 * Convierte un entero en centavos al valor numérico en pesos con 2 decimales para edición.
 * Ejemplo: 14550 -> "145.50"
 */
export function centavosAStringPesos(centavos: number): string {
  return (centavos / 100).toFixed(2);
}

/**
 * Convierte de forma determinista una entrada de texto en pesos a un entero en centavos.
 * Descompone parte entera y decimal para eliminar errores de coma flotante.
 * Ejemplo: "145.50" -> 14550
 */
export function pesosACentavos(input: string): number {
  const limpio = input.trim().replace('$', '').replace(/,/g, '');
  if (!limpio) {
    throw new Error('El precio es obligatorio.');
  }

  const regexMoneda = /^\d+(\.\d{1,2})?$/;
  if (!regexMoneda.test(limpio)) {
    throw new Error('El precio debe ser un número positivo con máximo 2 decimales (ej. 125.50).');
  }

  const partes = limpio.split('.');
  const enteros = parseInt(partes[0], 10);
  let centavos = 0;

  if (partes.length === 2) {
    const decimalesTexto = (partes[1] + '00').slice(0, 2);
    centavos = parseInt(decimalesTexto, 10);
  }

  const totalCentavos = enteros * 100 + centavos;
  if (totalCentavos <= 0) {
    throw new Error('El precio debe ser mayor que cero.');
  }

  return totalCentavos;
}
