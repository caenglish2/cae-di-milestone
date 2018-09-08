from flask import Flask, render_template, request, redirect
#App script that plots stock Adjusted Closing price for a user specified ticker symbol, start, and end dates; For DI onboarding 12-day course milestone project. Author: Charles A. English. Html templates are from DI and are modified from their original forms.

from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
import requests
from io import StringIO
from datetime import date
app = Flask(__name__)

def plot(ticker, year_start, month_start, year_end, month_end):
  r = requests.get('https://www.quandl.com/api/v1/datasets/WIKI/%s.csv?api_key=-E8j4sqcCKVyuwiyM6dq'%ticker)
  stringData=StringIO(r.text)
  data_to_plot=pd.read_csv(stringData,sep=",")
  data_to_plot['Date']=pd.to_datetime(data_to_plot['Date'])

  if month_end=='02':#There was an issue with specifying February as the end month when using 31 as the day of the month
     data_to_plot=data_to_plot[(data_to_plot['Date']>'%s-%s-01'%(year_start,month_start)) & (data_to_plot['Date']<'%s-%s-28'%(year_end,month_end))]
  else:
     data_to_plot=data_to_plot[(data_to_plot['Date']>'%s-%s-01'%(year_start,month_start)) & (data_to_plot['Date']<'%s-%s-31'%(year_end,month_end))]

  p = figure(title="Price history for %s"%ticker, x_axis_label='Date', y_axis_label='Adj. Close', x_axis_type="datetime")
  p.line(data_to_plot['Date'], data_to_plot['Adj. Close'], legend="%s"%ticker, line_width=2)
  script, div = components(p)
  return script, div

@app.route('/')
def index():
  return render_template('options_menu.html')

@app.route('/graph', methods=['POST','GET'])
def about():
  result = request.form
  ticker=result['ticker'];year_start=result['year_start'];month_start=result['month_start'];year_end=result['year_end'];month_end=result['month_end']
  script, div = plot(ticker, year_start, month_start, year_end, month_end)
  #Make sure the dates entered are in the correct order: We can't have and end date before the start date
  if date(int(year_start), int(month_start), 1)>date(int(year_end), int(month_end), 31):
     return render_template('error_invalid_dates.html')
  #If we are using QUANDL WIKI data, this data source stoped updating at the end of March 2018, so we should flag if the user wants a plot of dates later than the cutoff
  elif date(int(year_start), int(month_start), 1)>date(2018, 3, 31) or date(int(year_end), int(month_end), 1)>date(2018, 3, 31):
     return render_template('error_invalid_dates.html')
  else:
     return render_template('graph.html', script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507)
