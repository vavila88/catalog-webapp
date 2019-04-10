#!/usr/bin/python

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# timeout token implementation
import random
import string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer,
                         BadSignature, SignatureExpired)

# User table constants
UNAME_MAX = 32
EMAIL_MAX = 32

# Category table constants
CAT_NAME_MAX = 32

# Item table constants
ITEM_TITLE_MAX = 32
NUM_SLUG_CHARS = 5
ITEM_SLUG_MAX = ITEM_TITLE_MAX + NUM_SLUG_CHARS

Base = declarative_base()

# key used to create a timeout token
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                     for x in xrange(32))


class User(Base):
    """
    User - table used to store all registered users of this web app.
    A user contains the following information fields
        id - primary key for the user
        uname - the users name
        email - the email registered to this user
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    # create an index on the users to speed up user search
    uname = Column(String(UNAME_MAX))
    email = Column(String(EMAIL_MAX), index=True)
    picture = Column(String)

    def gen_auth_token(self, expiration=600):
        """
        gen_auth_token - generates a simple timeout token for a users session
        """
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id':self.id})

    # static method on this ORM object to verify an auth token.
    @staticmethod
    def verify_auth_token(token):
        """
        verify_auth_token - verifies the user token to ensure that the timeout
        hasn't elapsed
        """
        s = Serializer(secret_key)
        try: # attempt to extract the encrypted user id from the token
            data = s.loads(token)
        except SignatureExpired:# expired token - invalid
            return False
        except BadSignature:# tampered token - invalid
            return False

        # return the id on successful token decryption
        return data['id']

    @property
    def serialize(self):
        return {
                'id': self.id,
                'uname': self.uname,
                'email': self.email,
                }


class Category(Base):
    """
    """
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(CAT_NAME_MAX))
    slug = Column(String)

    @property
    def serialize(self):
        return {
                'slug': self.slug,
                'name': self.name,
                'id': self.id,
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
    __tablename__ = 'item'
    __table_args__ = tuple(UniqueConstraint('slug'))
    id = Column(Integer, primary_key=True)
    title = Column(String(ITEM_TITLE_MAX))
    description = Column(String)
    cat_id = Column(Integer, ForeignKey('category.id'))
    slug = Column(String(ITEM_SLUG_MAX))

    category = relationship(Category)

    @property
    def serialize(self):
        return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'cat_id': self.cat_id,
                'slug': self.slug
                }


engine = create_engine('sqlite:///catalog.db')
# This line actually creates the database on disk from the definitions above.
Base.metadata.create_all(engine)
