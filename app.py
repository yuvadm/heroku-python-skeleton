import os

from flask import Flask
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from marshmallow_sqlalchemy import ModelSchema


app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI': os.environ['DATABASE_URL'],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})
db = SQLAlchemy(app)
api = Api(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Name %r>' % self.name


class UserSchema(ModelSchema):
    class Meta:
        model = User


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        return UserSchema().dump(user)

    def put(self, user_id):
        user = User.query.get(user_id)
        UserSchema().load(request.form, instance=user, session=db.session)
        db.session.commit()
        return 'updated'

    def delete(self, user_id):
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()


class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return UserSchema(many=True).dump(users)

    def post(self):
        user = UserSchema().load(request.form, session=db.session).data
        db.session.add(user)
        db.session.commit()
        return 'created'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/robots.txt')
def robots():
    res = app.make_response('User-agent: *\nAllow: /')
    res.mimetype = 'text/plain'
    return res

api.add_resource(UserListResource, '/users/')
api.add_resource(UserResource, '/users/<user_id>/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
