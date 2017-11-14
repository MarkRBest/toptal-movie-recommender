'''
Recomendation model finds movies in the database that are similar
'''

from bisect import bisect_left
from collections import Counter
from nltk.stem.porter import PorterStemmer

from com.database import Database
import numpy as np
import pandas as pd
from random import sample

import matplotlib.pyplot as plt

MIN_RECOMENDATIONS = 1
MAX_RECOMENDATIONS = 25

class Model :

    def __init__(self, database):

        # cache is used to store movie similarities for popular movies to
        self.__score_cache = {}

        self.__movie_db = database
        self.__genres_db = database.getGenres()
        self.__keyword_db = database.getKeywords()

        # generate unique list of genres
        self.__genres = self.__genres_db.values()
        self.__genres  = [val for sublist in self.__genres for val in sublist]
        self.__genres = sorted(np.unique(self.__genres))

        # convert genres list into a set of binary vectors [0,1,0,1]
        # where there is a 1 if the genre exists in the movie
        self.__genre_vectors = {}
        for k, v in self.__genres_db.iteritems() :
            vec = [0] * len(self.__genres)
            for i, genre in enumerate(self.__genres) :
                if genre in v :
                    vec[i] = 1
            self.__genre_vectors[k] = vec

        # create a dictionary of get set of keywords
        self.__all_keywords = self.__keyword_db.values()
        self.__all_keywords = [val for sublist in self.__all_keywords for val in sublist]
        self.__all_keywords = sorted(np.unique(self.__all_keywords))

        # build keyword vectors
        self.__keyword_vectors = {}
        for k, v in self.__keyword_db.iteritems() :
            vec = [0] * len(self.__all_keywords)
            for i, keyword in enumerate(self.__all_keywords) :
                if keyword in v :
                    vec[i] = 1
            self.__keyword_vectors[k] = vec

        movie_db = self.__movie_db.getMovieData()

        # langauge popularity
        self.__lang_counts = Counter(movie_db.original_language)
#         print self.__lang_counts

        # caluculate the rating of the movie and adjust by our confidence in average from sqrt(count)
        self.__votes = movie_db.vote_average
        self.__votes = sorted(self.__votes)

    def invalidate_cache(self):
        self.__score_cache = {}

    ''' implements jarques distance for two vectors of binary digits '''
    def jarques_distance(self, v1, v2):
        num = np.sum(np.logical_and(v1, v2))
        dem = np.sum(np.logical_or(v1, v2))
        return 0 if dem == 0 else float(num)/dem

    def isSequel(self, m1, m2):
        ''' check if two movies are sequels '''
        db = self.__movie_db.getMovieData()

        # check if both movies exist
        if m1 not in db.id or m2 not in db.id :
            return 0

        m1 = db[db["id"] == m1].iloc[0]
        m2 = db[db["id"] == m2].iloc[0]

        # check if the same movie
        if m1.id == m2.id :
            return 1

        # same main charachter
        if m1.character1 == m2.character1 :
            return 1

        # same director and actors
        if m1.director ==  m2.director and m1.actor1 ==  m2.actor1 and m1.actor2 ==  m2.actor2 :
            return 1

        return 0

    def getDistance(self, movie1, movie2):
        ''' check if two movies are similar '''
        scores = []

        # compare director, producer and actors
#         scores.append(1 if movie1.director == movie2.director else 0)
        # scores.append(1 if row["producer"] == movie["producer"] else 0)
        scores.append(1 if movie1.actor1 == movie2.actor1 else 0)
#         scores.append(1 if movie1.actor2 == movie2.actor2 else 0)
        # scores.append(1 if row["original_language"] == movie["original_language"] else 0)

