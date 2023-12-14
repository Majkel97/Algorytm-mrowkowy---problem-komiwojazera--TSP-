from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("select_cities/", views.select_cities, name="select_cities"),
    path("display_cities/", views.display_cities, name="display_cities"),
    path("delete_city/<int:index>/", views.delete_city, name="delete_city"),
    path("load_map/", views.load_map, name="load_map"),
    path("config/", views.config, name="config"),
    path("logs/", views.logs, name="logs"),
    path("params/", views.params, name="params"),
    path("reset_data/", views.reset_data, name="reset_data"),
    path("info/", views.info, name="info"),
    path("desc/", views.desc, name="desc"),
    path("test_citites_set_1/", views.test_citites_set_1, name="test_citites_set_1"),
    path("test_citites_set_2/", views.test_citites_set_2, name="test_citites_set_2"),
    path("test_citites_set_3/", views.test_citites_set_3, name="test_citites_set_3"),
]
