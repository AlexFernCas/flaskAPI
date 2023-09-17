import jinja2
from flask import Flask, render_template, request, session, redirect, url_for, g
from werkzeug.security import  check_password_hash
from database import init_db, add_user, get_user, get_recipe, add_recipe, modify_recipe, get_allRecipe, get_allUserRecipe


app = Flask(__name__)


@app.before_request
def before_request():
    if "username" in session:
        g.user = session["username"]
    else:
        g.user = None

@app.errorhandler(404)
def page_not_found(e):
    return render_template("page_not_found.html"), 404


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        message_success, message_error = add_user(request.form["username"], request.form["password"])
        return render_template("login.html", message_success=message_success, message_error=message_error)

    return render_template("signup.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = get_user(request.form["username"])
        if user and check_password_hash(user.password, request.form["password"]):
            session["username"] = user.username
            return redirect(url_for("home"))
        return render_template("login.html", message_error="Your credentials are invalid.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    message = f'{g.user}, you are logged out.'
    return render_template("login.html", message_info=message)


@app.route("/home", methods=["POST", "GET"])
def home():
    if g.user:
        return render_template("home.html", welcome_message=f'Welcome {g.user}, what do you want to do?')
    else:
        return render_template("login.html", message_error="You must log in first.")


@app.route("/searchRecipe", methods=["POST", "GET"])
def search_recipe():
    if request.method == "POST":
        recipe = get_recipe(request.form["recipe-name"])
        if recipe:
            return render_template("showRecipe.html", recipe=recipe)
        else:
            return render_template("searchRecipe.html", message_error="Recipe not found")
    if g.user:
        return render_template("searchRecipe.html")

    return render_template("login.html", message_error="You must log in first.")

@app.route("/showOwnRecipes", methods=["GET"])
def search_ownRecipes():
    recipe = get_allUserRecipe(g.user)

    return render_template("showAllRecipes.html", recipe=recipe)


@app.route("/showAllRecipes", methods=["GET"])
def search_allRecipes():
    recipe = get_allRecipe()

    return render_template("showAllRecipes.html", recipe=recipe)

@app.route("/addRecipe", methods=["POST", "GET"])
def create_recipe():
    if request.method == "POST":
        message_success, message_error = add_recipe(request.form["recipe-name"],
                                                    request.form["duration"],
                                                    request.form["difficulty"],
                                                    request.form["ingredient-list"],
                                                    g.user)
        return render_template("addRecipe.html", message_success=message_success, message_error=message_error)

    if g.user:
        return render_template("addRecipe.html")
    return render_template("login.html", message_error="You must log in first.")


@app.route("/modifyRecipe", methods=["POST", "GET"])
def update_recipe():
    if request.method == "POST":
        recipe = get_recipe(request.form["recipe-name"])
        if recipe.user != g.user:
            return render_template("login.html", message_error="You can not modify the recipe that other user owns.")
        if recipe:
            message_success, message_error = modify_recipe (request.form["recipe-name"],
                                                            request.form["duration"],
                                                            request.form["difficulty"],
                                                            request.form["ingredient"])
            return render_template("modifyRecipe.html", message_success=message_success, message_error=message_error)
        else:
            return render_template("modifyRecipe.html", message_error="Recipe not found.")

    if g.user:
        return render_template("modifyRecipe.html")

    return render_template("login.html", message_error="You must log in first.")



if __name__ == "__main__":
    app.secret_key = "12345"
    app.config["JSON_SORT_KEYS"] = False
    db = init_db(app)
    app.run(debug=True)
    app.app_context().push()