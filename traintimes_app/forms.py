from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired

from .datasets import station_codes


class StationSelectForm(FlaskForm):
    station_select = SelectField("Station")
