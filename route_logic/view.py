from helper_funcs.database.collection import db, hero_output


class View():
    def templateSelector(self, request, player):
        template = f"{player}final_items.html"
        if 'starter_items' in request.url:
            template = f'{player}starter_items.html'
        return template

    def role(self, name, request):
        role = request.args.get('role')
        if role:
            role = request.args.get('role').replace('%20', ' ').title()
            best_games = [match for match in db['best_games'].find(
                {'hero': name, 'display_role': role}, {'_id': 0})]
        else:
            best_games = [match for match in db['best_games'].find(
                {'hero': name, 'display_role': None}, {'_id': 0})]
        return {'best_games': best_games}
