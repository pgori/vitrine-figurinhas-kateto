from datetime import datetime
from enum import Enum
import re

from pydantic import BaseModel, Field, field_validator


class KanbanColumn(str, Enum):
    NO_CONTACT = "Sem Contato"
    IN_CONTACT = "Em Contato"
    LOST = "Perdido"
    FINISHED = "Finalizado"


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    desired_item: str = Field(min_length=1, max_length=180)
    phone: str = Field(min_length=1, max_length=40)

    @field_validator("name", "desired_item", mode="before")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Campo deve ser texto.")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Campo obrigatorio.")

        return normalized_value

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Telefone deve ser texto.")

        digits = re.sub(r"\D", "", value)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Telefone deve ter entre 10 e 15 digitos.")

        return digits


class LeadMove(BaseModel):
    kanban_column: KanbanColumn


class SellerRead(BaseModel):
    id: int
    name: str
    queue_order: int


class LeadCardRead(BaseModel):
    id: int
    name: str
    desired_item: str
    phone: str
    kanban_column: KanbanColumn
    assigned_seller: SellerRead
    created_at: datetime
    updated_at: datetime
