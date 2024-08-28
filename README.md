# Limbus Mod Loader

This is a mod loader for loading Limbus Company visual mods. 

- You don't modify game files directly, so you kinda don't break limbus ToS
- It can work with multiple mods changing same folder but different files
- Saves space greatly, now you don't need to upload 2 GB to Google Drive, just upload a 3mb file on Discord instead
- Mods persists after game updates (might require a restart after updating the game to load the mods)

## Discord Servers:
- Limbus Company Modding Discord: https://discord.gg/T4kpeNcnnc

Ping @zenocara or @qifeetrying for support.

## Download
Check the [release](https://github.com/LEAGUE-OF-NINE/LimbusModLoader/releases) page for the newest version, it is available as `build.zip`.

## Installing Mods for Limbus Company

This guide explains how to install mods for Limbus Company using a modloader.

**1. Download and Prepare the Modloader:**

- Download the `modloader.zip` file.
- Extract the contents of the `modloader.zip` file into a new folder. This will create a `main.exe` file and a folder named `__internal`.

**2. Configure Steam Launch Options:**

- Right-click on Limbus Company in your Steam library.
- Select "Properties".
- Go to the "General" tab.
- In the "Launch Options" field, enter the following: `"path to main.exe" %command%`
  - Replace `"path to main.exe"` with the actual path to the `main.exe` file you extracted in step 1 (e.g., `"C:\loader\main.exe"`).
  
![Example](./readme/steam_launch_option.png)

**3. Launch Limbus Company:**

- Launch Limbus Company through Steam.
- The game should start normally.

**4. Locate the Mods Folder:**

- A new folder named `LimbusCompanyMods` will be created in your `AppData/Roaming` directory. This is where you'll install your mods.
   - This folder can be found by pressing Windows key + R to launch the Run dialog window, and entering `%AppData%`
   - Alternatively, try `C:\Users\user\AppData\Roaming\LimbusCompanyMods`


**5. Install Mods:**

- **Lunartique Format Mods:**
  - These are zip files containing installer and uninstaller scripts (`Installer.bat` and `Uninstaller.bat`).
  - Simply place the zip files directly into the `LimbusCompanyMods` folder.
  - The mod will be automatically loaded upon launching the game. No need to unzip!
- **Carra Format Mods:**
   - These are `.carra` files.
   - Place the `.carra` files directly into the `LimbusCompanyMods` folder.

**Important Notes:**

- Lunartique format mods will be converted to Carra format mods when launching the game. This compression can take a while.
- This conversion is irreversible. If you are a mod maker, ensure you keep a copy of the original zipped file.

