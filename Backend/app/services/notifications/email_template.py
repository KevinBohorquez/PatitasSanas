def build_reminder_html(
    cliente_nombre: str,
    mascota_nombre: str,
    fecha_formateada: str,
    hora_formateada: str,
    horas_antes: int,
    veterinario_nombre: str | None = None,
    servicio_nombre: str | None = None,
) -> str:
    alerta = "Tienes una cita en menos de 4 horas." if horas_antes <= 4 else "Tienes una cita programada para mañana."

    filas_extra = ""
    if servicio_nombre:
        filas_extra += f"""
                <tr>
                  <td style="padding:12px 16px;font-size:12px;color:#888888;
                             text-transform:uppercase;letter-spacing:0.6px;
                             border-bottom:1px solid #e8e8e8;">
                    Servicio
                  </td>
                  <td style="padding:12px 16px;font-size:14px;color:#222222;
                             border-bottom:1px solid #e8e8e8;">
                    {servicio_nombre}
                  </td>
                </tr>"""
    if veterinario_nombre:
        filas_extra += f"""
                <tr style="background:#f9f9f9;">
                  <td style="padding:12px 16px;font-size:12px;color:#888888;
                             text-transform:uppercase;letter-spacing:0.6px;
                             border-bottom:1px solid #e8e8e8;">
                    Veterinario
                  </td>
                  <td style="padding:12px 16px;font-size:14px;color:#222222;
                             border-bottom:1px solid #e8e8e8;">
                    {veterinario_nombre}
                  </td>
                </tr>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin:0;padding:0;background:#f7f7f7;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;color:#222222;">

  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0"
               style="max-width:520px;width:100%;background:#ffffff;border-radius:4px;
                      border:1px solid #e0e0e0;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1b5e20 0%,#2e7d32 60%,#388e3c 100%);
                       padding:36px 40px 28px;text-align:center;border-radius:4px 4px 0 0;">
              <div style="font-size:48px;line-height:1;margin-bottom:10px;">🐾</div>
              <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;
                         letter-spacing:0.5px;">Patitas Sanas</h1>
              <p style="margin:6px 0 0;color:#a5d6a7;font-size:14px;letter-spacing:1px;
                        text-transform:uppercase;">Clínica Veterinaria</p>
            </td>
          </tr>

          <!-- Cuerpo -->
          <tr>
            <td style="padding:24px 40px 0;">
              <p style="margin:0 0 16px;font-size:15px;line-height:1.6;color:#333333;">
                Hola, {cliente_nombre}.
              </p>
              <p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#333333;">
                {alerta} A continuación los detalles de la cita de <strong>{mascota_nombre}</strong>:
              </p>
            </td>
          </tr>

          <!-- Detalles -->
          <tr>
            <td style="padding:0 40px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e8e8e8;border-radius:4px;overflow:hidden;">
                <tr style="background:#f9f9f9;">
                  <td style="padding:12px 16px;font-size:12px;color:#888888;
                             text-transform:uppercase;letter-spacing:0.6px;
                             border-bottom:1px solid #e8e8e8;width:40%;">
                    Mascota
                  </td>
                  <td style="padding:12px 16px;font-size:14px;color:#222222;font-weight:600;
                             border-bottom:1px solid #e8e8e8;">
                    {mascota_nombre}
                  </td>
                </tr>
                <tr>
                  <td style="padding:12px 16px;font-size:12px;color:#888888;
                             text-transform:uppercase;letter-spacing:0.6px;
                             border-bottom:1px solid #e8e8e8;">
                    Fecha
                  </td>
                  <td style="padding:12px 16px;font-size:14px;color:#222222;
                             border-bottom:1px solid #e8e8e8;">
                    {fecha_formateada}
                  </td>
                </tr>
                <tr style="background:#f9f9f9;">
                  <td style="padding:12px 16px;font-size:12px;color:#888888;
                             text-transform:uppercase;letter-spacing:0.6px;
                             {'border-bottom:1px solid #e8e8e8;' if filas_extra else ''}">
                    Hora
                  </td>
                  <td style="padding:12px 16px;font-size:14px;color:#222222;
                             {'border-bottom:1px solid #e8e8e8;' if filas_extra else ''}">
                    {hora_formateada}
                  </td>
                </tr>{filas_extra}
              </table>
            </td>
          </tr>

          <!-- Nota -->
          <tr>
            <td style="padding:24px 40px 32px;">
              <p style="margin:0;font-size:14px;line-height:1.6;color:#666666;">
                Si necesitas cancelar o reprogramar la cita, comunícate con nosotros
                con la mayor anticipación posible.
              </p>
            </td>
          </tr>

          <!-- Separador -->
          <tr>
            <td style="padding:0 40px;">
              <div style="border-top:1px solid #eeeeee;"></div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#aaaaaa;line-height:1.6;">
                Patitas Sanas &mdash; Clínica Veterinaria<br/>
                Este es un mensaje automático, por favor no respondas a este correo.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""
