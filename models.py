from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # user, developer, seller
    phone = Column(String, nullable=True)
    listings = relationship("Listing", back_populates="seller")

class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True, index=True)
    kv_img = Column(String)  # путь к изображению или base64, если blob не нужен
    kv_name = Column(String)
    kv_zastr = Column(Text)  # инфа о продавце
    kv_stoim = Column(Float)
    kv_rayon = Column(String)
    kv_adres = Column(String)
    kv_about = Column(Text)
    kv_condition = Column(String)  # аренда/продажа
    kv_rule = Column(Text)
    title = Column(String)
    description = Column(Text)
    price = Column(Float)
    address = Column(String)
    region = Column(String)
    seller_id = Column(Integer, ForeignKey("users.id"))
    seller = relationship("User", back_populates="listings")
    images = relationship("Image", back_populates="listing")
    rooms = Column(String)
    area = Column(Float)
    floor = Column(String)
    kitchen_area = Column(Float)
    living_area = Column(Float)
    sanuzel = Column(String)
    remont = Column(String)
    mebel = Column(String)
    tehnika = Column(String)
    internet_tv = Column(String)
    balkon_lodjiya = Column(String)
    room_type = Column(String)
    zalog = Column(Float)
    komissiya = Column(Float)
    po_schetchikam = Column(String)
    other_zhku = Column(String)
    floors_total = Column(Integer)
    passenger_lift = Column(Integer)
    cargo_lift = Column(Integer)
    ceiling_height = Column(String)
    bathroom = Column(String)
    windows = Column(String)
    finish = Column(String)
    sale_type = Column(String)
    balcony = Column(String)
    participation_type = Column(String)
    completion_date = Column(String)
    building_type = Column(String)
    yard = Column(String)
    parking = Column(String)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    listing = relationship("Listing", back_populates="images")

class Inflation(Base):
    __tablename__ = "inflation"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    month = Column(Integer)
    rate = Column(Float) 

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sender = Column(String)  # 'user' или 'ai'
    message = Column(Text)
    timestamp = Column(String)  # Можно заменить на DateTime
    user = relationship("User") 

class CalendarSlot(Base):
    __tablename__ = "calendar_slots"
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    date = Column(String, index=True)  # YYYY-MM-DD
    time = Column(String, index=True)  # HH:MM
    is_booked = Column(Boolean, default=False)
    listing = relationship("Listing")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"))
    slot_id = Column(Integer, ForeignKey("calendar_slots.id"))
    created_at = Column(String)
    user = relationship("User")
    listing = relationship("Listing")
    slot = relationship("CalendarSlot") 