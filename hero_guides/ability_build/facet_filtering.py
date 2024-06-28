def facet_filter(match_data):
    facet_count = {}
    total = 0

    for match in match_data:
        if "variant" in match:
            total += 1
            variant = str(match["variant"])
            if variant in facet_count:
                facet_count[variant] += 1
            else:
                facet_count[variant] = 1

    facets = []
    for k, v in facet_count.items():
        o = {
            "key": int(k),
            "count": v,
            "perc": f"{(v / total) * 100:.2f}",
        }
        facets.append(o)

    return facets
