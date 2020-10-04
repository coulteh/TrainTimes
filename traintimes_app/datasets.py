import os
import json

# Import stations and halts. The data for whatever reason classifies stations and halts separately.
# For our purposes they may as well be exactly the same thing.
#     Station: Staffed station, mostly
#     Halt: Unstaffed station, mostly
station_datasets = {
    "stations": "https://www.opendatani.gov.uk/dataset/5f27f171-b8aa-4511-983d-6df6e87bbf20/resource/971b4e1c-a77e-4831-8681-ef69c8fb595c/download/translink-nir-rail-stations.txt",
    "halts": "https://www.opendatani.gov.uk/dataset/1f2a94b9-1e86-4aec-ad9a-90a3de233893/resource/57c4152b-d1ca-443f-9739-a7202adb7b3c/download/translink-nir-halts.txt",
    "station_codes": "http://apis.opendatani.gov.uk/translink/",
}


def station_codes():
    """Get a list of stations and their station codes.

    Returns:
        dict: Keys are stations by name, values are station codes
    """
    station_codes = dict()
    with open(
        os.path.join(os.path.dirname(__file__), "data", "station_codes.json"), "r"
    ) as jsonfile:
        json_data = json.load(jsonfile)
        for data in json_data["stations"]:
            # Open Data for Translink is stupid and they can't even update their own data to reflect their own rebrand, so do it for them
            if "Belfast Central" in data["name"]:
                station_codes["Lanyon Place"] = data["code"]
            else:
                station_codes[data["name"]] = data["code"]
        return station_codes


def station_traffic_data():
    stationcodes = station_codes()
    station_url = {}
    for key, value in stationcodes.items():
        station_url[key] = "https://apis.opendatani.gov.uk/translink/" + value + ".xml"
    return station_url