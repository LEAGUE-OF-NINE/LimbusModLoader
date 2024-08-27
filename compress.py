import hashlib
import lzma
from zipfile import ZipFile

import UnityPy

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
                            print("* New object found, ignored because new objects are currently unsupported", "/".join(parts))
                            continue
                        if vanilla_dict[key] == hashlib.md5(data).digest():
                            continue
                        with z.open(key, "w") as z_f:
                            print("* Writing", key)
                            z_f.write(compressor.compress(data))

