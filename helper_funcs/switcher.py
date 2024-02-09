def switcher(name: str) -> str:
    switch = {
        'necrophos': 'necrolyte',
        'clockwerk': 'rattletrap',
        "nature's_prophet": 'furion',
        'timbersaw': 'shredder',
        'io': 'wisp',
        'queen_of_pain': 'queenofpain',
        'doom': 'doom_bringer',
        'shadow_fiend': 'nevermore',
        'wraith_king': 'skeleton_king',
        'magnus': 'magnataur',
        'underlord': 'abyssal_underlord',
        'anti-mage': 'antimage',
        'outworld_destroyer': 'obsidian_destroyer',
        'outworld_devourer': 'obsidian_destroyer',
        'lifestealer': 'life_stealer',
        'windranger': 'windrunner',
        'zeus': 'zuus',
        'vengeful_spirit': 'vengefulspirit',
        'treant_protector': 'treant',
        'centaur_warrunner': 'centaur'
    }

    v = switch.get(name)
    if v:
        return v
    else:
        for key, value in switch.items():
            if value == name:
                return key
    return name
