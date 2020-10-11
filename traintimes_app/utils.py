import os

import requests

from .datasets import station_datasets


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
