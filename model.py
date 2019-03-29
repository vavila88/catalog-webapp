#!/usr/bin/python

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# User table constants
UNAME_MAX = 32
EMAIL_MAX = 32

# Category table constants
CAT_NAME_MAX = 32

# Item table constants
ITEM_TITLE_MAX = 32
NUM_SLUG_CHARS = 5
ITEM_SLUG_MAX = ITEM_TITLE_MAX + NUM_SLUG_CHARS

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
    # create an index on the users to speed up user search
    uname = Column(String(UNAME_MAX), index=True)
    email = Column(String(EMAIL_MAX))

    @property
    def serialize(self):
        return {
                'id':self.id,
                'uname':self.uname,
                'email':self.email,
                }


class Category(Base):
    """
    """
    __tablename__='category'
    id = Column(Integer, primary_key=True)
    name = Column(String(CAT_NAME_MAX))

    @property
    def serialize(self):
        return {
                'id':self.id,
                'name':self.name,
                }


class Item(Base):
    """
    Item - table used to hold an instance of an item inserted into the catalog.
    Item name uniqueness is enforced in the table.
    An item contains the following fields
        id - primary key for the items in the table.
        title - name of the item
        category - category the item falls under, e.g., "electronics"
        desc - description of the item
        created_by - a reference to an entry in the User table establishing a
            creator-item relationship
    """
    __tablename__='item'
    __table_args__=tuple(UniqueConstraint('slug'))
    id = Column(Integer, primary_key=True)
    title = Column(String(ITEM_TITLE_MAX))
    description = Column(String)
    cat_id = Column(Integer, ForeignKey('category.id'))
    slug = Column(String(ITEM_SLUG_MAX))

    category = relationship(Category)

    @property
    def serialize(self):
        return {
                'id':self.id,
                'title':self.title,
                'description':self.description,
                'cat_id':self.cat_id,
                'slug':self.slug
                }


engine = create_engine('sqlite:///catalog.db')
# This line actually creates the database on disk from the definitions above.
Base.metadata.create_all(engine)

