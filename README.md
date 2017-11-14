# toptal-movie-recommender
webservice app for recommending movies


************************************************************************************

Design
	App
		Flask used for routing and webservice
	Controller
		Used for interaction with database and model
	Database
		Wrapper for pandas and holds movie information
	Model
		Functionality for recommendations
		
 ************************************************************************************

 Webservice functionality

  "routes": [
    "/api/v1.0/",
    "/api/v1.0/all_movies/",
    "/api/v1.0/search_movies/<string:name>"
    "/api/v1.0/add_client/<string:name>/<string:email>",
    "/api/v1.0/add_movie/<int:client_id>/<int:movie_id>",
    "/api/v1.0/client_history/<int:client_id>",
    "/api/v1.0/recommend/<int:client_id>",
    "/api/v1.0/reset_client_history/<int:client_id>",
  ]

 ************************************************************************************

 Model Functions

 Distance measure
 	Measures :
 		jarques distance / (quadratic, mahatten etc)
 	Dimensions :
 		rating, year, director, producer, main_actor, support_actor, genre, keywords
 	NLTK :
 		stemming is needed for keywords to improve overlap
 	Normalisation :
 		pareto optimality
 		needed to combine
 	Combination
 		ranks movies by sum of similarities to movies in history
 		takes top 5
 	How would i train the weights? Look at peoples movie history and then test if from part you can predict the rest
 	P(recommended movie in history| given predicted)  // optimise this factor

 ************************************************************************************

 Logging

 Unit tests
 	Testing of model functionality
 	Testing of controller functionality

 ************************************************************************************
 	
 Report
 	Generation of null distribution
 	Testing model against the null distribution
 	Talk about cross validation/bagging/boosting

 Todo
 	persistence
 	performance
 	

 	


 
