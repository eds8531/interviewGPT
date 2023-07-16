from flask import Flask, render_template, request, Blueprint
import openai
import os

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

def get_job_questions(job='developer', company='yahoo', requirements='git,flask', question_index=1):
    messages = complete_prompt(job, company, requirements, question_index=question_index)
    gpt_questions = request_openai_api(messages)
    return gpt_questions

def complete_prompt(job, company, requirements, question_index=1):
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
            3. You then start asking them about the job requirements in {requirements}. \
            4. Ask a behavioral question: Behavioral questions ask the candidate to describe a past experience \
                An example of a behavioral question is "Tell me about a time when you developed and executed a marketing strategy." \
            5. Ask a follow up question that requires the candidate to go into specifics from their answer before.
            6. Ask a hypothetical question: Hypothetical questions ask the candidate to describe how they would handle a hypothetical situation \
                An example of a hypothetical question is "How would you develop and execute a marketing strategy?" \
            7. Ask a follow up question that requires the candidate to go into specifics from their answer before.
            8. Ask them if they have any questions for {company}.
                If they do, answer their questions. \
                If they don't, thank them for their time and end the interview. \   
                """
    }, 
    {
        "role": "user",
        "content": f"please provide interview question number {question_index}. Please only respond with the question number and the question itself. "
        
    }]

    print('using context', context)
    return context