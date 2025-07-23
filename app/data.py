import json
import os

SEED_DATA_DIR = os.path.join(os.path.dirname(__file__), "seed_data")


def load_json(filename):
    with open(os.path.join(SEED_DATA_DIR, filename), "r") as f:
        return json.load(f)


hotels = load_json("hotel_catalogue.json")
flights = load_json("flight_catalogue.json")
experiences = load_json("experiences_catalogue.json")
