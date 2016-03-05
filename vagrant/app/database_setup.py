from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()

"""
class User(Base):
    __tablename__ = 'user'
    name = Column(String(80), nullable=False)
    email = Column(String(128), nullable=False, unique=True)
    picture = Column(String(250))
    id = Column(Integer, primary_key=True)
    categories = relationship('Categories', backref='user', passive_deletes=True)
    items = relationship('Items', backref='user', passive_deletes=True)

    @property
    def serialize(self):
       Return object data in easily serializeable format
       return {
           'name'         : self.name,
           'email'         : self.email,
           'id'         : self.id,
           'picture'         : self.picture,
       }
"""
class Categories(Base):

    __tablename__ = 'categories'

    name = Column(String(64), nullable=False)
    id = Column(Integer, primary_key=True)
    # user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    items = relationship('Items', backref='categories', passive_deletes=True)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name': self.name,
           'id': self.id,
           'user_id': self.user_id,
       }

class Items(Base):

    __tablename__ = 'items'

    name = Column(String(120), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(240))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))
    # user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name': self.name,
           'id': self.id,
           'description': self.description,
           'category_id': self.category_id,
           'user_id': self.user_id,
       }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)