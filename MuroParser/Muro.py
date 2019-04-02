# -*- coding: UTF-8 -*-

'''
Muro Parser:
A tool that parses MuroBBS threads and outputs plots and stats from it
@author kari.vatjusanttila@gmail.com
'''

from __future__ import print_function
from builtins import input
from builtins import str
from builtins import range

from ggplot import *
from collections import OrderedDict
from optparse import OptionParser
import codecs
import datetime
import heapq
import os.path
import requests
import simplejson as json
import time
import pandas as pd
import sys

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib.dates import DateFormatter
matplotlib.style.use('ggplot')

# Python Progressbar
try:
    from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker
except ImportError:
    pbar_available = False
    print("Progressbar module not available and thus cannot be used!")
else:
    pbar_available = True

epoch = datetime.datetime(1970,1,1)

defaul_thread_url = "http://murobbs.muropaketti.com/threads/pc-ps4-xbox-one-wii-u-yhteinen-vaeittelyketju.1010222/"

def fetch_thread_header_info():
    ''' fetch thread data like thread ID and how much data it contains '''
    temp = list(str(requests.get(thread_url).text.encode("ascii", "ignore")).split("\\n"))
    for i in temp:
        if "data-last" in i: # strip the amount of pages in the thread
            data_last = int(i.split('=')[1].strip("\""))
        if "name=\"type[post][thread_id]\"" in i: # strip the thread_id that makes it unique
            thread_id = int(i.split('=')[-1].strip("\""))
    return data_last, thread_id

def clean_users(data, threshold):
    ''' delete keys (users) with lower or equal to threshold # of messages '''
    for k in list(data.keys()):
        try:
            if len(data[k]) <= threshold:
                del data[k]
        except KeyError:
            pass
        except ValueError:
            pass
    return data

def print_top_commenters(data, amount):
    ''' print top N commenters of the thread '''
    print(str.format("\n{0} Most active commenters in thread {1}", amount, thread_id))
    temp = []
    try:
        # dump data to list of tuples [nickname, # of messages]
        for k in list(data.keys()):
            try:
                temp.append([k.encode('ascii', 'ignore'), len(data[k])])
            except TypeError:
                pass
    except KeyError:
        print("Printing of top commenters failed. Check data integrity for errors")

    temp = heapq.nlargest(amount, temp, key=lambda x: x[1]) # sort based on amount of messages sent
    counter = 1
    for i in temp:
        print(str.format("{0}: {1} : {2} messages", str(counter).rjust(2, ' '), str(i[0]).ljust(25, ' '), str(i[1]).rjust(5, ' ')))
        counter += 1

def print_low_commenters(data, amount):
    ''' print low N commenters of the thread '''
    print(str.format("\n{0} Most inactive commenters in thread {1}", amount, thread_id))
    temp = []
    try:
        # dump data to list of tuples [nickname, # of messages]
        for k in list(data.keys()):
            try:
                temp.append([k.encode('ascii', 'ignore'), len(data[k])])
            except TypeError:
                pass
    except KeyError:
        print("Printing of inactive commenters failed. Check data integrity for errors")

    temp = heapq.nsmallest(amount, temp, key=lambda x: x[1]) # sort based on amount of messages sent
    counter = 1
    for i in temp:
        print(str.format("{0}: {1} : {2} messages", str(counter).rjust(2, ' '), str(i[0]).ljust(25, ' '), str(i[1]).rjust(5, ' ')))
        counter += 1

def save_data(filename, data):
    ''' saves dataset to a file '''
    print(str.format("Saving data to {0}", filename))
    with codecs.open(filename, "w", "utf-8") as f:
        json.dump(data, f, sort_keys=True)

def load_data(filename, head):
    ''' load a dataset from file '''
    temp = {}
    with open(filename, "r") as infile:
        temp = json.loads(infile.read())
        if temp["data_last"] < head:
            print(str.format("Data is out of date. {0} pages more since last update", head - temp["data_last"]))
            while True:
                choice = input("Do you want to update the dataset (Y/N): ")

                if choice in 'Yy':
                    downloaded_dict = download_thread_data(temp["data_last"], head)
                    if downloaded_dict is not None:
                        temp = merge_dicts(temp, downloaded_dict)
                    break
                elif choice in 'Nn':
                    return temp, False
        else:
            print("Data already up-to-date")
            return temp, True

    print(str.format("User data up-to-date and loaded for thread ID {0}", thread_id))
    return temp, True

