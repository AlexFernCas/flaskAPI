from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import os

dbDir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = dbDir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False
db = SQLAlchemy(app)

app.app_context().push()


class Users (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Recipes (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    duration = db.Column(db.Integer)
    difficulty = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)

@app.before_request
def before_request():
    if "username" in session:
        g.user = session["username"]
    else:
        g.user = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        if Users.query.filter_by(username=request.form["username"]).first():
            flash("The username already exist", "error")
            return render_template("signup.html")
        if len(request.form["username"]) < 5:
            flash("The username must have 5 characters at last", "error")
            return render_template("signup.html")
        if len(request.form["password"]) < 8:
            flash("The password must have 8 characters at last", "error")
            return render_template("signup.html")

        hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = Users(username=request.form["username"], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("You have been successfully registered.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["username"] = user.username
            return redirect(url_for("home"))
        flash("Your credentials are invalid.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop(g.user, None)
    flash(f'{g.user}, you are logged out.', "info")
    return render_template("login.html")


@app.route("/home", methods=["POST", "GET"])
def home():
    if g.user:
        flash(f'Welcome {g.user}, what do you want to do?', "info")
        return render_template("home.html")
    else:
        flash("You must log in first.", "error")
        return render_template("login.html")


@app.route("/addRecipe", methods=["POST", "GET"])
def add_recipe():
    if request.method == "POST":
        if Recipes.query.filter_by(name=request.form["recipe-name"]).first():
            flash("This recipe's name already exists", "error")
        else:
            new_recipe = Recipes(name=request.form["recipe-name"], duration=request.form["duration"],
                                 difficulty=request.form["difficulty"], ingredients=request.form["ingredient"])
            db.session.add(new_recipe)
            db.session.commit()

    if g.user:
        return render_template("addRecipe.html")

    flash("You must log in first.", "error")
    return render_template("login.html")


@app.route("/searchRecipe", methods=["POST", "GET"])
def search_recipe():
    if request.method == "POST":
        recipe = Recipes.query.filter_by(name=request.form["recipe-name"]).first()
        if recipe:
            response_recipe =[{
                "Id": recipe.id,
                "Name": recipe.name,
                "Duration": recipe.duration,
                "Difficulty": recipe.difficulty,
                "Ingredients": recipe.ingredients
            }]
            return jsonify(response_recipe)
        else:
            flash("Recipe not found.", "error")

    if g.user:
        return render_template("searchRecipe.html")

    flash("You must log in first.", "error")
    return render_template("login.html")


@app.route("/modifyRecipe", methods=["POST", "GET"])
def modify_recipe():
    if request.method == "POST":
        recipe = Recipes.query.filter_by(name=request.form["recipe-name"]).first()
        if recipe:
            recipe.name = request.form["recipe-name"]
            recipe.duration = request.form["duration"]
            recipe.difficulty = request.form["difficulty"]
            recipe.ingredients = request.form["ingredient"]
            flash("Recipe has been successfully modified.")
            db.session.commit()
            return render_template("modifyRecipe.html")
        else:
            flash("Recipe not found.", "error")

    if g.user:
        return render_template("modifyRecipe.html")

    flash("You must log in first.", "error")
    return render_template("login.html")


app.secret_key = "12345"


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)