# import flask, datetime, sqlalchemy
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# create engine to read hawaii sqlite database 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session
session = Session(engine)

# create an app, being sure to pass __name__
app = Flask(__name__)

# define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/temperature<br/>"
            f"/api/v1.0/start<br/>"
            f"/api/v1.0/start/end")
                            
# convert the query results to a Dictionary using date as the key and prcp as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    prcp_list = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    prcp_dict = dict(prcp_list)
# return the JSON representation of your dictionary.    
    return jsonify(prcp_dict)

# return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def station():
    print("Server received request for 'stations' page...")
    stations = session.query(Measurement.station, func.count(Measurement.id)).\
    group_by(Measurement.station).order_by((func.count(Measurement.id)).desc()).all()
    return jsonify(stations)

# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/temperature")
def temp():
    print("Server received request for 'temperature' page...")
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    hist_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    return jsonify (hist_temp) 

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, 
# and TMAX for all dates greater than and equal to the start date.

def calc_temps(start_date):
    return session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).group_by(Measurement.date).all()

@app.route("/api/v1.0/start")
def sdate_route():
    print("Server received request for 'temperature within date range' page...")
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    temps = calc_temps(year_ago)   
    return jsonify(temps)

# When given the start and the end date, 
# calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def calc_tempse(start_date, end_date):
    return session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()

@app.route("/api/v1.0/start/end")
def s_e_date_route():
    print("Server received request for 'temperature within date range' page...")
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
    edate = year_ago + dt.timedelta(days=365)
    tempse = calc_tempse(year_ago, edate)   
    return jsonify(tempse)

if __name__ == "__main__":
    app.run(debug=True)
