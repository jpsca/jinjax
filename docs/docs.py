"""
JinjaX
Copyright (c) Juan-Pablo Scaletti <juanpablo@jpscaletti.com>
"""
import logging

from claydocs import Docs, theme_path


LOGGER_LEVEL = logging.INFO
logging.getLogger("claydocs").setLevel(LOGGER_LEVEL)
logging.getLogger("jinjax").setLevel(LOGGER_LEVEL)

# languages = {
#     "en": "English",
#     "es": "Español",
# }

pages = [
    "index.mdx",
    ["Guides", [
        "guides/index.mdx",
        "guides/components.mdx",
        "guides/arguments.mdx",
        "guides/organization.mdx",
        "guides/slots.mdx",
        "guides/css_and_js.mdx",
    ]],
    "api.mdx",
    "motivation.mdx",
]


def get_docs() -> Docs:
    docs = Docs(
        pages,
        content_folder="./content",
        search=False,
        cache=False,
        domain="https://jinjax.scaletti.dev",
        default="Page",
        default_social="SocialCard",
        metadata={
            "default_title": "JinjaX Documentation",
            "repo": "https://github.com/jpsca/jinjax",
            "logo": "/static/img/jinjax-logo.svg",
        }
    )

    # Custom component + theme overrides
    docs.add_folder("./components")
    # Default theme
    docs.add_folder(theme_path)
    return docs


if __name__ == "__main__":
    get_docs().run()

