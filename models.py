import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, Integer, BigInteger, ARRAY, String

db = SQLAlchemy()

class Jobs(db.Model):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    requirements = Column(String)
    company = Column(String)


    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}



class Interviews(db.Model):
    __tablename__ = 'interviews'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, db.ForeignKey('jobs.id'))
    messages = Column(String)


    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


