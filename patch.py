import glob
import xxhash
import lzma
import os.path
import shutil
import logging
from pathlib import Path
from zipfile import ZipFile
from compress import compress_lunartique_mod

import UnityPy


def bundle_data_paths(appdata: str = os.getenv("APPDATA")):
    cache_path = os.path.join(appdata, "../LocalLow/Unity/ProjectMoon_LimbusCompany/*/*/")
    return map(os.path.normpath, glob.glob(cache_path))


def file_digest(file_path):
    with open(file_path, "rb") as ff:
        xxdigest = xxhash.xxh128()
        while chunk := ff.read(8192):
            xxdigest.update(chunk)

        return xxdigest.hexdigest()


def detect_lunartique_mods(mod_zips_root: str):
    for mod_zip in glob.glob(f"{mod_zips_root}/*.zip"):
        logging.info("Compressing lunartique format mod (might take a while!): %s", mod_zip)
        try:
            compress_lunartique_mod(mod_zip, mod_zip.replace(".zip", ".carra"))
            os.remove(mod_zip)
            logging.info("* Done")
        except Exception as e:
            logging.info("* Error: %s", e)


def mod_file_size(file):
    try:
        return os.path.getsize(file)
    except:
        return 1 << 64


def extract_assets(mod_asset_root: str, mod_zips_root: str):
    for mod_zip in sorted(glob.glob(f"{mod_zips_root}/*.carra"), key=mod_file_size, reverse=True):
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

    for mod_carra in glob.glob(f"{mod_asset_root}/*/*/*"):
        mod_carra_path = Path(mod_carra)
        new_mod_carra = os.path.join(mod_carra_path.parent.parent, mod_carra_path.name)
        os.replace(mod_carra, new_mod_carra)


def cleanup_assets(bundle_data=bundle_data_paths):
    logging.info("Restoring data")
    for bundle_root in bundle_data():
        bundle_path = os.path.join(bundle_root, "__data")
        new_path = os.path.join(bundle_root, "__original")
        if not os.path.isfile(new_path):
            continue

        try:
            env = UnityPy.load(bundle_path)
            if env.file.version_player != "limbus_modded":
                os.remove(new_path)
                continue
        except Exception as e:
            logging.info("Corrupted file detected %s: %s", bundle_path, e)

        logging.info("Restoring %s", bundle_path)
        os.replace(new_path, bundle_path)


def patch_assets(mod_asset_root: str, bundle_data=bundle_data_paths):
    for bundle_root in bundle_data():
        # Move the original data to a new location temporarily
        bundle_root_path = Path(bundle_root)
        mod_path = os.path.join(mod_asset_root, bundle_root_path.parent.name)
        if not os.path.isdir(mod_path):
            continue

        bundle_path = os.path.join(bundle_root, "__data")
        new_path = os.path.join(bundle_root, "__original")
        os.chmod(bundle_path, 0o777)
        logging.info("Backing up %s", bundle_path)
        os.replace(bundle_path, new_path)

        logging.info("Patching %s", bundle_path)
        env = UnityPy.load(new_path)
        for obj in env.objects:
            mod_part_path = os.path.join(mod_path, str(obj.path_id))
            if not os.path.isfile(mod_part_path):
                continue
            logging.info("- Loading %s", mod_part_path)
            with open(mod_part_path, "rb") as f:
                obj.set_raw_data(lzma.decompress(f.read(), format=lzma.FORMAT_XZ))

        env.file.version_player = "limbus_modded"
        with open(bundle_path, "wb") as f:
            f.write(env.file.save(packer="none"))
        logging.info("* Patching complete %s (%d) -> %s (%d)", file_digest(new_path), os.path.getsize(new_path),
                     file_digest(bundle_path), os.path.getsize(bundle_path))
