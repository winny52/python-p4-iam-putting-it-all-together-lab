#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        json = request.get_json()

        if json.get('username') != None:
            user = User(username=json['username'],
                         password_hash= json['password'],
                           image_url= json['image_url'],
                           bio = json['bio']
                           )

            db.session.add(user)
            db.session.commit()
            return user.to_dict(),201
        return {'error':'User not valid'}, 422

class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id ==session['user_id']).first()
            return user.to_dict(), 200
        else:
            return {'error': 'Not logged in'}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter(User.username == json.get('username')).first()
        if user == None:
            return {'error': 'Username or Password Incorrect'}, 401
        if user.authenticate(json.get('password')):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'error': 'Username or Password Incorrect'}, 401

class Logout(Resource):
    def delete(self):
            if session.get('user_id') ==None:
                session['user_id'] = None
                return {'error': 'Login first silly'},401
            session['user_id']= None
            return '', 204

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id') != None:
            recipes = Recipe.query.all()
            return [recipe.to_dict() for recipe in recipes],200
        else:
            return {'error':'Login to see this'}, 401

    def post(self):
        json = request.get_json()
        title = None if type(json) == None else json['title']
        instructions = json['instructions']
        if session.get('user_id') != None:
            if title != None and len(instructions) >50:

                recipe = Recipe(
                    title =json['title'],
                    instructions = json['instructions'],
                    minutes_to_complete =json['minutes_to_complete'],
                                )
                recipe.user_id =session['user_id']

                db.session.add(recipe)
                db.session.commit()

                return recipe.to_dict(), 201
            else:
                return {'error':'Invalid recipe'},422
        else:
            return {'error': 'Not logged in'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
