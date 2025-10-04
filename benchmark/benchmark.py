"""
JinjaX Benchmark
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import timeit
from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

from jinjax import Catalog


here = Path(__file__).parent
number = 10_000

catalog = Catalog()
catalog.add_folder(here)

env = Environment(loader=FileSystemLoader(here))

templates = Jinja2Templates(directory=here)


def render_jinjax_simple():
    """simple case"""
    catalog.render("Simple", message="Hey there")


def render_jinjax_real():
    """realistic case"""
    catalog.render("Real", message="Hey there")


def render_jinja():
    env.get_template("hello.html").render(message="Hey there")


def render_fastapi():
    templates.TemplateResponse("hello.html", {"request": None, "message": "Hey there"})


def benchmark_no_cache(func):
    print(f"NO CACHE: {number:_} renders of {func.__doc__}...\n")
    catalog.use_cache = False
    benchmark(func)


def benchmark_auto_reload(func):
    print(f"CACHE, AUTO-RELOAD: {number:_} renders of {func.__doc__}...\n")
    catalog.use_cache = True
    catalog.auto_reload = True
    benchmark(func)


def benchmark_no_auto_reload(func):
    print(f"CACHE, NO AUTO-RELOAD: {number:_} renders of {func.__doc__}...\n")
    catalog.use_cache = True
    catalog.auto_reload = False
    benchmark(func)


def benchmark(func):
    time_jinjax = timeit.timeit(func, number=number)
    print_line("JinjaX", time_jinjax)
    print(f"{time_jinjax / time_jinja:.1f} times Jinja")
    print(f"{time_jinjax / time_fastapi:.1f} times FastApi")


def print_line(name, time):
    print(f"{name}: {(time / number):.12f}s per render ({(1_000_000 * time / number):.0f}µs), {time:.1f}s total")


def print_separator():
    print()
    print("-" * 60)


if __name__ == "__main__":
    print("Benchmarking...\n")
    time_jinja = timeit.timeit(render_jinja, number=number)
    time_fastapi = timeit.timeit(render_fastapi, number=number)

    print_line("Jinja", time_jinja)
    print_line("FastApi", time_fastapi)
    print_separator()
    benchmark_auto_reload(render_jinjax_real)
    print()
    benchmark_no_auto_reload(render_jinjax_real)
    print()
