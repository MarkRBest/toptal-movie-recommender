# toptal-movie-recommender

## webservice app for recommending movies based on movie history

example usage python app.py --port 5000

************************************************************************************

## Design

* App        - Flask used for routing and webservice
* Controller - Used for interaction with database and model
* Database   - Wrapper for pandas and holds movie information
* Model      - Functionality for recommendations
		
 ************************************************************************************

## Webservice functionality


  "routes": [ <br/>
  "/api/v1.0/"  <br/>
  "/api/v1.0/all_movies/", <br/>
   "/api/v1.0/search_movies/<string:name>" <br/>
   "/api/v1.0/add_client/<string:name>/<string:email>", <br/>
   "/api/v1.0/add_movie/<int:client_id>/<int:movie_id>", <br/>
   "/api/v1.0/client_history/<int:client_id>",  <br/>
   "/api/v1.0/recommend/<int:client_id>",   <br/>
   "/api/v1.0/reset_client_history/<int:client_id>", <br/>
  ] <br/>


 ************************************************************************************

## Model Functions

* Measures : Jarques distance / (quadratic, mahatten etc)
* Dimensions : Rating, year, director, producer, main_actor, support_actor, genre, keywords
* NLTK : Stemming is needed for keywords to improve overlap
* Normalisation : Pareto optimality, needed to combine
* Combination: Ranks movies by sum of similarities to movies in history
 		
* How would i train the weights? Look at peoples movie history and then test if from part you can predict the rest
* P(recommended movie in history| given predicted)  // optimise this factor

 ************************************************************************************

## Logging
* Configurable using logging.conf

 ************************************************************************************

## Unit tests

* Model functionality tests
* Controller functionality tests

 ************************************************************************************
 	
## Report

* Generation of null distribution
* Testing model against the null distribution

************************************************************************************

## Todo

* persistence
* performance
 	
