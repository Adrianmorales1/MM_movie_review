from flask_app import app
from flask_app.models.user import User

from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

class Review:
    db = "MM_movie_critic"

    def __init__(self,data):
        self.id = data['id']
        self.title = data['title']
        self.rating = data['rating']
        self.date_watched = data['date_watched']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.creator = None
        self.users_who_favorited = []
        self.user_ids_who_favorited = []

    @classmethod
    def save_review(cls,data):
        query = "INSERT INTO reviews (user_id, title, rating, date_watched, content) VALUES (%(user_id)s, %(title)s, %(rating)s, %(date_watched)s, %(content)s)"
        result = connectToMySQL(cls.db).query_db(query,data)
        return result
    
    @classmethod
    def delete_review(cls,data):
        query = "DELETE FROM reviews WHERE id = %(id)s"
        result = connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def update_review(cls,data):
        query = "UPDATE reviews SET title = %(title)s, rating = %(rating)s, date_watched = %(date_watched)s, content = %(content)s WHERE id = %(id)s"
        result = connectToMySQL(cls.db).query_db(query,data)


    @classmethod
    def favorite(cls,data):
        query = "INSERT INTO favorited_reviews(user_id, review_id) VALUES (%(user_id)s, %(id)s)"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def unfavorite(cls,data):
        query = "DELETE FROM favorited_reviews WHERE user_id = %(user_id)s AND review_id = %(id)s"
        return connectToMySQL(cls.db).query_db(query, data)


    @classmethod
    def get_one_review(cls,data):
        query = """SELECT * FROM reviews JOIN users AS creators on reviews.user_id = creators.id 
                LEFT JOIN favorited_reviews ON reviews.id = favorited_reviews.review_id 
                LEFT JOIN users AS users_who_favorited ON favorited_reviews.user_id = users_who_favorited.id WHERE reviews.id = %(id)s"""
        results = connectToMySQL(cls.db).query_db(query, data)

        new_review = True
        for row in results:
            #if this is the first row being processed
            if new_review:
                review = cls(row)
                #create a user object
                one_review_user_info = {
                    "id" : row['creators.id'],
                    "first_name" : row['first_name'],
                    "last_name" : row['last_name'],
                    "email" : row['email'],
                    "password" : row['password'],
                    "created_at" : row['creators.created_at'],
                    "updated_at" : row['creators.updated_at']
                }

                creator = User(one_review_user_info)
                review.creator = creator
                new_review = False

            if row['users_who_favorited.id']:
                user_who_favorited_data = {
                    "id" : row['users_who_favorited.id'],
                    "first_name" : row['users_who_favorited.first_name'],
                    "last_name" : row['users_who_favorited.last_name'],
                    "email" : row['users_who_favorited.email'],
                    "password" : row['users_who_favorited.password'],
                    "created_at" : row['users_who_favorited.created_at'],
                    "updated_at" : row['users_who_favorited.updated_at']
                }
                user_who_favorited = User(user_who_favorited_data)
                print(user_who_favorited_data)
                review.users_who_favorited.append(user_who_favorited)
                review.user_ids_who_favorited.append(row['users_who_favorited.id'])


        return review


    @classmethod
    def get_review_with_one_user(cls, data):
        query = "SELECT * FROM reviews LEFT JOIN users ON reviews.user_id = users.id WHERE users.id = %(id)s"
        results = connectToMySQL(cls.db).query_db(query, data)

        all_reviews = []

        for row in results:
            one_review = cls(row)

            one_review_user_info = {
                "id" : row['users.id'],
                "first_name" : row['first_name'],
                "last_name" : row['last_name'],
                "email" : row['email'],
                "password" : row['password'],
                "created_at" : row['users.created_at'],
                "updated_at" : row['users.updated_at']
            }

            user_data = User(one_review_user_info)

            one_review.creator = user_data

            all_reviews.append(one_review)
        return all_reviews

    @classmethod
    def get_all_review_with_user(cls):
        #query = "SELECT * FROM reviews JOIN users ON reviews.user_id = users.id"
        query = """SELECT * FROM reviews JOIN users AS creators on reviews.user_id = creators.id
                LEFT JOIN favorited_reviews ON reviews.id = favorited_reviews.review_id
                LEFT JOIN users AS users_who_favorited ON favorited_reviews.user_id = users_who_favorited.id;"""
        results = connectToMySQL(cls.db).query_db(query)

        all_reviews = []
        for row in results:
            new_review = True
            user_who_favorited_data = {
                "id" : row['users_who_favorited.id'],
                "first_name" : row['users_who_favorited.first_name'],
                "last_name" : row['users_who_favorited.last_name'],
                "email" : row['users_who_favorited.email'],
                "password" : row['users_who_favorited.password'],
                "created_at" : row['users_who_favorited.created_at'],
                "updated_at" : row['users_who_favorited.updated_at']
            }

            number_of_reviews = len(all_reviews)
            if number_of_reviews > 0:
                last_review = all_reviews[number_of_reviews - 1]
                if last_review.id == row['id']:
                    last_review.user_ids_who_favorited.append(row['users_who_favorited.id'])
                    last_review.users_who_favorited.append(User(user_who_favorited_data))
                    new_review = False


            if new_review:

                one_review = cls(row)

                one_review_user_info = {
                    "id" : row['creators.id'],
                    "first_name" : row['first_name'],
                    "last_name" : row['last_name'],
                    "email" : row['email'],
                    "password" : row['password'],
                    "created_at" : row['creators.created_at'],
                    "updated_at" : row['creators.updated_at']
                }

                user_data = User(one_review_user_info)

                one_review.creator = user_data
                #check to see if anyone favorited 
                if row['users_who_favorited.id']:
                    one_review.user_ids_who_favorited.append(row['users_who_favorited.id'])
                    one_review.users_who_favorited.append(User(user_who_favorited_data))

                all_reviews.append(one_review)
        return all_reviews


    @staticmethod
    def validate_review(data):
        is_valid = True
        if len(data['title']) < 2:
            flash('Title of Review must be at least 2 characters', 'review')
            is_valid = False
        if int(data['rating']) > 10 or int(data['rating']) < 0:
            flash('Rating of Review must be inbetween 0-10', 'review')
            is_valid = False
        if not data['date_watched']:
            flash('Date watched of Review must be entered', 'review')
            is_valid = False
        if len(data['content']) < 10:
            flash('Description of Review must be at least 10 characters', 'review')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_edit_delete(user, other_user):
        is_valid = True
        if user['id'] != other_user['id']:
            flash('Returned to Login form', 'session')
            is_valid = False
        return is_valid