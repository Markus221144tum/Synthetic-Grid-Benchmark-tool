import numpy as np
import networkx as nx


def total_line_length(network):
    """Summe aller Leitungslaengen im Netz (in km)."""
    total_length = 0.0
    for line in network.lines:
        total_length += line.length_km
    return total_length

def line_length_per_customer(network):
    """Leitungslänge pro Kunde (gesamt / Anzahl Kunden)."""
    if hasattr(network, 'num_customers') and network.num_customers is not None:
        num_customers = network.num_customers
    else:
        num_customers = len(list(network.loads))  # Fix: map in list umwandeln
    return total_line_length(network) / num_customers if num_customers > 0 else 0.0

def line_length_per_area(network):
    buses = list(network.buses)  # map vermeiden
    coords = []
    for bus in buses:
        if isinstance(bus, dict):
            coords.append((bus.get('x', 0.0), bus.get('y', 0.0)))
        else:
            coords.append((getattr(bus, 'x', 0.0), getattr(bus, 'y', 0.0)))
    if not coords:
        return 0.0
    min_x = min(p[0] for p in coords)
    max_x = max(p[0] for p in coords)
    min_y = min(p[1] for p in coords)
    max_y = max(p[1] for p in coords)
    area = (max_x - min_x) * (max_y - min_y)
    total_line_length_km = sum(line.length_km for line in network.lines)
    return total_line_length_km / area if area > 0 else 0.0

def overhead_underground_share(network):
    overhead_len = 0.0
    underground_len = 0.0
    for line in network.lines:
        if hasattr(line, 'type'):
            if line.type.lower() in ['overhead', 'ohl']:
                overhead_len += line.length_km
            elif line.type.lower() in ['underground', 'cable', 'uhl']:
                underground_len += line.length_km
    total_len = overhead_len + underground_len
    if total_len == 0:
        return (0.0, 0.0)
    perc_overhead = overhead_len / total_len * 100.0
    perc_underground = underground_len / total_len * 100.0
    return (perc_overhead, perc_underground)

def transformer_stats(network):
    """Gibt Kenngrößen der Transformatoren zurück: Anzahl, mittlere kVA, mittleres X/R."""
    if not hasattr(network, 'transformers'):
        return {'count': 0}

    transformers = list(network.transformers)
    if len(transformers) == 0:
        return {'count': 0}

    count = 0
    total_kva = 0.0
    total_x_r = 0.0
    for trafo in transformers:
        count += 1
        total_kva += getattr(trafo, 'rating_kva', 0.0)
        r = getattr(trafo, 'r_ohm', 0.0)
        x = getattr(trafo, 'x_ohm', 0.0)
        if r > 0:
            total_x_r += (x / r)
    return {
        'count': count,
        'avg_kva': total_kva / count if count > 0 else 0.0,
        'avg_x_over_r': total_x_r / count if count > 0 else 0.0
    }


def load_stats(network):
    total_p = 0.0
    total_q = 0.0
    loads = list(network.loads)
    for load in loads:
        total_p += getattr(load, 'p_kw', getattr(load, 'p_mw', 0.0) * 1000.0)
        total_q += getattr(load, 'q_kvar', getattr(load, 'q_mvar', 0.0) * 1000.0)
    num_customers = len(loads)
    avg_p_per_customer = total_p / num_customers if num_customers > 0 else 0.0
    total_s = (total_p**2 + total_q**2) ** 0.5
    cosphi = total_p / total_s if total_s > 1e-6 else 1.0
    return {
        'total_p_kw': total_p,
        'total_q_kvar': total_q,
        'avg_p_per_customer_kw': avg_p_per_customer,
        'power_factor': cosphi
    }

def generation_stats(network):
    total_pv = 0.0
    total_wind = 0.0
    total_other = 0.0
    if hasattr(network, 'generators'):
        for gen in network.generators:
            gen_p = getattr(gen, 'p_kw', 0.0)
            gtype = getattr(gen, 'type', '').lower()
            if 'pv' in gtype or 'solar' in gtype:
                total_pv += gen_p
            elif 'wind' in gtype:
                total_wind += gen_p
            else:
                total_other += gen_p
    return {
        'pv_kw': total_pv,
        'wind_kw': total_wind,
        'other_kw': total_other,
        'total_gen_kw': total_pv + total_wind + total_other
    }

def compute_system_metrics(network):
    metrics = {}
    metrics['total_line_length_km'] = total_line_length(network)
    metrics['line_length_per_customer_km'] = line_length_per_customer(network)
    metrics['line_length_per_area_km_per_km2'] = line_length_per_area(network)
    oh_perc, uh_perc = overhead_underground_share(network)
    metrics['overhead_share_percent'] = oh_perc
    metrics['underground_share_percent'] = uh_perc
    trafo = transformer_stats(network)
    metrics.update({f"trafo_{k}": v for k,v in trafo.items()})
    load = load_stats(network)
    metrics.update({f"load_{k}": v for k,v in load.items()})
    gen = generation_stats(network)
    metrics.update({f"gen_{k}": v for k,v in gen.items()})
    if trafo.get('count', 0) > 0 and hasattr(network, 'loads'):
        metrics['customers_per_transformer'] = len(list(network.loads)) / trafo['count']
    return metrics
