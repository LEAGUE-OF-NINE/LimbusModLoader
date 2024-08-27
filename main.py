import glob
import os
from zipfile import ZipFile

import UnityPy
import hashlib
import lzma
import json
import grequests
import pickle

limbus_root_path = "/Users/octeep/Library/Containers/com.isaacmarovitz.Whisky/Bottles/5A2D544D-6B2F-46D3-BF44-AF8DE2AE9764/drive_c/Program Files (x86)/Steam/steamapps/common/Limbus Company"
app_data_root = "/Users/octeep/Library/Containers/com.isaacmarovitz.Whisky/Bottles/5A2D544D-6B2F-46D3-BF44-AF8DE2AE9764/drive_c/users/crossover/AppData"
bundle_hashes_path = "bundle_hashes.pickle"

bundle_reqs = []
bundle_hashes = {}
catalog_json_path = f"{limbus_root_path}/LimbusCompany_Data/StreamingAssets/aa/catalog.json"

def catalog_hash() -> str:
    with open(catalog_json_path, "rb") as catalog:
        return hashlib.md5(catalog.read()).hexdigest()

if os.path.exists(bundle_hashes_path):
    with open(bundle_hashes_path, "rb") as f:
        saved_bundle_hashes = pickle.load(f)
    try:
        if saved_bundle_hashes["catalog"] == catalog_hash():
            print("Bundle hashes are up to date, loading from file")
            bundle_hashes = saved_bundle_hashes
    except Exception as e:
        bundle_hashes = {}

if bundle_hashes == {}:
    print("Downloading bundle hashes")
    with open(catalog_json_path, "rb") as f:
        data = json.load(f)
        for url in data["m_InternalIds"]:
            if not (url.startswith("https://") and url.endswith(".bundle")):
                continue
            bundle_id = url.split("_")[-1].split(".")[0]
            if len(bundle_id) != 32:
                continue
            bundle_reqs.append(grequests.head(url))

    for resp in grequests.imap(bundle_reqs, size=16):
        if "ETag" not in resp.headers:
            continue
        eTag = resp.headers["ETag"]
        if eTag.startswith("\"") and eTag.endswith("\""):
            eTag = eTag[1:-1]
        if len(eTag) != 32:
            continue
        bundle_id = resp.url.split("_")[-1].split(".")[0]
        bundle_hashes[bundle_id] = eTag

    bundle_hashes["catalog"] = catalog_hash()
    with open(bundle_hashes_path, "wb") as f:
        pickle.dump(bundle_hashes, f)

    print("Saved bundle hashes to file")

for bundle_path in glob.glob(f"{app_data_root}/LocalLow/Unity/ProjectMoon_LimbusCompany/*/*/__data"):
    bundle_id = bundle_path.split("/")[-2]
    if bundle_id not in bundle_hashes:
        print(bundle_id, "not found in bundle hashes")
    # print(bundle_id, bundle_path)

def scan_lunartique_mod_root(zip_file: ZipFile) -> str:
    names = set()
    root = None
    for name in zip_file.namelist():
        names.add(name)
        if name.endswith("Assets/"):
            root = name
    if root is None:
        raise Exception("Assets folder not found")
    if f"{root}Uninstallation/" not in names:
        raise Exception("Uninstallation folder not found")
    if f"{root}Installation/" not in names:
        raise Exception("Installation folder not found")
    return root

def scan_lunartique_data(zip_path: ZipFile, data_folder: str) -> set[str]:
    root = scan_lunartique_mod_root(zip_path)
    names = set()
    for name in zip_path.namelist():
        if name.startswith(f"{root}{data_folder}/") and name.endswith("/__data"):
            names.add(name)
    return names

def compress_lunartique_mod(zip_path: str, output: str):
    with ZipFile(zip_path, "r") as root:
        vanilla_dict = {}
        vanilla_paths = scan_lunartique_data(root, "Uninstallation")
        if len(vanilla_paths) == 0:
            raise Exception("No asset files found")

        for vanilla_path in vanilla_paths:
            parts = vanilla_path.split("/")[-3:]
            with root.open(vanilla_path, "r") as f:
                env = UnityPy.load(f)

                for obj in env.objects:
                    data = obj.get_raw_data()
                    parts[2] = str(obj.path_id)
                    vanilla_dict["/".join(parts)] = hashlib.md5(data).digest()

        compressor = lzma.LZMACompressor(preset=9)

        with ZipFile(output, "w") as z:
            for modded_path in map(lambda s: s.replace("Uninstallation", "Installation"), vanilla_paths):
                parts = modded_path.split("/")[-3:]
                with root.open(modded_path, "r") as f:
                    env = UnityPy.load(f)

                    for obj in env.objects:
                        data = obj.get_raw_data()
                        parts[2] = str(obj.path_id)
                        key = "/".join(parts)
                        if key not in vanilla_dict:
                            print("New object found, ignored because new objects are currently unsupported", "/".join(parts))
                            continue
                        if vanilla_dict[key] == hashlib.md5(data).digest():
                            continue
                        with z.open(key, "w") as z_f:
                            print("Writing", key)
                            z_f.write(compressor.compress(data))

compress_lunartique_mod("/Users/octeep/Downloads/sanging cairn.zip", "output.zip")

