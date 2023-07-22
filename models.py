import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Float, Integer, BigInteger, ARRAY, String, Boolean

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
    base_prompt = Column(String)
    completed = Column(Boolean)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)


    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}



def startup_load(app, db):
    with app.app_context():
        db.create_all()

        # Load initial data for Jobs table
        initial_jobs_data = [{"title": "Developer", "requirements": "flask,git,html,css", "company": "yahoo"},
            {"title": "Project Manager", "requirements": "jira,quality assurance,conflict/resolution", "company": "google"},
            {"title": "DevOps Engineer", "requirements": "kubernetes,docker,ansible", "company": "facebook"}
        ]
        
        for job_data in initial_jobs_data:
            existing_job = Jobs.query.filter(Jobs.title==job_data['title']).first()
            if not existing_job:
                job = Jobs(**job_data)
                db.session.add(job)
        
        db.session.commit()