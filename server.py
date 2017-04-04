"""Paws Finder. Uses AJAX and JSON"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
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
    sizes = {'S': 'small', 'M': 'medium', 'L': 'large', 'XL': 'extra large'}
    genders = {"F": "female", "M": "male"}
    # breeds = add this

    return render_template("home.html", 
                           animals=animals, ages=ages, 
                           sizes=sizes, genders=genders)


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST']) 
def register_process():
    """Process registration."""

    # Get form variables from reg form
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    email = request.form.get("email") 
    password = request.form.get("password")    
    address1 = request.form.get("address1")    
    address2 = request.form.get("address2")      
    city = request.form.get("city")
    state = request.form.get("state")    
    zipcode = request.form.get("zipcode")    
    phone = request.form.get("phone")
    
    new_user = User(first_name=first_name, last_name=last_name,
                  email=email, password=password, 
                    address1=address1, address2=address2,
                    city=city, state=state,
                    zipcode=zipcode, phone=phone)

    # if new_user in # make sure to add that a user is already registered

    db.session.add(new_user)
    db.session.commit()

    flash("Welcome %s %s!  You now have an account with Fur Finder. \
          Your username is your email address, %s." 
          % (first_name, last_name, email))
    return redirect("/")


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")


@app.route("/login.json", methods=["POST"])
def perform_login():
    """Checks credentials, processes log in"""

    # Get credentials from form 
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()    

    if not user:
        results = {"success": False,
        "message": "No user exists, please register."}
        return jsonify(results)  
           
    if user.password != password:
        results = {"success": False,
        "message": "Invalid username/password, try again."}
        return jsonify(results)  
    
    session["user_id"] = user.user_id

    results = {"success": True,
              "firstname": user.first_name}
    
    return jsonify(results) 

@app.route("/logout")
def logout_navbar():
    """Log out."""
    del session["user_id"]
    return redirect("/")

@app.route("/logout.json")
def logout_json():
    """Log out."""

    del session["user_id"]
    results = {"success": True,
              "message": "You are now logged out."}
    
    return jsonify(results)


@app.route("/search", methods=["GET"])
def process_search():
    """Process form variables from quick search fields. No account needed."""
    
    genders = {"F": "female", "M": "male"}

    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 
    animal = request.args.get("animal")  
    gender = request.args.get("gender")

    # assign location to either zipcode or city, state
    if not zipcode:
        location = city + " " + state 
    else:
        location = zipcode    

    # Call api and process search, note variables are singular.
    pets = api.pet_find(location=location,
                            animal=animal, 
                            gender=gender, 
                            output="basic", 
                            count=50)

    # import pdb; pdb.set_trace()

    pet_list = []
    # loop through a range from the api call
    # append to pet_list
    for i in range(20):
        pet = pets.next()
        pet_list.append(pet)        
   
    return render_template("results.html",
                            location=location,
                            animal=animal, 
                            genders=genders, # dictionary that contain gender data 
                            gender=gender, # user form input
                            pets=pet_list)



@app.route("/search-complete", methods=["GET"])
def process_complete_search():
    """Process form variables from complete search fields. User is logged in."""
    
    sizes = {'S': 'small', 'M': 'medium', 'L': 'large', 'XL': 'extra large'}
    genders = {"F": "female", "M": "male"}

    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 
    animal = request.args.get("animal")  
    age = request.args.get("age")
    size = request.args.get("size")
    gender = request.args.get("gender")
    breed= request.args.get("breed")
    # dict to enable users to save their searches
    search_info = {'zipcode':zipcode,
                   'animal': animal,
                   'age': age,
                   'size': size,
                   'gender': gender,
                   'breed': breed}
                   
    session['last_search'] = search_info
    # add condition for dog breed versus cat breed

    # assign location to either zipcode or city, state
    if not zipcode:
        location = city + " " + state 
    else:
        location = zipcode    

    # Call api and process complete search, note variables are singular.
    pets = api.pet_find(location=location,
                            animal=animal, 
                            age=age,
                            size=size,
                            gender=gender, 
                            breed=breed,
                            output="basic", 
                            count=50)

    # import pdb; pdb.set_trace()

    pet_list = []
    # loop through a range from the api call
    # append to pet_list
    for i in range(20):
        pet = pets.next()
        pet_list.append(pet)        
   
    return render_template("results_complete.html",
                            location=location,
                            animal=animal, 
                            age=age,
                            sizes=sizes, # dictionary that contain sizes data
                            size=size, # user form input
                            genders=genders, # dictionary that contain gender data 
                            gender=gender, # user form input
                            breed=breed,
                            pets=pet_list,
                            search_info = search_info)    


@app.route("/save-search.json", methods=["POST"])
def save_search_results():
    """Save search criteria."""

    # Get form variables
    zipcode = request.form.get("zipcode")
    animal = request.form.get("animal")  
    age = request.form.get("age")
    size = request.form.get("size")
    gender = request.form.get("gender")
    breed= request.form.get("breed")

    saved_searches = UserSearch(user_id=user_id,
                                zipcode=session['last_search']['zipcode'],  
                                animal=session['last_search']['animal'], 
                                age=session['last_search']['age'],  
                                size=session['last_search']['size'],  
                                gender=session['last_search']['gender'],
                                breed=session['last_search']['breed'])

    # We need to add to the session or it won't ever be stored
    db.session.add(saved_searches)
    # Once we're done, we should commit our work
    db.session.commit() 

    results = {"message": "Your search was saved."}
    
    return jsonify(results)    


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
