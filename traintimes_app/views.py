import os
import urllib
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
@app.route("/<station_name>", methods=["GET", "POST"])
def home(station_name=None):
    form = StationSelectForm()
    stationdata = None
    form.station_select.choices = ["--Select Station--"]
    form.station_select.choices.extend(sorted(list(station_codes().keys())))
    if form.validate_on_submit():
        if form.station_select.data == "--Select Station--":
            pass  # Do nothing on purpose
        else:
            return redirect(url_for("home", station_name=form.station_select.data))

    if station_name not in list(station_codes().keys()):
        station = "Select a station to see departures."
    else:
        stationdata = fetch_live_data(station_name)
        form.station_select.default = station_name
        station = stationdata.station_name
    return render_template(
        "home.html", station=station, form=form, stationdata=stationdata
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


@app.before_first_request
def cache_station_data():
    """Check the cached station data. If it's more than 4 weeks old, update it."""
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