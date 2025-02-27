#!/usr/bin/env python
import logging
from pathlib import Path

import jinjax_ui
from claydocs import Docs


logging.getLogger("jinjax").setLevel(logging.INFO)
logging.getLogger("jinjax").addHandler(logging.StreamHandler())

here = Path(__file__).parent

pages = [
    "index.md",
        [
            "Guide",
            [
                "guide/index.md",
                "guide/components.md",
                "guide/slots.md",
                "guide/css_and_js.md",
                # "guide/integrations.md",
                # "guide/performance.md",
                "guide/motivation.md",
            ],
        ],
        [
            "API",
            [
                "api.md",
            ],
        ],
        [
            "UI components", [
                "ui/index.md",
                "ui/button.md",
                "ui/tabs.md",
                "ui/popover.md",
                "ui/menu.md",
                "ui/accordion.md",
                "ui/linkedlist.md",
                "ui/reldate.md",
            ],
        ],
]

def get_docs() -> Docs:
    root_path = here / "content"
    docs = Docs(
        pages,
        content_folder=root_path,
        add_ons=[jinjax_ui],
        search=False,
        cache=False,
        domain="https://jinjax.scaletti.dev",
        default_component="Page",
        default_social="SocialCard",
        metadata={
            "name": "JinjaX",
            "language": "en",
            "license": "MIT",
            "version": "0.43",
            "web": "https://jinjax.scaletti.dev",
        }
    )
    docs.add_folder(here / "components")
    docs.add_folder(here / "theme")
    return docs


if __name__ == "__main__":
    get_docs().run()
