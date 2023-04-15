CATEGORIES = {
    "Food": {
        "EN": [
            "Beverage",
            "Dairy_product",
            "Dish",
            "Fish",
            "Fruit",
            "Grain",
            "Herb",
            "Ingredient",
            "Meat",
            "Seafood",
            "Spice",
            "Vegetable",
            "Food"
        ],
        "IT": [  # Sorted following english order
            "Bevanda",          # Beverage
            "Latticino",        # Dairy_product
            "Piatto",           # Dish
            "Pesce",            # Fish
            "Frutta",           # Fruit
            "Granaglie",        # Grain
            "Erba",             # Herb
            "Ingrediente",      # Ingredient
            "Carne",            # Meat
            "Frutti_di_mare",   # Seafood
            "Spezia",           # Spice
            "Verdura",          # Vegetable
            "Cibo"              # Food
        ]
    }
}

LANG = {
    "EN1": {
        "spaCy": "en_core_web_sm",
        "nltk": "eng"
    },
    "EN2": {
        "spaCy": "en_core_web_md",
        "nltk": "eng"
    },
    "EN3": {
        "spaCy": "en_core_web_lg",
        "nltk": "eng"
    },
    "EN4": {
        "spaCy": "en_core_web_trf",
        "nltk": "eng"
    },
    "IT1": {
        "spaCy": "it_core_news_sm",
        "nltk": "ita"
    },
    "IT2": {
        "spaCy": "it_core_news_md",
        "nltk": "ita"
    },
    "IT3": {
        "spaCy": "it_core_news_lg",
        "nltk": "ita"
    }
}

FLAVOUR_TEXT = {
    "EN": {
        "Param_check_end": "Parameters verified. Loading dataset.",
        "Data_load_end": "Loading complete. Starting extraction from {} entries.",
        "Elab_loop": "-Entry {} evaluated. Continuing processing...",
        "Extract_end": "Extraction complete. Starting categorization of {} possible objects.",
        "Categ_loop": "-Object {} categorized. Continuing categorization...",
        "Categ_end": "Categorization complete. Generating output file."
    }
}
