import os
import urllib
from collections import OrderedDict
from datetime import datetime, timedelta

import babel
import flask_babel
import xmltodict
from flask import Flask, redirect, render_template, url_for

from . import app
from .datasets import station_codes, station_traffic_data
from .fetch_data import fetch_live_data
from .forms import StationSelectForm
from .utils import fetch_station_data


@app.route("/", methods=["GET", "POST"])
def home(station_name=None):
    return render_template("home.html")


@app.route("/station")
@app.route("/station/<station_name>")
def station(station_name=None):
    has_arrivals = False
    has_departures = False
    if station_name not in station_codes().keys():
        return redirect(url_for("home"))
    else:
        stationdata = fetch_live_data(station_name)
        if stationdata.all_services == None:
            has_arrivals = False
            has_departures = False
        else:
            for service in stationdata.all_services:
                if service.type == "Originating":
                    has_departures = True
                elif service.type == "Terminating":
                    has_arrivals = True
                elif service.type == "Through":
                    has_arrivals = True
                    has_departures = True
        return render_template(
            "stations.html",
            station=station_name,
            stationdata=stationdata,
            has_arrivals=has_arrivals,
            has_departures=has_departures,
        )


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/contact/")
def contact():
    return render_template("contact.html")


@app.template_filter()
def get_year(value):
    return babel.dates.format_datetime(value, "yyyy")


@app.context_processor
def inject_datetime():
    return dict(inject_datetime=datetime.now())


@app.context_processor
def station_list():
    return {"station_list": station_codes()}


@app.before_first_request
def cache_station_data():
    """Check the cached station data. If any of it's more than 4 weeks old, or missing, update it."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    json_files_exist = False
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            json_files_exist = True
            modtime = os.path.getmtime(
                os.path.join(data_dir, filename)
            )  # Get the last time the file was modified.
            diff = (
                datetime.now() - timedelta(days=28)
            ).timestamp()  # Get the timestamp for 28 days ago
            if modtime < diff:
                fetch_station_data()
    if json_files_exist == False:
        fetch_station_data()
