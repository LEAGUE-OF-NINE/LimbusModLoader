import atexit
import signal
import subprocess
import sys
import tempfile

from patch import *

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
