def build_reminder_html(
    cliente_nombre: str,
    mascota_nombre: str,
    fecha_formateada: str,
    hora_formateada: str,
    horas_antes: int,
) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <style>
        body      {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
        .container{{ max-width: 580px; margin: 32px auto; background: #ffffff;
                     border-radius: 8px; overflow: hidden;
                     box-shadow: 0 2px 8px rgba(0,0,0,.12); }}
        .header   {{ background: #2e7d32; padding: 24px 32px; }}
        .header h1{{ color: #ffffff; margin: 0; font-size: 20px; }}
        .body     {{ padding: 28px 32px; color: #333333; }}
        .body p   {{ line-height: 1.6; margin: 8px 0; }}
        .highlight{{ background: #e8f5e9; border-left: 4px solid #2e7d32;
                     border-radius: 4px; padding: 14px 18px; margin: 20px 0; }}
        .highlight p {{ margin: 4px 0; }}
        .badge    {{ display: inline-block; background: #2e7d32; color: #fff;
                     padding: 4px 12px; border-radius: 12px; font-size: 13px; }}
        .footer   {{ background: #f0f0f0; text-align: center; padding: 14px;
                     font-size: 12px; color: #888888; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🐾 Patitas Sanas — Recordatorio de cita</h1>
        </div>
        <div class="body">
          <p>Hola, <strong>{cliente_nombre}</strong>.</p>
          <p>Te recordamos que tu mascota tiene una cita programada
             <span class="badge">en {horas_antes} horas</span>.</p>

          <div class="highlight">
            <p><strong>Mascota:</strong> {mascota_nombre}</p>
            <p><strong>Fecha:</strong> {fecha_formateada}</p>
            <p><strong>Hora:</strong> {hora_formateada}</p>
          </div>

          <p>Por favor, llega con al menos 10 minutos de anticipación.</p>
          <p>Si necesitas cancelar o reprogramar, contáctanos a la brevedad.</p>
          <p>¡Hasta pronto! 🐶🐱</p>
        </div>
        <div class="footer">
          Veterinaria Patitas Sanas — Este correo es generado automáticamente.
        </div>
      </div>
    </body>
    </html>
    """
