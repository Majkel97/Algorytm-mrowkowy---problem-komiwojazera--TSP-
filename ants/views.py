from django.shortcuts import render, redirect
from ants.forms import CitiesForm, ConfigForm
from django.contrib import messages
from django.http import HttpResponse
from geopy.geocoders import Nominatim
import json
import numpy as np
from geopy.distance import geodesic


CONVERSION_FACTOR = 111.32


def distance(point1, point2, speed):
    """
    Calculate the distance between two points.

    Parameters:
    - point1 (numpy.ndarray or tuple): Coordinates of the first point.
    - point2 (numpy.ndarray or tuple): Coordinates of the second point.
    - speed (str): The speed mode. If "fast," Euclidean distance is used.
    Otherwise, Haversine distance for geographic coordinates is used.

    Returns:
    - float: The calculated distance.

    Note:
    - For "fast" speed, Euclidean distance is calculated using NumPy.
    - For other speeds, Haversine distance is calculated using geopy.distance.geodesic.

    Make sure to replace CONVERSION_FACTOR with the actual conversion factor for Euclidean distance.
    """
    if speed == "fast":
        return np.sqrt(np.sum((point1 - point2) ** 2)) * CONVERSION_FACTOR
    else:
        coord1 = (float(point1[0]), float(point1[1]))
        coord2 = (float(point2[0]), float(point2[1]))
        return geodesic(coord1, coord2).kilometers


def ant_colony_optimization(
    request, locations, ants, iterations, alpha, beta, evaporation_rate, Q, speed
):
    """
    Perform Ant Colony Optimization for solving the Traveling Salesman Problem.

    Parameters:
    - request: Django HttpRequest object.
    - locations (list): List of locations, where each location is represented as [id, x, y].
    - ants (int): Number of ants in the colony.
    - iterations (int): Number of iterations to perform.
    - alpha (float): Weight for pheromone influence.
    - beta (float): Weight for distance influence.
    - evaporation_rate (float): Rate at which pheromone evaporates.
    - Q (float): Pheromone deposit constant.
    - speed (str): The speed mode. Pass "fast" for Euclidean distance or any other value for Haversine distance.

    Returns:
    - result_path (list): List of location IDs representing the best path found.
    - result_locations (list): List of locations representing the best path with coordinates.

    The function also updates the session with logs, best path, and best path length.
    """

    n_locations = len(locations)
    points = np.array([location[1:] for location in locations], dtype=float)

    pheromone = np.ones((n_locations, n_locations))
    best_path = None
    best_path_length = np.inf

    for starting_point in range(n_locations):
        for iteration in range(iterations):
            paths, path_lengths = generate_paths(
                ants,
                starting_point,
                n_locations,
                points,
                pheromone,
                alpha,
                beta,
                speed,
            )
            update_pheromone(
                pheromone, paths, path_lengths, evaporation_rate, Q, n_locations
            )

            request.session["logs"].append(
                f"{int(min(path_lengths))} km --> {paths[path_lengths.index(min(path_lengths))]}"
            )
            HttpResponse(
                status=204,
                headers={"HX-Trigger": json.dumps({"logsListChanged": None})},
            )

            if min(path_lengths) < best_path_length:
                best_path = paths[path_lengths.index(min(path_lengths))]
                best_path_length = min(path_lengths)

    result_path = [locations[i][0] for i in best_path]
    result_locations = [
        [result_path[i]] + list(locations[best_path[i]][1:])
        for i in range(len(result_path))
    ]

    request.session["best_path"] = result_path
    request.session["best_path_length"] = f"{int(best_path_length)} km"

    return result_path, result_locations


def generate_paths(
    ants, starting_point, n_locations, points, pheromone, alpha, beta, speed
):
    """
    Generate paths for a given number of ants starting from a specified location.

    Parameters:
    - ants (int): Number of ants.
    - starting_point (int): Index of the starting location.
    - n_locations (int): Total number of locations.
    - points (numpy.ndarray): Array of location coordinates (excluding IDs).
    - pheromone (numpy.ndarray): Pheromone matrix.
    - alpha (float): Weight for pheromone influence.
    - beta (float): Weight for distance influence.
    - speed (str): The speed mode. Pass "fast" for Euclidean distance or any other value for Haversine distance.

    Returns:
    - paths (list): List of paths, where each path is a list of location indices.
    - path_lengths (list): List of corresponding path lengths.

    The function uses ant colony optimization to generate paths for the given number of ants starting from the specified location.
    """
    paths = []
    path_lengths = []

    for ant in range(ants):
        visited = [False] * n_locations
        current_point = starting_point
        visited[current_point] = True
        path = [current_point]
        path_length = 0

        while False in visited:
            unvisited = np.where(np.logical_not(visited))[0]
            probabilities = calculate_probabilities(
                pheromone, current_point, unvisited, points, alpha, beta, speed
            )

            next_point = np.random.choice(unvisited, p=probabilities)
            path.append(next_point)
            path_length += distance(points[current_point], points[next_point], speed)
            visited[next_point] = True
            current_point = next_point

        paths.append(path)
        path_lengths.append(path_length)

    return paths, path_lengths


