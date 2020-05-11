import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/start_date   (Note: format date as 'yyyy-mm-dd')<br/>"
        f"/api/v1.0/start_date/end_date (Note: format dates as 'yyyy-mm-dd')<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_12m = (dt.datetime.strptime(last_date[0],'%Y-%m-%d').date())-dt.timedelta(days=365.25)

    results = session.query(measurement.date, measurement.prcp).\
              filter(measurement.date >= last_12m, measurement.date <= last_date[0])
    session.close()

    result_dict = {}
    for date, prcp in results:
        result_dict[date] = prcp

    return jsonify(result_dict)


@app.route("/api/v1.0/stations")
def station_name():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(measurement.station).distinct().all()
    session.close()

    results_list = list(np.ravel(results))

    return jsonify(results_list)


@app.route("/api/v1.0/tobs")
def station_temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_12m = (dt.datetime.strptime(last_date[0],'%Y-%m-%d').date())-dt.timedelta(days=365.25)

    results = session.query(measurement.tobs).\
              filter(measurement.date >= last_12m, measurement.date <= last_date[0]).\
              filter(measurement.station == 'USC00519281').all()
    session.close()

    results_list = list(np.ravel(results))

    return jsonify(results_list)


@app.route("/api/v1.0/<start>")
def temp_w_start(start):
    
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
              filter(measurement.date >= start).first()
    session.close()

    results_list = list(np.ravel(results))

    return jsonify(results_list)


@app.route("/api/v1.0/<start>/<end>")
def temp_w_start_end(start, end):
    
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
              filter(measurement.date >= start, measurement.date <= end).first()
    session.close()

    results_list = list(np.ravel(results))

    return jsonify(results_list)


if __name__ == '__main__':
    app.run(debug=True)