# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start> (Enter a start date to get min, max, and average temperatures. Format: Year-Month-Day)<br/>"
        "/api/v1.0/<start>/<end> (Enter start and end dates to get min, max, and average temperatures. Most Recent Day in Database is '2017-08-23')"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the jsonified data of precipitation for the last year."""
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary with date as the key and precipitation as the value
    precipitation_data = {date: prcp for date, prcp in results}

    session.close()
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Returns jsonified data of all of the stations in the database"""
    # Query all the stations in the database
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Convert the Row objects to dictionaries
    station_data = []
    for result in results:
        station_dict = {}
        station_dict['station'] = result.station
        station_dict['name'] = result.name
        station_dict['latitude'] = result.latitude
        station_dict['longitude'] = result.longitude
        station_dict['elevation'] = result.elevation
        station_data.append(station_dict)

    session.close()
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns jsonified data for the most active station (USC00519281) for the last year."""
    # Query the most active station for the last year of temperature observations
    most_active_station_id = 'USC00519281'
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id)\
        .filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_data.append(tobs_dict)

    session.close()
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return the min, max, and average temperatures from the given start date to the end of the dataset."""
    # Query the min, max, and average temperatures from the start date to the end of the dataset
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start).all()

    # Convert the query results to a list
    temp_data = []
    for min_temp, max_temp, avg_temp in results:
        temp_dict = {}
        temp_dict['Min Temp'] = min_temp
        temp_dict['Max Temp'] = max_temp
        temp_dict['Avg Temp'] = avg_temp
        temp_data.append(temp_dict)

    session.close()
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return the min, max, and average temperatures from the given start date to the given end date."""
    # Query the min, max, and average temperatures from the start date to the end date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date <= end).all()

    # Convert the query results to a list
    temp_data = []
    for min_temp, max_temp, avg_temp in results:
        temp_dict = {}
        temp_dict['Min Temp'] = min_temp
        temp_dict['Max Temp'] = max_temp
        temp_dict['Avg Temp'] = avg_temp
        temp_data.append(temp_dict)

    session.close()
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)