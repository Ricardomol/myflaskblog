from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries
from app import app, db, lm
from .forms import ComposeForm, LoginForm
from .models import User, Post
import datetime as dt
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, DATABASE_QUERY_TIMEOUT


@app.route("/")
def index():
    print("EN posts")
    posts = Post.query.order_by(Post.id.desc()).limit(10)
    return render_template('index.html', posts=posts)


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route("/about")
def about():
	return render_template('about.html')


@app.route("/post/<int:post_id>")
def template_post(post_id):
    post = Post.query.get(post_id)
    return render_template('entry1.html', post=post)


@app.route("/archive")
def archive():
    posts_data = []

    posts = Post.query.order_by(Post.id.desc()).all()

    for post in posts:
        post_dict  = {}
        post_dict['timestamp'] = post.timestamp.strftime('%B %d %Y')
        post_dict['id'] = post.id
        post_dict['title'] = post.title

        posts_data.append(post_dict)

    import json
    return render_template('archive.html', posts=json.dumps(posts_data))
    # return render_template('archive.html', posts=posts)


@app.route("/compose/", methods=['GET', 'POST'])
@app.route("/compose/<int:post_id>", methods=['GET', 'POST'])
@login_required
def compose(post_id=None):
    print "En def compose"

    form = ComposeForm()

    if form.validate_on_submit():
        print "Form.validate on sunmit"
        if post_id:
            post = Post.query.get(post_id)
            flash('Your post has been saved.')
        else:
            print ("No post id")
            post = Post()
            flash('Your post has been saved.')

        post.title = form.title.data
        post.intro = form.intro.data
        post.body = form.body.data
        post.timestamp = dt.datetime.utcnow() 

        print ("Post.body = %s" % post.body)

        db.session.add(post)
        db.session.commit()
        print ("Antes de return redirect")
        return redirect(url_for('index'))

    elif request.method != "POST":
        print "request method not POST"
        post = Post.query.get(post_id) if post_id is not None else None        
        form.title.data = post.title if post_id is not None else ""
        form.intro.data = post.intro if post_id is not None else ""
        form.body.data = post.body if post_id is not None else ""
        print "Antes de return render templ"

	return render_template('compose.html', form=form, post=post)


@app.route("/delete/<int:post_id>", methods=['GET', 'POST'])
@login_required
def delete(post_id=None):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted.")
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    print("En before request")
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = dt.datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        # g.search_form = SearchForm()
    # g.locale = get_locale()


# @app.after_request
# def after_request(response):
#     print("En after request")
#     for query in get_debug_queries():
#         if query.duration >= DATABASE_QUERY_TIMEOUT:
#             app.logger.warning(
#                 "SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
#                 (query.statement, query.parameters, query.duration,
#                  query.context))
#     return response


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully.')
    return redirect(request.args.get('next') or url_for('index'))


# @oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'))
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('index'))