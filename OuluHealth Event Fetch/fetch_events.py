#!/usr/bin/python3.4
#  -*- coding: UTF-8 -*-

'''

'''

from __future__ import print_function
from builtins import input
from builtins import str
from builtins import range

import requests
import codecs
import re
from optparse import OptionParser

apache_dir = "C:\\Apache24\\htdocs\\"

if __name__ == "__main__":
    ''' tool for parsing through OuluHealth related news and output a webpage from it'''
    parser = OptionParser(usage="Usage: %prog [OPTIONS]\nTry '%prog --help' for more information.", version="%prog 1.0")
    parser.add_option("--url",
                  action="store",
                  dest="url",
                  default="http://ouluhealth.fi/events/",
                  help="direct URL to the target page that contains news",)
    (options, args) = parser.parse_args()

    url = options.url
    news_headline = False
    archive_headline = False

    news = {}
    archive = {}
    news_index = 0
    archive_index = 0
    news[news_index] = []
    archive[archive_index] = []

    # helper variables
    date_start = ""
    date_end = ""
    headline = ""
    event_url = ""
    events = list(str(requests.get(url).text.encode('UTF-8', 'ignore')).split("\\n"))

    for line in events:
        if "<div class=\"news__item" in line: # we found a news headline
            news_headline = True
            archive_headline = False
            news[news_index] = []
        elif "</div>" in line and news_headline: # end of news headline
            print("Added: %s - %s %s" % (date_start, date_end, headline))
            news[news_index].append(headline)
            news[news_index].append(date_start)
            news[news_index].append(date_end)
            news[news_index].append(event_url)
            news_headline = False
            news_index +=1
        if "class=\"news__archive-item" in line: # we found a archive headline
            news_headline = False
            archive_headline = True
            archive[archive_index] = []
        elif "</a>" in line and archive_headline: # end of archive headline
            #print("%s %s %s" % (date_start, date_end, headline))
            archive[archive_index].append(headline)
            archive[archive_index].append(date_start)
            archive[archive_index].append(date_end)
            archive[archive_index].append(event_url)
            archive_headline = False
            archive_index +=1
            if archive_index >= 5:
                break
        if news_headline or archive_headline: # parse the news section
            if "tribe-event-date-start" in line: # start date
                date_start = line.split(">")
                date_start = date_start[2].rstrip("</span").replace(" at ", " ")
            if "tribe-event-time" in line:
                date_end = line.split(">")
                date_end = date_end[4].rstrip("</span").replace(" at ", " ")
            elif "tribe-event-date-end" in line: # end date
                date_end = line.split(">")
                date_end = date_end[4].rstrip("</span").replace(" at ", " ")
            elif "<h3>" in line: # headline
                headline = line.split(">")
                headline = re.sub(r"\</h3$", "", headline[1])   
            elif "class=\"link--read-more" in line: # url in news section
                event_url = line.strip("\\t").split("\"")[1]
            elif "class=\"news__archive-item" in line: # url in archive section
                event_url = line.strip("\\t").split("\"")[1]

    with codecs.open("events.txt", "w", "utf-8") as f:
        f.write("<table>\n")
        f.write("<colgroup\n")
        f.write("<col class=\"column30\"/>\n")
        f.write("<col class=\"column60\"/>\n")
        f.write("<col class=\"column10\"/>\n")
        f.write("</colgroup>\n")
        f.write("<tr>")
        f.write("<th>Tapahtuma</th>")
        f.write("<th>Tietoa</th>")
        f.write("<th>Milloin</th>")
        f.write("</tr>")

        for key in news.keys(): 
            f.write("<tr>\n")
            f.write("<td class=\"event_name\" data-swiper-parallax=\"-200\">" + news[key][0] + "</td>\n")
            f.write("<td class=\"event_info\" data-swiper-parallax=\"-200\">Event information can be read from <a href=\"JavaScript:newPopup('"  + news[key][3] + "');\">here</td>\n")
            if(news[key][2] == "" or news[key][1] == news[key][2]):           
                f.write("<td class=\"eventdate\" data-swiper-parallax=\"-200\">"+ news[key][1] + "</td>\n")
            else:
                f.write("<td class=\"eventdate\" data-swiper-parallax=\"-200\">"+ news[key][1] + " - " + news[key][2] + "</td>\n")
            f.write("</tr>\n")
        f.write("</table>\n")

        f.write("<div class=\"headline_archive\" data-swiper-parallax=\"-200\">Archived Events</div>\n")
        f.write("<table>\n")
        f.write("<colgroup\n")
        f.write("<col class=\"column30\"/>\n")
        f.write("<col class=\"column60\"/>\n")
        f.write("<col class=\"column10\"/>\n")
        f.write("</colgroup>\n")  
        f.write("<tr>")
        f.write("<th>Tapahtuma</th>")
        f.write("<th>Tietoa</th>")
        f.write("<th>Milloin</th>")
        f.write("</tr>")

        for key in archive.keys():
            f.write("<tr>\n")
            f.write("<td class=\"event_name\" data-swiper-parallax=\"-200\">" + news[key][0] + "</td>\n")
            f.write("<td class=\"event_info\" data-swiper-parallax=\"-200\">Event information can be read from <a href=\""  + news[key][3] + "\" target=\"_blank\">here</td>\n")            
            f.write("<td class=\"eventdate\" data-swiper-parallax=\"-200\">"+ news[key][1] + " - " + news[key][2] + "</td>\n")
            f.write("</tr>\n")
        f.write("</table>")