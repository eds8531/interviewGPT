import json
import openai
from flask import Flask, render_template, request, redirect
import os
from openai_factory import get_job_questions, openai_bp
from models import Interviews, Jobs, db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'not-a-very-secure-key'

db.init_app(app)

app.register_blueprint(openai_bp)

openai.api_key = os.getenv('OPENAI_APIKEY')

@app.route('/', methods=['GET', 'POST'])
def interview():
    if request.method == 'POST':
        job = Jobs(title=request.form['title'], requirements=request.form['requirements'], company=request.form['company'])
        db.session.add(job)
        db.session.commit()
    jobs = [{**x.as_dict(), 'interview_link': f'/create_interview?job_id={x.id}'} for x in Jobs.query.all()]
    return render_template('index.html', jobs=jobs)
    
@app.route('/create_interview')
def create_interview():
    job_id = int(request.args.get('job_id'))
    job = Jobs.query.filter(Jobs.id==job_id).first()
    interview = Interviews(job_id=job.id, messages=json.dumps([]), completion_tokens=0, prompt_tokens=0)
    db.session.add(interview)
    db.session.commit()
    return redirect(f'/interview?id={interview.id}')

@app.route('/interview', methods=['GET','POST'])
def conduct_interview():

    interview_id = int(request.args.get('id'))
    print('querying for interview id', interview_id)
    job, interview = db.session.query(Jobs, Interviews)\
        .filter(Jobs.id==Interviews.job_id)\
        .filter(Interviews.id==interview_id)\
        .first()
    

    if request.method == 'POST':
        print(interview, interview.as_dict())
        messages = json.loads(interview.messages)
        messages.append(request.form['answer'])
        interview.messages = json.dumps(messages)
        db.session.commit()
    
    # do integer division (divide by 2 and round down)
    # e.g 7 // 2 = 3, 4 // 2 = 2, 1 // 2 = 0
    # add 1 because "question_index" starts at 1 
    messages = []
    if interview.messages:
        messages = json.loads(interview.messages)

    question = get_job_questions(job, interview)
    
    messages.append(question['content'])
    interview.messages = json.dumps(messages)
    db.session.commit()

    messages = json.loads(interview.messages)
    return render_template('interview.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')