def calculate_probabilities(
    pheromone, current_point, unvisited, points, alpha, beta, speed
):
    """
    Calculate probabilities for the next location based on pheromone levels and distance.

    Parameters:
    - pheromone (numpy.ndarray): Pheromone matrix.
    - current_point (int): Index of the current location.
    - unvisited (numpy.ndarray): Array of indices of unvisited locations.
    - points (numpy.ndarray): Array of location coordinates (excluding IDs).
    - alpha (float): Weight for pheromone influence.
    - beta (float): Weight for distance influence.
    - speed (str): The speed mode. Pass "fast" for Euclidean distance or any other value for Haversine distance.

    Returns:
    - probabilities (numpy.ndarray): Array of probabilities for each unvisited location.

    The function calculates the probability of selecting each unvisited location based on pheromone levels and distance.

    """
    probabilities = np.zeros(len(unvisited))

    for i, unvisited_point in enumerate(unvisited):
        probabilities[i] = (
            pheromone[current_point, unvisited_point] ** alpha
            / distance(points[current_point], points[unvisited_point], speed) ** beta
        )

    probabilities /= np.sum(probabilities)
    return probabilities


def update_pheromone(pheromone, paths, path_lengths, evaporation_rate, Q, n_locations):
    """
    Update pheromone levels on paths based on ant traversal.

    Parameters:
    - pheromone (numpy.ndarray): Pheromone matrix.
    - paths (list): List of paths, where each path is a list of location indices.
    - path_lengths (list): List of corresponding path lengths.
    - evaporation_rate (float): Rate at which pheromone evaporates.
    - Q (float): Pheromone deposit constant.
    - n_locations (int): Total number of locations.

    The function updates pheromone levels on paths based on ant traversal, considering evaporation and pheromone deposit.
    """
    pheromone *= evaporation_rate

    for path, path_length in zip(paths, path_lengths):
        for i in range(n_locations - 1):
            pheromone[path[i], path[i + 1]] += Q / path_length
        pheromone[path[-1], path[0]] += Q / path_length


def index(request):
    """
    Render the index page.
    """
    context = {}
    return render(request, "ants/index.html", context)


def select_cities(request):
    """
    Handle the selection of cities using a form.

    If the form is submitted via POST, it validates the input, retrieves the coordinates
    for the specified city, and adds the city to the session's list of cities.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response or a JSON response with HX-Trigger header.
    """
    if request.method == "POST":
        form = CitiesForm(request.POST, request.FILES)
        if form.is_valid():
            city = f"{form.cleaned_data['country']}, {form.cleaned_data['city']}"
            new_city = get_city_cords(city)
            if "cities" in request.session:
                request.session["cities"].append(new_city)
            else:
                request.session["cities"] = [new_city]
            request.session.save()
            return HttpResponse(
                status=204,
                headers={"HX-Trigger": json.dumps({"citiesListChanged": None})},
            )
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, error)
    form = CitiesForm()
    context = {"form": form}
    return render(request, "ants/select_cities.html", context)


def get_city_cords(city):
    """
    Get the latitude and longitude coordinates of a city using the Nominatim geocoding service.

    Parameters:
    - city (str): The name of the city to retrieve coordinates for.

    Returns:
    - list: A list containing the city name, latitude, and longitude.
    """
    app = Nominatim(user_agent="tutorial")
    location = app.geocode(city).raw
    city_with_cords = [
        city,
        location["lat"],
        location["lon"],
    ]
    return city_with_cords


def display_cities(request):
    """
    Display the list of cities stored in the session.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response.
    """
    cities = request.session.get("cities")
    context = {"cities": cities}
    return render(request, "ants/display_cities.html", context)


def delete_city(request, index):
    """
    Delete a city from the list of cities stored in the session.

    Parameters:
    - request: Django HttpRequest object.
    - index (int): The index of the city to be deleted from the list.

    Returns:
    - HttpResponse: JSON response with HX-Trigger header indicating cities list change.
    """
    cities = request.session.get("cities", [])
    if 0 <= index < len(cities):
        del cities[index]
        request.session["cities"] = cities
        request.session.save()

    return HttpResponse(
        status=204,
        headers={"HX-Trigger": json.dumps({"citiesListChanged": None})},
    )


def config(request):
    """
    Handle the configuration for ant colony optimization.

    This view sets up the session variables, retrieves the input parameters from the form,
    performs ant colony optimization, and updates the session with the results.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: JSON response with HX-Trigger header indicating changes.
    """
    try:
        request.session["result"] = False
        request.session["logs"] = []
        if request.session.get("cities"):
            if request.method == "POST":
                form = ConfigForm(request.POST)
                if form.is_valid():
                    output = ant_colony_optimization(
                        request,
                        request.session["cities"],
                        form.cleaned_data["ants"],
                        form.cleaned_data["iterations"],
                        form.cleaned_data["alpha"],
                        form.cleaned_data["beta"],
                        form.cleaned_data["evaporation_rate"],
                        form.cleaned_data["q"],
                        form.cleaned_data["speed"],
                    )
                    request.session["params"] = form.cleaned_data
                    request.session["result"] = True
                    request.session["cities"] = output[1]
                    return HttpResponse(
                        status=204,
                        headers={
                            "HX-Trigger": json.dumps(
                                {
                                    "citiesListChanged": None,
                                    "logsListChanged": None,
                                    "paramsListChanged": None,
                                },
                            )
                        },
                    )
        else:
            pass
    except:
        pass
    form = ConfigForm()
    context = {"form": form}
    return render(request, "ants/config.html", context)


