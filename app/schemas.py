"""Esquemas Pydantic v2 (DTOs) de SplitMate API.

El dinero entra como número o como texto ("150.00") y sale siempre como
texto con 2 decimales para que ningún cliente lo convierta a float.
"""

import unicodedata
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    computed_field,
    field_validator,
)

from app.money import split_evenly, to_money
from app.names import clean_name, has_hidden_chars

SUPPORTED_CURRENCIES = frozenset({"USD", "EUR", "GTQ", "MXN"})
MAX_MONEY = Decimal("100000.00")

ExpenseCategory = Literal["food", "transport", "lodging", "activities", "other"]


def _clean_text(value: str) -> str:
    if has_hidden_chars(value):
        raise ValueError("Contiene caracteres de control o invisibles")
    return " ".join(unicodedata.normalize("NFC", value).split())


def _person_name(value: str) -> str:
    if has_hidden_chars(value):
        raise ValueError("El nombre contiene caracteres de control o invisibles")
    cleaned = clean_name(value)
    if not 2 <= len(cleaned) <= 40:
        raise ValueError("El nombre debe tener entre 2 y 40 caracteres")
    return cleaned


def _currency_code(value: str) -> str:
    code = value.strip().upper()
    if code not in SUPPORTED_CURRENCIES:
        raise ValueError("Moneda no soportada; usa USD, EUR, GTQ o MXN")
    return code


def _description(value: str) -> str:
    cleaned = _clean_text(value)
    if len(cleaned) < 3:
        raise ValueError("La descripción debe tener al menos 3 caracteres")
    return cleaned


def _unique_people(people: list[str]) -> list[str]:
    if len(set(people)) != len(people):
        raise ValueError("La lista no puede repetir participantes")
    return people


def _money_text(value: Decimal) -> str:
    return "0.00" if value == 0 else f"{to_money(value):.2f}"


PersonName = Annotated[str, Field(max_length=60), AfterValidator(_person_name)]
CurrencyCode = Annotated[str, Field(max_length=8), AfterValidator(_currency_code)]
Description = Annotated[str, Field(max_length=120), AfterValidator(_description)]
People = Annotated[
    list[PersonName],
    Field(min_length=1, max_length=20),
    AfterValidator(_unique_people),
]
Money = Annotated[
    Decimal,
    Field(gt=0, le=MAX_MONEY, max_digits=8, decimal_places=2),
    AfterValidator(to_money),
]
MoneyText = Annotated[
    Decimal,
    PlainSerializer(_money_text, return_type=str),
]


class TripCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=3, max_length=80)
    default_currency: CurrencyCode = "USD"
    participants: Annotated[People, Field(min_length=2)]

    @field_validator("name")
    @classmethod
    def clean_trip_name(cls, value: str) -> str:
        cleaned = _clean_text(value)
        if len(cleaned) < 3:
            raise ValueError("Mínimo 3 caracteres")
        return cleaned


class TripResponse(BaseModel):
    id: str
    name: str
    default_currency: str
    participants: list[str]
    created_at: datetime
    expense_count: int
    total_spent: MoneyText


class ExpenseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: Description
    amount: Money = Field(examples=["150.00"])
    currency: CurrencyCode = "USD"
    category: ExpenseCategory = "other"
    paid_by: PersonName
    split_among: People


class ExpenseResponse(BaseModel):
    id: str
    trip_id: str
    description: str
    amount: MoneyText
    currency: str
    category: ExpenseCategory
    paid_by: str
    split_among: list[str]
    created_at: datetime
    updated_at: datetime | None = None

    @computed_field
    @property
    def shares(self) -> dict[str, MoneyText]:
        return split_evenly(self.amount, self.split_among)


class SettlementTransfer(BaseModel):
    from_participant: str
    to_participant: str
    amount: MoneyText
    currency: str


class SettlementSummaryResponse(BaseModel):
    trip_id: str
    currency: str
    total_spent: MoneyText
    net_balances: dict[str, MoneyText]
    transfers: list[SettlementTransfer]
