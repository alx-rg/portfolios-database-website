
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
portfolio = db.portfolios
project = db.projects
article = db.articles

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
    'username': "",
    'name': "",
  }
  return render_template('users_new.html', user=user, title='New User')

@app.route('/users', methods=['POST'])
def users_submit():
    """Submit a new user."""
    user = {
        'username': request.form.get('username'),
        'name': request.form.get('name'),
    }
    db.users.insert_one(user)
    return redirect(url_for('users_index'))

@app.route('/users/<user_id>')
def users_show(user_id):
  user = db.users.find_one({'_id': ObjectId(user_id)})
  user_projects = project.find({'user_id': ObjectId(user_id)})
  user_articles = article.find({'user_id': ObjectId(user_id)})
  return render_template('users_show.html', user=user, project=user_projects, articles=user_articles) 

@app.route('/users/<user_id>/edit')
def users_edit(user_id):
  user = db.users.find_one({'_id': ObjectId(user_id)})
  return render_template('users_edit.html', user=user, title='Edit User')

@app.route('/users/<user_id>', methods=['POST'])
def users_update(user_id):
    updated_user = {
        'username': request.form.get('username'),
        'name': request.form.get('name'),
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
def articles_new():
    """Submit a new project"""
    project = {
        'title': request.form.get('title'),
        'date': request.form.get('date'), 
        'description': int(request.form.get('description')),
        'user_id': ObjectId(request.form.get('user_id')),
    }
    project.insert_one(project)
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/users/project/<articles_id>', methods=['POST'])
def articles_del(articles_id):
    project.delete_one({'_id': ObjectId(articles_id)})
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/project/new')
def project_new():
  # Hidden Form element to add the project to the user
    return render_template('articles_new.html')

@app.route('/article_info', methods=["GET"])
def articles_info(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    user_projects = project.find({'user_id': ObjectId(user_id)})
    article_info_totals = project.aggregate([{"$match": {"user_id": ObjectId(user_id)}},
                                                {"$group": {"_id": None,
                                                            "total_given": {"$sum": "$amount"}}},
                                              ])
    article_info_list = list(article_info_totals)
    article_info = article_info_list[0] if len(article_info_list) != 0 else None
    return render_template("users_show.html", user=user, project=user_projects, article_info=article_info)


#PROJECT ABOVE: --------------------------------------------------------------    


# turn the server on for servering
if __name__ == '__main__':
  app.run(debug=True, port=3000)

                 