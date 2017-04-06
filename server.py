"""Paws Finder. Uses AJAX and JSON"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Animal, Shelter, UserAnimal, UserSearch

import os, sys
import petfinder
from sqlalchemy import exc # this handles Integrity Errors

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
    dog_breeds = {"dogs": ["None", "American Bulldog", "Australian Cattledog", 
                  "American Staffordshire Terrier", "Beagle", "Border Collie", 
                  "Boxer", "Chihuahua", "Dachshund", "German Shepherd","Labrador Retriever", 
                  "Mixed Breed", "Pit Bull Terrier", "Yorkshire Terrier"]}
    cat_breeds = {"cats": ["None", "American Shorthair", "Calico", "Domestic Long Hair", 
                 "Domestic Medium Hair", "Domestic Short Hair", "Siamese", "Tabby", 
                 "Tabby-Brown", "Tabby-Gray","Tabby-Orange", "Tortoiseshell", "Tuxedo"]}

    return render_template("home.html", 
                           animals=animals, ages=ages, 
                           sizes=sizes, genders=genders,
                           dog_breeds=dog_breeds,
                           cat_breeds=cat_breeds)


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
    
    # handles registration duplicate, flashes message
    try:     
        db.session.add(new_user)
        db.session.commit()
    except exc.IntegrityError:
        flash("User already exists. Please login")
        db.session().rollback() 
          

    flash("Welcome %s %s!  You now have an account with Paws Finder. \
          Your username is your email address, %s." 
          % (first_name, last_name, email))
    return redirect("/register")


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
    
    # genders = {"F": "female", "M": "male"}

    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 
    animal = request.args.get("animal")  
    gender = request.args.get("gender")
    # message = "Your search yielded no results. Try different criteria."

    # assign location to either zipcode or city, state
    if not zipcode:
        location = city + " " + state 
    else:
        location = zipcode 



    # Call api and process search, note variables are singular.
    # Error handler for when search yields no results.
    try:
        pets = api.pet_find(location=location,
                            animal=animal, 
                            gender=gender, 
                            output="basic", 
                            count=50)
    except jinja2.exceptions.UndefinedError:
        flash("Your search yielded no results. Try different criteria.")
        return redirect("/")
        

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
    genders = {"F": "female", "M": "male"}# figure out why i need this

    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 
    animal = request.args.get("animal")  
    age = request.args.get("age")
    size = request.args.get("size")
    gender = request.args.get("gender")
    if animal == "dog":
        breed = request.args.get("dog-breeds")
    else:   
        breed = request.args.get("cat-breeds") 


    search_info = {"zipcode":zipcode,
                   "animal": animal,
                   "age": age,
                   "size": size,
                   "gender": gender,
                   "breed": breed}
                   
    session["last_search"] = search_info 

    # assign location to either zipcode or city, state
    if not zipcode:
        location = city + " " + state 
    else:
        location = zipcode    

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
    for i in range(30):
        try:
            pet = pets.next()
            pet_list.append(pet)   
        except: 
            break    

    # print type(pet_list[0]["photos"])

   
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
                            search_info=search_info)    


@app.route("/save-search.json", methods=["POST"])
def save_search_results():
    """Save search criteria."""

    #get credentials from form
    title = request.form.get("title")
    description = request.form.get("description")

    saved_search = UserSearch(user_id=session["user_id"],
                              zipcode=session['last_search']['zipcode'],  
                              animal=session['last_search']['animal'], 
                              age=session['last_search']['age'],  
                              size=session['last_search']['size'],  
                              gender=session['last_search']['gender'],
                              breed=session['last_search']['breed'],
                              title=title,
                              description=description)

    # We need to add to the session or it won't ever be stored
    db.session.add(saved_search)
    # Once we're done, we should commit our work
    db.session.commit() 

    results = {"success": True, 
    "message": "Your search is saved!"}

    return jsonify(results)  

@app.route("/get-saved-searches.json", methods=["GET"])
def get_saved_searches():
    """Retrieve saved searches from dB."""
    loggedin_user = session.get("user_id")#session is a dict, so .get() enables 
    #value of user_id to be returned

    if loggedin_user:
        searches = UserSearch.query.filter(UserSearch.user_id == loggedin_user).all()
    else:
        flash("You need to be logged in to see your saved searches!  Do it NOW!")  
        return redirect("/")     

    saved_searches = []

    for search in searches:
        search_dict = {}
        search_dict["title"] = search.title
        search_dict["description"] = search.description
        search_dict["usersearch_id"] = search.user_search_id
        saved_searches.append(search_dict)


    return jsonify(saved_searches)       


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
