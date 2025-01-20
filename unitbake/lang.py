import os
import json

language = {'units': {'names': {}}}
language_loaded = False

def load_languages(path):
    global language
    global language_loaded
    if language_loaded:
        return
    with open(os.path.join(path, 'language', 'en', 'units.json')) as f:
        language = json.load(f)
        language_loaded = True

def get_unit_name(unit_name):
    return language['units']['names'].get(unit_name, unit_name)

def decorate_unit_name(unit_name):
    name = language['units']['names'].get(unit_name, unit_name)
    if name != unit_name:
        return "{} ({})".format(name, unit_name)
    return name


