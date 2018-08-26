# We need to import `request` to access the details of the POST request
# and `render_template`, to render our templates (form and response).
# We'll use `url_for` to get some URLs for the app in the templates.
from flask import Flask, render_template, request, url_for



import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time

# Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()

fig.savefig("./static/test.png")

time.sleep(1)


# Initialize the Flask application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0





# Define a route for the default URL, which loads the form
@app.route('/',methods=['POST','GET'])
def form():

    response = render_template('form_audio.html')

    return response


# Run the app
if __name__ == '__main__':
    app.run(threaded=True,
        #host="0.0.0.0",
        port=int("8000")
    )
