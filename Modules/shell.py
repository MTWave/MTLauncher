import os 

#THIS MODULE ONLY FOR LINUX

#TODO: add OS Windows support

def shell():

    print("MTLauncher shell")

    while True:
        shell = input("-->")

        if shell.lower()=="reset-data":
            os.system("rm -rf settings.json")
            print("Файл настроек удален")


        if shell.lower()=="exit":
            print("Был выполнен выход из оболочки")
            break

        if shell.lower()=="help":
            print("reset-data - Удалить файл с настройками")
            print("remove-game - Удаление игры")
            print("clean - Очистка от не нужных файлов и папок")
            print("exit - Выход из оболочки")

        if shell.lower()=="remove-game":
            accept = input("Удалить игру? Д/Н")
            if accept=="Д":
                os.system("rm -rf mtwave")
            else:
                print("Отмена")

        if shell.lower()=="clean":
            os.system("rm -rf logs")
            os.system("rm -rf __pycache__")