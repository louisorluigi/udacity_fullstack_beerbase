# BeerBase
BeerBase is a website for beer lovers. It is a database that allows facebook users to add, edit and remove beer types and beers.

## Getting Started
First run the model.py file in the terminal to create a database via the command $ python model.py

To start with a pre-populated database
Load the beeritems.py file via the command $ python beerItems.py

To start with an empty database:
Go straight to the next step.

Load the views.py file in terminal via the command $ python views.py
The file points to the 8000 port on your computer so open up and a browser and type localhost://8000 in the url bar.

You should now see the beerbase home page and can navigate using the browser

### Installing
To run beerbase you will need to install the following:
Flask
sqlalchemy
oauth2client.client
httplib2
json
requests

If you do not have any of these on your machine use pipenv (the python installer) to download the libraries you are missing. The specifics of each can be found on their websites.

## Built with
Python 2.7
flask
sqlachemy
sql postgress

## Authors
louisorlugi

## Acknowledgements
* This is part fo the Udacity fullstack nano degree, therefore lots of the code has come from the classes
* Also lots of help has some from my fellow Udacians and all their great work on the forums.
