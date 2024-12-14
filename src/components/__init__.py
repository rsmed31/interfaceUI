from .cpu import cpu_layout, update_cpu_graph
from .disk import disk_layout, update_disk_graph
from .ram import ram_layout, update_ram_graph
from .logs import log_layout

__all__ = [
    "cpu_layout",
    "update_cpu_graph",
    "disk_layout",
    "update_disk_graph",
    "ram_layout",
    "update_ram_graph",
    "log_layout",
]
