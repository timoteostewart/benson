import pathlib
import yaml
import os
import logging

logger = logging.getLogger(__name__)

with open("settings.yaml", "r", encoding="utf-8") as f:
    settings = yaml.safe_load(f)

# check for required directories
required_directories = []
required_directories.append(settings["OUTPUT_DIR_MP3_FILES"])
for each_dir in required_directories:
    if not os.path.isdir(pathlib.Path(each_dir)):
        os.makedirs(pathlib.Path(each_dir))
        logger.warning(f"{each_dir} had to be created")
