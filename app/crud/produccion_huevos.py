from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Optional
import logging

from app.schemas.produccion_huevos import ProduccionHuevosCreate, ProduccionHuevosUpdate

logger = logging.getLogger(__name__)

def create_produccion_huevos(db: Session, produccion: ProduccionHuevosCreate) -> Optional[bool]:
    try:
        sentencia = text("""
            INSERT INTO produccion_huevos (
                id_galpon, cantidad, fecha, id_tipo_huevo
            ) VALUES (
                :id_galpon, :cantidad, :fecha, :id_tipo_huevo
            )
        """)
        db.execute(sentencia, produccion.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear produccion_huevos: {e}")
        raise Exception("Error de base de datos al crear la producción de huevos")

def get_produccion_huevos_by_id(db: Session, produccion_id: int):
    try:
        query = text("""
            SELECT 
                ph.id_produccion,
                g.nombre AS nombre_galpon,
                ph.cantidad,
                ph.fecha,
                th.tamaño
            FROM produccion_huevos ph
            JOIN galpones g ON ph.id_galpon = g.id_galpon
            JOIN tipo_huevos th ON ph.id_tipo_huevo = th.id_tipo_huevo
            WHERE ph.id_produccion = :id_produccion;
        """)
        result = db.execute(query, {"id_produccion": produccion_id}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener produccion_huevos por ID: {e}")
        raise Exception("Error de base de datos al obtener la producción de huevos")


def get_all_produccion_huevos(
    db: Session,
    limit: int = 10,
    fecha_inicio: str = None,
    fecha_fin: str = None
):
    """
    Obtiene todas las producciones de huevos con JOINs a galpones y tipo_huevos,
    soportando paginación y filtrado por rango de fechas.

    Parámetros:
        db: sesión activa de SQLAlchemy
        limit: cantidad máxima de registros a devolver
        fecha_inicio: fecha inicial (YYYY-MM-DD) para filtrar registros
        fecha_fin: fecha final (YYYY-MM-DD) para filtrar registros
    """
    try:
        base_query = """
            SELECT 
                produccion_huevos.id_produccion,
                galpones.nombre AS nombre_galpon,
                produccion_huevos.cantidad,
                produccion_huevos.fecha,
                tipo_huevos.tamaño
            FROM produccion_huevos
            LEFT JOIN tipo_huevos 
                ON produccion_huevos.id_tipo_huevo = tipo_huevos.id_tipo_huevo
            LEFT JOIN galpones 
                ON produccion_huevos.id_galpon = galpones.id_galpon
        """

        # Agregar filtro por rango de fechas si se proporcionan ambos parámetros
        params = {"limit": limit}
        if fecha_inicio and fecha_fin:
            base_query += " WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin"
            params["fecha_inicio"] = fecha_inicio
            params["fecha_fin"] = fecha_fin

        # Orden y paginación
        base_query += " ORDER BY produccion_huevos.fecha ASC LIMIT :limit"

        result = db.execute(text(base_query), params).mappings().all()
        return result

    except SQLAlchemyError as e:
        logger.error(f"Error al obtener todas las producciones de huevos: {e}")
        raise Exception("Error de base de datos al obtener las producciones de huevos")
    
def update_produccion_huevos_by_id(db: Session, produccion_id: int, produccion: ProduccionHuevosUpdate) -> Optional[bool]:
    try:
        produccion_data = produccion.model_dump(exclude_unset=True)
        if not produccion_data:
            return False

        set_clauses = ", ".join([f"{key} = :{key}" for key in produccion_data.keys()])
        sentencia = text(f"""
            UPDATE produccion_huevos
            SET {set_clauses}
            WHERE id_produccion = :id_produccion
        """)

        produccion_data["id_produccion"] = produccion_id

        result = db.execute(sentencia, produccion_data)
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar produccion_huevos {produccion_id}: {e}")
        raise Exception("Error de base de datos al actualizar la producción de huevos")
