import numpy as np
import networkx as nx

# --- Systemmetriken ---
def total_line_length(network):
    """
    Berechnet die gesamte Leitungslänge des Netzwerks in Kilometern.
    """
    return sum(line.length_km for line in network.lines)

def line_length_per_customer(network):
    """
    Leitungslänge pro Kunde. Fallback: Anzahl Loads als Kunden.
    """
    num_customers = network.num_customers or len(list(network.loads))
    return total_line_length(network) / num_customers if num_customers > 0 else 0.0

def line_length_per_area(network):
    """
    Leitungslänge pro Quadratkilometer Netzfläche, anhand Buskoordinaten.
    """
    coords = [(getattr(bus, 'x', 0.0), getattr(bus, 'y', 0.0)) for bus in network.buses]
    if not coords:
        return 0.0
    min_x, max_x = min(p[0] for p in coords), max(p[0] for p in coords)
    min_y, max_y = min(p[1] for p in coords), max(p[1] for p in coords)
    area = (max_x - min_x) * (max_y - min_y)
    return total_line_length(network) / area if area > 0 else 0.0

def overhead_underground_share(network):
    """
    Anteil oberirdischer und unterirdischer Leitungen in Prozent.
    """
    overhead = sum(line.length_km for line in network.lines if getattr(line, 'type', '').lower() in ['overhead', 'ohl'])
    underground = sum(line.length_km for line in network.lines if getattr(line, 'type', '').lower() in ['underground', 'uhl', 'cable'])
    total = overhead + underground
    return (overhead / total * 100 if total else 0.0,
            underground / total * 100 if total else 0.0)

def transformer_stats(network):
    """
    Anzahl, mittlere Leistung (kVA) und mittleres X/R-Verhältnis von Transformatoren.
    """
    trafos = list(network.transformers)
    count = len(trafos)
    kva = [getattr(t, 'rating_kva', 0.0) for t in trafos]
    xr = [(getattr(t, 'x_ohm', 0.0) / getattr(t, 'r_ohm', 1e-6)) for t in trafos if getattr(t, 'r_ohm', 0.0) > 0]
    return {
        'count': count,
        'avg_kva': np.mean(kva) if kva else 0.0,
        'std_kva': np.std(kva) if kva else 0.0,
        'xr_values': xr,
        'avg_xr': np.mean(xr) if xr else 0.0,
        'std_xr': np.std(xr) if xr else 0.0
    }

def load_stats(network):
    """
    Gesamtleistung (P, Q), mittlere Last pro Kunde, Leistungsfaktor.
    """
    loads = list(network.loads)
    p_values = [getattr(l, 'p_kw', getattr(l, 'p_mw', 0.0) * 1000) for l in loads]
    q_values = [getattr(l, 'q_kvar', getattr(l, 'q_mvar', 0.0) * 1000) for l in loads]
    total_p, total_q = sum(p_values), sum(q_values)
    avg_p = np.mean(p_values) if p_values else 0.0
    s_values = [(p ** 2 + q ** 2) ** 0.5 for p, q in zip(p_values, q_values)]
    power_factors = [p / s if s > 1e-6 else 1.0 for p, s in zip(p_values, s_values)]
    return {
        'total_p_kw': total_p,
        'total_q_kvar': total_q,
        'avg_p_kw': avg_p,
        'std_p_kw': np.std(p_values) if p_values else 0.0,
        'power_factor_mean': np.mean(power_factors) if power_factors else 1.0,
        'power_factor_std': np.std(power_factors) if power_factors else 0.0
    }

def generation_stats(network):
    """
    PV/Wind/Andere Einspeisung in kW, jeweils aufsummiert und verteilt.
    """
    gen = list(network.generators)
    pv = [getattr(g, 'p_kw', 0.0) for g in gen if 'pv' in getattr(g, 'type', '').lower()]
    wind = [getattr(g, 'p_kw', 0.0) for g in gen if 'wind' in getattr(g, 'type', '').lower()]
    other = [getattr(g, 'p_kw', 0.0) for g in gen if 'pv' not in getattr(g, 'type', '').lower() and 'wind' not in getattr(g, 'type', '').lower()]
    return {
        'total_pv_kw': sum(pv), 'std_pv_kw': np.std(pv) if pv else 0.0,
        'total_wind_kw': sum(wind), 'std_wind_kw': np.std(wind) if wind else 0.0,
        'total_other_kw': sum(other), 'std_other_kw': np.std(other) if other else 0.0
    }

def compute_system_metrics(network):
    """
    Ermittelt alle Systemmetriken inkl. Verteilungen und statistischer Kenngrößen.
    """
    metrics = {
        'total_line_length_km': total_line_length(network),
        'line_length_per_customer_km': line_length_per_customer(network),
        'line_length_per_area_km2': line_length_per_area(network),
    }
    oh, uh = overhead_underground_share(network)
    metrics['overhead_share_percent'] = oh
    metrics['underground_share_percent'] = uh

    # Transformatorenmetriken
    metrics.update({f"trafo_{k}": v for k, v in transformer_stats(network).items()})

    # Lastmetriken
    metrics.update({f"load_{k}": v for k, v in load_stats(network).items()})

    # Erzeugungsmetriken
    metrics.update({f"gen_{k}": v for k, v in generation_stats(network).items()})

    # Kunden pro Trafo
    num_customers = network.num_customers or len(list(network.loads))
    trafo_count = metrics.get('trafo_count', 1)
    metrics['customers_per_transformer'] = num_customers / trafo_count if trafo_count > 0 else 0.0

    return metrics
