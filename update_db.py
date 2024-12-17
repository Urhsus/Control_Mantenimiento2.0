import logging
from app import create_app
from extensions import db
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_updates.log'),
        logging.StreamHandler()
    ]
)

app = create_app()

def update_table(conn, table_name, date_field='created_at'):
    """
    Actualiza los registros NULL en el campo de fecha especificado para una tabla.
    Retorna el número de registros actualizados.
    """
    try:
        result = conn.execute(
            text(f'UPDATE {table_name} SET {date_field} = :date WHERE {date_field} IS NULL'),
            {'date': datetime.utcnow()}
        )
        return result.rowcount
    except SQLAlchemyError as e:
        logging.error(f"Error actualizando tabla {table_name}: {str(e)}")
        return 0

def update_database():
    """
    Actualiza los campos de fecha NULL en todas las tablas relevantes.
    """
    tables_to_update = [
        'repairs',
        'repair_parts',
        'parts',
        'users'
    ]
    
    total_updates = 0
    
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                for table in tables_to_update:
                    rows_updated = update_table(conn, table)
                    if rows_updated > 0:
                        logging.info(f"Actualizados {rows_updated} registros en la tabla {table}")
                        total_updates += rows_updated
                
                try:
                    conn.commit()
                    if total_updates > 0:
                        logging.info(f"Total de registros actualizados: {total_updates}")
                    else:
                        logging.info("No se encontraron registros para actualizar")
                except SQLAlchemyError as e:
                    conn.rollback()
                    logging.error(f"Error al hacer commit de las actualizaciones: {str(e)}")
                    raise
                
    except Exception as e:
        logging.error(f"Error general durante la actualización: {str(e)}")
        raise
    
    return total_updates

if __name__ == '__main__':
    try:
        records_updated = update_database()
        if records_updated > 0:
            print(f"\nActualización completada. Total de registros actualizados: {records_updated}")
        else:
            print("\nNo se requirieron actualizaciones en la base de datos.")
    except Exception as e:
        print(f"\nError durante la actualización de la base de datos: {str(e)}")
        exit(1)
