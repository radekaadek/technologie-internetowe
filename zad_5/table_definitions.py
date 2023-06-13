from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy import String, DateTime
from sqlalchemy.orm import relationship

Base = declarative_base()


class Clan(Base):
    __tablename__ = 'clan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    tag = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    is_admin = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=False)
    clan_id = Column(Integer, ForeignKey('clan.id'))
    server_id = Column(Integer, ForeignKey('server.id'))
    achievements = relationship('PlayerAchievement', backref='player')


class Server(Base):
    __tablename__ = 'server'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    ip = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey('player.id'))


class Achievement(Base):
    __tablename__ = 'achievement'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
