from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, ForeignKey, Float, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC, date
from typing import Optional, List, Dict, Any

db = SQLAlchemy()

# Tabla de asociación para la relación muchos a muchos entre User y Restaurant
# Esta tabla permite que un usuario pueda marcar varios restaurantes como favoritos
user_favorite = Table(
    "user_favorite",
    db.metadata,
    Column("user_id", ForeignKey('User.user_id'), primary_key=True),
    Column('restaurant_id', ForeignKey('Restaurant.restaurant_id'), primary_key=True)
)

# Tabla de asociación para la relación muchos a muchos entre Dish y Tag
# Esta tabla permite que un plato pueda tener múltiples etiquetas y una etiqueta pueda aplicarse a múltiples platos
dish_tag = Table(
    "dish_tag",
    db.metadata,
    Column("dish_id", ForeignKey("Dish.dish_id"), primary_key=True),
    Column("tag_id", ForeignKey("Tag.tag_id"), primary_key=True)
)
    

class User(db.Model):
    __tablename__ = 'User'
    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), default="user")
    create_at: Mapped[date] = mapped_column(Date(), nullable=False, default=datetime.now(UTC))

#Relacion de uno a muchos 
    restaurants: Mapped[List["Restaurant"]] = relationship("Restaurant", back_populates="owner")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="user")
    reservations: Mapped[List["Reservation"]] = relationship("Reservation", back_populates="user")
    favorites: Mapped[List["Restaurant"]] = relationship("Restaurant", secondary=user_favorite, back_populates="fans")
    payment: Mapped[List["Payment"]] = relationship("Payment", back_populates="user")   

    def serialize(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,            
            "email": self.email,
            # do not serialize the password, its a security breach
            "is_active": self.is_active,
            "avatar_url": self.avatar_url,
            "role": self.role, 
            "create_at": self.create_at
        }

class Restaurant(db.Model):
    __tablename__ = 'Restaurant'
    restaurant_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(200))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    owner_id: Mapped[int] = mapped_column(ForeignKey('User.user_id'), nullable=False)
    photos: Mapped[Optional[Dict[str, Any]]] = mapped_column(db.JSON) #Ej: ['photo1.jpg, 'photo2.jpg]
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)

    #Relaciones de uno a muchos
    owner: Mapped['User'] = relationship('User', back_populates='restaurants')
    dishes: Mapped[List['Dish']] = relationship('Dish', back_populates='restaurant')
    reviews: Mapped[List['Review']] = relationship('Review', back_populates='restaurant')
    reservations: Mapped[List['Reservation']] = relationship('Reservation', back_populates='restaurant')
    fans: Mapped[List['User']] = relationship('User', secondary=user_favorite, back_populates='favorites')

class Dish(db.Model):
    __tablename__ = 'Dish'
    dish_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float)
    photos: Mapped[Optional[Dict[str, Any]]] = mapped_column(db.JSON) #Ej: ['photo1.jpg, 'photo2.jpg]
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('Restaurant.restaurant_id'), nullable=False)
    
    #Relaciones
    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='dishes')
    tags: Mapped[List['Tag']] = relationship('Tag', secondary=dish_tag, back_populates='dishes')

class Tag(db.Model):
    __tablename__ = 'Tag'
    tag_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    #Relacion con dishes
    dishes: Mapped[List['Dish']] = relationship('Dish', secondary=dish_tag, back_populates='tags')

class Review(db.Model):
    __tablename__ = 'Review'
    review_id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False) # 1-5
    comment: Mapped[Optional[str]] = mapped_column(String(200))
    photos: Mapped[Optional[Dict[str, Any]]] = mapped_column(db.JSON) 
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('Restaurant.restaurant_id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id'), nullable=False)
    created_at: Mapped[date] = mapped_column(Date(), nullable=False, default=datetime.now(UTC))

    #Relaciones de uno a muchos
    user: Mapped['User'] = relationship('User', back_populates='reviews')
    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='reviews')

class Reservation(db.Model):
    __tablename__ = 'Reservation'
    reservation_id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[date] = mapped_column(Date(), nullable=False)
    guests: Mapped[int] = mapped_column(nullable=False)
    special_request: Mapped[Optional[str]] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(default='pending') # 'pending', 'confirmed', 'canceled'
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id'), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('Restaurant.restaurant_id'), nullable=False)
    created_at: Mapped[date] = mapped_column(Date(), nullable=False, default=datetime.now(UTC))

    #Relaciones de uno a muchos
    user: Mapped['User'] = relationship('User', back_populates='reservations')
    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='reservations')
    payment: Mapped[Optional['Payment']] = relationship('Payment', back_populates='reservation')

class Payment(db.Model):
    __tablename__ = 'Payment'
    payment_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False) # 'credit_card', 'paypal', etc.
    status: Mapped[str] = mapped_column(String(20), nullable=False) # 'pending', 'completed', 'failed'
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey('Reservation.reservation_id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('User.user_id'), nullable=False)
    created_at: Mapped[date] = mapped_column(Date(), nullable=False, default=datetime.now(UTC))

    #Relaciones de uno a uno 
    user: Mapped['User'] = relationship('User', back_populates='payment')
    reservation: Mapped['Reservation'] = relationship('Reservation', back_populates='payment')