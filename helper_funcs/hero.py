import json
from .database.collection import db, hero_list
from .switcher import switcher


class Hero:
    def __init__(self):
        self.data = hero_list

    def sanitise_name(self, name):
        self.name = name.lower()
        self.name = name.replace(" ", "_")
        return self.name

    def get_id(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        try:
            return [
                hero["id"]
                for hero in self.data
                if self.name == switcher(hero["name"]) or self.name == hero["name"]
            ][0]
        except IndexError:
            return False

    def get_hero_name(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [
            hero["name"] for hero in self.data if self.name == switcher(hero["name"])
        ]

    def hero_name_from_hero_id(self, _id):
        return [hero["name"] for hero in self.data if hero["id"] == _id][0]

    def calculate_level(self, exp):
        level_table = [
            0,
            230,
            600,
            1080,
            1660,
            2260,
            2980,
            3730,
            4620,
            5550,
            6520,
            7530,
            8580,
        ]
        for i, level in enumerate(level_table):
            if exp > level:
                continue
            return i + 1

    @property
    def hero_list(self):
        return self.data
