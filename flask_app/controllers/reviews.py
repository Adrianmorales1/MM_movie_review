from flask_app import app
from flask import Flask, request, redirect, session, render_template, flash
from flask_app.models.review import Review
from flask_app.models.user import User
from flask_app.controllers import users

@app.route('/show/<int:id>')
def show_review(id):
    if not User.validate_session(session):
        return redirect('/')
    review_data = {
        'id' : id
    }
    return render_template('show_review.html', review = Review.get_one_review(review_data))

@app.route('/add/review')
def add_review():
    return render_template("add_review.html")

@app.route('/add/review/one', methods = ['POST'])
def add_reviews():
    data_review = {
        'user_id' : session['user_id'],
        'title' : request.form['title'],
        'rating' : request.form['rating'],
        'date_watched' : request.form['date_watched'],
        'content' : request.form['content']
    }
    Review.save_review(data_review)
    return redirect('/dashboard')

@app.route('/edit/<int:id>')
def edit_review(id):
    if not User.validate_session(session):
        return redirect('/')
    review_data = {
        'id' : id
    }
    user_in_review = {
        'id' : Review.get_one_review(review_data).creator.id
    }
    user_in_session = {
        'id' : session['user_id']
    }
    if not Review.validate_edit_delete(user_in_review, user_in_session):
        return redirect('/')

    return render_template("edit_review.html", review = Review.get_one_review(review_data))

@app.route('/edit/review/one', methods = ['POST'])
def edit_reviews():
    if not Review.validate_review(request.form):
        id = request.form['id']
        return redirect('/edit/'+ str(id))
    Review.update_review(request.form)
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    if not User.validate_session(session):
        return redirect('/')
    review_data = {
        'id' : id
    } 
    Review.delete_review(review_data)
    return redirect('/dashboard')

@app.route('/reviews/<int:id>/favorite', methods = ['POST'])
def favorite_review(id):
    Review.favorite(request.form)
    return redirect('/dashboard')
@app.route('/reviews/<int:id>/unfavorite', methods = ['POST'])
def unfavorite_review(id):
    Review.unfavorite(request.form)
    return redirect('/dashboard')