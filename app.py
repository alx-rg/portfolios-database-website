
# python3 -m venv env
# source env/bin/activate 
# If you ever want to deactivate your virtual environment, just type deactivate in your terminal window.#
# export FLASK_ENV=development; flask run
# http://127.0.0.1:5000/
# localhost:5000

# MongoDB   brew services start mongodb-community@5.0     Verify that it's running with : brew services list
# to stop MongoDB brew services stop mongodb-community@5.0

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

uri = os.environ.get('MONGODB_URI')
client = MongoClient(uri)
db = client.get_database('SimplyPortfolio')
projects = db.projects
articles = db.articles

app = Flask(__name__)

@app.route('/')
def users_index():
  #Show All users
  users = db.users.find({})
  return render_template('users_index.html', users=users)

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/users/new')
def users_new():
  user = {
    'name': "",
    'company': "",
    'position': "",
    'bio': "",
  }
  return render_template('users_new.html', user=user, title='New User')

@app.route('/users', methods=['POST'])
def users_submit():
    """Submit a new user."""
    user = {
        'name': request.form.get('name'),
        'company': request.form.get('company'),
        'position': request.form.get('position'),
        'bio': request.form.get('bio'),
    }
    db.users.insert_one(user)
    return redirect(url_for('users_index'))

@app.route('/users/<user_id>')
def users_show(user_id):
  user = db.users.find_one({'_id': ObjectId(user_id)})
  user_projects = projects.find({'user_id': ObjectId(user_id)})
  user_articles = articles.find({'user_id': ObjectId(user_id)})
  return render_template('users_show.html', user=user, projects=user_projects, articles=user_articles) 

@app.route('/users/<user_id>/edit')
def users_edit(user_id):
  user = db.users.find_one({'_id': ObjectId(user_id)})
  return render_template('users_edit.html', user=user, title='Edit User')

@app.route('/users/<user_id>', methods=['POST'])
def users_update(user_id):
    updated_user = {
        'name': request.form.get('name'),
        'company': request.form.get('company'),
        'position': request.form.get('position'),
        'bio': request.form.get('bio'),
    }
    db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': updated_user})
    return redirect(url_for('users_show', user_id=user_id))

@app.route('/users/<user_id>/delete', methods=['POST'])
def users_del(user_id):
    db.users.delete_one({'_id': ObjectId(user_id)})
    return redirect(url_for('users_index'))


# NEW PROJECT BELOW: --------------------------------------------------------------

@app.route('/users/project', methods=['POST'])
def projects_new():
    """Submit a new project"""
    
    project = {
        'title': request.form.get('title'),
        'date': request.form.get('date'), 
        'description': request.form.get('description'),
        'link': request.form.get('link'),
        'user_id': ObjectId(request.form.get('user_id')),
    }
    projects.insert_one(project)
    print(project)
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/users/project/<projects_id>', methods=['POST'])
def projects_del(projects_id):
    projects.delete_one({'_id': ObjectId(projects_id)})
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/project/new')
def project_new():
  # Hidden Form element to add the project to the user
    return render_template('projects_new.html')

@app.route('/article_info', methods=["GET"])
def articles_info(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    user_projects = projects.find({'user_id': ObjectId(user_id)})
    article_info_totals = projects.aggregate([{"$match": {"user_id": ObjectId(user_id)}},
                                                {"$group": {"_id": None,
                                                            "total_given": {"$sum": "$amount"}}},
                                              ])
    article_info_list = list(article_info_totals)
    article_info = article_info_list[0] if len(article_info_list) != 0 else None
    return render_template("users_show.html", user=user, project=user_projects, article_info=article_info)


#PROJECT ABOVE: --------------------------------------------------------------    

@app.route('/users/articles', methods=['POST'])
def articles_new():
    """Submit a new article"""
    article = {
        'title': request.form.get('title'),
        'date': request.form.get('date'), 
        'description': request.form.get('description'),
        'link': request.form.get('link'),
        'user_id': ObjectId(request.form.get('user_id')),
    }
    articles.insert_one(article)
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/users/artile/<articles_id>', methods=['POST'])
def articles_del(articles_id):
    articles.delete_one({'_id': ObjectId(articles_id)})
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/article/new')
def article_new():
  # Hidden Form element to add the project to the user
    return render_template('articles_new.html', title='New Article')



# turn the server on for servering
if __name__ == '__main__':
  app.run(debug=True, port=5000)

                 