from pydantic import BaseModel


class SeatResponse(BaseModel):
    id: int
    row: int
    col: str
    seat_number: str
    seat_class: str
    status: str = "AVAILABLE"

    class Config:
        from_attributes = True
