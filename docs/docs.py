#!/usr/bin/env python
import logging

import jinjax_ui
from claydocs import Docs


logging.getLogger("jinjax").setLevel(logging.INFO)
logging.getLogger("jinjax").addHandler(logging.StreamHandler())

pages = [
    "index.md",
    [
        "Guide",
        [
            "guide/index.md",
            "guide/components.md",
            "guide/extra.md",
            "guide/css_and_js.md",
        ],
    ],
]


# pages = {
#     "en": ["index.md", ...],
#     "es": ["index.md", ...],
# }
# languages = {
#     "en": "English",
#     "es": "Español",
# }

docs = Docs(
    pages,
    # languages=languages,
    # default="en",
    DEFAULT_COMPONENT="Page",
    add_ons=[jinjax_ui],
)
docs.add_folder("components")
docs.add_folder("theme")

docs.catalog.use_cache = False


if __name__ == "__main__":
    docs.run()
