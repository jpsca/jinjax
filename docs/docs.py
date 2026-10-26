"""
# JinjaX Documentation

- `python docs.py run` to start a local server with live reload.
- `python docs.py build` to build the documentation for deployment.

"""
from writeadoc import Docs


pages = [
    {
        "title": "Guides",
        "pages": [
            "guides/introduction.md",
            "guides/components.md",
            "guides/arguments.md",
            "guides/organization.md",
            "guides/slots.md",
            "guides/css_and_js.md",
        ],
    },
    "api.md",
    "motivation.md",
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "JinjaX",
        "description": "Super components powers for your Jinja templates",
        "base_url": "https://jinjax.scaletti.dev",
        "lang": "en",
        "source_code": "https://github.com/jpsca/jinjax",
    },
)


if __name__ == "__main__":
    docs.cli()