def download_thread_data(start, end):
    ''' download userdata from thread '''
    print("Downloading thread data...")
    dict = {}
    
    if pbar_available: 
        widgets = ['Downloading:', Percentage(), ' ', ETA(), ' ', Bar(marker=RotatingMarker())]
        pbar = ProgressBar(widgets=widgets, maxval=end-start).start()
    try:
        for i in range(start, end):
            temp = list(str(requests.get(thread_url + "page-" + str(i)).text.encode('UTF-8', 'ignore')).split("\\n"))
            for j in temp:
                # strip the nickname and insert it to users dictionary as a key
                if "data-author" in j and "class=\"sectionMain message" in j:
                    currentuser = j.split(" ")[7].split("=")[1].strip("\">")
                    # if the parsed user does not yet exist -> Add it
                    if currentuser not in list(dict.keys()):
                        #print(str.format("Adding new user {0}", currentuser.encode('ascii', 'ignore')))
                        dict[currentuser] = []

                if "datePermalink" in j and "DateTime" in j and currentuser is not None:
                    # newer comments has it like this. Use this as a workaround I guess
                    if "data-datestring" in j and "data-timestring" in j:
                        timestamp = str(j.split('=')[9].split(">")[1]).replace(' klo', '').replace('</abbr', '')
                    else: # older timestamps can be parsed like this
                        timestamp = str(j.split('=')[6].split("\"")[1]).replace(' klo', '')

                    # convert timestamp to epoch
                    date = datetime.datetime.strptime(timestamp, "%d.%m.%Y %H:%M")
                    delta_time = (date - epoch).total_seconds()
                    dict[currentuser].append(int(delta_time))

            # update progressbar
            if pbar_available:
                pbar.update(i - start)

        # done with download, update data_last field
        dict["data_last"] = end
    except KeyboardInterrupt:
        print("Keyboard interrupt. Download stopped")
        if pbar_available:
            pbar.finish()
        return None

    if pbar_available:
        pbar.finish()
    return dict

def merge_dicts(dicta, dictb):
    '''  merge two dictionaries into one '''
    if dictb is not None:
        for key in list(dictb.keys()):
            if key in list(dicta.keys()):
                if key == "data_last":
                    dicta[key] = dictb[key]
                else:
                    for i in range(len(dictb[key])):
                        dicta[key].append(dictb[key][i])
            else:
                dicta[key] = []
                dicta[key].append(dictb[key])
    return dicta

def to_dataframe(data, username):
    ''' convert epoch timestamps to datetime. Return: Pandas DataFrame '''
    converted_dataset = OrderedDict()
    first_day = datetime.datetime.fromtimestamp(data[username][0]).strftime('%Y-%m-%d')
    first_day = datetime.datetime.strptime(first_day, '%Y-%m-%d')
    today = datetime.datetime.today()
    dates = pd.date_range(first_day, today, freq='D')
    temp_df = pd.DataFrame(index = dates, columns=['Activity'])

    for i in range(len(data[username])):
        date = datetime.datetime.fromtimestamp(data[username][i]).strftime('%Y-%m-%d')
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        if date in converted_dataset:
            converted_dataset[date] += 1
        else:
            converted_dataset[date] = 1

    for val, item in converted_dataset.items():
        temp_df.ix[val] = item

    temp_df['Activity'] = temp_df['Activity'].astype(float)
    temp_df = temp_df.interpolate(method='cubic')
    temp_df = temp_df.fillna(0)

    df = pd.DataFrame.from_dict(converted_dataset, 'index').reset_index()
    df.columns = ['Date', 'Activity']
    return temp_df

