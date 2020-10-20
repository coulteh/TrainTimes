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
            service_list[0] = self.Service(temp)
            return service_list
        else:
            normalised_list = []
            for service in service_list:
                normalised_list.append(self.Service(service))
            return normalised_list

    def __get_service_type(self, service_list, service_type="dep"):
        departure_list = []
        arrival_list = []
        if service_list == None:
            return None
        for service in service_list:
            if service.type in {"Originating", "Through"}:
                departure_list.append(service)
            if service.type in {"Terminating", "Through"}:
                arrival_list.append(service)
        if service_type == "dep":
            return departure_list
        elif service_type == "arr":
            return arrival_list
        else:
            raise ValueError("service_type must be either \"dep\" or \"arr\".")

    def __init__(self, station_name):
        xml_data = self.__get_data(station_name)
        self.all_services = self.__normalise_services(xml_data)
        self.departures = self.__get_service_type(self.all_services, "dep")
        self.arrivals = self.__get_service_type(self.all_services, "arr")
        self.station_name = xml_data["@name"]

    class Service:
        """
        An instance of a service to/from a station
        """

        class Platform:
            """
            Platform data for a train service
            """

            def __platform_changed(self, train):
                try:
                    if train["Platform"]["@Changed"] == "No":
                        return False
                    elif train["Platform"]["@Changed"] == "Yes":
                        return True
                except KeyError:
                    return None

            def __init__(self, train):
                self.number = train["Platform"]["@Number"]
                self.changed = self.__platform_changed(train)
                self.parent = train["Platform"]["@Parent"]

        class LastReport:
            def __init__(self, train):
                last_report = train["LastReport"]
                self.time = last_report["@time"]
                self.type = last_report["@type"]
                self.station1 = last_report["@station1"]
                self.station2 = last_report["@station2"]

        class CallingPoint:
            def __init__(self, call_point):
                try:
                    self.station = call_point["@Name"]
                except KeyError:
                    try:
                        self.station = call_point["@name"]
                    except KeyError:
                        self.station = None
                try:
                    self.tt_arrival_time = call_point["@ttarr"]
                except:
                    self.tt_arrival_time = None
                try:
                    self.tt_depart_time = call_point["@ttdep"]
                except:
                    self.tt_depart_time = None
                try:
                    self.exp_arrival_time = call_point["@etarr"]
                except:
                    self.exp_arrival_time = None
                try:
                    self.exp_depart_time = call_point["@etdep"]
                except:
                    self.exp_depart_time = None
                try:
                    self.type = call_point["@type"]
                except:
                    self.type = None

        def __get_call_points(self, train):
            call_points = []
            if train["Dest1CallingPoints"]["@NumCallingPoints"] == "0":
                return None
            else:
                for call_point in train["Dest1CallingPoints"]["CallingPoint"]:
                    call_points.append(self.CallingPoint(call_point))
                call_points.append(self.CallingPoint(train["Destination1"]))
                return call_points


        def __init__(self, train):
            self.type = train["ServiceType"]["@Type"]
            self.uid = train["@Uid"]
            self.origin = train["Origin1"]["@name"]
            self.destination = train["Destination1"]["@name"]
            self.arr_time = train["ArriveTime"]["@time"]
            self.dep_time = train["DepartTime"]["@time"]
            self.exp_arr_time = train["ExpectedArriveTime"]["@time"]
            self.exp_dep_time = train["ExpectedDepartTime"]["@time"]
            self.platform = self.Platform(train)
            self.status = train["ServiceStatus"]["@Status"]
            self.delay = train["Delay"]["@Minutes"]
            self.last_report = self.LastReport(train)
            self.calling_points = self.__get_call_points(train)


def fetch_live_data(station_name):
    return LiveStationData(station_name)
