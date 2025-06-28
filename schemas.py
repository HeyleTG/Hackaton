from pydantic import BaseModel
from typing import List, Optional

class Image(BaseModel):
    id: int
    url: str
    class Config:
        from_attributes = True

class ListingBase(BaseModel):
    kv_img: Optional[str] = None
    kv_name: Optional[str] = None
    kv_zastr: Optional[str] = None
    kv_stoim: Optional[float] = None
    kv_rayon: Optional[str] = None
    kv_adres: Optional[str] = None
    kv_about: Optional[str] = None
    kv_condition: Optional[str] = None
    kv_rule: Optional[str] = None
    title: str
    description: str
    price: float
    address: str
    region: str
    rooms: int
    area: float
    floor: int
    kitchen_area: float
    living_area: float
    sanuzel: str
    remont: str
    mebel: str
    tehnika: str
    internet_tv: str
    balkon_lodjiya: str
    room_type: str
    zalog: float
    komissiya: float
    po_schetchikam: str
    other_zhku: str

class ListingCreate(ListingBase):
    pass

class Listing(ListingBase):
    id: int
    seller_id: int
    images: List[Image] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: str
    role: str
    phone: str | None = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    listings: List[Listing] = []
    class Config:
        from_attributes = True

class Inflation(BaseModel):
    id: int
    year: int
    month: int
    rate: float
    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    sender: str
    message: str
    timestamp: str

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessage(ChatMessageBase):
    id: int
    class Config:
        from_attributes = True

class CalendarSlotBase(BaseModel):
    listing_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    is_booked: bool = False

class CalendarSlotCreate(CalendarSlotBase):
    pass

class CalendarSlotOut(CalendarSlotBase):
    id: int
    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    user_id: int
    listing_id: int
    slot_id: int
    created_at: str

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: int
    class Config:
        orm_mode = True 