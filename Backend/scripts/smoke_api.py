#!/usr/bin/env python3
"""
Script de pruebas para la API de Veterinaria
Ejecutar: python test_api.py
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Función helper para probar endpoints"""
    print(f"\n{'='*60}")
    print(f"🧪 PROBANDO: {description}")
    print(f"📡 {method} {BASE_URL}{endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(f"📄 Respuesta:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def main():
    print("🏥 SISTEMA VETERINARIA - PRUEBAS DE API")
    print("=" * 60)
    
    # 1. Probar endpoint raíz
    test_endpoint("/", description="Endpoint raíz")
    
    # 2. Probar salud del sistema
    test_endpoint("/health", description="Estado del sistema")
    
    # 3. Probar conexión a la base de datos
    test_endpoint("/test-db", description="Conexión a la base de datos")
    
    # 4. Obtener estadísticas
    test_endpoint("/stats", description="Estadísticas del sistema")
    
    # 5. Listar clientes (primera página)
    result = test_endpoint("/clientes", description="Lista de clientes (página 1)")
    
    # 6. Listar clientes con paginación
    test_endpoint("/clientes?page=1&per_page=5", description="Lista de clientes (5 por página)")
    
    # 7. Filtrar clientes por estado
    test_endpoint("/clientes?estado=Activo", description="Clientes activos")
    
    # 8. Buscar clientes
    test_endpoint("/clientes/search/?nombre=Juan", description="Buscar clientes por nombre 'Juan'")
    
    # 9. Probar obtener cliente específico (si existe)
    if result and result.get('clientes') and len(result['clientes']) > 0:
        primer_cliente = result['clientes'][0]
        cliente_id = primer_cliente.get('id_cliente')
        test_endpoint(f"/clientes/{cliente_id}", description=f"Cliente específico (ID: {cliente_id})")
    
    # 10. Probar crear cliente (datos de prueba)
    nuevo_cliente = {
        "nombre": "Juan Carlos",
        "apellido_paterno": "Pérez",
        "apellido_materno": "García",
        "dni": "12345678",
        "telefono": "987654321",
        "email": f"juan.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "direccion": "Av. Prueba 123, Lima",
        "estado": "Activo"
    }
    
    cliente_creado = test_endpoint(
        "/clientes", 
        method="POST", 
        data=nuevo_cliente,
        description="Crear nuevo cliente"
    )
    
    # 11. Si se creó correctamente, probamos actualizarlo
    if cliente_creado and cliente_creado.get('id_cliente'):
        cliente_id = cliente_creado['id_cliente']
        
        # Actualizar cliente
        datos_actualizacion = {
            "direccion": "Nueva Dirección 456, Lima",
            "telefono": "912345678"
        }
        
        test_endpoint(
            f"/clientes/{cliente_id}",
            method="PUT",
            data=datos_actualizacion,
            description=f"Actualizar cliente (ID: {cliente_id})"
        )
        
        # Obtener cliente actualizado
        test_endpoint(f"/clientes/{cliente_id}", description="Verificar cliente actualizado")
        
        # Soft delete (desactivar)
        test_endpoint(
            f"/clientes/{cliente_id}",
            method="DELETE",
            description=f"Desactivar cliente (ID: {cliente_id})"
        )
    
    # 12. Probar búsqueda por DNI (si tenemos clientes)
    test_endpoint("/clientes/dni/12345678", description="Buscar cliente por DNI")
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("\n💡 CONSEJOS:")
    print("- Si hay errores de conexión, verifica que el servidor esté ejecutándose")
    print("- Para iniciar el servidor: uvicorn main:app --reload")
    print("- Para ver la documentación: http://localhost:8000/docs")

if __name__ == "__main__":
    main()