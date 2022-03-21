import yaml

with open("settings.yaml", "r", encoding="utf-8") as f:
    settings = yaml.safe_load(f)
    