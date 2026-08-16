from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum as en

from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Enum, Field, Relationship, SQLModel

SQLModel.metadata.clear()

class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=2)
    email: str = Field(unique=True, nullable=False)
    saldo_actual: Decimal = Field(default=0.00, max_digits=12, decimal_places=2)
    telefono: str | None = Field(unique=True, default=None, max_length=20)
    ciudad: str | None = Field(default=None)
    
    transacciones: list["Transaccion"] = Relationship(back_populates="cliente")
    contactos: list["Contacto"] = Relationship(back_populates="cliente")

    def __repr__ (self):
        return f"Cliente {self.id} - {self.nombre} ({self.email},{self.telefono})"

# Class that determines the cashflow of the transaction.
class Direction (str, en): 
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"

class Transaccion(SQLModel, table=True):
    __tablename__ = "transacciones"
    
    id: int | None = Field(default=None, primary_key=True)
    direction: Direction = Field(sa_column=Column(Enum(Direction)))
    monto: Decimal = Field(gt=0 ,max_digits=12, decimal_places=2)
    categoria: str|None = Field(default = None)
    detalles: str | None = Field(default=None) # Ej: "Pago de alquiler", "Bizum"
    fecha: datetime = Field(default_factory=lambda: datetime.now(UTC),
                            nullable=False)

    cliente_id: int = Field(foreign_key="clientes.id")
    cliente: Cliente = Relationship(back_populates="transacciones")

    def __repr__(self):
        return f"Transacción {self.id} - {self.monto},{self.detalles},{self.categoria} ({self.fecha})"

class FAQ(SQLModel, table=True):
    __tablename__ = "faqs"

    id: int|None = Field(default=None, primary_key=True)
    pregunta: str
    respuesta: str
    embedding: list[float] = Field(sa_column=Column(Vector(1536), nullable=False))

    def __repr__(self):
        return f"Question: {self.pregunta}\nAnswer: {self.respuesta}"

class Contacto(SQLModel, table=True):
    __tablename__ = "contactos"

    id: int|None = Field(default=None, primary_key=True)
    nombre: str|None = Field(default=None)
    tel: str = Field(unique=True)

    cliente_id: int = Field(foreign_key="clientes.id")
    cliente: Cliente = Relationship(back_populates="contactos")

    def __repr__ (self):
        return f"<Contacto {self.nombre} ({self.tel})>"