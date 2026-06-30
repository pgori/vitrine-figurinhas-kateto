from sqlmodel import Field, SQLModel


class LeadCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    desired_item: str = Field(min_length=1, max_length=180)
    phone: str = Field(min_length=1, max_length=40)

