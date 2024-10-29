import atexit
import signal
import subprocess
import sys
import tempfile
import pathlib

# Needed for embedded python
import os

import logging

# DO NOT IMPORT ANY FILES BEFORE THESE TWO LINES
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from modfolder import get_mod_folder
import patch
import sound

mod_zips_root_path = get_mod_folder()
os.makedirs(mod_zips_root_path, exist_ok=True)


if len(sys.argv) < 2:
    logging.info("Usage: main.py <game_path>")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(mod_zips_root_path, "log.txt")),
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logging.info("Limbus Mod Loader version: v1.7.2")


def kill_handler(*args) -> None:
    sys.exit(0)


def cleanup_assets():
    try:
        logging.info("Cleaning up assets")
        patch.cleanup_assets()
        sound.restore_sound()
    except Exception as e:
        logging.error("Error: %s", e)

limbus_data_path = None
for arg in sys.argv:
    if arg.endswith("LimbusCompany.exe"):
        data_path = pathlib.Path(arg).parent
        data_path = os.path.join(data_path, "LimbusCompany_Data")
        if os.path.isdir(data_path):
            limbus_data_path = data_path

additional_folders = []

if limbus_data_path:
    logging.info("Detected limbus steam data folder: %s", limbus_data_path)
    additional_folders.append(limbus_data_path)
else:
    logging.info("Could not detect limbus steam data folder, are you in dev mode?")


try:
    logging.info("Limbus args: %s", sys.argv)
    cleanup_assets()
    atexit.register(cleanup_assets)
    signal.signal(signal.SIGINT, kill_handler)
    signal.signal(signal.SIGTERM, kill_handler)

    logging.info("Detecting lunartique mods")
    patch.detect_lunartique_mods(mod_zips_root_path)
    tmp_asset_root = tempfile.mkdtemp()
    logging.info("Extracting mod assets to %s", tmp_asset_root)
    patch.extract_assets(tmp_asset_root, mod_zips_root_path)
    logging.info("Backing up data and patching assets....")
    patch.patch_assets(tmp_asset_root, additional_folders)
    patch.shutil.rmtree(tmp_asset_root)
    sound.replace_sound(mod_zips_root_path)
    logging.info("Starting game")
    subprocess.call(sys.argv[1:])
except Exception as e:
    logging.error("Error: %s", e)
    sys.exit(1)