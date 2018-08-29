# We need to import `request` to access the details of the POST request
# and `render_template`, to render our templates (form and response).
# We'll use `url_for` to get some URLs for the app in the templates.
from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rc
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
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from copy import copy


errors = []

## How to hash:
# hashlib.sha256(b'Hello World').hexdigest()
password_hash = '9ec0057874675f64383d5c634b78844d3c7da32fee5245c3bdf6937c64d443a3'

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

    date_string = datetime.now().strftime("%Y-%m-%d_%H%M_%S.%f")
    plot_path = "./static/plot_{}.png".format(date_string)

    search_string_name = ''
    try:
        search_string = request.form['search_string']
        try:
            search_string_name = request.form['search_string_name']
        except:
            pass
    except Exception as e:
        print(e)
        search_string = ''
        search_string_name = ''

    try: raw_count = request.form['raw_count']
    except: raw_count = 'false'

    try: case_sensitive = request.form['case_sensitive']
    except: case_sensitive = 'false'

    try: start_date_unix = request.form['start_date_unix']
    except: start_date_unix = 0

    try:
        start_date = request.form['start_date']
        if start_date.strip() == '':
            start_date = '2012-03-20'
    except: start_date = '2012-03-20'

    try: end_date_unix = request.form['end_date_unix']
    except: end_date_unix = 0

    try:
        end_date  = request.form['end_date']
        if end_date.strip() == '':
            end_date = '2013-04-24'
            #end_date = '2018-04-24'
    except:
        end_date = '2013-04-24'
        #end_date = '2018-04-24'

    try: resolution_level = request.form['resolution']
    except Exception as e:
        errors.append(e)
        with open('errors.txt', 'w') as fo:
            fo.write(str(e))
            fo.write('\n')
        resolution_level = 'month'
    ## 'day', 'week', or 'month'

    csv_path = './static/' + resolution_level + '_plot_' + search_string.replace(' ', '_').replace(':', '_').replace('/', '_') + "_" + date_string + '.csv'

    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    ### Verifying auth key ###
    try: auth_key = request.form['auth_key']
    except: auth_key = ''

    if password_hash != hashlib.sha256((auth_key + 'arbitrary_salt').encode(encoding='UTF-8')).hexdigest():
        response = render_template('auth.html', auth_key=auth_key)
        return response


    header = ["Transaction Date", "Message", "Sender Name", "Sender ID", "Target Name", "Target ID"]

    random_transactions = []
    random_transaction_lol = []

    if search_string.strip() != '':

        j = 0

        while len(random_transaction_lol) < 25:
            cursor = records.aggregate( [{ "$sample": { "size": 1000 } }] )
            for item in cursor:
                if search_string.lower() in item['message'].lower():
                    random_transactions.append(item)

                    unix_time = item['unix_time']
                    try: account_created = item['actor']['date_created']
                    except: account_created = 'Unknown'
                    sender_name = item['actor']['name']
                    sender_id = item['actor']['id']
                    picture_url = item['actor']['picture']
                    username = item['actor']['username']
                    message = item['message']
                    transaction_date = item['created_time']
                    try: target_name = item['transactions'][0]['target']['name']
                    except: target_name = 'Unknown'
                    try: target_id = item['transactions'][0]['target']['id']
                    except: target_id = 'Unknown'
                    row = [transaction_date, message, sender_name, sender_id, target_name, target_id]
                    random_transaction_lol.append(row)
            if j > 12:
                break
            j+=1


        with open('./static/random_messages.csv', 'a') as fo:
            csv_writer = csv.writer(fo)
            csv_writer.writerows(random_transaction_lol)



    def search_and_plot(start_date, end_date, resolution, date_string):

        client = MongoClient()
        records = client.venmo_data.transactions

                        ## Rounding to full weeks
        # Monday is 0 and Sunday is 6.



        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')


        if resolution == 'day':
            end_datetime += timedelta(days=1)

        elif resolution == 'week':
            while start_datetime.weekday() != 0:
                start_datetime += timedelta(days=1)
            while end_datetime.weekday() != 6:
                end_datetime -= timedelta(days=1)
            end_datetime += timedelta(days=1)

        elif resolution == 'month':
            end_datetime += timedelta(days=1)
            while int(start_datetime.strftime("%d")) != 1:
                start_datetime += timedelta(days=1)
            while int(end_datetime.strftime("%d")) != 1:
                end_datetime -= timedelta(days=1)



        start_datetime_list = []

        if resolution == 'day':
            temp_datetime = copy(start_datetime)
            for i in range((end_datetime-start_datetime).days):
                start_datetime_list.append(copy(temp_datetime))
                temp_datetime += timedelta(days=1)
            del temp_datetime

        elif resolution == 'week':
            temp_datetime = copy(start_datetime)
            weeks = int((end_datetime - start_datetime).days / 7)
            for i in range(weeks):
                start_datetime_list.append(copy(temp_datetime))
                temp_datetime += timedelta(days=7)
            del temp_datetime

        elif resolution == 'month':
            temp_datetime = copy(start_datetime)
            while temp_datetime <= end_datetime:
                start_datetime_list.append(copy(temp_datetime))
                time.sleep(0.01)
                temp_datetime += relativedelta(months=+1)
                time.sleep(0.01)
            del temp_datetime

        x_ticks = []

        if resolution == 'day':
            for item in start_datetime_list:
                x_ticks.append(item.strftime("%Y-%m-%d"))
            start_datetime_list = start_datetime_list[:-1] ## Removing extraneous last day label

        elif resolution == 'week':
            for item in start_datetime_list:
                x_ticks.append(item.strftime("%Y-%m-%d"))
            start_datetime_list = start_datetime_list[:-1] ## Removing extraneous last week label

        elif resolution == 'month':
            for item in start_datetime_list:
                x_ticks.append(item.strftime("%Y-%m"))
            start_datetime_list = start_datetime_list[:-1] ## Removing extraneous last month label


        unix_start_times = [int(item.timestamp()) for item in start_datetime_list]

        transaction_counts = []
        total_counts = []

        percentages = []

        counter = 0



        for i in list(range(len(unix_start_times)-1)):
            start_date_temp = unix_start_times[i]-1
            end_date_temp = unix_start_times[i+1]

            if case_sensitive == 'true':
                cursor = records.find({ "unix_time": { "$gt": start_date_temp, "$lt": end_date_temp }, 'message': {'$regex': ".*{}.*".format(search_string)}})
            else:
                #### NEED TO GET
                #### A COMMAND THAT ACTUALLT WORKS:
                cursor = records.find({ "unix_time": { "$gt": start_date_temp, "$lt": end_date_temp }, 'message': {'$regex': ".*{}.*".format(search_string)}}).collation( { "locale": 'en', "strength": 2 } )
                #### Currently a dummy command; canse insensitivity doesn't work yet. @@@@

            uses = cursor.count()

            # Calculating total transactions over the same period
            transaction_counts.append(uses)
            total = records.find({ "unix_time": { "$gt": start_date_temp, "$lt": end_date_temp }}).count()
            #total_counts.append(total)
            try:
                percentages.append(100 * (uses/total))
            except:
                percentages.append(0)
            #print(unix_start_times[i])
            counter += 1
            counter_path = './static/counter_{}.txt'.format(date_string)
            with open(counter_path, 'w') as fo:
                counter_string = str(round(100.0*(int(counter)/(len(unix_start_times)-1)), 2))+'%'
                if counter_string == '100.0%':
                    counter_string == '99.9%'
                fo.write(counter_string)

            #try: os.remove(counter_path)
            #except: pass
            #print(counter)




