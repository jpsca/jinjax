#!/usr/bin/env python
import logging

import jinjax_ui
from claydocs import Docs


# logging.getLogger("claydocs").setLevel(logging.INFO)
# logging.getLogger("claydocs").addHandler(logging.StreamHandler())

logging.getLogger("jinjax").setLevel(logging.INFO)
logging.getLogger("jinjax").addHandler(logging.StreamHandler())

# pages = {
#     "en": [
#         "index.mdx",
#         [
#             "Guide",
#             [
#                 "guide/index.mdx",
#                 "guide/components.mdx",
#                 "guide/extra.mdx",
#                 "guide/css_and_js.mdx",
#             ],
#         ],
#     ],
#     "es": [
#         "index.mdx",
#         [
#             "Guía",
#             [
#                 "guia/index.mdx",
#                 "guia/componentes.mdx",
#                 "guia/extra.mdx",
#                 "guia/css_y_js.mdx",
#             ],
#         ],
#     ],
# }

# languages = {
#     "en": "English",
#     "es": "Español",
# }

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

docs = Docs(
    pages,
    # languages=languages,
    # default="en",
    DEFAULT_COMPONENT="Page",
)
docs.catalog.add_module(jinjax_ui, prefix="UI")

if __name__ == "__main__":
    docs.run()
