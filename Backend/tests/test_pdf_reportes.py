import os
import pytest
from datetime import datetime
from app.services.pdf.appointments_pdf import generar_pdf_citas_diarias
from app.services.pdf.medical_history_pdf import generar_pdf_historial_clinico

def test_generar_pdf_citas_diarias_con_datos():
    mock_citas = [
        {"horario": "09:00 AM", "mascota": "Firulais", "cliente": "Juan Perez", "veterinario": "Dr. Smith", "estado": "Programada"}
    ]
    file_path = generar_pdf_citas_diarias(mock_citas, datetime.now())
    
    # Verificar que devuelva una ruta válida y el archivo exista
    assert file_path is not None
    assert os.path.exists(file_path)
    assert file_path.endswith(".pdf")
    
    # Limpiar archivo de prueba
    if os.path.exists(file_path):
        os.remove(file_path)

def test_generar_pdf_citas_diarias_vacio():
    mock_citas = []
    file_path = generar_pdf_citas_diarias(mock_citas, datetime.now())
    
    assert file_path is not None
    assert os.path.exists(file_path)
    
    # Limpiar archivo de prueba
    if os.path.exists(file_path):
        os.remove(file_path)

def test_generar_pdf_historial_clinico():
    mock_mascota = {"nombre": "Test", "raza": "Mestizo", "edad": 2, "sexo": "Hembra", "cliente": "Test User"}
    mock_historial = [{"fecha": "10/05/2026", "motivo": "Vacunación", "diagnostico": "Ok", "veterinario": "Dr. Test"}]
    
    file_path = generar_pdf_historial_clinico(mock_historial, mock_mascota)
    
    assert file_path is not None
    assert os.path.exists(file_path)
    
    # Limpiar archivo de prueba
    if os.path.exists(file_path):
        os.remove(file_path)
