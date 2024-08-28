import sys

from patch import *
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

def test_bundle_data_paths():
    return map(os.path.normpath, glob.glob("assets/bundle/Uninstallation/*/*/"))

cleanup_assets(bundle_data=test_bundle_data_paths)
patch_assets("assets/mod_root", bundle_data=test_bundle_data_paths)