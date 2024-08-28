from functools import reduce
import operator
from hero_guides.ability_build.ability_filtering import fill_abilities


class AbilityParser:
    @staticmethod
    def parse_abilities(site_data, build_data):
        abilities = site_data["ability_builds"][0]
        talents = site_data["talents"]
        talent_build = [
            {str((i + 2) * 5): talent[0]}
            if int(talent[1]["level"]) < (i + 2) * 5
            else {str(int((talent[1]["level"]))): talent[0]}
            for i, talent in enumerate(talents)
        ]
        # useless probably

        ability_build = fill_abilities(
            talents=talent_build,
            count=abilities,
            site_data=site_data,
            build_data=build_data,
        )
        # ability_build = [{str(i+1): ability}
        #                  for i, ability in enumerate(ability_build[0])]
        talent_tooltips = [
            {talent[0]: f"Pick rate: {talent[1]['perc']}%"} for talent in talents
        ]
        talent_tooltips = reduce(operator.ior, talent_tooltips, {})
        ability_build = ability_build
        ability_build = reduce(operator.ior, ability_build, {})
        ability_build = {
            "ability_build": ability_build,
            "abilityTooltips": talent_tooltips,
        }
        return ability_build
