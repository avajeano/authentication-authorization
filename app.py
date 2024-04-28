from flask import Flask, render_template, redirect, session 
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///login_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "password123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

app.app_context().push()
connect_db(app) 

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        # adding the username to the session
        session['user_username'] = new_user.username
        return redirect(f'/users/{username}')
    return render_template('register.html', form=form)

@app.route('/users/<username>', methods=['GET', 'POST'])
def show_secrets(username):
    # only allows logged in users to view this route
     if "user_username" not in session or session["user_username"] != username:
          return redirect('/login')
     user = User.query.filter_by(username=username).first_or_404()
     form = FeedbackForm()
     return render_template('secret.html', user=user, form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Form to edit feedback."""
    feedback = Feedback.query.get(feedback_id)

    if "user_username" not in session or feedback.username != session['user_username']:
        return redirect('/login')
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f'/users/{feedback.username}')
    
    return render_template('feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""
    feedback = Feedback.query.get(feedback_id)

    if "user_username" not in session or feedback.username != session['user_username']:
        return redirect('/login')
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    
    return redirect(f"/users/{feedback.username}")

@app.route('/users/<username>/feedback/new', methods=["GET", "POST"])
def new_feedback(username):
    """Add new feedback."""
    
    if "user_username" not in session or username != session['user_username']:
        return redirect('/login')
    
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    else:
        return render_template("new_feedback.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate is a method we created in the User Model
        user = User.authenticate(username, password)
        if user:
            # we got this user back from authenticate 
            session['user_username'] = user.username
            return redirect(f'/users/{username}')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
     #removes the user from the session 
     session.pop('user_username')
     return redirect('/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Deletes user and user feedback."""

    if "user_username" not in session or username != ['user_username']:
        return redirect('/login')
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    return redirect("login")