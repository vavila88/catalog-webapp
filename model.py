#!/usr/bin/python

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    """
    User - table used to store all registered users of this web app.
    A user contains the following information fields
        id - primary key for the user
        uname - the users name
        email - the email registered to this user
    """
    __tablename__='user'
    id = Column(Integer, primary_key=True)
    uname = Column(String(32))
    email = Column(String(32))

    @property
    def serialize(self):
        return {
                'id':self.id,
                'uname':self.uname,
                'email':self.email,
                }


class Item(Base):
    """
    Item - table used to hold an instance of an item inserted into the catalog.
    An item contains the following fields
        id - primary key for the items in the table.
        name - name of the item
        category - category the item falls under, e.g., "electronics"
        desc - description of the item
        created_by - a reference to an entry in the User table establishing a
            creator-item relationship
    """
    __tablename__='item'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    category = Column(String(32))
    desc = Column(String)
    created_by = Column(Integer, ForeignKey('user.id'))

    user = relationship(User)

    @property
    def serialize(self):
        return {
                'id':self.id,
                'name':self.name,
                'category':self.category,
                'created_by':self.created_by
                }


engine = create_engine('sqlite:///catalog.db')
# This line actually creates the database on disk from the definitions above.
Base.metadata.create_all(engine)

