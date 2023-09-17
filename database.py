from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from werkzeug.security import generate_password_hash
import os


dbDir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"
db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    duration = db.Column(db.Integer)
    difficulty = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(ARRAY(db.String), nullable=False)
    user = db.Column(db.String(50), nullable=False)


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = dbDir
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db


def add_user(username, password):
    if get_user(username):
        return ("", "The username already exists")
    if len(username) < 5:
        return ("", "The username must have at least 5 characters")
    if len(password) < 8:
        return ("", "The password must have at least 8 characters")

    hashed_pw = generate_password_hash(password, method="sha256")
    new_user = Users(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return ("You have been successfully registered.", "")


def get_user(username):
    return Users.query.filter_by(username=username).first()


def basic_check(duration, ingredients):
    if duration == '':
        return ("", "You must enter a recipe's duration")
    try:
        int(duration)
    except ValueError:
        return ("", "The recipe's duration must be an integer")
    if ingredients == '':
        return ("", "You must enter a recipe's ingredient")

    return "True"


def recipe_check(name, duration, ingredients):
    if get_recipe(name):
        return ("", "This recipe's name already exists")
    if name == '':
        return ("", "You must enter a recipe's name")
    return basic_check(duration, ingredients)


def split_string(string):
    fragments = string.split(",")

    fragments = [fragment.strip() for fragment in fragments]

    return fragments

def add_recipe(name, duration, difficulty, ingredients, user):

    check = recipe_check(name, duration, ingredients)
    if check == "True":
        newRecipe = Recipes(name=name,
                            duration=duration,
                            difficulty=difficulty,
                            ingredients=ingredients,
                            user=user)

        db.session.add(newRecipe)
        db.session.commit()
        return ("Recipe stored successfully", "")

    return check


def modify_recipe(name, duration, difficulty, ingredients):
    check = basic_check(duration, ingredients)

    if check == "True":
        recipe = get_recipe(name)
        recipe.duration = duration
        recipe.difficulty = difficulty
        recipe.ingredients = ingredients
        db.session.commit()
        return ("Recipe has been successfully modified.", "")

    return check


def get_recipe(recipe):
    return Recipes.query.filter_by(name=recipe).first()


def get_allUserRecipe(user):
    return Recipes.query.filter_by(user=user).all()
def get_allRecipe():
    return Recipes.query.all()