#         scores = [0,0,0]

        # compare genres
        if self.__genre_vectors.has_key(movie1.id) and self.__genre_vectors[movie2.id] :
            v1 = self.__genre_vectors[movie1.id]
            v2 = self.__genre_vectors[movie2.id]
            dist = self.jarques_distance(v1, v2)
            scores.append(dist)
        else:
            scores.append(0)
        # compare keywords
        if self.__keyword_vectors.has_key(movie1.id) and self.__keyword_vectors[movie2.id] :
            v1 = self.__keyword_vectors[movie1.id]
            v2 = self.__keyword_vectors[movie2.id]
            dist = self.jarques_distance(v1, v2)
            scores.append(dist)
        else:
            scores.append(0)

        return scores


    def getRecomendations(self, movies, numRecs=5) :
        movie_db = self.__movie_db.getMovieData()

        # check numRecs makes sense
        numRecs = max(MIN_RECOMENDATIONS, min(numRecs, MAX_RECOMENDATIONS))

        # for all known movies generate a score which will be used to create recomendations
        agg_scores = {}

        # initalise scores with the vote quantile to make higher voted movies more likely to be chosen
        lenVotes = len(self.__votes)
        for i, row in movie_db.iterrows() :
            norm_votes = bisect_left(self.__votes, row.vote_average)
            agg_scores[row.id] = 0.25 * float(norm_votes) / lenVotes

        for movie_id in movies :

            # see if we have already processed this movie
            if self.__score_cache.has_key(movie_id) :
                movie_scores = self.__score_cache[movie_id]
            else:

                movie = movie_db[movie_db["id"]==movie_id]

                # check this id is in the database
                if len(movie) == 0 :
                    continue

                movie_scores = {}
                movie = movie.iloc[0]
                for i, row in movie_db.iterrows() :
                    scores = self.getDistance(movie, row)
                    movie_scores[row.id] = scores

                # normalise genre and keyword scores as percentiles rather than abs overlap
                gscores, kscores = [], []
                for v in movie_scores.values() :
                    kscores.append(v[-1])
                    gscores.append(v[-2])
                kscores = sorted(kscores)
                gscores = sorted(gscores)
                nscores = len(kscores)
                for v in movie_scores.values() :
                    gperc = bisect_left(gscores, v[-2])
                    v[-2] = float(gperc) / nscores

                    kperc = bisect_left(kscores, v[-1])
                    v[-1] = float(kperc) / nscores

                # take average of all features as distance measure
                for k in movie_scores.keys() :
#                     movie_scores[k] = movie_scores[k][-1]
                    movie_scores[k] = np.average(movie_scores[k])

                self.__score_cache[movie_id] = movie_scores

            # find movies which are closest to one of the movies in the history
            for k, v in movie_scores.iteritems():
                if not agg_scores.has_key(k) :
                    agg_scores[k] = v
                else :
                    agg_scores[k] = np.add(agg_scores[k], v)


        results = []
        for k, v in agg_scores.iteritems() :
            results.append((k,v))

        results = sorted(results, key=lambda x: x[1], reverse=True)
        candidates, scores = zip(*results)

        results = []
        cptr = 0
        while len(results) < numRecs and cptr < len(candidates):
            candidate = candidates[cptr]
            cptr+=1

            # check if its already been watched
            if candidate not in movies :
                # check if the move is a sequel to one already recomended
                sequels = map(lambda other: self.isSequel(candidate, other), results)
                if len(results) == 0 or max(sequels) == 0 :
                    results.append(candidate)

        names = movie_db[movie_db.id.isin(results)].title

        return zip(results, names)

def runNullComparison():
    pass

if __name__ == '__main__':

    pd.set_option('display.expand_frame_repr', False)

    print "building database"
    database = Database("../../data/")

    movie_data = database.getMovieData()
    print "building model"
    model = Model(database)

    movies = [672]
    movies = [109445, 1422, 285]

    print ""
    print "Movies history"
    print movie_data[movie_data["id"].isin(movies)][[ "id", "title", "director", "character1", "actor1", "actor2", "vote_average"]]
    rec = model.getRecomendations(movies)

    print ""
    print "Movies Results"
    rec_ids, names = zip(*rec)
    print movie_data[movie_data["id"].isin(rec_ids)][["id", "title", "director", "character1", "actor1", "actor2", "vote_average"]]

    # create a set of avearge distances based of picking movies at random. This will generate out null distrbution for uniformed choice
    ids = list(movie_data.id)
    s = []
    for i in xrange(1000) :
        rsample = sample(ids, 5)
        vals = []
        for m1 in movies :
            movie1 = movie_data[movie_data.id == m1].iloc[0]
            for m2 in rsample :
                movie2 = movie_data[movie_data.id == m2].iloc[0]
                dists = model.getDistance(movie1, movie2)
                vals.append(np.mean(dists))
        s.append(np.mean(vals))

    # our recs

    vals = []
    for m1 in movies :
        movie1 = movie_data[movie_data.id == m1].iloc[0]
        for m2 in rec_ids :
            movie2 = movie_data[movie_data.id == m2].iloc[0]
            dists = model.getDistance(movie1, movie2)
            vals.append(np.mean(dists))

#     print "vals", vals
    result = np.mean(vals)

    s = sorted(s)
    pos = bisect_left(s, result)
    p_val = 1.0-(float(pos)/len(s))
    print " "
    limits = np.percentile(s, [50,90,95,99])
    print "null quantiles: 10%% %.3f 5%% %.3f 1%% %.3f, Model Distance %.3f, %.3f p_val" % (limits[1],limits[2],limits[3], result, p_val)

    plt.title("Recommendation Comparison")
    plt.hist(s, bins=50)
    plt.axvline(result, color='r', linewidth=3)
    plt.axvline(np.mean(s), color='g', linewidth=3)
    plt.ylabel("Frequency")
    plt.xlabel("Similarity")
    plt.show()