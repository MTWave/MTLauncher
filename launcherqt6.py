import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QLabel, QComboBox, QTextBrowser, QProgressBar
from PyQt6.QtCore import Qt, QFile, QTextStream, QThread, pyqtSignal
import json
import subprocess
import minecraft_launcher_lib
from Modules.telemetry import getSystemName
from Modules.downloader import version_manager
from Modules.shell import shell

trial = True

try:
    with open('settings.json', 'r') as f:
        trial = json.load(f)['trial']
except FileNotFoundError:
    trial = True



class NewsLoaderThread(QThread):
    news_loaded = pyqtSignal(str) 

    def run(self):
        html_content = """
        <style>
            body { font-family: sans-serif; background-color: #ffffff; color: #333333; margin: 10px; }
            .news-card { margin-bottom: 16px; padding: 12px; border: 1px solid #e0e0e0; border-radius: 6px; background-color: #fafafa; }
            .news-title { margin: 0 0 4px 0; color: #1b5e20; font-size: 14px; font-weight: bold; }
            .news-category { font-size: 10px; color: #757575; text-transform: uppercase; letter-spacing: 0.5px; }
            .news-text { margin-top: 8px; margin-bottom: 0; font-size: 12px; line-height: 1.4; }
        </style>
        """
        try:
            news_data = minecraft_launcher_lib.news.get_minecraft_news()
            entries = news_data.get("entries", [])
            
            if not entries:
                html_content += "<p style='font-size: 12px; text-align: center;'>Новостей пока нет.</p>"
            
            for entry in entries:
                title = entry.get("title", "Без названия")
                text = entry.get("text", "")
                category = entry.get("category", "Общее")
                
                html_content += f"""
                <div class='news-card'>
                    <div class='news-title'>{title}</div>
                    <div class='news-category'>{category}</div>
                    <p class='news-text'>{text}</p>
                </div>
                """
        except Exception as e:
            html_content += f"<p style='color: red; font-size: 12px;'>Не удалось загрузить новости: {e}</p>"
        
        self.news_loaded.emit(html_content)


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройки')
        self.trial = False
        self.resize(256, 177)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.text = QLabel("Trial Mode (Выключение на вашей совести.)")
        layout.addWidget(self.text)
        self.trial_checkbox = QCheckBox('Trial')
        self.trial_checkbox.stateChanged.connect(self.checkbox_changed)
        layout.addWidget(self.trial_checkbox)

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)



    def checkbox_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self.trial = True
        else:
            self.trial = False

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump({'trial': self.trial}, f)

class About(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("О приложении")
        self.resize(328, 282)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.text = QLabel("Beta 4")
        layout.addWidget(self.text)
        self.text2 = QLabel("MTWave")
        layout.addWidget(self.text2)
        self.text3 = QLabel("Ваша ОС: "+getSystemName())
        layout.addWidget(self.text3)


class News(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Новости")
        self.resize(328, 282)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) 
        self.progress_bar.setFixedHeight(4) 
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.news_display = QTextBrowser()
        self.news_display.setOpenExternalLinks(True)  # Клик по ссылкам откроет браузер
        layout.addWidget(self.news_display)

        self.loader_thread = NewsLoaderThread()
        self.loader_thread.news_loaded.connect(self.on_news_received)
        self.loader_thread.start()

    def on_news_received(self, html_text):
        self.news_display.setHtml(html_text)
        self.progress_bar.hide()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MTLauncher')
        self.resize(256, 177)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Имя пользователя')
        layout.addWidget(self.username_input)

        version_label = QLabel("Версия игры:")
        layout.addWidget(version_label)

        self.version_input = QComboBox()
        layout.addWidget(self.version_input)
        self.load_versions()

        self.start_button = QPushButton('Начать игру')
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)

        self.settings_button = QPushButton('Настройки')
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        self.about_button = QPushButton('О приложении')
        self.about_button.clicked.connect(self.open_about_window)
        layout.addWidget(self.about_button)

        self.news_button = QPushButton('Новости')
        self.news_button.clicked.connect(self.open_news)
        layout.addWidget(self.news_button)

        if getSystemName()=="Linux":
            self.shell_button = QPushButton('Shell(Beta)')
            self.shell_button.clicked.connect(self.open_shell)
            layout.addWidget(self.shell_button)

        self.startVersionManager_button = QPushButton('Менеджер версий')
        self.startVersionManager_button.clicked.connect(self.start_versionManager)
        layout.addWidget(self.startVersionManager_button)

        self.setCustomTheme("customTheme.qss")

    def load_versions(self):
        versions_dir = os.path.join('mtwave', 'versions')
        
        if os.path.exists(versions_dir):
            versions = [name for name in os.listdir(versions_dir) 
                       if os.path.isdir(os.path.join(versions_dir, name))]
            
            self.version_input.addItems(versions)
        else:
            print("Папка с версиями не найдена. Для загрузки игры используйте 'Менеджер версий'. После установки перезапустите лаунчер.")

    def start_game(self):
        username = self.username_input.text()
        version = self.version_input.currentText()


        options = {
            'username': username,
            'uuid': '',
            'token': '',
            'demo': trial,
            #"disableChat": disablechat,
            'launcher_name': 'MTLauncher'
        }


        print("Подождите...")

        try:
            subprocess.call(minecraft_launcher_lib.command.get_minecraft_command(version=version, minecraft_directory="mtwave",options=options))
        except FileNotFoundError:
            print("Не удалось запустить игру, возможно версия которую вы выбрали не установлена.")
        

    def open_settings(self):
        self.settings_window = Settings()
        self.settings_window.show()

    def open_about_window(self):
        self.about_window = About()
        self.about_window.show()

    def open_news(self):
            self.news_window = News()
            self.news_window.show()

    def open_shell(self):
        shell()

    def start_versionManager(self):
        try:
            version_manager()
        except ImportError:
            print("Готово")

    def setCustomTheme(self, theme_file):
        file = QFile(theme_file)
        if not file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            print("Файл с пользовательской темой не загружен")
            return

        stream = QTextStream(file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        file.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
