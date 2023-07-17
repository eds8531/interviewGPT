from flask import Flask, render_template, request, Blueprint
import openai
import os

from models import Jobs

# Set up the API endpoint and your API key
API_KEY = os.getenv('OPENAI_APIKEY')
openai.api_key = API_KEY

openai_bp = Blueprint('openai', __name__)

@openai_bp.route('/openai_test', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prompt = request.form['prompt']
        messages = [{"role": "user", "content": prompt}]
        generated_text = request_openai_api(messages)
        return render_template('openai.html', prompt=prompt, generated_text=generated_text)
    return render_template('openai.html')

def request_openai_api(messages):
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    print(response)
    return response.choices[0].message.content

@openai_bp.route('/job_questions', methods=['GET', 'POST'])
def sample_job_questions():
    if request.method == 'POST':
        question_index = request.form['prompt']
        gpt_questions = get_job_questions(question_index=question_index)
        return render_template('openai_job_questions.html', prompt=question_index, generated_text=gpt_questions)
    return render_template('openai_job_questions.html')

def get_job_questions(job='developer', company='yahoo', requirements='git,flask', question_index=1, messages=None, generate_answer=False):
    messages = complete_prompt(job, company, requirements, question_index=question_index, messages=messages, generate_answer=generate_answer)
    gpt_questions = request_openai_api(messages)
    return gpt_questions

def complete_prompt(job, company, requirements, question_index=1, messages=None, generate_answer=False):
    
    context = [{
        "role": "system",
        "content": f"""You are a hiring manager ChatBot for company {company} interviewing \
                a potential hire for the position of {job}. \
            Your name is Gary. \
            For the whole conversation, only ask one question per text box. \
            You will ask them a total of 8 questions, outlined below.\
            1. You first greet the candidate and thank them for meeting with you, \
                tell them a little about the job they will be interviewing for \
                then ask them to introduce themselves. \
            2. You then ask them to tell you about their experience and why they are \
                interested in the position.\
            3. Pick a requirement from this list of skills: {requirements} Ask them about their experience with this requirement. \
            4. Pick a second, different skill from {requirements} that wasn't previously discussed. Ask them about their level of expertise with this item. \
            5. Ask a behavioral question: Behavioral questions ask the candidate to describe a past experience \
                An example of a behavioral question is "Tell me about a time when you developed and executed a marketing strategy." \
            6. Ask a follow up question that requires the candidate to go into specifics from their answer before.
            7. Ask a hypothetical question: Hypothetical questions ask the candidate to describe how they would handle a hypothetical situation \
                An example of a hypothetical question is "How would you develop and execute a marketing strategy?" \
            8. Ask a follow up question that requires the candidate to go into specifics about their plan to deal with the hypothetical sitaution.
            9. Ask them if they have any questions for {company}.
                If they do, answer their questions. \
                If they don't, thank them for their time and end the interview. \   
                """
    }]

    if messages:
        conversation = [{
            "role": "system",
            "content": f"The interview is partially complete. Here is the current interview log: {'... '.join(messages)}"
        }]
        context.extend(conversation)

    if question_index < 10:
        action = [{
            "role": "user",
            "content": f"please provide interview question number {question_index}. Please only respond with the question number and the question itself. "
            
        }]

    else:
        action = [{
            "role": "user",
            "content": f"Try to answer their questions if they have any. Then thank them for their time. Then provide positive encouragement on what was good about \
                        their answers. Then provide one specific criticism on something they could improve for their answers. Then rate their interview skills on a \
                        1-10 scale with 1 as terrible and 10 as well informed and amazing communication. If the applicant gave extremely short answers, you should not \
                        rate them above a 3. If the applicant did not elaborate with specific details they can't be rated above a 5. Be a very harsh grader with the rating. "
        }]

    if generate_answer:

        action = [{
            "role": "user",
                        "content": f"Try to provide a typical user answer to the last question asked. Basically pretend to be the user for this response. "
        }]
        
    context.extend(action)


    print('using context', context)
    return context

from models import db, Interviews
import json
@openai_bp.cli.command("do_test")
def do_conversation():
    # do a mock conversation, count the costs, report the results
    
    # pick a job
    job = Jobs.query.first()
    
    messages = []
    interview = Interviews(job_id=job.id, messages=json.dumps(messages))
    db.session.add(interview)
    db.session.commit()

    question_index = 1
    while len(messages) < 6:
        # get question
        question = get_job_questions(job=job.title, company=job.company, requirements=job.requirements, messages=messages, question_index=question_index)
        messages.append(question)

        # generate answer
        answer = get_job_questions(job=job.title, company=job.company, requirements=job.requirements, 
                                     messages=messages, question_index=question_index,
                                     generate_answer=True)
        messages.append(answer)
        interview.messages = json.dumps(messages)
        db.session.commit()
        question_index += 1
    
    print(messages)
