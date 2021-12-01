
# python3 -m venv env
# source env/bin/activate 
# If you ever want to deactivate your virtual environment, just type deactivate in your terminal window.#
# export FLASK_ENV=development; flask run
# http://127.0.0.1:5000/
# localhost:5000

# MongoDB     brew services start mongodb-community@5.0     Verify that it's running with : brew services list
# to stop MongoDB brew services stop mongodb-community@5.0

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

uri = os.environ.get('MONGODB_URI')
client = MongoClient(uri)
db = client.get_database('CharityTracker')
donations = db.donations

app = Flask(__name__)

@app.route('/')
def users_index():
  #Show All users
  users = db.users.find({})
  return render_template('users_index.html', users=users)

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
  user_donations = donations.find({'user_id': ObjectId(user_id)})
  return render_template('users_show.html', user=user, donations=user_donations) 

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


# NEW DONATION BELOW: --------------------------------------------------------------

@app.route('/users/donations', methods=['POST'])
def donations_new():
    """Submit a new donation"""
    donation = {
        'charity': request.form.get('charity'),
        'date': request.form.get('date'), 
        'amount': int(request.form.get('amount')),
        'user_id': ObjectId(request.form.get('user_id')),
    }
    donations.insert_one(donation)
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/users/donations/<donations_id>', methods=['POST'])
def donations_del(donations_id):
    donations.delete_one({'_id': ObjectId(donations_id)})
    return redirect(url_for('users_show', user_id=request.form.get('user_id')))

@app.route('/donations/new')
def donation_new():
  # Hidden Form element to add the donation to the user
    return render_template('donations_new.html')

@app.route('/donation_info', methods=["GET"])
def donations_info(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    user_donations = donations.find({'user_id': ObjectId(user_id)})
    donation_info_totals = donations.aggregate([{"$match": {"user_id": ObjectId(user_id)}},
                                                {"$group": {"_id": None,
                                                            "total_given": {"$sum": "$amount"}}},
                                              ])
    donation_info_list = list(donation_info_totals)
    donation_info = donation_info_list[0] if len(donation_info_list) != 0 else None
    return render_template("users_show.html", user=user, donations=user_donations, donation_info=donation_info)


#DONATION ABOVE: --------------------------------------------------------------    


# turn the server on for servering
if __name__ == '__main__':
  app.run(debug=True, port=3000)

                 