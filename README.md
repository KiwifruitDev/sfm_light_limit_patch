# SFM Light Limit Patch

![Light Limit Patch Dialog](https://i.imgur.com/2yj6WpJ.png)

This is a patch for the shadowed light limit in Source Filmmaker.

It allows you to have more than 8 shadowed lights in a scene.

## Installation

Choose one of the following methods:

- Install from the [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2963450977).
- Clone the GitHub repository into your `SourceFilmmaker/game/` directory and add the folder to your `gameinfo.txt` file.
- Download the [script](scripts/sfm/mainmenu/KiwifruitDev/Light_Limit_Patch.py) as a raw *.py file and place it into `SourceFilmmaker/game/usermod/scripts/sfm/mainmenu/KiwifruitDev/` (create the folders if they don't exist).

## Usage

- Launch Source Filmmaker.
- At the top, click `Scripts` > `KiwifruitDev` > `Light Limit Patch`.
- Once the dialog pop-up appears, type in the maximum number of shadowed lights you want to have in your scene and click `OK`.
- A patch will be applied and your new limit will be active.

## Known Issues

In a previous iteration of this patch, using special launch parameters such as `-sfm_shadowmapres 8192` would cause SFM to crash.

Because this patch is now applied dynamically, this issue may no longer occur.

Testing is very limited, so if you encounter any issues, please report them on the [issues page](https://github.com/KiwifruitDev/sfm_light_limit_patch).

## Credits

This project is derived from [Directional Scale Controls](https://github.com/kumfc/sfm-tools) by [LLIoKoJIad (kumfc/umfc)](https://github.com/kumfc).

Directional Scale Controls provides the memory patching functionality that is used in this project.

If you would like to support the creator of Directional Scale Controls, you can donate to them on [boosty](https://boosty.to/umfc).
