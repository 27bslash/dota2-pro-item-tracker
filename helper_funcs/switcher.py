def switcher(name):
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
        'outworld_devourer': 'obsidian_destroyer',
        'windranger': 'windrunner',
        'zeus': 'zuus',
        'vengeful_spirit': 'vengefulspirit',
        'treant_protector': 'treant',
        'centaur_warrunner': 'centaur'
    }
    # print(h, switch.get(h))
    if switch.get(name):
        return switch.get(name)
    return name


if __name__ == "__main__":
    pass
