from datetime import date
from sqlalchemy import String, Date, Integer, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    firstname: Mapped[str] = mapped_column(String(25), index=True)
    surname: Mapped[str] = mapped_column(String(25), index=True)
    email: Mapped[str] = mapped_column(String(50), index=True)
    phone: Mapped[str] = mapped_column(String(20), index=True)
    birthday: Mapped[Date] = mapped_column(Date)
    details: Mapped[str | None] = mapped_column(String(150), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    user: Mapped['User'] = relationship('User', backref='contacts', lazy='joined')



class User(Base):
    __tablename__= 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)