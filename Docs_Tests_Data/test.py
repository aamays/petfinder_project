# This Python file uses the following encoding: utf-8
import os, sys
import petfinder

# Instantiate the client with your credentials.
api = petfinder.PetFinderClient(api_key="3edba6cadbd9d8fcdc5864a85e648862", 
                                api_secret="e3be377653ead49c13322f42134370d0")

# Query away!
# zip_code = int(raw_input("Enter your zip code to find a shelter near you: "))

# try:
#     for shelter in api.shelter_find(location=zip_code, count=500):
#         import pdb; pdb.set_trace() # ability to pause program, for debugging    
#         print(shelter["name"])
# except petfinder.exceptions.LimitExceeded: 
    # pass   


species = raw_input("Would you like to adopt a dog or a cat?  ")
breed = raw_input("Enter a breed:  ")

# Search for pets.
for pet in api.pet_find(animal=species, location=94132, output="basic",
                        breed=breed, count=200):

    import pdb; pdb.set_trace() # ability to pause program, for debugging 

    print("%s - %s" % (pet["id"], pet["name"]))
# TODO: Find homes for these guys.