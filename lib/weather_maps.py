"""
    Library for getting weather maps
"""

import os
from datetime import datetime
from glob import glob
import time
import json
import requests

from pyowm import OWM
from pyowm.utils.geo import Point
from pyowm.commons.tile import Tile
from pyowm.tiles.enums import MapLayerEnum

from sketchingdev.image_to_ascii import converter

from globals import OWM_KEY, PNG_CACHE

# Time limit to store cached images in minutes
CACHED_TIME_LIMIT = 30

# Version 1 of the OpenWeatherMaps Maps API

class WeatherMaps:
    def __init__(self):
        self.owm = OWM(OWM_KEY)
        # Set up cache to cache
        if not os.path.exists(PNG_CACHE):
            os.makedirs(PNG_CACHE)

    # Method to process weather map request
    def get_weather_map(self, location, layer, convert=False):
        # convert layer parameter to enum key
        _layer = self.get_map_layer(layer)

        if _layer is None: 
            return f"Map Layer: {layer} is not supported"

        # Default zoom
        _zoom = 3
        
        # Create tile manager object
        tile_manager = self.owm.tile_manager(_layer)

        # convert lat/lon to tile axis
        lat, lon = [float(loc) for loc in location.split(",")]
        geopoint = Point(lon, lat)
        x_tile, y_tile = Tile.tile_coords_for_point(geopoint, _zoom)

        # Get image tile
        tile = tile_manager.get_tile(x_tile, y_tile, _zoom)

        # Check for cached map
        cached_map = self.check_cache(f"{lat}_{lon}", layer)
        if cached_map is not None:
            # If cached map was found, check for ascii conversion before returning
            if convert is True:
                return self.convert_to_ascii(cached_map)
            return cached_map

        # Save image to cache if not found or is outdated
        saved_file = open(
            self.save_cache(tile, f"{lat}_{lon}", layer),
            "rb"
        )

        # Check if conversion to ascii should happen
        if convert is True:
            return self.convert_to_ascii( saved_file )
        return saved_file

    # Method to convert image to ASCII
    def convert_to_ascii(self, image):
        return converter.format_image((100, 100), image)

    # Method to process requested map layer
    def get_map_layer(self, layer):
        if layer == "prec":
            return MapLayerEnum.PRECIPITATION
        elif layer == "pres":
            return MapLayerEnum.PRESSURE
        elif layer == "wind":
            return MapLayerEnum.WIND
        elif layer == "temp":
            return MapLayerEnum.TEMPERATURE
        return None

    # Method to check if cache exists and is not outdated
    def check_cache(self, location, layer):
        # Construct map cache path using wildcard for timestamp matching
        cached_image_path = os.path.join(
            PNG_CACHE,
            location + "_*_" + layer + "_.png"
        )

        # test if path exists, will be empty list if nonexistent
        cached_image = glob(cached_image_path)
        
        # If the cache exists, check if it is outdated or if it can be used
        if len(cached_image) > 0 and os.path.isfile(cached_image[0]):
            cached_image_path = cached_image[0]
            _file = cached_image_path.split("/")[-1]
            cached_date = float(_file.split("_")[2])
            current_date = float(self.get_timestamp())

            # Only reload new cache every 30 minutes or so. Can be changed for different API tiers.
            if ((current_date - cached_date) / 60) > 1:
                print("Weather map cache: Outdated.")
                # Remove outdated cache
                os.remove(cached_image_path)
                return None
            else:
                print("Weather map cache: Found.")
                return open(cached_image_path, "rb")
        # No cache found
        return None

    # Save weather map for location to cache
    def save_cache(self, tile, location, layer):
        image_path = os.path.join(
            PNG_CACHE,
            f"{location}_{self.get_timestamp()}_{layer}_.png"
        )

        # Save .png
        tile.persist(image_path)

        # rerturn image path to retrieve .png
        return image_path

    # Helper method to create timestamp
    def get_timestamp(self):
        return time.mktime(
            datetime.now().timetuple()
        )


if __name__ == '__main__':
    exit()
