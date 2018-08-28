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
import random
import collections
import csv

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


## Initializing file
with open('test.txt', 'w') as fo:
    fo.write('')



# Define a route for the default URL, which loads the form
@app.route('/',methods=['POST','GET'])
def form():

    # Initializing CSV file
    with open('./static/random_messages.csv', 'w') as fo:
        fo.write('')

    client = MongoClient()

    records = client.venmo_data.transactions

    plot_complete = 'false'

    search_string_name = ''
    try:
        search_string_name = ''
        search_string = request.form['search_string']
        try:
            search_string_name = request.form['search_string_name']
        except:
            pass
    except:
        search_string = ''
        search_string_name = ''



    try: case_sensitive = request.form['case_sensitive']
    except: case_sensitive = 'false'

    try: emoji_tokenize = request.form['emoji_tokenize']
    except: emoji_tokenize = 'false'

    try: start_time_unix = request.form['start_time_unix']
    except: start_time_unix = 0

    try: start_time = request.form['start_time']
    except: start_time = 0

    try: end_time_unix = request.form['end_time_unix']
    except: end_time_unix = 0

    try: end_time  = request.form['end_time']
    except: end_time = 0

    try: resolution = request.form['resolution']
    except: resolution = 'month'
    ## 'day', 'week', or 'month'


    ### Verifying auth key ###
    try: auth_key = request.form['auth_key']
    except: auth_key = ''

    if password_hash != hashlib.sha256(auth_key.encode(encoding='UTF-8')).hexdigest():
        response = render_template('auth.html', auth_key=auth_key)
        return response


    header = ["Transaction Date", "Message", "Sender Name", "Sender ID", "Target Name", "Target ID"]

    def search_and_plot():

        client = MongoClient()
        records = client.venmo_data.transactions

        month_unix_start_times = []

        for year in range(2012, 2019):
            for month in range(1,13):
                unix_time_start = int(datetime.datetime(year, month, 1, 0, 0).timestamp())
                month_unix_start_times.append(unix_time_start)

        ## Including this value for debugging purposes. Set the number of
        # months to 12 or 24 to make a quick plot of the first year or two.

        number_of_months = len(month_unix_start_times)
        number_of_months = 16

        transaction_counts_by_month = []
        total_counts_by_month = []

        percentages_by_month = []

        counter = 0



        for i in list(range(len(month_unix_start_times)-1))[:number_of_months]:
            start_time = month_unix_start_times[i]-1
            end_time = month_unix_start_times[i+1]+1
            month_string = datetime.datetime.fromtimestamp(month_unix_start_times[i]).strftime('%Y-%m')

            if case_sensitive == 'true':
                cursor = records.find({ "unix_time": { "$gt": start_time, "$lt": end_time }, 'message': {'$regex': ".*{}.*".format(search_string)}})
            else:
                #### NEED TO GET
                #### A COMMAND THAT ACTUALLT WORKS:
                cursor = records.find({ "unix_time": { "$gt": start_time, "$lt": end_time }, 'message': {'$regex': ".*{}.*".format(search_string)}})
                #### Currently a dummy command; canse insensitivity doesn't work yet. @@@@

            uses = cursor.count()

            try: random_indices = set(random.sample(list(range(uses)), 3))
            except: random_indices = set()

            random_transactions = []
            random_transaction_lol = []


            cursor = records.find({ "unix_time": { "$gt": start_time, "$lt": end_time }, 'message': {'$regex': ".*{}.*".format(search_string)}})

            j=0
            for item in cursor:
                if j in random_indices:
                    random_transactions.append(item)
                    unix_time = item['unix_time']
                    account_created = item['actor']['date_created']
                    sender_name = item['actor']['name']
                    sender_id = item['actor']['id']
                    picture_url = item['actor']['picture']
                    username = item['actor']['username']
                    message = item['message']
                    transaction_date = item['created_time']
                    target_name = item['transactions'][0]['target']['name']
                    target_id = item['transactions'][0]['target']['id']
                    row = [transaction_date, message, sender_name, sender_id, target_name, target_id]
                    random_transaction_lol.append(row)
                j+=1


            with open('./static/random_messages.csv', 'a') as fo:
                csv_writer = csv.writer(fo)
                csv_writer.writerows(random_transaction_lol)




            transaction_counts_by_month.append(uses)
            #total = records.find({ "unix_time": { "$gt": start_time, "$lt": end_time }}).count()
            #total_counts_by_month.append(total)
            try:
                percentages_by_month.append(uses/total)
            except:
                percentages_by_month.append(0)
            #print(month_unix_start_times[i])
            counter += 1
            with open('./static/counter.txt', 'w') as fo:
                fo.write(str(round(100*counter/number_of_months, 2))+'%')
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
        if search_string_name.strip() == '':
            plt.ylabel('Number of messages containing "{}"'.format(search_string))
            plt.title('"{}" use over time'.format(search_string))
        else:
            plt.ylabel('Number of messages containing "{}"'.format(search_string_name.lower()))
            plt.title('"{}" use over time'.format(search_string_name))
        plt.xlabel('Month')
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


    response = render_template('form.html', plot_complete=plot_complete, search_string=search_string, \
    search_string_name=search_string_name, case_sensitive=case_sensitive, emoji_tokenize=emoji_tokenize, \
    start_time_unix=start_time_unix, start_time=start_time, end_time_unix=end_time_unix, end_time=end_time, \
    resolution=resolution, auth_key = auth_key, header=header)
    return response



    #, search_string=search_string,start_time=start_time, end_time=end_time, resolution=resolution, title=title, xlabel=xlabel, ylabel=ylabel)


            ### Venmo search Flask app variables ###
            # start_time=start_time,
            # end_time=end_time,
                ## ^ either entered as text or generated via dropdowns using javascript
            #resolution=resolution,
                ## day, week, or month
            # title=title, xlabel=xlabel, ylabel=ylabe
                ## Title and labels to be rendered in plot. Reasonable default if not specified.





