#import dependencies
import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, MetaData
from sqlalchemy.pool import StaticPool

from flask import Flask, jsonify

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

engine = create_engine("sqlite:///Resources/hawaii.sqlite",
    connect_args={'check_same_thread':False},
    poolclass=StaticPool)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our connection object
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
    """List all available api routes."""
    return (
        "<img src=\"https://github.com/UCF-Coding-Boot-Camp/UCFLM201809DATA2/raw/master/10-Advanced-Data-Storage-and-Retrieval/Homework/Instructions/Images/surfs-up.jpeg\" alt=\"Surfs Up\" width=\"800\" height=\"300\"/>"+
        "<br/>"+
        "<br/>"+
        "Available Routes:<br/>" +
        "<br/>"+
        "/api/v1.0/precipitation<br/>"+
        "Return a list of all dates and precipitation<br/>"+
        "<br/>"+
        "/api/v1.0/stations<br/>"+
        "Return a list of stations data<br/>"+
        "<br/>"+
        "/api/v1.0/tobs<br/>"+
        "Return a list of Temperature Observations (tobs) for the previous year<br/>"+
        "<br/>"+
        "/api/v1.0/<start><br/>"+
        "When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>"+
        "<br/>"+
        "/api/v1.0/<start>/<end>"
        "When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all dates and precipitation"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    print(last_date)
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).\
                                  filter(Measurement.date>year_ago).order_by(Measurement.date).all()

    # Convert list of tuples into normal list
    #all_dates = list(np.ravel(results))

# Create a dictionary from the row data and append to a list of all_dates
    dates = []
    n=0
    for d in precipitation:
        dates_dict = {}
        dates_dict[precipitation[n][0]] = precipitation[n][1]
        #dates_dict["prcp"] = precipitation[1]
        dates.append(dates_dict)
        n=n+1

    return jsonify(dates)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations data """
    # Query all station
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of Temperature Observations (tobs) for the previous year """
    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_year_ago = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                                  filter(Measurement.date>year_ago).\
                                  filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of temp
    temp = []
    n=0
    for d in temp_year_ago:
        temp_dict = {}
        temp_dict["station"] = temp_year_ago[n][0]
        temp_dict["date"] = temp_year_ago[n][1]
        temp_dict["temp"] = temp_year_ago[n][2]
        temp.append(temp_dict)
        n=n+1

    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a list of the minimum temperature, the average temperature, and the max temperature for a given start """
     # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Return a list of the minimum temperature, the average temperature, and the max temperature for a given start-end range. """
    # Query all station
    # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)


#  Define main behavior
if __name__ == "__main__":
    app.run(debug=True)