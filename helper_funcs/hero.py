import json
from .database.collection import db
from .switcher import switcher


class Hero:
    def __init__(self):
        self.data = db['hero_list'].find_one({})

    def sanitise_name(self, name):
        self.name = name.lower()
        self.name = name.replace(' ', '_')
        return self.name

    def get_id(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [hero['id'] for hero in self.data['heroes'] if self.name == switcher(hero['name']) or self.name == hero['name']][0]

    def get_hero_name(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [hero['name'] for hero in self.data['heroes'] if self.name == switcher(hero['name'])]

    def hero_name_from_hero_id(self, _id):
        return [hero['name'] for hero in self.data['heroes'] if hero['id'] == _id][0]
