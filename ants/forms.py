from django import forms
from django.core.exceptions import ValidationError
import requests

SPEED = [
    ("fast", "Szybka"),
    ("slow", "Dokładna"),
]


class ConfigForm(forms.Form):
    """
    Django form for configuring parameters for ant colony optimization.

    Form Fields:
    - ants: Number of ants.
    - iterations: Number of iterations.
    - alpha: Alpha parameter for ant colony optimization.
    - beta: Beta parameter for ant colony optimization.
    - evaporation_rate: Evaporation rate for pheromones.
    - q: Pheromone deposit constant.
    - speed: Speed mode choice.

    Note: The form includes range input widgets for numerical fields and a choice field for the speed parameter.
    """

    ants = forms.IntegerField(
        widget=forms.TextInput(
            attrs={"type": "range", "min": "1", "max": "100", "step": "1"}
        ),
        initial=50,
    )
    iterations = forms.IntegerField(
        widget=forms.TextInput(
            attrs={"type": "range", "min": "1", "max": "250", "step": "1"}
        ),
        initial=125,
    )
    alpha = forms.FloatField(
        widget=forms.TextInput(
            attrs={"type": "range", "min": "0.1", "max": "2", "step": "0.05"}
        ),
        initial=1,
    )
    beta = forms.FloatField(
        widget=forms.TextInput(
            attrs={"type": "range", "min": "0.1", "max": "2", "step": "0.05"}
        ),
        initial=1,
    )
    evaporation_rate = forms.FloatField(
        widget=forms.TextInput(
            attrs={"type": "range", "min": "0", "max": "1", "step": "0.05"}
        ),
        initial=0.5,
    )
    q = forms.FloatField(
        widget=forms.TextInput(
            attrs={"type": "range", "min": "1", "max": "10", "step": "0.5"}
        ),
        initial=1,
    )
    speed = forms.ChoiceField(choices=SPEED, widget=forms.Select)


class ChoiceFieldNoValidation(forms.ChoiceField):
    """ """

    def validate(self, value):
        pass


class CitiesForm(forms.Form):
    """
    Django form for selecting a country and city.

    Form Fields:
    - country: ChoiceField for selecting a country.
    - city: Custom ChoiceFieldNoValidation for selecting a city.

    Note: The form fetches country data from an external API and dynamically updates city choices based on the selected country.
    """

    country = forms.ChoiceField(
        choices=[], widget=forms.Select(attrs={"class": "form-control"})
    )
    city = ChoiceFieldNoValidation(
        choices=[], widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = self.get_country_choices()
        self.fields["country"].choices.insert(0, ("", "Select a country"))

    def clean(self):
        """
        Custom clean method to validate the selected city based on the chosen country.

        Raises:
        - ValidationError: If an invalid city is selected.
        """
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        city = cleaned_data.get("city")
        response = requests.get(f"https://countriesnow.space/api/v0.1/countries")
        countries = response.json()
        cities = [
            item["cities"] for item in countries["data"] if item["country"] == country
        ][0]
        if city not in cities:
            raise ValidationError("Invalid city selected.")

        return cleaned_data

    def get_country_choices(self):
        """
        Fetch country choices from an external API.

        Returns:
        - list: List of country choices.
        """
        response = requests.get("https://countriesnow.space/api/v0.1/countries")
        countries = response.json()
        choices = [
            (country["country"], country["country"]) for country in countries["data"]
        ]

        return choices
