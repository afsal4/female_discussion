from django.shortcuts import render, redirect
from cs50 import SQL
from django.shortcuts import HttpResponse
import requests

db = SQL(
    "sqlite:////home/afsal/Desktop/Github/womens_health_discussion/female_discussion/data.db"
)




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
    }

    return render(request, "discussion.html", context)


def add_discussion(request):
    result = request.POST["add_discussion"].strip()
    question_id = request.POST['question_id']
    print(question_id, result)
    if result:
        db.execute(
            "INSERT INTO discussion (answer, question_id) VALUES (?, ?)",
            result,
            question_id,
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
       'q=Apple&'
       'sortBy=popularity&'
       'apiKey=fill this section')



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
    
    
    


