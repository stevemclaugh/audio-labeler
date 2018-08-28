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
import hashlib
import multiprocessing

## How to hash:
# hashlib.sha256(b'Hello World').hexdigest()
password_hash = '06899b046ad79b40e5ce4aca5cac0f9bbdfcfa2b405900f7ef10ace146fe2710'

client = MongoClient()

records = client.venmo_data.transactions

## Flask launch loop bash command (for testing):
#  while :; do python2 app.py & sleep 30 && killall python2; sleep 0.5; done



    # Initialize the Flask application
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


try: os.remove("./static/plot.png")
except: pass



# Define a route for the default URL, which loads the form
@app.route('/',methods=['POST','GET'])
def form():

    client = MongoClient()

    records = client.venmo_data.transactions

    plot_complete = 'false'

    try: case_sensitive = request.form['case_sensitive']
    except: case_sensitive = 'false'

    try: emoji_tokenize = request.form['emoji_tokenize']
    except: emoji_tokenize = 'false'

    try: start_date_unix = request.form['start_date_unix']
    except: start_date_unix = 0

    try: start_date = request.form['start_date']
    except: start_date = 0

    try: end_time_unix = request.form['end_time_unix']
    except: end_time_unix = 0

    try: end_time  = request.form['end_time']
    except: end_time = 0

    try: resolution = request.form['resolution']
    except: resolution = 'month'
    ## 'day', 'week', or 'month'



    ## Verifying auth key
    try: auth_key = request.form['auth_key']
    except: auth_key = ''

    if password_hash != hashlib.sha256(auth_key.encode(encoding='UTF-8')).hexdigest():
        response = render_template('auth.html', auth_key=auth_key)
        return response



    try:
        search_string = request.form['search_string']
        try:
            search_string_name = request.form['search_string_name']
            if search_string_name.strip()=='':
                search_string_name = search_string
        except:
            search_string_name = search_string
    except:
        search_string = ''
        search_string_name = ''



    def search_and_plot():


        month_unix_start_dates = []

        for year in range(2012, 2019):
            for month in range(1,13):
                unix_time_start = int(datetime.datetime(year, month, 1, 0, 0).timestamp())
                month_unix_start_dates.append(unix_time_start)

        ## Including this value for debugging purposes. Set the number of
        # months to 12 or 24 to make a quick plot of the first year or two.

        number_of_months = len(month_unix_start_dates)
        number_of_months = 48

        transaction_counts_by_month = []
        total_counts_by_month = []

        percentages_by_month = []

        counter = 0

        for i in list(range(len(month_unix_start_dates)-1))[:number_of_months]:
            start_date = month_unix_start_dates[i]-1
            end_time = month_unix_start_dates[i+1]+1
            month_string = datetime.datetime.fromtimestamp(month_unix_start_dates[i]).strftime('%Y-%m')
            cursor = records.find({ "unix_time": { "$gt": start_date, "$lt": end_time }, 'message': {'$regex': ".*{}.*".format(search_string)}})
            uses = cursor.count()
            transaction_counts_by_month.append(uses)
            #total = records.find({ "unix_time": { "$gt": start_date, "$lt": end_time }}).count()
            #total_counts_by_month.append(total)
            try:
                percentages_by_month.append(uses/total)
            except:
                percentages_by_month.append(0)
            #print(month_unix_start_dates[i])
            counter += 1
            with open('./static/counter.txt', 'w') as fo:
                fo.write(str(100*counter/number_of_months)+'%')
            #print(counter)

        percentages_by_month = [item*100 for item in percentages_by_month]

        month_strings = ['2012-01', '2012-02', '2012-03', '2012-04', '2012-05', '2012-06', '2012-07', '2012-08', \
                         '2012-09', '2012-10', '2012-11', '2012-12', '2013-01', '2013-02', '2013-03', '2013-04', \
                         '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12', \
                         '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', \
                         '2014-09', '2014-10', '2014-11', '2014-12', '2015-01', '2015-02', '2015-03', '2015-04', \
                         '2015-05', '2015-06', '2015-07', '2015-08', '2015-09', '2015-10', '2015-11', '2015-12', \
                         '2016-01', '2016-02', '2016-03', '2016-04', '2016-05', '2016-06', '2016-07', '2016-08', \
                         '2016-09', '2016-10', '2016-11', '2016-12', '2017-01', '2017-02', '2017-03', '2017-04', \
                         '2017-05', '2017-06', '2017-07', '2017-08', '2017-09', '2017-10', '2017-11', '2017-12', \
                         '2018-01', '2018-02', '2018-03', '2018-04', '2018-05', '2018-06', '2018-07', '2018-08', \
                         '2018-09', '2018-10', '2018-11'][:number_of_months]


        #High-res file:
        #plt.figure(figsize = (30,16))
        plt.figure(figsize = (15,8))
        plt.xticks(range(len(month_strings)), month_strings)  # two arguments: tick positions, tick display list
        plt.xticks(rotation=-85)
        plt.ylabel('Number of messages containing "{}"'.format(search_string_name.lower()))
        plt.xlabel('Month')
        plt.title('"{}" use over time'.format(search_string_name))
        plt.plot(transaction_counts_by_month)
        plt.savefig("./static/plot.png")

        time.sleep(0.005)
        plot_complete = 'true'



    #response = render_template('form_audio.html')
    if search_string.strip() != '':
        background_process = multiprocessing.Process\
                         (name='background_process',\
                          target=search_and_plot)
        background_process.daemon = True
        background_process.start()


    response = render_template('form.html', plot_complete=plot_complete, search_string=search_string, search_string_name=search_string_name, case_sensitive=case_sensitive, emoji_tokenize=emoji_tokenize, start_date_unix=start_date_unix, start_date=start_date, end_time_unix=end_time_unix, end_time=end_time, resolution=resolution, auth_key = auth_key)
    return response



    #, search_string=search_string,start_date=start_date, end_time=end_time, resolution=resolution, title=title, xlabel=xlabel, ylabel=ylabel)


            ### Venmo search Flask app variables ###
            # start_date=start_date,
            # end_time=end_time,
                ## ^ either entered as text or generated via dropdowns using javascript
            #resolution=resolution,
                ## day, week, or month
            # title=title, xlabel=xlabel, ylabel=ylabe
                ## Title and labels to be rendered in plot. Reasonable default if not specified.





# Run the app
if __name__ == '__main__':
    app.run(threaded=True,
        #host="0.0.0.0",
        port=int("8000")
    )
