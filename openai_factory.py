import json
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
    return {'content': response.choices[0].message.content, 'prompt_tokens': response.usage.prompt_tokens, 'completion_tokens': response.usage.completion_tokens}

@openai_bp.route('/job_questions', methods=['GET', 'POST'])
def sample_job_questions():
    if request.method == 'POST':
        question_index = request.form['prompt']
        gpt_questions = get_job_questions(question_index=question_index)
        return render_template('openai_job_questions.html', prompt=question_index, generated_text=gpt_questions)
    return render_template('openai_job_questions.html')

def get_job_questions(job, interview, generate_answer=False):
    messages = complete_prompt(job, interview, generate_answer=generate_answer)
    gpt_questions = request_openai_api(messages)
    return gpt_questions

def complete_prompt(job, interview, generate_answer=False):
    
    title = job.title
    company = job.company
    requirements = job.requirements
    messages = json.loads(interview.messages)

    base_prompt = f"""You are a hiring manager ChatBot for company {company} interviewing a potential hire for the position of {title}. \
            Your name is Gary. For the whole conversation, ASK ONE QUESTION AT A TIME. You will ask them a sequence of questions, outlined below."""
    
    questions =      [
        f"The first thing you should do is greet the candidate and thank them for meeting with you, \
                tell them a little about the job they will be interviewing for \
                then ask them to introduce themselves. ",
        f"You then ask them to tell you about their experience and why they are \
                interested in the position.",
        f"Pick a requirement from this list of skills: {requirements} Ask them about their experience with this requirement.",
        f"Pick a second, different skill from {requirements} that wasn't previously discussed. Ask them about their level of expertise with this item.",
        f"Next ask a behavioral question: Behavioral questions ask the candidate to describe a past experience \
            An example of a behavioral question is 'Tell me about a time when you developed and executed a marketing strategy.'",
        f"Ask a follow up question that requires the candidate to go into specifics from their answer before.",
        f"Almost done! Next ask a hypothetical question: Hypothetical questions ask the candidate to describe how they would handle a hypothetical situation \
                An example of a hypothetical question is 'How would you develop and execute a marketing strategy?'",
        f"Ask a follow up question that requires the candidate to go into specifics about their plan to deal with the hypothetical sitaution.",
        f"Finish the interview with by asking them if they have any questions for {company}.\
            If they do, answer their questions. \
            If they don't, thank them for their time and end the interview. ",
    ]
    
    for i,question in enumerate(questions):
        base_prompt += f'question {i} start. {question} --- '

    context = [{
        "role": "system",
        "content": base_prompt
    }]

    interview.base_prompt = json.dumps(context)

    maybe_completed = len(messages)//2 > len(questions)
    completed_text = "Answer their question and then include 'the interview is completed' in the response. Provide some feedback on how their interview went and rate them 1-10"
    intermediate_text = "Ask the question to continue the interview using the interview sequence given. Only respond with the question. Do not tell the user what question they are on"
    maybe_completed_text = intermediate_text if not maybe_completed else completed_text
    contents = [x['content'] for x in messages]
    if generate_answer:
        action = [{
            "role": "user",
            "content": f"The interview is partially complete. Here is the current interview log: {'... '.join(contents)}. For reference you are on question {len(contents)//2} \
                {maybe_completed_text.replace('question', 'answer')} \
                Try to provide a typical user answer to the last question asked. Basically pretend to be the user for this response. The last question was {contents[-1]} "
        }]
    else:
        action = [{
            "role": "user",
            "content": f"The interview is partially complete. Here is the current interview log: {'... '.join(contents)}. For reference you are on question {len(contents)//2} \
                {maybe_completed_text} "
        }] 

    context.extend(action)


    # print('using context', context)
    return context

from models import db, Interviews
import json
@openai_bp.cli.command("do_test")
def do_conversation():
    # do a mock conversation, count the costs, report the results
    
    # pick a job
    job = Jobs.query.first()
    
    messages = []
    interview = Interviews(job_id=job.id, messages=json.dumps(messages), prompt_tokens=0, completion_tokens=0)
    db.session.add(interview)
    db.session.commit()

    while len(messages) < 20:
        # get question
        question = get_job_questions(job, interview)
        bot_message = {
            'content': question['content'],
            'source': 'bot'
        }
        messages.append(bot_message)
        interview.prompt_tokens += question['prompt_tokens']
        interview.completion_tokens += question['completion_tokens']
        interview.messages = json.dumps(messages)
        db.session.commit()

        # generate answer
        answer = get_job_questions(job, interview, generate_answer=True)
        user_message = {
            'content': answer['content'],
            'source': 'user'
        }
        messages.append(user_message)
        interview.prompt_tokens += answer['prompt_tokens']
        interview.completion_tokens += answer['completion_tokens']
        interview.messages = json.dumps(messages)
        db.session.commit()

        if 'interview is completed' in answer['content'].lower() or 'interview completed' in question['content'].lower():
            break
    
    print('======= printing out messages ========')
    for message in messages:
        print('----->', message)
    
    cost_rate = 0.0015
    total_tokens = interview.prompt_tokens + interview.completion_tokens
    print(f'total token usage: {interview.prompt_tokens}-{interview.completion_tokens} over {len(messages)} messages. cost: {cost_rate*total_tokens/1000}')
