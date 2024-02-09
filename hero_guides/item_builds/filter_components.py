import re


def recursive_remove(item, itemdata, components, data, keys, removed_components):
    bad_quals = ['component', 'common', 'consumable', 'secret_shop']
    for component in components:
        component_stats = itemdata[component]
        has_components = True if 'components' in component_stats and component_stats[
            'components'] else False
        # print(component_stats)
        try:
            idx = keys.index(component)
        except ValueError as e:
            continue

        data_component = data[idx]
        if not data_component or component == 'blink' or component == 'boots' or component == 'travel_boots' or component == 'magic_stick' \
                or component == 'ultimate_scepter':
            continue

        if 'qual' in component_stats and component_stats['qual'] in bad_quals and component_stats['components'] is None:
            if ('hint' not in component_stats or 'attrib' not in component_stats) and data_component[1]['time'] > 600:
                removed_components.append(component)
                continue
            elif not component.startswith(('boots', 'ring_of_health', 'helm_of_iron_will')) and abs(data_component[1]['time'] - item[1]['time']) < 300 and item[1]['value'] > 3:
                removed_components.append(component)
                continue

        elif 'qual' in component_stats and component_stats['qual'] in bad_quals and component_stats['components']:
            if 'hint' not in component_stats and data_component[1]['time'] > 1500:
                removed_components.append(component)
                continue
        if data_component and component_stats['cost'] < 1500 and data_component[1]['time'] > 700 and item[1]['value'] * 2 > data_component[1]['value']:
            removed_components.append(component)
            continue
        elif data_component and item[1]['value'] > 3 and item[1]['value'] * 2 > data_component[1]['value'] and abs(item[1]['time'] - data_component[1]['time']) < 400 \
                and data_component[1]['time'] > 400 and component_stats['cost'] < 2000:
            removed_components.append(component)
            continue

        if has_components and component_stats['cost'] < 900 and abs(item[1]['time'] - data_component[1]['time']) < 300:
            removed_components.append(component)
            continue

        if component == 'sange':
            removed_components.append(component)

        if 'hint' in component_stats and data_component[1]['time'] > 1200 and component != 'ultimate_scepter':
            removed_components.append(component)

        if data_component[1]['time'] > 1800:
            removed_components.append(component)

    return removed_components


def filter_components(data, itemData):
    toRemove = []
    removedComponents = []
    disassembleable = ['arcane_boots', 'echo_sabre',
                       'octarine_core', 'vanguard', 'mask_of_madness']
    keys = [x[0] for x in data]
    itemUses = []
    for item in data:
        itemKey = item[0]
        itemTime = item[1]['time']
        try:
            itemStats = itemData[re.sub(r'__\d+', '', itemKey)]
        except Exception as e:
            print('exception', itemKey)
            continue
        if not itemStats:
            continue
        if itemTime > 1000 and itemStats['cost'] < 500:
            toRemove.append(item[0])
            continue
        cost = itemStats['cost']
        if itemStats and itemStats['components']:
            components = itemStats['components']
            toRemove = recursive_remove(
                item, itemdata, components, data, keys, removedComponents)
            if components and (re.sub(r'__\d+', '', itemKey) in disassembleable or 'kaya' in components or 'sange' in components):
                for component in components:
                    slicedData = data[data.index(item) + 1:]
                    # itemUses = list(filter(lambda x: True if all(
                    #     x in itemdata[x[0]]['components'] for x in component) else False, slicedData))
                    for j, componentItem in enumerate(slicedData):
                        if componentItem[1]['adjustedValue'] < 8:
                            continue

                        parentComponents = all_components(
                            itemdata[componentItem[0]]['components'], [], itemdata)
                        if parentComponents and component in parentComponents:
                            core = componentItem[1]['adjustedValue'] > 20 and item[1]['adjustedValue'] > 20
                            situtational = componentItem[1]['adjustedValue'] < 20 and item[1]['adjustedValue'] < 20
                            componentInParent = [
                                x[0] for k, x in enumerate(slicedData) if x[0] in parentComponents and k <= j]
                            if componentInParent and component not in componentInParent and componentItem[1]['value'] > item[1]['value'] / 2 and itemKey not in parentComponents and (core or situtational) \
                                    and not [x[0] for x in itemUses if x[0] in componentInParent]:
                                itemUses.append(componentItem)

                    for itemUse in itemUses:

                        idx = keys.index(itemUse[0])
                        dissassembledComponents = list(filter(lambda x: x in components, all_components(
                            itemdata[itemUse[0]]['components'], [], itemdata)))
                        dissassembledComponents.insert(0, itemKey)
                        if len(dissassembledComponents) % 2 != 0:
                            dissassembledComponents.pop()
                        if len(dissassembledComponents) > 1:
                            if 'dissassembledComponents' in data[idx][1]:
                                data[idx][1]['dissassembledComponents'].append(
                                    dissassembledComponents)
                            else:
                                data[idx][1]['dissassembledComponents'] = [
                                    dissassembledComponents]
                            item[1]['disassemble'] = True
    for component in itemUses:
        if component[0] in toRemove:
            f_item = final_item(component, data, itemdata)
            if f_item:
                idx = keys.index(f_item[0])
                data[idx][1]['dissassembledComponents'] = component[1]['dissassembledComponents']
                print(data[idx])
    for item in toRemove:
        try:
            idx = keys.index(item)
        except ValueError as e:
            # print(item)
            continue
        if idx != -1:
            data.pop(idx)
            keys.pop(idx)
    return data


def final_item(component, data, itemdata):
    for item in data:
        itemStats = itemdata[re.sub(r'__\d+', '', item[0])]
        components = itemStats['components']
        if not components:
            continue
        if component[0] in components:
            print(item, component[0])
            if item[1]['adjustedValue'] >= component[1]['adjustedValue']/2:
                return item


def all_components(components, res, itemdata):
    if not components:
        return res
    for component in components:
        res.append(component)
        component_stats = itemdata[component]['components']
        if component_stats:
            for sub_component in component_stats:
                res.append(sub_component)
    return res
