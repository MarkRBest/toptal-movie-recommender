import pdfkit

import matplotlib.pyplot as plt
from com.database import Database
from com.model import Model
from random import sample
import numpy as np
from bisect import bisect_left
import pandas as pd


def genHtmlTable(movies):
    ''' convert a list of movies into an html table '''
    html = "<TABLE><TR><TH>ID</TH><TH>Title</TH><TH>Director</TH><TH>Main Character</TH><TH>Main Actor</TH><TH>Support Actor</TH><TH>Rating</TH><TR>"
    db = movie_data[movie_data["id"].isin(movies)][[ "id", "title", "director", "character1", "actor1", "actor2", "vote_average"]]
    for i in xrange(len(db)) :
        html += "<TR>"
        for item in list(db.iloc[i]) :
            html += "<TD>%s</TD>" % item
        html += "</TR>"
    html += "</TABLE>"

    return html

if __name__ == '__main__':

    pd.set_option('display.expand_frame_repr', False)

    print "building database"
    database = Database("../../data/")

    movie_data = database.getMovieData()
    print "building model"
    model = Model(database)

    movies = [672]   # harry potter
    movies = [109445, 1422, 285]   #
    movies = [12107]   # nutty proffessor
    movies = [1452]    # superman

    html = """
    <html>
      <head>
        <meta name="pdfkit-page-size" content="Legal"/>
        <meta name="pdfkit-orientation" content="Landscape"/>
      </head>
      <body>
      <H3>Recomendation Performance Report</H3>
      <p>This report shows the recomendations for a give set of moives and outputs the performance of the model compared with guessing movies at random</p>
    """
    html += "<H3>Client history</H3>"
    html += genHtmlTable(movies)
    html += "</br>"
    print ""
    print "Movies history"
    print movie_data[movie_data["id"].isin(movies)][[ "id", "title", "director", "character1", "actor1", "actor2", "vote_average"]]
    rec = model.getRecomendations(movies)

    print ""
    print "Movies Reccomendations"
    rec_ids, names = zip(*rec)
    print movie_data[movie_data["id"].isin(rec_ids)][["id", "title", "director", "character1", "actor1", "actor2", "vote_average"]]

    html += "<H3>Client Recomendations</H3>"
    html += genHtmlTable(rec_ids)
    html += "</br>"

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

    plt.savefig("//tmp/improvement.png")

    html += "<H3>Model Performance</H3>"
    html += "<p>null quantiles: 10%% %.3f 5%% %.3f 1%% %.3f, Model Distance %.3f, %.3f p_val</p>" % (limits[1],limits[2],limits[3], result, p_val)
    html += """<img border="0" alt="W3Schools" src="improvement.png" width=800 height=400> """

    html += """</body></html>"""

    # generate report
    _dir = "../../report/"
    fname = ""
    for i in sorted(movies) :
        fname += "%s_" % i
    pdfkit.from_string(html, _dir+fname+'report.pdf')
