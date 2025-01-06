import json
import os

def test_translations():
    base_path = os.path.dirname(__file__)
    languages = ["en", "it", "es"]
    for lang in languages:
        translations_path = os.path.join(base_path, "../translations", f"{lang}.json")
        try:
            with open(translations_path, "r") as file:
                data = json.load(file)
                print(f"Successfully loaded translations for {lang}")
        except Exception as e:
            print(f"Error loading {lang}.json: {e}")

test_translations()
