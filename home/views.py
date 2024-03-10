from django.shortcuts import render, redirect
from cs50 import SQL
from django.shortcuts import HttpResponse
import requests

from langchain.schema import AIMessage, SystemMessage, HumanMessage


import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

db = SQL(
    "sqlite:////workspaces/female_discussion/data.db"
)

os.environ['OPENAI_API_KEY'] = ''




# check session on login and sighnup
def if_session(func):
    def wrapper(request):
        if 'username' in request.session:
            return redirect('home')
        else:
            return func(request)
    return wrapper

def no_session(func):
    def wrapper(request):
        if 'username' not in request.session:
            return redirect('login')
        else:
            return func(request)
    return wrapper
        


# Create your views here.
@if_session
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        res = db.execute(
            "SELECT * FROM login WHERE username = ? and password = ?",
            username,
            password,
        )
        if res:
            request.session["username"] = username
            request.session["login_id"] = res[0]['id']
            return redirect("home")
        else:
            return redirect("login")

    return render(request, "login.html")

@if_session
def signup(request):
    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = db.execute("SELECT * FROM login WHERE username = ?", email)

        if user:
            return HttpResponse(
                "Email is already taken. Please choose a different one."
            )

        login_id = db.execute(
            'INSERT INTO login(username, password, status) VALUES (?, ?, "user")',
            email,
            password,
        )
        user = db.execute(
            "INSERT INTO user(name, email, login_id) VALUES (?, ?, ?)",
            name,
            email,
            login_id,
        )

        if user is not None:
            request.session["username"] = email
            request.session["login_id"] = login_id
            return redirect("home")

    return render(request, "signup.html")

@no_session
def home(request):

    questions = db.execute("SELECT * FROM questions LIMIT 10")
    
    if "search_data" in request.session:
        questions = request.session["search_data"]
        del request.session["search_data"]

    context = {"questions": questions}

    return render(request, "home.html", context)


def add_question(request):
    question = request.POST["question"]
    description = request.POST["description"]
    login_id = request.session['login_id']
    db.execute("INSERT INTO questions(question, description, login_id) values(?, ?, ?)", question, description, login_id)
    return redirect("home")


def search_question(request):
    question = request.POST["question"]
    questions = db.execute(
        "SELECT * FROM questions WHERE question LIKE ? LIMIT 10", "%" + question + "%"
    )

    request.session["search_data"] = questions
    return redirect("home")

def question_post(request):
    question_id = int(request.POST["question_id"])
    request.session['discussion_qid'] = question_id
    return redirect('discussion')
    
@no_session
def discussion(request):
    if 'discussion_qid' not in request.session:
        return redirect('home')
    
    question_id = request.session['discussion_qid']
    
    question = db.execute("SELECT * FROM questions where id = ?", question_id)
    answers = db.execute("SELECT * FROM discussion where question_id = ?", question_id)

    if question is None:
        return HttpResponse("invalid question")

    context = {
        "question": question,
        "discussions": answers,
        'login_id': request.session['login_id']
    }

    return render(request, "discussion.html", context)


def add_discussion(request):
    result = request.POST["add_discussion"].strip()
    question_id = request.POST['question_id']
    login_id = request.session['login_id']

    if result:
        db.execute(
            "INSERT INTO discussion (answer, question_id, login_id) VALUES (?, ?, ?)",
            result,
            question_id,
            login_id
        )
    return redirect('discussion')


def logout(request):
    print('yes')
    del request.session['username']
    print(request.session)
    return redirect('login')


def profile(request):
    login_id = request.session['login_id']
    questions = db.execute('SELECT * FROM questions WHERE login_id = ?', login_id)
    context = {
        'questions': questions
    }
    return render(request, 'profile.html', context)

datada = []

def articles(request):
    global datada
    
    
    if datada:
        data = datada
    else:
        url = ('https://newsapi.org/v2/everything?'
       'q=womens+health&'
       'sortBy=popularity&'
       'apiKey=apikey')

        response = requests.get(url)

        res = response.json()

        if res['status'] != 'ok':
            return HttpResponse('error occured')

        data = res['articles']
        datada = data

    if request.method == "POST":
        search = request.POST['search_article']
        search = "+".join(search.split())
        url = ('https://newsapi.org/v2/everything?'
       'q='+search+'&'
       'sortBy=popularity&'
       'apiKey=18d6d6c5963d4a52a44c74c2d325d598')

        response = requests.get(url)

        res = response.json()

        if res['status'] != 'ok':
            return HttpResponse('error occured')

        data = res['articles']
        datada = data

    context = {
        'data' : data
    }
    return render(request, 'articles.html', context)


qna = []
b = None


def chat(request):

    global qna
    global b

    qna = []

    b = bot()
    question = b.get_question('hi')

    qna.append({'question':question, 'answer': None})  

    return redirect('chat_bot')

def chat_bot(request):
    global qna
    global b 
    if request.method == 'POST':
        answer = request.POST['question']
        qna[-1]['answer'] = answer 

        question = b.get_question(answer)

        qna.append({'question':question, 'answer': None})  

    return render(request, 'chat.html', {'data': qna}) 

def remove_discussion(request):
    login_id = request.session['login_id']
    
    discussion_id = request.POST['remove']
    db.execute('DELETE FROM discussion WHERE login_id = ? and id = ?', login_id, discussion_id)
    return redirect('discussion')





class bot:
    message = [SystemMessage(content="""
        
        you are an personal chat bot for a user things that you should do while interacting:

        * ask about the problems that the user is facing 
        * ask the details of the problem 
        * if the problems is health related ask for symptoms etc
        * help the person if he/she is facing emotional scars
        * answer him how to solve or cure the problem they are facing
        * should only replay within 100 character like chatting
        
        """
    )]
    chat_bot = ChatOpenAI(temperature=.5)



    def get_question(self, answer=''):
            
        llm = self.chat_bot
        
        if answer:
            self.message.append(HumanMessage(answer))
        
        # response from the llm model 
        response = llm.invoke(input=self.message).content
        print(response)
        self.message.append(AIMessage(response))
        
        return response


    
    
    


