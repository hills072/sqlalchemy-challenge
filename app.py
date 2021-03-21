import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#import flask and jsonify; create Flask server
from flask import Flask, jsonify
app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


@app.route("/")
def welcome():
    return (
        f"Routes To Station Data:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def Precipitation():
    
    session = Session(engine)
    
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    
    one_year_stop = dt.datetime.strptime(most_recent, '%Y-%m-%d') - dt.timedelta(days=365)

    dates_precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_stop).all()

    session.close()

    precip_list = []

    for date, prcp in dates_precip:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['precipitation'] = prcp
        precip_list.append(precip_dict)

    return jsonify(precip_list)


@app.route("/api/v1.0/stations")
def Stations():

    session = Session(engine)

    stations = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    stations_list = []

    for station, name, lat, lon, el in stations:
        stations_dict = {}
        stations_dict["Station"] = station
        stations_dict["Name"] = name
        stations_dict["Latitude"] = lat
        stations_dict["Longitude"] = lon
        stations_dict["Elevation"] = el
        stations_list.append(stations_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def Tobs():

    session = Session(engine)

    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    most_active_station_id = most_active[0][0]

    most_active_most_recent = session.query(Measurement.date).filter(Measurement.station == most_active_station_id).\
    order_by(Measurement.date.desc()).first().date

    last12_temp_mostactive = dt.datetime.strptime(most_active_most_recent, '%Y-%m-%d') - dt.timedelta(days=365)

    temp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last12_temp_mostactive).all()

    session.close()

    temps_list = []

    for date, temp in temp_data:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature(F)"] = temp
        temps_list.append(temp_dict)

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>")
def TempByStartDate(start):

    session = Session(engine)

    temp_values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    session.close()

    temp_values_list = []

    for min,avg,max in temp_values:
        temp_storage_dict = {}
        temp_storage_dict["Min"] = min
        temp_storage_dict["Average"] = avg
        temp_storage_dict["Max"] = max
        temp_values_list.append(temp_storage_dict)

    return jsonify(temp_values_list)

@app.route("/api/v1.0/<start>/<end>")
def TempByDateRange(start,end):

    session = Session(engine)

    temp_values = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_values_list = []
    
    for min,avg,max in temp_values:
        temp_storage_dict = {}
        temp_storage_dict["Min"] = min
        temp_storage_dict["Average"] = avg
        temp_storage_dict["Max"] = max
        temp_values_list.append(temp_storage_dict)

    return jsonify(temp_values_list)


if __name__ == '__main__':
    app.run(debug=True)