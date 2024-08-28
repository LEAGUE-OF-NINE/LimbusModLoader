import atexit
import glob
import hashlib
import lzma
import os.path
import shutil
import subprocess
import sys
import logging
import tempfile
from pathlib import Path
import signal
from zipfile import ZipFile
from compress import compress_lunartique_mod

import UnityPy

if appdata := os.getenv("APPDATA"):
    mod_zips_root_path = os.path.join(appdata, "LimbusCompanyMods")
else:
    raise Exception("APPDATA not found")

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

def bundle_data_paths():
    cache_path = os.path.join(appdata, "../LocalLow/Unity/ProjectMoon_LimbusCompany/*/*/")
    return map(os.path.normpath, glob.glob(cache_path))

def file_digest(file_path):
    with open(file_path, "rb") as ff:
        return hashlib.md5(ff.read()).hexdigest()

def detect_lunartique_mods(mod_zips_root: str):
    for mod_zip in glob.glob(f"{mod_zips_root}/*.zip"):
        logging.info("Compressing lunartique format mod (might take a while!): %s", mod_zip)
        try:
            compress_lunartique_mod(mod_zip, mod_zip.replace(".zip", ".carra"))
            os.remove(mod_zip)
            logging.info("* Done")
        except Exception as e:
            logging.info("* Error: %s", e)

def extract_assets(mod_asset_root: str, mod_zips_root: str):
    for mod_zip in glob.glob(f"{mod_zips_root}/*.carra"):
        mod_zip = os.path.normpath(mod_zip)
        try:
            with ZipFile(mod_zip) as z:
                for name in z.namelist():
                    # Validate the path
                    parts = name.split("/")
                    if len(parts) != 3:
                        raise Exception("Invalid path", name)
                    if len(parts[0]) != 32 or len(parts[1]) != 32:
                        raise Exception("Invalid path", name)
                    int(parts[2])
                logging.info("Extracting %s", mod_zip)
                z.extractall(mod_asset_root)
        except Exception as e:
            logging.info("Error processing %s: %s", mod_zip, e)

def cleanup_assets():
    logging.info("Restoring data")
    for bundle_root in bundle_data_paths():
        bundle_path = os.path.join(bundle_root, "__data")
        new_path = os.path.join(bundle_root, "__original")
        if os.path.isfile(new_path):
            logging.info("Restoring %s", bundle_path)
            shutil.move(new_path, bundle_path)

def patch_assets(mod_asset_root: str):
    for bundle_root in bundle_data_paths():
        # Move the original data to a new location temporarily
        bundle_root_path = Path(bundle_root)
        parts = [bundle_root_path.parent.name, bundle_root_path.name]
        mod_path = os.path.join(mod_asset_root, *parts)
        if not os.path.isdir(mod_path):
            continue

        bundle_path = os.path.join(bundle_root, "__data")
        new_path = os.path.join(bundle_root, "__original")

        logging.info("Backing up %s", bundle_path)
        os.rename(bundle_path, new_path)

        logging.info("Patching %s", bundle_path)
        env = UnityPy.load(new_path)
        for obj in env.objects:
            mod_part_path = os.path.join(mod_path, str(obj.path_id))
            if not os.path.isfile(mod_part_path):
                continue
            logging.info("- Loading %s", mod_part_path)
            with open(mod_part_path, "rb") as f:
                obj.set_raw_data(lzma.decompress(f.read(), format=lzma.FORMAT_XZ))

        with open(bundle_path, "wb") as f:
            f.write(env.file.save(packer="original"))
        logging.info("* Patching complete %s -> %s", file_digest(new_path), file_digest(bundle_path))

def kill_handler(*args) -> None:
    sys.exit(0)

cleanup_assets()
atexit.register(cleanup_assets)
signal.signal(signal.SIGINT, kill_handler)
signal.signal(signal.SIGTERM, kill_handler)

logging.info("Detecting lunartique mods")
detect_lunartique_mods(mod_zips_root_path)
tmp_asset_root = tempfile.mkdtemp()
logging.info("Extracting mod assets to %s", tmp_asset_root)
extract_assets(tmp_asset_root, mod_zips_root_path)
logging.info("Backing up data and patching assets....")
patch_assets(tmp_asset_root)
shutil.rmtree(tmp_asset_root)
logging.info("Starting game")
subprocess.call(sys.argv[1:])
