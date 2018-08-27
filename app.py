# We need to import `request` to access the details of the POST request
# and `render_template`, to render our templates (form and response).
# We'll use `url_for` to get some URLs for the app in the templates.
from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time
import os
from pymongo import MongoClient
from pprint import pprint
import datetime

client = MongoClient()

records = client.venmo_data.transactions

## Flask launch loop bash command (for testing):
#  while :; do python2 app.py & sleep 30 && killall python2; sleep 0.5; done



    # Initialize the Flask application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


try: os.remove("./static/plot.png")
except: pass


dd="HELLPPPPPPPP"

# Define a route for the default URL, which loads the form
@app.route('/',methods=['POST','GET'])
def form():




    # Data for plotting
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots()
    ax.plot(t, s)

    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='About as simple as it gets, folks')
    ax.grid()

    fig.savefig("./static/plot.png")




    #response = render_template('form_audio.html')
    response = render_template('form_audio.html')

    #, search_string=search_string,start_time=start_time, end_time=end_time, resolution=resolution, title=title, xlabel=xlabel, ylabel=ylabel)


            ### Venmo search Flask app variables ###
            # start_time=start_time,
            # end_time=end_time,
                ## ^ either entered as text or generated via dropdowns using javascript
            #resolution=resolution,
                ## day, week, or month
            # title=title, xlabel=xlabel, ylabel=ylabe
                ## Title and labels to be rendered in plot. Reasonable default if not specified.


    return response


# Run the app
if __name__ == '__main__':
    app.run(threaded=True,
        #host="0.0.0.0",
        port=int("8000")
    )
