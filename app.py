from flask import Flask, render_template,request,redirect

import quandl as Qd
import pandas as pd
import numpy as np
import os
import time

from bokeh.io import curdoc
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components,file_html
from os.path import dirname, join  

app = Flask(__name__)
app.vars={}

###Load data from Quandl

def datetime(x):
    return np.array(x, dtype=np.datetime64)

def get_data(name):
    API_key = 'Lna2bo1e94UxhDJSsb8D'
    data = Qd.get('WIKI/%s' %name, trim_start = '2010-01-01', trim_end = '2017-06-01', authtoken=API_key)
    columns_tokeep =['Adj. Open','Adj. High','Adj. Low','Adj. Close','Adj. Volume']
    df = pd.DataFrame(data)
    mydf = df[columns_tokeep]
    mydf.reset_index(level=0, inplace=True)
    myticker = mydf.rename(index =datetime, columns = {"Adj. Open": "Open", "Adj. High":"High", "Adj. Low" :"Low", "Adj. Close": "Close", "Adj. Volume" : "Volume"})
    return myticker

def get_feature(name):
    mydata = get_data(name)
    feature = mydata.columns[0:-1].values.tolist()
    return feature

# feature_names = mydata.columns[1:-1].values.tolist()
def create_figure(mydata, current_feature_name):
    ticker = np.array(mydata[current_feature_name])
    ticker_dates = np.array(mydata['Date'])

    window_size = 30
    window = np.ones(window_size)/float(window_size)
    ticker_avg = np.convolve(ticker, window, 'same')

    p = figure(x_axis_type="datetime", title="%s One-Month Average" % current_feature_name)
    p.grid.grid_line_alpha = 0
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = '%s Price' % current_feature_name
    p.ygrid.band_fill_color = "green"
    p.ygrid.band_fill_alpha = 0.1

    p.circle(ticker_dates, ticker, size=4, legend='%s' % current_feature_name,
              color='darkgrey', alpha=0.2)

    p.line(ticker_dates, ticker_avg, legend='avg', color='navy')
    p.legend.location = "top_left"
    return p



@app.route("/index", methods=['GET','POST'])    

def index():
    
    if request.method == 'GET':
        return render_template('Search.html')
        
    else:
        #request was a POST
        app.vars['symbol'] = request.form['ticker']
        mydata = get_data(app.vars['symbol'])

        feature_names = get_feature(app.vars['symbol'])

        current_feature_name = request.args.get("feature_name")

        if current_feature_name == None:
            current_feature_name = "Close"
        
        plot = create_figure(mydata, current_feature_name)

        script, div = components(plot)       
        return render_template('Plot.html', script=script, div=div)
       
@app.route('/', methods=['GET','POST'])
def main():
    return redirect('/index')

if __name__== "__main__":

    app.run(port=33508, debug = True)