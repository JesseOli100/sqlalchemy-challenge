# Import the dependencies.
#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
# reflect the tables
# Save references to each table
# Create our session (link) from Python to the DB
#################################################
# Flask Setup
#################################################
#################################################
# Flask Routes
#################################################

from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Define the home route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/><br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start_date'>/api/v1.0/start_date</a><br/>"
        f"<a href='/api/v1.0/start_date/end_date'>/api/v1.0/start_date/end_date</a>"
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session
    session = Session(engine)

    # Calculate the date one year from the last date in the data set
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    precipitation_df = pd.DataFrame(precipitation_data, columns=['Date', 'Precipitation'])

    # Convert results to dictionary
    precipitation_dict = dict(zip(precipitation_df['Date'], precipitation_df['Precipitation']))

    # Close the session
    session.close()
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Create a session
    session = Session(engine)

    # Design a query to find the most active stations (i.e. which stations have the most rows?)
    # List the stations and their counts in descending order
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Extract station names into a list
    station_list = [station[0] for station in most_active_stations]

# Close the session
    session.close()
    return jsonify(station_list)


# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session
    session = Session(engine)

    # Design a query to find the most active stations
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    # Using the most active station id from the previous query
    most_active_station = most_active_stations[0][0]

    # Calculate the date one year from the last date in the data set for the most active station
    last_date_most_active = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    one_year_ago_most_active = dt.datetime.strptime(last_date_most_active, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the temperature observation data for the last 12 months for the most active station
    temperature_data_most_active = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago_most_active).all()

    # Extract temperatures into a list
    temperature_list = [temp[0] for temp in temperature_data_most_active]

# Close the session
    session.close()
    return jsonify(temperature_list)


# Start and start/end date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    # Create a session
    session = Session(engine)

    # Design a query to calculate the lowest, highest, and average temperature for the specified date range
    if end:
        temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    # Extract results
    lowest_temp, highest_temp, avg_temp = temperature_stats[0]

# Close the session
    session.close()

    return jsonify({"TMIN": lowest_temp, "TAVG": avg_temp, "TMAX": highest_temp})


if __name__ == "__main__":
    app.run(debug=True)
