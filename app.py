import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
oldest_date = session.query(Measurement.date).order_by(Measurement.date).first()
oldest_date = oldest_date[0]
oldest_date = dt.datetime.strptime(oldest_date, '%Y-%m-%d').date()

most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
recent_date = most_recent_date[0]
recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d').date()
date_12_months_back = recent_date - dt.timedelta(days=365)
session.close()
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Use the following Routes to serach for min, avg, max temperatues for all stations for a given start or start-end range.<br />\
            Make sure the date is in the yyyy-mm-dd format<br/><br/>"
        f"/api/v1.0/{date_12_months_back}<br/>"
        f"/api/v1.0/{date_12_months_back}/{recent_date}<br/><br/>"

        f"Use the following Routes to view info for each indiviadual station for a given start or start-end range<br/><br/>"
        f"/api/v1.0/stations/{date_12_months_back}<br/>"
        f"/api/v1.0/stations/{date_12_months_back}/{recent_date}"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a list of all dates and precipitation
    results = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= date_12_months_back).\
    filter(Measurement.prcp != None).\
    order_by(Measurement.date).all()

    session.close()

    
    all_dates_precp = []
    for date, prcp in results:
        dates_precp_dict = {}
        dates_precp_dict[date] = prcp
                
        all_dates_precp.append(dates_precp_dict)

    return jsonify(all_dates_precp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a list of all stations names
    results = session.query(Station.name).order_by(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
#   Create our session (link) from Python to the DB
    session = Session(engine)

    active_sation = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()
    active_sation = active_sation[0]

#   Query
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == active_sation).\
    filter(Measurement.date >= date_12_months_back).\
    order_by(Measurement.date).all()

    session.close()

#   Create a dictionary from the row data and append to a list
    all_dates_temps = []
    for date, tobs in results:
        dates_temps_dict = {}
        dates_temps_dict[date] = tobs
                
        all_dates_temps.append(dates_temps_dict)

    return jsonify(all_dates_temps)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):    
    if (start_date != ""):
        try:
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
            session = Session(engine)
            
            if (start_date>= oldest_date and start_date<= recent_date):
                #   Query
                results = session.query(
                    func.min(Measurement.tobs).label("TMin"), func.avg(Measurement.tobs).label("TAvg"),\
                    func.max(Measurement.tobs).label("TMax")).\
                    filter(Measurement.date >= start_date).all()    
                    
                session.close()
                results_conv = list(np.ravel(results))
                return jsonify(results_conv)
            else:
                return("We do not have information for that date")   

        except ValueError:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")   
        except:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")    
        else:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")  
              
          
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date,end_date):    
    if (start_date != "" and end_date != ""):
        try:
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
            session = Session(engine)
            
        #   Query
            results = session.query(
                func.min(Measurement.tobs).label("TMin"), func.avg(Measurement.tobs).label("TAvg"),\
                func.max(Measurement.tobs).label("TMax")).\
                filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).all()    

            session.close()

            results_conv = list(np.ravel(results))
            return jsonify(results_conv)

        except ValueError:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")   
        except:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")    
        else:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")       
               

@app.route("/api/v1.0/stations/<start_date>")
def start_date_all_stations(start_date):    
    if (start_date != ""):
        try:
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
            session = Session(engine)
            
            if (start_date>= oldest_date and start_date<= recent_date):
            #   Query
                results = session.query(Measurement.station, Station.name,\
                    func.min(Measurement.tobs).label("TMin"), func.avg(Measurement.tobs).label("TAvg"),\
                    func.max(Measurement.tobs).label("TMax")).\
                    filter(Measurement.station == Station.station).\
                    filter(Measurement.date >= start_date).\
                    group_by(Measurement.station).\
                    order_by(Station.name).all()    
                    
                session.close()

            # Create a dictionary from the row data and append to a list
                all_dates_temps = []
                for station, name, TMin, TAvg, TMax in results:
                    dates_temps_dict = {}
                    dates_temps_dict["StationID"] = station
                    dates_temps_dict["Station"] = name
                    dates_temps_dict["Min Temp"] = TMin
                    dates_temps_dict["Avg Temp"] = TAvg
                    dates_temps_dict["Max Temp"] = TMax
                            
                    all_dates_temps.append(dates_temps_dict)

                return jsonify(all_dates_temps)
            else:
                return("We do not have information for that date")  


        except ValueError:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")   
        except:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")    
        else:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")       
          

    

@app.route("/api/v1.0/stations/<start_date>/<end_date>")
def start_end_date_all_stations(start_date,end_date):    
    if (start_date != "" and end_date != ""):
        try:
            start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
            session = Session(engine)
            
            
        #   Query
            results = session.query(Measurement.station, Station.name,\
                func.min(Measurement.tobs).label("TMin"), func.avg(Measurement.tobs).label("TAvg"),\
                func.max(Measurement.tobs).label("TMax")).\
                filter(Measurement.station == Station.station).\
                filter(Measurement.date >= start_date).\
                filter(Measurement.date <= end_date).\
                group_by(Measurement.station).\
                order_by(Station.name).all()    
                    
            session.close()

        #  Create a dictionary from the row data and append to a list
            all_dates_temps = []
            for station, name, TMin, TAvg, TMax in results:
                dates_temps_dict = {}
                dates_temps_dict["StationID"] = station
                dates_temps_dict["Station"] = name
                dates_temps_dict["Min Temp"] = TMin
                dates_temps_dict["Avg Temp"] = TAvg
                dates_temps_dict["Max Temp"] = TMax
                            
                all_dates_temps.append(dates_temps_dict)

            return jsonify(all_dates_temps)
               


        except ValueError:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")   
        except:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")    
        else:
            return("Make sure to enter date is in the yyyy-mm-dd format<br/>")       
               
     
        
if __name__ == '__main__':
    app.run(debug=True, port=5000)