import jinjax_ui
from claydocs import Docs


pages = {
    "en": [
        "index.md",
        [
            "Guide",
            [
                "guide/index.md",
                "guide/arguments.md",
                "guide/extra.md",
                "guide/css_and_js.md",
            ],
        ],
    ],
    "es": [
        "index.md",
        [
            "Guía",
            [
                "guia/index.md",
                "guia/argumentos.md",
                "guia/extra.md",
                "guia/css_y_js.md",
            ],
        ],
    ],
}

languages = {
    "en": "English",
    "es": "Español",
}

docs = Docs(
    pages,
    languages=languages,
    default="en",
    add_ons=[jinjax_ui],
    search=False,
)


if __name__ == "__main__":
    docs.run()
