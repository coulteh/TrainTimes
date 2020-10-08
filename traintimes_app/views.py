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
from .fetch_data import fetch_live_data, fetch_station_data
from .forms import StationSelectForm


@app.route("/", methods=["GET", "POST"])
# @app.route("/<station_name>", methods=["GET", "POST"])
def home(station_name=None):
    return render_template("home.html")


@app.route("/departures")
@app.route("/departures/<station_name>")
def departures(station_name=None):
    if station_name not in station_codes().keys():
        return redirect(url_for("home"))
    else:
        form = StationSelectForm()
        stationdata = fetch_live_data(station_name)
        return render_template(
            "departures.html", station=station_name, form=form, stationdata=stationdata
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
    """Check the cached station data. If any of it's more than 4 weeks old, update it."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            modtime = os.path.getmtime(
                os.path.join(data_dir, filename)
            )  # Get the last time the file was modified.
            diff = (
                datetime.now() - timedelta(days=28)
            ).timestamp()  # Get the timestamp for 28 days ago
            if modtime < diff:
                fetch_station_data()
