#!/usr/local/bin/python3.7
# -*- coding: utf-8 -*-
###############################################################################
#
#  The MIT License (MIT)
#  Copyright (c) 2021 Philippe Ostiguy
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
###############################################################################

"""Module for sentiment analysis on tickers of our choice. By default, data comes from the Finnhub API, which means
that the analysis should be done on company listed on US Exchange. We must use the same directory path to get the data
 as we use in the`webscrap_headlines` project"""

import os
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sentiment_analysis import VaderAnalysis
from data_extraction import HistoricalReturn
import matplotlib.pyplot as plt # Impot the relevant module
import pandas as pd

class Init():
    """Class that initializes global value for the project. It also use general method to initialize value.
     """

    def __init__(self):
        """Built-in method to inialize the global values for the module

        Attributes
        -------------------
        `self.start.date` : str
            start date of the training period. Must be within the last year for the free version of FinHub. Format
            must be "YYYY-mm-dd"
        `self.end_date` : str
            end date of the training period. Format must be "YYYY-mm-dd"
        `self.tickerS` : list
            tickers on which we want to perform the test. Can be one ticker in form of a list as well as a list
            of tickers like the s&p 500.
        `self.db_name` : str
            name of the sqlite3 database
        `self.news_header` : list
            default name of the column from the Finnhub API for news headlines
        `self.dir_path` : str
            directory where the data are saved. It takes into account the `self.start_date` and `self.end_date`
        `self.start_date_` : datetime object
            same thing as `start_date` but as a datetime object
        `self.end_date_` : datetime object
            same thing as `start_date` but as a datetime object
        `self.sentiment_name` : str
            Name of the sentiment analysis score in the pd Dataframe
        `self.daily_return` : str
            Name for the daily return column
        """

        #initialize value here
        self.start_date = "2020-09-22"
        self.end_date = "2021-02-22"
        self.tickers = ['AMZN']

        self.db_name = 'financial_data'
        self.news_header = ['category', 'datetime', 'headline', 'id', 'image', 'related', 'source', 'summary', 'url']
        self.sentiment_name = 'Sentiment Score'
        self.daily_return = 'Daily Return'

        #transform to datetime object
        self.start_date_ = datetime.strptime(self.start_date, "%Y-%m-%d")
        self.end_date_ = datetime.strptime(self.end_date, "%Y-%m-%d")
        self.delta_date = abs((self.end_date_ - self.start_date_).days) #number of days between 2 dates

        # directory to get data from `webscrap_headlines` project
        self.parent_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent
        self.dir_path = os.path.join(self.parent_dir,'webscrap_headlines/output',self.start_date + '_' + self.end_date
                                     + '/')

        self.pd_data = pd.DataFrame()
        try:
            self.start_date_ > self.end_date_
        except:
            print("'start_date' is after 'end_date'")


        if (datetime.strptime(self.start_date, "%Y-%m-%d") <= (datetime.now()- relativedelta(years=1))) :
            raise Exception("'start_date' is older than 1 year. It doesn't work with the free version of FinHub")

        if not os.path.isdir(self.dir_path):
            raise Exception("The directory doesn't exist, check date range, webscrap_headlines project directory or"
                            "path name")

if __name__ == '__main__':
    init_ = Init()
    for ticker in init_.tickers:
        fig, ax = plt.subplots() # Create the figure and axes object
        hist_ret = HistoricalReturn(start_date=init_.start_date, end_date=init_.end_date, start_date_=init_.start_date_,
                                  end_date_=init_.end_date_, ticker=ticker, dir_path=init_.dir_path,
                                  db_name=init_.db_name,daily_return=init_.daily_return)
        init_.pd_data = hist_ret.historical_price()

        v_analysis = VaderAnalysis(hist_price = init_.pd_data,start_date=init_.start_date, end_date=init_.end_date,
                                   start_date_=init_.start_date_,end_date_=init_.end_date_, ticker=ticker + '_',
                                   dir_path=init_.dir_path,db_name=init_.db_name, news_header = init_.news_header,
                                   sentiment_name=init_.sentiment_name)
        init_.pd_data = v_analysis.vader_analysis()
        init_.pd_data.plot(x =init_.sentiment_name,y=init_.daily_return,style = "o")
        print(init_.pd_data[init_.daily_return].corr(init_.pd_data[init_.sentiment_name]))

