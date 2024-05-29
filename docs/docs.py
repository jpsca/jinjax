#!/usr/bin/env python
import logging

import jinjax_ui
from claydocs import Docs


logging.getLogger("jinjax").setLevel(logging.INFO)
logging.getLogger("jinjax").addHandler(logging.StreamHandler())

pages = [
    "index.mdx",
    [
        "Guide",
        [
            "guide/index.mdx",
            "guide/components.mdx",
            "guide/extra.mdx",
            "guide/css_and_js.mdx",
        ],
    ],
]


# pages = {
#     "en": ["index.mdx", ...],
#     "es": ["index.mdx", ...],
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
