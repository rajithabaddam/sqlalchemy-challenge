import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,desc

import datetime as dt
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt<br/>"
        f"/api/v1.0/&lt;start&gt/&lt;end&gt<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using `date` as the key and `prcp` as the value."""
    last= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
#last_date = session.query(Measurement.date).order_by(desc('date')).first()
    #print(last_date)
    
    last_date = dt.datetime.strptime(last[0],'%Y-%m-%d')
    #print(last_date)
    year_old_date = last_date-dt.timedelta(days=365)
    year_old_date = dt.datetime.strftime(year_old_date, "%Y-%m-%d")

   # print(year_old_date)


# Perform a query to retrieve the data and precipitation scores

    results = session.query(Measurement.station,Measurement.date, Measurement.prcp).\
       filter(Measurement.date >= year_old_date).all()

    session.close()



    #dict = {date: prcp for date, prcp in results}    

    #return jsonify(dict)

    # Create a dictionary from the row data and append to a list of all_precipitation


    precipitation_data = {}
    for row in results:
        if row[0] not in precipitation_data:
            precipitation_data[row[0]] = {}
        precipitation_data[row[0]][row[1]] = row[2] 

    return jsonify( precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using station."""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()


    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

   
   # Calculate the date 1 year ago from the last data point in the database
    last= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
#last_date = session.query(Measurement.date).order_by(desc('date')).first()
    #print(last_date)
    
    last_date = dt.datetime.strptime(last[0],'%Y-%m-%d')
    #print(last_date)
    year_old_date = last_date-dt.timedelta(days=365)
    year_old_date = dt.datetime.strftime(year_old_date, "%Y-%m-%d")

   # print(year_old_date)


# Perform a query to retrieve the data and precipitation scores

    results = session.query(Measurement.station,Measurement.date, Measurement.tobs).\
       filter(Measurement.date >= year_old_date).all()

   
    session.close()


    # Convert to dictonary
    #all_tobs = dict(results)

      # Create a dictionary from the row data and append to a list of all_precipitation
    tobs_data = {}
    for row in results:
        if row[0] not in tobs_data:
            tobs_data[row[0]] = {}
        tobs_data[row[0]][row[1]] = row[2] 

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
   # start_date = input('Please enter start date(format %Y-%m-%d):')
   # start_date = request.args.get("start_date")
   # return "The date is " +  start_date
    results =session.query(func.min(Measurement.tobs).label("tmin"), func.avg(Measurement.tobs).label("tavg"), func.max(Measurement.tobs).label("tmax")).\
        filter(Measurement.date >= start_date).all()
    

    # Convert to dictonary
    all_start = []
    for tmin,tavg,tmax in results:
        start_dict = {}
        start_dict["tmin"] = tmin
        start_dict["tavg"] = tavg
        start_dict["tmax"] = tmax
        all_start.append(start_dict)
    return jsonify(start_dict)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #start_date = input('Please enter start date(format %Y-%m-%d) for temperature calcualtions :')
    #end_date = input('Please enter end date(format %Y-%m-%d)  for temperature calcualtions :')
    results =session.query(func.min(Measurement.tobs).label("tmin"), func.avg(Measurement.tobs).label("tavg"), func.max(Measurement.tobs).label("tmax")).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()


   # Create a dictionary from the row data and append to a list of all_precipitation
    all_end = []
    for tmin,tavg,tmax in results:
        end_dict = {}
        end_dict["tmin"] = tmin
        end_dict["tavg"] = tavg
        end_dict["tmax"] = tmax
        all_end.append(end_dict)
    return jsonify(end_dict)


    #return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)