def ask_pages_to_fetch(data_last):
    start = 1
    end = data_last
    filename = str(thread_id) + ".dat"
    choice = ""
    while True:
        try:
            choice = input("Thread is quite massive. Download all " + str(data_last) + " pages? (y/n)")
            if choice == "":
                pass
            elif choice in 'Yy':
                break
            elif choice in 'Nn':
                while True:
                    try:
                        choice = input("Please specify a range in format <start>-<end>, or page number where to start (1-" + str(data_last) + ") (0 skips): ")
                        if "-" in choice:   #range most likely is the scenario
                            pagerange = choice.split("-")
                            start = int(pagerange[0])
                            end = int(pagerange[1])
                            if start < 1 or end < 1 or start > data_last or end > data_last:
                                raise IndexError
                            if end <= start:
                                raise IndexError
                            filename = str(thread_id) + "pages" + str(start) + "-" + str(end) + ".dat"
                            break
                        else:
                            start = int(choice)
                            end = data_last
                            if start > data_last:
                                raise ValueError
                            else:
                                filename = str(thread_id) + "from" + str(start) +".dat"
                                break
                    except TypeError:
                        print("Invalid page range or page number!")
                    except IndexError:
                        print("Invalid page range specified!")
                    except ValueError:
                        print("Invalid page range or page number!")
                    except KeyboardInterrupt:
                        print("\nCancelled")
                        sys.exit(0)
                break
        except KeyboardInterrupt:
            print("\nCancelled")
            sys.exit(0)
    return start, end, filename

if __name__ == "__main__":
    ''' tool for parsing through a thread and visualize certain aspects of it '''
    print("Muro Parser 3000 - Welcome")
    parser = OptionParser(usage="Usage: %prog [OPTIONS]\nTry '%prog --help' for more information.", version="%prog 1.0")
    parser.add_option("--url",
                  action="store",
                  dest="thread_url",
                  default="",
                  help="direct URL to the target thread",)
    (options, args) = parser.parse_args()

    # init common variables
    userdata = {}
    should_save = False
    currentuser = None
    data_last = 0
    thread_id = 0
    thread_url = options.thread_url
    start = 0
    end = 0

    if thread_url == "":
        print("No thread URL provided. Using a default one...")
        thread_url = defaul_thread_url

    data_last, thread_id = fetch_thread_header_info()
    filename = str(thread_id) + ".dat"

    # if a data file belonging to this thread exists. Read dataset from file instead of downloading it
    if os.path.isfile(filename) == True:
        print(str.format("User data for thread ID {0} found. Reading from file...", thread_id))
        userdata, should_save = load_data(filename, data_last)
        if should_save == False:
            start, end, filename = ask_pages_to_fetch(data_last)
    else:
        if data_last > 500:
            start, end, filename = ask_pages_to_fetch(data_last)
        # if user wanted to fetch a range of pages, check if that range exists and load it instead of downloading
        if os.path.isfile(filename) == True:
            print(str.format("User data for thread ID {0} found with this page range. Reading from file...", thread_id))
            userdata, should_save = load_data(filename, data_last)
        else: # just download the thread data
            userdata = download_thread_data(start, end)
            should_save = True

    # prints out the top and low commenters of the thread
    print_top_commenters(userdata, 10)
    print_low_commenters(userdata, 10)

    username = ""

    while True:
        username = str(input("Please give a username you want to print statistics of (blank username quits): "))
        if username == "":
            break
        else:
            try:
                if username in userdata.keys():
                    break;
                else:
                    print("Unknown username \"" + username + "\" provided. Try again.")
            except KeyError:
                print("Unknown username \"" + username + "\" provided. Try again.")
                pass

    if username != "":
        plt.figure();
        df = to_dataframe(userdata, username)
        df = df.reset_index()
        ax = df.plot(x='index', y='Activity', title='Summary of messages sent for user ' + username + '. Thread ID: ' + str(thread_id), figsize=(14, 8))
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of messages")
        plt.ylim((0,80))
        plt.grid(True)
        plt.savefig(username + str(thread_id) + '.png')

    # save data to a file for future use if dataset was altered
    if should_save == True and userdata is not None:
        save_data(filename, userdata)

    print("Thank you for using MuroParser and come again. Exiting...")