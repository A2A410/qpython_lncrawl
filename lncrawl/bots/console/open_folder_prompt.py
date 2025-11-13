import os

from questionary import prompt

from ...utils.platforms import Platform
from ...core.arguments import get_args


def display_open_folder(folder_path):
    args = get_args()

    if args.suppress:
        return
    if Platform.java or Platform.docker:
        return

    answer = prompt(
        [
            {
                "type": "confirm",
                "name": "exit",
                "message": "Open the output folder?",
                "default": True,
            },
        ]
    )

    if not answer["exit"]:
        return

    if Platform.windows:
        os.system('explorer.exe "{}"'.format(folder_path))
    elif Platform.wsl:
        os.system('cd "{}" && explorer.exe .'.format(folder_path))
    elif Platform.linux:
        os.system('xdg-open "{}"'.format(folder_path))
    elif Platform.mac:
        os.system('open "{}"'.format(folder_path))
    else:
        print("Output Folder: {}".format(folder_path))
