// utils/userDisplay.js
// Nombre a mostrar del usuario logueado, con el mismo criterio en todos los
// dashboards: prioriza el nombre real, luego el nombre completo de la sesión y,
// por último, el username o el rol por defecto.

export function getUserDisplayName(user, fallback = 'USUARIO') {
  if (user?.name && user.name !== user?.username) {
    return user.name;
  }
  if (user?.session_info?.nombre_completo) {
    return user.session_info.nombre_completo;
  }
  return user?.username || fallback;
}
