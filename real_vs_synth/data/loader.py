import os
from typing import List, Callable

from synthetic_loader import load_synthetic_folder
from simbench_loader import load_simbench_folder
from dingo_loader import load_dingo_folder
from cvs_loader import load_cvs_folder
from pt_loader import load_pt_folder


LOADERS = {
    "synthetic": load_synthetic_folder,
    "simbench": load_simbench_folder,
    "dingo": load_dingo_folder,
    "cvs": load_cvs_folder,
    "pt": load_pt_folder
}

def get_loader(name_or_path: str) -> Callable[[str], List]:
    name_or_path = name_or_path.lower()

    if os.path.isdir(name_or_path):
        has_bus_csv = any(
            os.path.isdir(os.path.join(name_or_path, d)) and
            os.path.exists(os.path.join(name_or_path, d, "bus.csv"))
            for d in os.listdir(name_or_path)
        )
        if has_bus_csv:
            return load_cvs_folder
        elif any(file.endswith(".pt") for file in os.listdir(name_or_path)):
            return load_pt_folder
        else:
            return load_synthetic_folder
    elif name_or_path.endswith(".pkl"):
        return lambda _: load_dingo_folder(os.path.dirname(name_or_path))
    else:
        return load_simbench_folder
