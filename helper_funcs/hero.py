import json

class Hero:
    def __init__(self):
        with open('json_files/hero_ids.json') as f:
            self.data = json.load(f)

    def sanitise_name(self, name):
        self.name = name.lower()
        self.name = name.replace(' ', '_')
        return self.name

    def get_id(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [hero['id'] for hero in self.data['heroes'] if self.name == hero['name']][0]

    def get_hero_name(self, name):
        self.sanitise_name(name)
        if self.name is None:
            return False
        return [hero['name'] for hero in self.data['heroes'] if self.name == hero['name']]

    def hero_name_from_hero_id(self, _id):
        return [hero['name'] for hero in self.data['heroes'] if hero['id'] == _id][0]