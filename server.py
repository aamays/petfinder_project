"""BFF Finder."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Animal, Shelter, UserAnimal

import os, sys
import petfinder

# Instantiate petfinder api with my credentials.
api = petfinder.PetFinderClient(api_key="3edba6cadbd9d8fcdc5864a85e648862", 
                                api_secret="e3be377653ead49c13322f42134370d0")


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "LGkjsdFlfkjaBldsmDasVfd36p9!9u0m43qlnXalrCd1f43aB"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""

    animals = ["dog", "cat"]
    ages = ["Baby", "Young", "Adult", "Senior"]
    sizes = ["S", "M", "L", "XL"] 
    # Consider creating a dictionary where key is S, value is small
    # pass key value pairs to jinja, same for ages
    genders = ["F", "M"] # F is female, M is male

    return render_template("home.html", 
                           animals=animals, ages=ages, 
                           sizes=sizes, genders=genders)


@app.route("/search", methods=["GET"])
def process_search():
    """Process form variables from search fields."""
    
    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 

    # assign location to either zipcode or city, state

    if not zipcode:
        location = city + " " + state 
    else:
        location = zipcode    

    animals = request.args.get("animal") 
    # breed= request.form["<breed>"] # figure this out
    ages = request.args.get("age")
    sizes = request.args.get("size")
    genders = request.args.get("gender")

    # Call api and process search.
    pets = api.pet_find(location=location,
                            animal=animals, 
                            age=ages,
                            size=sizes,
                            gender=genders, 
                            output="basic", 
                            count=25)

    pet_list = []
    # loop through a range from the api call
    # append to pet_list
    for i in range(10):
        pet = pets.next()
        pet_list.append(pet)        
   
    return render_template("results.html",
                            location=zipcode,
                            animal=animals, 
                            age=ages,
                            size=sizes,
                            gender=genders,  
                            pets=pet_list)


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST']) 
def register_process():
    """Process registration."""

    # Get form variables from reg form
    first_name = request.form["firstname"]
    last_name = request.form["lastname"] 
    email = request.form["email"]
    password = request.form["password"]
    address1 = request.form["address1"]
    address2 = request.form["address2"]       
    city = request.form["city"]
    state = request.form["state"]   
    zipcode = request.form["zipcode"] 
    phone = request.form["phone"]

    new_user = User(first_name=first_name, last_name=last_name,
                    email=email, password=password, 
                    address1=address1, address2=address2,
                    city=city, state=state,
                    zipcode=zipcode, phone=phone)

    db.session.add(new_user)
    db.session.commit()

    flash("Welcome %s %s!  You now have an account with Find Your BFF. \
          Your username is your email address, %s." 
          % (first_name, last_name, email))
    return redirect("/")


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No user exists, you need to register.")
        return redirect("/register")

    if user.password != password:
        flash("Incorrect password, try again.")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("You are logged in")
    return render_template("user.html", 
                            user=user,
                           email=email, 
                           password=password)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
