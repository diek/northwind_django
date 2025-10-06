import djclick as click
from django.conf import settings
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from pathlib import Path

geolocator = Nominatim(user_agent="geo_test")


@click.command()
@click.option("--file", default="employees_users.csv", help="Path to movies JSON file")
def command(file):
    timezones = []
    file_path = Path(settings.BASE_DIR) / file

    with open("", "r") as infile:
        next(infile)
        customer_time_zones = {}
        for line in infile:
            data = line.split("|")
            city_country = f"{data[4]}, {data[5].rstrip()}"

            location = geolocator.geocode(city_country, timeout=10)
            if location:
                tf = TimezoneFinder()
                customer_time_zone = tf.timezone_at(
                    lat=location.latitude, lng=location.longitude
                )
                customer_time_zones[data[1]] = customer_time_zone

            else:
                print(f"{city_country} failed to geocode.")

    for k, v in customer_time_zones.items():
        print(f"{k}: {v}")
