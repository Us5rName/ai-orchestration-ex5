"""Supporting services — metrics collection, persistence, and visualization.

Metrics service collects timing and memory data via psutil.
ResultWriter persists MetricsRecord instances to JSON.
Visualizer service generates charts and tables via matplotlib/pandas.
"""

from .metrics import MetricsCollector, MetricsRecord
from .result_writer import ResultWriter
from .visualizer import VisualizationResult, Visualizer

__all__ = [
    "MetricsCollector",
    "MetricsRecord",
    "ResultWriter",
    "VisualizationResult",
    "Visualizer",
]