###
        if raw_count == 'true':

            #High-res file:
            #plt.figure(figsize = (30,16))
            plt.figure(figsize = (15,8))
            plt.tight_layout()
            plt.xticks(range(len(x_ticks)), x_ticks)  # two arguments: tick positions, tick display list
            plt.xticks(rotation=-85)
            if search_string_name.strip() == '':
                plt.ylabel('Number of messages containing "{}"'.format(search_string))
                plt.title('"{}" use over time'.format(search_string))
            else:
                plt.ylabel('Number of messages containing {}'.format(search_string_name.lower()))
                plt.title('"{}" use over time'.format(search_string_name))
            plt.xlabel('Month')
            plt.plot(transaction_counts)
            plt.savefig("./static/plot.png")

            with open(csv_path, 'w') as fo:
                csv_writer = csv.writer(fo)
                csv_writer.writerow(['Start date', 'String appearance count'])
                csv_writer.writerows(list(zip(x_ticks, transaction_counts)))

###
        else:

            #rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
            rc('font',**{'family':'serif','serif':['Times']})
            rc('text', usetex=False)


            font = {
                    'weight' : 'normal',
                    'size'   : 26}

            matplotlib.rc('font', **font)


            plt.figure(figsize = (30,16))

            plt.tight_layout()


            lol = [[item, '', '', ''] for item in x_ticks[::4]]
            final_ticks = [item for sublist in lol for item in sublist]

            plt.xticks(range(len(x_ticks)), final_ticks)  # two arguments: tick positions, tick display list

            plt.tick_params(pad=15)
            plt.xticks(rotation=-85)

            if search_string_name.strip() == '':
                plt.ylabel('Percent (%) of messages containing "{}"'.format(search_string))
                plt.title('"{}" use over time'.format(search_string))
            else:
                plt.ylabel('Percent (%) of messages containing {}'.format(search_string_name.lower()))
                plt.title('"{}" use over time'.format(search_string_name))

            plt.xlabel('Month', labelpad=25)


            plt.gcf().subplots_adjust(bottom=0.17)
            plt.plot(percentages)
            time.sleep(0.005)

            plt.savefig(plot_path)

            with open(csv_path, 'w') as fo:
                csv_writer = csv.writer(fo)
                csv_writer.writerow(['Start date', 'String appearance percentage (%)'])
                csv_writer.writerows(list(zip(x_ticks, percentages)))

            with open(counter_path, 'w') as fo:
                fo.write('100.0%')

