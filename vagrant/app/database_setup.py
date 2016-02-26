import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class Categories(Base):

    __tablename__ = 'categories'

    name = Column(String(64), nullable=False)
    id = Column(Integer, primary_key=True)
    items = relationship('Items', backref='categories', passive_deletes=True)


class Items(Base):

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(String(240))
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'))


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)