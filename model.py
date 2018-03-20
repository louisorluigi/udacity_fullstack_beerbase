import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String)

class BeerType(Base):
    __tablename__='BeerType'
    id = Column(Integer, primary_key=True)
    type = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship(User)
    Beer = relationship('Beer', cascade='all, delete-orphan')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'type': self.type,
        }

class Beer(Base):
    __tablename__='Beer'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    type_id = Column(Integer, ForeignKey('BeerType.id'))
    type = relationship(BeerType)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type_id': self.type_id,
        }
engine = create_engine('sqlite:///beerbase.db')

Base.metadata.create_all(engine)
