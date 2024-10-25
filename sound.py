import glob
import logging
import os
import shutil
import time
from threading import Thread

from modfolder import get_mod_folder


def sound_folder(appdata: str = os.getenv("APPDATA")):
    return os.path.join(appdata, "../LocalLow/ProjectMoon/LimbusCompany/Assets/Sound/FMODBuilds/Desktop")

def sound_data_paths(appdata: str = os.getenv("APPDATA")):
    return map(os.path.normpath, glob.glob(sound_folder(appdata) + "/*.bank"))

def smallest_sound_file(appdata: str = os.getenv("APPDATA")):
    return min(sound_data_paths(appdata), key=os.path.getsize)

def wait_for_validation():
    smallest = smallest_sound_file()
    os.remove(smallest)
    while not os.path.exists(smallest):
        time.sleep(0.1)

def sound_replace_thread(mod_folder: str):
    wait_for_validation()

    logging.info("Validation complete, replacing sound files")
    target_folder = sound_folder()
    for sound_file in glob.glob(f"{mod_folder}/*.bank"):
        logging.info("Replacing %s", sound_file)
        target = os.path.join(target_folder, os.path.basename(sound_file))
        os.replace(target, target + ".bak")
        shutil.copyfile(sound_file, target)

def restore_sound():
    target_folder = sound_folder()
    for sound_file in glob.glob(f"{target_folder}/*.bank.bak"):
        target = sound_file.replace(".bak", "")
        os.replace(sound_file, target)

def replace_sound(mod_folder: str):
    mod_zips_root_path = get_mod_folder()
    if not any(file_name.endswith(".bank") for file_name in os.listdir(mod_zips_root_path)):
        Thread(target=sound_replace_thread, args=(mod_folder,)).start()
    else:
        logging.info("No .bank found, skip sound replacing process.")