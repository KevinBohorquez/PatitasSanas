// Configuración de los componentes de cronograma para reutilizarlos con veterinarios
// o recepcionistas (mismos endpoints y estructura, distinta entidad).

export const CONFIG_VET = {
  base: '/api/v1/horarios',
  rosterKey: 'veterinarios',       // clave del arreglo en /dia y /semana
  nameKey: 'veterinario',          // clave del nombre en cada entrada del roster
  personUrl: '/api/v1/veterinarios/?limit=100',
  personArrayKey: 'veterinarios',  // clave del arreglo en la respuesta de la lista
  personIdKey: 'id_veterinario',   // id de la persona (dropdown y filas)
  label: 'veterinario',
  labelPlural: 'veterinarios',
};

export const CONFIG_RECEP = {
  base: '/api/v1/horarios-recep',
  rosterKey: 'recepcionistas',
  nameKey: 'recepcionista',
  personUrl: '/api/v1/recepcionistas/?limit=100',
  personArrayKey: 'recepcionistas',
  personIdKey: 'id_recepcionista',
  label: 'recepcionista',
  labelPlural: 'recepcionistas',
};
