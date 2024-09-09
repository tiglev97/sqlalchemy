# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model

engine = create_engine("sqlite:///C:/Users/tigra/OneDrive/Documents/GitHub/sqlalchemy-challenge/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)



# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB


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
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Query for the date and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station).all()
    
    session.close()

    # Convert list of tuples into a normal list
    stations_list = list(map(lambda x: x[0], results))
    
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations (tobs) for the previous year for the most active station."""
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    
    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Query the temperature observations for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert the query results to a list
    tobs_list = list(map(lambda x: x[1], results))
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start=None, end=None):
    """Return a JSON list of the minimum, average, and maximum temperature for a given start or start-end range."""
    session = Session(engine)
    
    # Set up date filtering based on start and end date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        # For the given start date
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        # For the given start and end date range
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    # Convert the query results to a list
    temp_stats = list(map(lambda x: {"TMIN": x[0], "TAVG": x[1], "TMAX": x[2]}, results))
    
    return jsonify(temp_stats)



if __name__ == '__main__':
    app.run(debug=True)