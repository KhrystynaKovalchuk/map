import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from geopy.distance import geodesic
import operator


def get_year():
    """
    Function for getting a year from user.
    """
    year = input("Please enter a year you would like to have a map for: ")
    return year


def get_latitude_longitude():
    """
    Function for getting a latitude and longitude from user.
    """
    result = input("Please enter your location (format: lat, long): ")
    return result


def get_place_from_user(user_data):
    """
    Gets coordinates from user and convert it to certain name of the place.
    """
    try:
        geolocator = Nominatim(user_agent="Map")
        line = geolocator.reverse(user_data, language="en").address
        return line.split(", ")[-1]
    except GeocoderUnavailable:
        pass


def read_file(file):
    """
    Reads file and return list of lists of needed elements.
    """
    content = open(file, "r+")
    items = []
    for line in content.readlines()[14:-1]:
        solid = line.strip().split("\t")
        if "(" in solid[-1] and ")" in solid[-1]:
            items.append([solid[0], ' '.join(solid[-2:])])
        else:
            items.append([solid[0], solid[-1]])
    return items


def years(file):
    """
    Returns film, its year and place.
    """
    content = read_file(file)
    inf = []
    for lst in content:
        indeks_bracket = lst[0].index("(")
        splitted = lst[0].split(lst[0][indeks_bracket])
        # splitted = lst[0].split("(")
        film = splitted[0]
        year = splitted[-1].strip(")")
        place = lst[-1]
        inf.append([film, year, place])
    return inf


def filter_years(file, user_data):
    """
    Filter films by year and country.
    """
    same = []
    year = get_year()
    place = get_place_from_user(user_data)
    for lst in years(file):
        country = lst[-1].split(", ")[-1]
        if lst[1] == year and country == place:
            same.append(lst)
    return same


def format_place(file, user_data):
    """
    Returns correct format of data for using it in geopy.
    """
    lst = filter_years(file, user_data)
    new_lst = []
    for element in lst:
        place = element[-1]
        first_part = place.split(",")[-3:-1]
        last_el = place.split(",")[-1].split()[0]
        if len(first_part) != 0:
            formatted = '{}, {}'.format(",".join(first_part), last_el)
        else:
            formatted = '{}{}'.format(",".join(first_part), last_el)
        del element[-1]
        element.append(formatted)
        new_lst.append(element)
    return new_lst


def find_coordinates(file, user_data):
    """
    Search for coordinates of needed places and returns list.
    """
    items = format_place(file, user_data)
    geolocator = Nominatim(user_agent="Maps")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    for lst in items:
        try:
            try:
                location = geolocator.geocode(lst[-1])
                coordinates = (location.latitude, location.longitude)
                lst.append(coordinates)
            except AttributeError:
                lst.append('TTT')
        except GeocoderUnavailable:
            pass
    return items


def find_distance(file, user_data):
    """
    Returns data with distance between points.
    """
    initial_coordinates = user_data.split(", ")
    lat, long = initial_coordinates[0], initial_coordinates[1]
    you = (lat, long)
    inf = find_coordinates(file, user_data)

    inf_true = [_ for _ in inf if _[-1] != 'TTT']
    for lst in inf_true:
        miles = geodesic(you, lst[-1]).miles
        lst.append(round(miles, 2))
    sorted_list = sorted(inf_true, key=operator.itemgetter(-1))
    ten_points = sorted_list[:11]
    return ten_points


def change_map(file):
    """
    Function for making changes to map.
    """
    user_data = get_latitude_longitude()
    information = find_distance(file, user_data)
    loc = [i for i in user_data.split(", ")]
    your_map = folium.Map(location=loc, zoom_start=10)
    folium.Marker(location=loc, popup="Ви тут!", icon=folium.Icon(color='lightblue', icon="home")).add_to(your_map)
    space = folium.FeatureGroup(name="The closest points")
    for lst in information:
        try:
            folium.Marker(location=list(lst[-2]), popup=lst[0], icon=folium.Icon(color="red")).add_to(space)
        except ValueError:
            continue

    distances = folium.FeatureGroup(name="Distances from you to points")
    for element in information:
        try:
            folium.Marker(location=list(element[-2]), popup=element[-1], icon=folium.Icon(color="green", icon="cloud")).add_to(distances)
        except ValueError:
            continue
    your_map.add_child(space)
    your_map.add_child(distances)
    your_map.add_child(folium.LayerControl())
    your_map.save("Your_map.html")
    return "Finished!"


print(change_map("locations.list"))