# Define a route for the default URL, which loads the form
@app.route('/user',methods=['POST','GET'])
def user():

    try: actor_id = request.form['actor_id']
    except: actor_id = request.args['id']

    try: auth_key = request.form['auth_key']
    except: auth_key = ''

    try: pass_status = request.args['pass']
    except: pass_status = 'false'



    if password_hash != hashlib.sha256(auth_key.encode(encoding='UTF-8')).hexdigest():
        if pass_status != 'true':
            response = render_template('auth_user.html', auth_key=auth_key, actor_id=actor_id)
            return response


    transaction_list = []
    transaction_lol = []
    cursor = records.find({'actor.id': str(actor_id)})
    header = ["Transaction Date", "Message", "Target Name", "Target ID"]




    for item in cursor:
        transaction_list.append(str(item))
        unix_time = item['unix_time']
        account_created = item['actor']['date_created']
        actor_name = item['actor']['name']
        picture_url = item['actor']['picture']
        username = item['actor']['username']
        message = item['message']
        transaction_date = item['created_time']
        target_name = item['transactions'][0]['target']['name']
        target_id = item['transactions'][0]['target']['id']
        row = [transaction_date, message, target_name, target_id]
        transaction_lol.append(row)

    transaction_lol.sort(key=lambda x: x[0])



    incoming_transaction_list = []
    incoming_transaction_lol = []
    cursor = records.find({'transactions.0.target.id': str(actor_id)})
    header_incoming = ["Transaction Date", "Message", "Sender Name", "Sender ID"]


    for item in cursor:
        incoming_transaction_list.append(str(item))
        sender_name = item['actor']['name']
        sender_id = item['actor']['id']
        picture_url = item['actor']['picture']
        username = item['actor']['username']
        message = item['message']
        transaction_date = item['created_time']
        row = [transaction_date, message, sender_name, sender_id]
        incoming_transaction_lol.append(row)

    incoming_transaction_lol.sort(key=lambda x: x[0])




    ## Creating a list of top friends
    friends_lol = [(item[2], item[3]) for item in transaction_lol]
    counter=collections.Counter(friends_lol)
    top_friends = counter.most_common(5)

    transaction_count = len(transaction_list)
    incoming_transaction_count = len(incoming_transaction_lol)

    response = render_template('user.html', actor_id=actor_id, username=username, header = header, header_incoming=header_incoming, \
    transaction_count=transaction_count, account_created=account_created, actor_name=actor_name, \
    picture_url=picture_url, transaction_lol=transaction_lol, incoming_transaction_lol=incoming_transaction_lol, \
    top_friends=top_friends, auth_key=auth_key, incoming_transaction_count=incoming_transaction_count)
    return response





# Run the app
if __name__ == '__main__':
    app.run(threaded=True,
        #host="0.0.0.0",
        port=int("8000")
    )