#####

    #response = render_template('form_audio.html')
    if search_string.strip() != '':
        background_process = multiprocessing.Process\
                         (name='background_process',\
                          target=search_and_plot, \
                          args = (start_date, end_date, resolution_level, date_string))
        background_process.daemon = True
        background_process.start()

    time.sleep(0.5)
    response = render_template('form.html', search_string=search_string, \
    search_string_name=search_string_name, case_sensitive=case_sensitive, raw_count=raw_count, \
    start_date_unix=start_date_unix, start_date=start_date, end_date_unix=end_date_unix, end_date=end_date, \
    resolution=resolution_level, auth_key = auth_key, header=header, \
    random_transaction_lol=random_transaction_lol, random_transaction_length=len(random_transaction_lol), \
    date_string=date_string, plot_path=plot_path, csv_path=csv_path)
    return response



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

    # Including this in case we get an account with no public outgoing transactions
    account_created = 'Unknown'
    actor_name = 'Unknown'

    for item in cursor:
        transaction_list.append(str(item))
        unix_time = item['unix_time']
        try: account_created = item['actor']['date_created']
        except: account_created = 'Unknown'
        try: actor_name = item['actor']['name']
        except: actor_name = 'Unknown'
        picture_url = item['actor']['picture']
        username = item['actor']['username']
        message = item['message']
        transaction_date = item['created_time']
        try: target_name = item['transactions'][0]['target']['name']
        except: target_name = 'Unknown'
        try: target_id = item['transactions'][0]['target']['id']
        except: target_id = 'Unknown'
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
    top_friends=top_friends, auth_key=auth_key, incoming_transaction_count=incoming_transaction_count, errors=errors)
    return response





# Run the app
if __name__ == '__main__':
    app.run(threaded=True,
        host="0.0.0.0",
        port=int("8050")
    )
