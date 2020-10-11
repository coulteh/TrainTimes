import os
import urllib
from collections import OrderedDict

import requests
import xmltodict

from .datasets import station_traffic_data


class LiveStationData:
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
            service_list = []
            service_list[0] = temp
            return service_list
        else:
            return service_list

    def __init__(self, station_name):
        xml_data = self.__get_data(station_name)
        self.all_services = self.__normalise_services(xml_data)
        self.station_name = xml_data["@name"]

    class Service:
        """
        An instance of a service at a station
        """

        def __init__(self, train):
            self.type = train["ServiceType"]["@Type"]
            self.arr_time = None
            self.dep_time = None
            self.exp_arr_time = None
            self.exp_dep_time = None
            self.platform = None
            self.status = None
            self.delay = None
            self.last_report = None
            self.calling_points = None


def fetch_live_data(station_name):
    return LiveStationData(station_name)
