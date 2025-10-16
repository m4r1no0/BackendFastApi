from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ProduccionHuevosBase(BaseModel):
    id_galpon: int = Field(..., gt=0)
    cantidad: int = Field(..., ge=0)
    fecha: date
    id_tipo_huevo: int = Field(..., gt=0)

class ProduccionHuevosCreate(ProduccionHuevosBase):
    pass

class ProduccionHuevosUpdate(BaseModel):
    id_galpon: Optional[int] = Field(default=None, gt=0)
    cantidad: Optional[int] = Field(default=None, ge=0)
    fecha: Optional[date] = None
    id_tipo_huevo: Optional[int] = Field(default=None, gt=0)

class ProduccionHuevosOut(ProduccionHuevosBase):
    id_produccion: int
