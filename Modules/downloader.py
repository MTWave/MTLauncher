import minecraft_launcher_lib
import subprocess
import sys
import time
from colorama import init
init()
from colorama import Fore, Style

def version_manager():

    print(Fore.WHITE+"MTWave")

    print(Fore.WHITE+"Version-manager")

    print(Fore.WHITE+"Version 1.4")

    current_max = 0


    def set_status(status: str):
        print(status)


    def set_progress(progress: int):
        if current_max != 0:
            print(f"{progress}/{current_max}")

    def set_max(new_max: int):
        global current_max
        current_max = new_max

    callback = {
    'setStatus': set_status,
    'setProgress': set_progress,
    'setMax': set_max
    }

    print(Fore.GREEN+"Выберите тип")
    print("1-Vanilla")
    print("2-Fabric")
    print("3-Quilt")

    game = input("-->")

    if game=="1":
        print(Fore.YELLOW+"Выберите версию...")

        version = input("-->")

        time.sleep(1)

        minecraft_launcher_lib.install.install_minecraft_version(versionid=version, minecraft_directory="mtwave", callback=callback)


    if game=="2":
        print(Fore.YELLOW+"Выберите версию...")

        version = input("-->")

        time.sleep(1)

        try:
            minecraft_launcher_lib.fabric.install_fabric(version, minecraft_directory="mtwave", callback=callback)
        except:
            print(Fore.RED+"Версия не поддерживается")


    if game=="3":
        print(Fore.YELLOW+"Выберите версию...")

        version = input("-->")

        time.sleep(1)

        try:
            minecraft_launcher_lib.quilt.install_quilt(version, minecraft_directory="mtwave", callback=callback)
        except:
            print("Версия не поддерживается")