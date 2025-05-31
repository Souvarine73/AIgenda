"""
Script to test the database funcionality of the task management application.
This script performes a series of tests to ensure that the databse is working correctly,
including creating, saving, retrieving and querying tasks.
"""

import sys
import os
from datetime import datetime, timedelta
from loguru import logger

# Add src to the system path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the models and session managment from databse module and logs configutarion
# Importar desde el mismo directorio (database/)
from models import Tarea, get_session
from utils.logger import logs_config

# loguru configuration
def config_local_project(root_project):
    """Configurar loguru usando la utilidad compartida"""
    logs_config(root_project, "test_database.log")

def test_database():
    """Prueba completa de la base de datos"""
    
    logger.info("🚀 Iniciando pruebas de base de datos...")
    
    try:
        # 1. Crear sesión con debug activado para ver el SQL
        logger.info("1️⃣ Creando sesión con debug activado...")
        session = get_session(debug=True)
        logger.success("✅ Sesión creada correctamente")
        
        # 2. Crear una tarea de prueba
        logger.info("2️⃣ Creando tarea de prueba...")
        tarea_prueba = Tarea(
            title="Tarea de prueba",
            description="Esta es una tarea creada para probar que la BD funciona",
            due_date=datetime.now() + timedelta(days=7)  # Vence en 7 días
        )
        logger.debug(f"Tarea creada: {tarea_prueba.title}")
        
        # 3. Guardar en la base de datos
        logger.info("3️⃣ Guardando en la base de datos...")
        session.add(tarea_prueba)
        session.commit()
        logger.success(f"✅ Tarea guardada con ID: {tarea_prueba.id}")
        
        # 4. Verificar que se guardó correctamente
        logger.info("4️⃣ Verificando que se guardó...")
        tarea_recuperada = session.query(Tarea).filter_by(id=tarea_prueba.id).first()
        if tarea_recuperada:
            logger.success(f"✅ Tarea recuperada: {tarea_recuperada}")
            logger.debug(f"   - Title: {tarea_recuperada.title}")
            logger.debug(f"   - Description: {tarea_recuperada.description}")
            logger.debug(f"   - Created at: {tarea_recuperada.created_at}")
            logger.debug(f"   - Due date: {tarea_recuperada.due_date}")
        else:
            logger.error("❌ No se pudo recuperar la tarea")
            return False
        
        # 5. Probar to_dict()
        logger.info("5️⃣ Probando conversión a diccionario...")
        tarea_dict = tarea_recuperada.to_dict()
        logger.success("✅ Conversión a diccionario exitosa")
        logger.debug(f"Diccionario: {tarea_dict}")
        
        # 6. Crear varias tareas para probar consultas
        logger.info("6️⃣ Creando varias tareas...")
        tareas_adicionales = [
            Tarea(title="Comprar leche", description="En el súper de la esquina", 
                  due_date=datetime.now() + timedelta(days=2)),
            Tarea(title="Estudiar Python", description="Revisar SQLAlchemy", 
                  due_date=datetime.now() + timedelta(days=3)),
            Tarea(title="Llamar al médico", due_date=datetime.now() + timedelta(days=1))
        ]
        
        for tarea in tareas_adicionales:
            session.add(tarea)
            logger.debug(f"Añadida tarea: {tarea.title}")
        
        session.commit()
        logger.success(f"✅ {len(tareas_adicionales)} tareas adicionales creadas")
        
        # 7. Listar todas las tareas
        logger.info("7️⃣ Listando todas las tareas...")
        todas_las_tareas = session.query(Tarea).all()
        logger.success(f"✅ Total de tareas en BD: {len(todas_las_tareas)}")
        
        for i, tarea in enumerate(todas_las_tareas, 1):
            logger.debug(f"   {i}. {tarea}")
        
        # 8. Probar consulta con filtro
        logger.info("8️⃣ Probando consultas con filtro...")
        tareas_con_vencimiento = session.query(Tarea).filter(Tarea.due_date.isnot(None)).all()
        logger.success(f"✅ Tareas con fecha de vencimiento: {len(tareas_con_vencimiento)}")
        
        for tarea in tareas_con_vencimiento:
            logger.debug(f"   - {tarea.title} (vence: {tarea.due_date.strftime('%Y-%m-%d')})")
        
        # 9. Cerrar sesión
        logger.info("9️⃣ Cerrando sesión...")
        session.close()
        logger.success("✅ Sesión cerrada correctamente")
        
        logger.success("🎉 ¡Todas las pruebas pasaron! Tu base de datos funciona perfectamente.")
        logger.info(f"📁 Base de datos creada en: data/tareas.db")
        logger.info(f"📝 Logs guardados en: logs/test_database.log")
        
        return True
        
    except Exception as e:
        logger.exception(f"❌ Error durante las pruebas: {e}")
        logger.warning("💡 Revisa que el directorio 'data' existe y que models.py está bien configurado")
        return False

def limpiar_base_datos():
    """Elimina todas las tareas para empezar limpio"""
    logger.info("🧹 Limpiando base de datos...")
    try:
        session = get_session()
        count = session.query(Tarea).count()
        session.query(Tarea).delete()
        session.commit()
        session.close()
        logger.success(f"✅ Base de datos limpiada ({count} tareas eliminadas)")
        return True
    except Exception as e:
        logger.error(f"❌ Error limpiando la base de datos: {e}")
        return False

def crear_directorios():
    """Crear directorios necesarios si no existen"""
    # Como estamos en src/database/, necesitamos ir 2 niveles arriba para crear data/ y logs/
    proyecto_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directorios = [
        os.path.join(proyecto_root, 'data'),
        os.path.join(proyecto_root, 'logs')
    ]
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            logger.debug(f"Directorio creado: {os.path.relpath(directorio)}/")
    
    return proyecto_root

if __name__ == "__main__":
    # Crear directorios necesarios y configurar logs
    proyecto_root = crear_directorios()
    config_local_project(proyecto_root)
    
    logger.info("=== INICIANDO PRUEBAS DE BASE DE DATOS ===")
    
    # Opción para limpiar la BD antes de probar
    respuesta = input("¿Quieres limpiar la BD antes de probar? (s/N): ").lower()
    if respuesta == 's':
        if not limpiar_base_datos():
            logger.error("No se pudo limpiar la base de datos. Abortando...")
            sys.exit(1)
    
    # Ejecutar pruebas
    exito = test_database()
    
    if exito:
        logger.info("=== PRUEBAS COMPLETADAS CON ÉXITO ===")
        sys.exit(0)
    else:
        logger.error("=== PRUEBAS FALLARON ===")
        sys.exit(1)