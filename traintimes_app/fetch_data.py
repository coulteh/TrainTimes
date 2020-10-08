import os
import urllib
from collections import OrderedDict

import requests
import xmltodict

from .datasets import station_datasets, station_traffic_data


class LiveTrainData:
    def __get_data(self, station_name):
        try:
            with urllib.request.urlopen(
                station_traffic_data()[station_name]
            ) as raw_data:
                return xmltodict.parse(raw_data.read())["StationBoard"]
        except urllib.error.URLError:
            return None

    def __normalise_services(self, xml_data):
        service_list = None
        try:
            service_list = xml_data["Service"]
        except KeyError:
            return None
        if "@Uid" in service_list:
            temp = service_list
            service_list = OrderedDict()
            service_list[0] = temp
            return service_list
        else:
            return service_list

    def __init__(self, station_name):
        xml_data = self.__get_data(station_name)
        self.services = self.__normalise_services(xml_data)
        self.station_name = xml_data["@name"]


def fetch_live_data(station_name):
    return LiveTrainData(station_name)


def fetch_station_data():
    for key, value in station_datasets.items():
        r = requests.get(value)

        dirname = os.path.dirname(__file__)
        tmp_filename = key + ".tmp.json"
        fin_filename = key + ".json"
        tmp_path = os.path.join(dirname, "data", tmp_filename)
        fin_path = os.path.join(dirname, "data", fin_filename)

        for item in {tmp_path, fin_path}:
            try:
                os.remove(item)
            except FileNotFoundError:
                pass

        with open(os.path.join(tmp_path), "w") as f:
            f.write(r.text)

        os.rename(tmp_path, fin_path)
