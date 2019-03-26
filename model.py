#!/usr/bin/python

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Item(Base):
    __tablename__='item'

class User(Base):
    __tablename__='user'

engine = create_engine('mysql:///catalog.db')
Base.metadata.create_all(engine)

