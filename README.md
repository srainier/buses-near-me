buses-near-me
=============

A small project playing with 511.org's real-time departures API

Summary
=======

I created this project as an entry into the [Uber coding challenge](https://github.com/uber/coding-challenge-tools). You can see a hosted version of this project at [BusesNear.me](http://busesnear.me).

The project allows you to enter a location, either by using your browser's geolocation feature or by typing in a location, and will present you with a list of bus stops nearby served by SF-MUNI and AC Transit. If a stop has routes with departures in the next hour you can click on the stop to show the departure times.

What Powers the App
===================

The backend is runs a Flask application hosted in Apache. You can see the pip requirements file to see the many python modules used to help the application run. The main logic of the app can be found in app/busesnearme/ in the following components:

* models.py: This file contains the single model used - Stops. All other data is retrieved from 3rd-party APIs.
* views.py: This file has the single top-level view served by the app.
* api.py: This file contains all of the API endpoints exposed by the app.
* helpers.py: This file contains utility methods that are used multiple places.

The frontend is a single-page app with views structured via [Backbone](http://backbonejs.org). Backbone models, collections, and views can be found in app/static/js/main.js. The single page html, including the templates used by the backbone views can be found in app/templates/html. The notable views are:

* AppView: This is the top-level view.
* InputView: This view gathers the user's location.
* StopsView and StopView: These views combine to display stops near the user.
* DepartureViews and DepartureView: These views are to display departures for a stop in a StopView.

What's Missing
==============

This was a fun project to work on but I had to gate the time I spent on it. Here are some notable omissions that didn't make the cut for the time I spent on this:

* Automated tests: I think this is the most glaring omision, and is representative of my desire to polish features as well as my lack of familiarity with Flask (for API tests).
* User accounts and user favorites: You don't need a user account to user the service, but it would be a nice addition to let a user save favorite locations, stops, and routes in order to get information more quickly.
* Better search options: I would have liked to have allowed the user to have some advanced search options, like specifying a maximum distance (currently set at one mile for all services) and limiting searches to a specific agency.
* More agencies: NextBus did not give me a list of BART stops (that I could tell), so some extra work would have been involved add BART support.
* More information about routes when looking at departures.

What I Learned
==============

Prior to this project I had never worked with Flask before. (All of server work had been with Django). It certainly is fair to call it a microframework and I'm not sure if I like the bare-bones nature of it. I also learned a bit about SQLAlchemy (also a new project for me) though not nearly to the same extent.

About Me
========

I've been a software developer since graduating from college in 2004. You can see my full history on [my resume here](http://shanearney.com/resume/). I also have some Objective-C projects on [my Github account](https://github.com/srainier) that were created as part of some side projects I created for myself.