def load_map(request):
    """
    Load and render the map using OpenStreetMap with cities and optimization results.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response.
    """
    cities = request.session.get("cities")
    result = request.session.get("result")
    context = {"cities": cities, "result": result}
    return render(request, "ants/map.html", context)


def logs(request):
    """
    Display logs and information about the best path obtained from ant colony optimization.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response.
    """
    best_path_length = request.session.get("best_path_length")
    best_path = request.session.get("best_path")
    logs = request.session.get("logs")
    context = {
        "logs": logs,
        "best_path": best_path,
        "best_path_length": best_path_length,
    }
    return render(request, "ants/logs.html", context)


def params(request):
    """
    Display parameters used in ant colony optimization.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response.
    """
    params = request.session.get("params")
    context = {"params": params}
    return render(request, "ants/params.html", context)


def info(request):
    """
    Display information modal.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response.
    """
    context = {}
    return render(request, "ants/info.html", context)


def desc(request):
    """
    Display modal with algo description.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponse: Rendered HTML response.
    """
    context = {}
    return render(request, "ants/desc.html", context)


def reset_data(request):
    """
    Reset session data and redirect to the index page.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponseRedirect: Redirects to the index page.
    """
    request.session.flush()
    return redirect("index")


def test_citites_set_1(request):
    """
    Set a predefined list of cities in the session for testing purposes and redirect to the index page.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponseRedirect: Redirects to the index page.
    """
    reset_data(request)
    request.session["cities"] = [
        ["Wrocław", "51.1089776", "17.0326689"],
        ["Bydgoszcz", "53.12974625", "18.029369658534854"],
        ["Lublin", "51.250559", "22.5701022"],
        ["Gorzów Wielkopolski", "52.7309926", "15.2400451"],
        ["Łódź", "51.7728245", "19.478485931307937"],
        ["Kraków", "50.0469432", "19.997153435836697"],
        ["Warszawa", "52.2319581", "21.0067249"],
        ["Opole", "50.6668184", "17.9236408"],
        ["Rzeszów", "50.0374531", "22.0047174"],
        ["Białystok", "53.132398", "23.1591679"],
        ["Gdańsk", "54.3482907", "18.6540233"],
        ["Katowice", "50.2598987", "19.0215852"],
        ["Kielce", "50.8719903", "20.6310488"],
        ["Olsztyn", "53.7767239", "20.477780523409734"],
        ["Poznań", "52.4082663", "16.9335199"],
        ["Szczecin", "53.4301818", "14.5509623"],
    ]
    return redirect("index")


def test_citites_set_2(request):
    """
    Set a predefined list of cities in the session for testing purposes and redirect to the index page.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponseRedirect: Redirects to the index page.
    """
    reset_data(request)
    request.session["cities"] = [
        ["Albania, Shkoder", "42.0681371", "19.5121437"],
        ["Georgia, Sukhumi", "43.0033629", "41.0192741"],
        ["Guam, Barrigada Village", "13.5049972", "144.8301568"],
        ["Austria, Adnet", "47.6963575", "13.1307565"],
        ["Russia, Aksay", "47.268696", "39.861362"],
        ["Brazil, Altamira", "-3.204065", "-52.209961"],
        ["Andorra, Sispony", "42.5338717", "1.515627"],
        ["Denmark, Bylderup-Bov", "54.9441897", "9.0910721"],
        ["United States, Miami", "25.7741728", "-80.19362"],
        ["Canada, Audet", "45.656288", "-70.735817"],
    ]
    return redirect("index")


def test_citites_set_3(request):
    """
    Set a predefined list of cities in the session for testing purposes and redirect to the index page.

    Parameters:
    - request: Django HttpRequest object.

    Returns:
    - HttpResponseRedirect: Redirects to the index page.
    """
    reset_data(request)
    request.session["cities"] = [
        ["Austria, Aifersdorf", "46.7183929", "13.6252384"],
        ["Uruguay, Canelones", "-34.6222482", "-55.9903797"],
        ["Gabon, Moanda", "-1.554004", "13.220574"],
        ["Moldova, Orhei", "47.3782288", "28.8246754"],
        ["Uzbekistan, Andijon Viloyati", "40.7740809", "72.5355339"],
        ["Canada, Abbotsford", "49.0521162", "-122.329479"],
        ["Malawi, Blantyre", "-15.7862543", "35.0035694"],
        ["Greenland, Nuussuaq", "74.1111111", "-57.0611111"],
        ["Australia, Adelaide", "-34.9281805", "138.5999312"],
    ]
    return redirect("index")
