"""
JinjaX Benchmark
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
from pathlib import Path

from jinjax import Catalog, Component
from line_profiler import LineProfiler


HERE = Path(__file__).parent

catalog = Catalog()
catalog.add_folder(HERE)

profile = LineProfiler(
    Catalog.irender,
    Catalog._get_from_file,
    Component.__init__,
    Component.from_cache,
    Component.filter_args,
    Component.render,
)

def render_jinjax():
    for _ in range(1000):
        catalog.render("Hello", message="Hey there")


if __name__ == "__main__":
    print("Profiling...")
    profile.runcall(render_jinjax)
    profile.print_stats()
