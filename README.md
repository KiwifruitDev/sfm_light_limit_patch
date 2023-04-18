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
- When the dialog appears, enter the desired light limit and your current `-sfm_shadowmapres` value.
- Please read the warning before clicking `OK`.
- Once applied, your new limit will be active.

## Known Issues

Using high `-sfm_shadowmapres` values such as `8192` can cause SFM to crash with a high amount of lights.

This can be mitigated by using a lower `-sfm_shadowmapres` value when increasing the light limit.

Testing is very limited, so if you encounter any issues, please report them on the [issues page](https://github.com/KiwifruitDev/sfm_light_limit_patch).

## Credits

This project is derived from [Directional Scale Controls](https://github.com/kumfc/sfm-tools) by [LLIoKoJIad (kumfc/umfc)](https://github.com/kumfc).

Directional Scale Controls provides the memory patching functionality that is used in this project.

If you would like to support the creator of Directional Scale Controls, you can donate to them on [boosty](https://boosty.to/umfc).
