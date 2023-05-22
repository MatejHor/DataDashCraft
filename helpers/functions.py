import importlib
import re
import os
import dash_bootstrap_components as dbc

def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

def snake_to_camel(name):
    names = re.split('_+', name)
    return "".join([name.capitalize() for name in names])

def import_data_model(name):
    model = getattr(importlib.import_module("models." + camel_to_snake(name)), name)
    return model

def get_input_add(column_name):
    return dbc.DropdownMenuItem(header=True, children=[
                dbc.Label(f"{snake_to_camel(column_name)} column"),
                dbc.Input(value='', id=f"add-column-{column_name}", type="text")
            ])

def get_button_add(hide=True):
    style = {"display": "none"} if hide else {}
    return dbc.DropdownMenuItem(
        header=True,
        children=dbc.Button("Add-button-item", id="btn-add", color="primary", style=style),
    )


def get_models():
    # models = filter(lambda x: '.py' in x, models)
    # models = map(snake_to_camel, models)
    data_models = []
    for model in os.listdir('models'):
        if '.py' in model:
            model = snake_to_camel(model)
            model = re.sub('.py', '', model)
            data_models.append(model)
    return data_models
