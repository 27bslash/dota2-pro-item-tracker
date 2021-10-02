from helper_funcs.database.collection import db, hero_output


class View():
    def templateSelector(self, request, player):
        template = f"{player}final_items.html"
        if 'starter_items' in request.url:
            template = f'{player}starter_items.html'
        return template

    def role(self, name, request):
        if request.args:
            role = request.args.get('role').replace('%20', ' ').title()
            data = hero_output.find(
                {'hero': name, 'role': role})
            match_data = [hero for hero in data]
            best_games = [match for match in db['best_games'].find(
                {'hero': name, 'display_role': role})]
        else:
            match_data = self.find_hero('hero', name)
            best_games = [match for match in db['best_games'].find(
                {'hero': name, 'display_role': None})]
        return {'match_data': match_data, 'best_games': best_games}

    def find_hero(self, query, hero):
        data = hero_output.find({query: hero})
        match_data = [hero for hero in data]
        return match_data
