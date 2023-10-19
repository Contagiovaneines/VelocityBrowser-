import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon
import sqlite3
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineSettings
from PyQt5.QtGui import QKeySequence


class AdBlocker(QWebEnginePage):
    def __init__(self):
        super().__init__()

    def acceptNavigationRequest(self, url, navType, isMainFrame):
        if isMainFrame:
            if "https://www.youtube.com/" in url.toString():
                return False

        return super().acceptNavigationRequest(url, navType, isMainFrame)

class FavoritedItem(QListWidgetItem):
    def __init__(self, url):
        super().__init__()
        self.url = url

        icon = QIcon("favorite_icon.png")  
        self.setIcon(icon)

        self.setText(url)

class Tab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)
        self.web_view.setUrl(QUrl("https://www.google.com"))

        ad_blocker = AdBlocker()
        self.web_view.setPage(ad_blocker)

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Adicionando atalhos de teclado
        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab_shortcut.activated.connect(self.add_new_tab)

        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(self.close_current_tab)

        switch_next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        switch_next_tab_shortcut.activated.connect(self.switch_to_next_tab)

        switch_prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        switch_prev_tab_shortcut.activated.connect(self.switch_to_prev_tab)

        self.night_mode = False

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        action_group = QActionGroup(self)

        back_btn = QAction(QIcon("back_icon.png"), "Back", self)  
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(self.navigate_back)
        action_group.addAction(back_btn)

        next_btn = QAction(QIcon("forward_icon.png"), "Forward", self)  
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(self.navigate_forward)
        action_group.addAction(next_btn)

        reload_btn = QAction(QIcon("reload_icon.png"), "Reload", self)  
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.navigate_reload)
        action_group.addAction(reload_btn)

        home_btn = QAction(QIcon("home_icon.png"), "Home", self)  
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        action_group.addAction(home_btn)

        favorite_btn = QAction(QIcon("favorite_icon.png"), "Favorite", self)
        favorite_btn.setStatusTip("Add to favorites")
        favorite_btn.triggered.connect(self.add_to_favorites)
        action_group.addAction(favorite_btn)

        show_favorites_btn = QAction(QIcon("favorite_icon.png"), "Mostrar Favoritos", self)
        show_favorites_btn.setStatusTip("Show Favorites")
        show_favorites_btn.triggered.connect(self.show_favorites)
        action_group.addAction(show_favorites_btn)

        show_history_btn = QAction(QIcon("history_icon.png"), "Histórico", self)
        show_history_btn.setStatusTip("Mostrar Histórico")
        show_history_btn.triggered.connect(self.show_history)
        action_group.addAction(show_history_btn)

        night_mode_btn = QAction(QIcon("night_mode_icon.png"), "Night Mode", self)
        night_mode_btn.setStatusTip("Toggle Night Mode")
        night_mode_btn.setCheckable(True)
        night_mode_btn.toggled.connect(self.toggle_night_mode)
        action_group.addAction(night_mode_btn)

        new_tab_btn = QAction(QIcon("new_tab_icon.png"), "Nova Aba", self)  
        new_tab_btn.setStatusTip("Criar nova aba")
        new_tab_btn.triggered.connect(self.add_new_tab)
        action_group.addAction(new_tab_btn)

        navtb.addActions(action_group.actions())
        navtb.addSeparator()
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon("stop_icon.png"), "Stop", self)  
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(self.navigate_stop)
        navtb.addAction(stop_btn)

        self.browser = None

        with open("styles.css", "r") as file:
            css = file.read()

        self.setStyleSheet(css)

        self.status.showMessage("Ready", 5000)

        self.add_new_tab()
        self.browser.setUrl(QUrl.fromLocalFile(QDir.currentPath() + '/index.html'))

        self.showMaximized()

        self.show()
        

    def update_title(self):
        try:
            title = self.browser.page().title()
            current_tab_index = self.tabs.currentIndex()
            self.tabs.setTabText(current_tab_index, title)
            self.setWindowTitle("% s -  VelocityBrowser " % title)
        except Exception as e:
            print(f"Erro ao atualizar título: {e}")

    def navigate_home(self):
        self.browser.setUrl(QUrl.fromLocalFile(QDir.currentPath() + '/index.html'))


    def navigate_back(self):
        self.browser.back()

    def navigate_forward(self):
        self.browser.forward()

    def navigate_reload(self):
        self.browser.reload()

    def navigate_stop(self):
        self.browser.stop()

    def navigate_to_url(self):
        url_text = self.urlbar.text()
        try:
            q = QUrl(url_text)
            if q.scheme() == "":
                q.setScheme("http")
            self.tabs.currentWidget().web_view.setUrl(q)

            # Adicionar a URL ao histórico
            conn = sqlite3.connect('historico.db')
            conn.execute('INSERT INTO historico (url) VALUES (?)', (q.toString(),))
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Erro ao navegar para a URL: {e}")

    def update_urlbar(self, q):
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def add_to_favorites(self):
        favorite_url = self.browser.url().toString()
        with open('favorites.txt', 'r') as f:
            if favorite_url + '\n' not in f.readlines():
                with open('favorites.txt', 'a') as f:
                    f.write(favorite_url + '\n')

    def show_favorites(self):
        with open('favorites.txt', 'r') as f:
            favorites = f.readlines()

        favorites = [favorite.strip() for favorite in favorites]

        dialog = QDialog(self)
        dialog.setWindowTitle("Favoritos")
        layout = QVBoxLayout()

        list_widget = QListWidget()
        list_widget.addItems(favorites)
        layout.addWidget(list_widget)

        dialog.setLayout(layout)
        dialog.exec_()

    def show_history(self):
        conn = sqlite3.connect('historico.db')
        cursor = conn.execute('SELECT * FROM historico ORDER BY data_acesso DESC')

        dialog = QDialog(self)
        dialog.setWindowTitle("Histórico")
        layout = QVBoxLayout()

        list_widget = QListWidget()
        for row in cursor:
            list_widget.addItem(row[1])
        layout.addWidget(list_widget)

        dialog.setLayout(layout)
        dialog.exec_()

        conn.close()

    def apply_night_mode_to_web_page(self):
        script = """
            var style = document.createElement('style');
            style.textContent = 'body { background-color: #1a1a1a; color: #ffffff; }';
            document.head.append(style);
        """
        self.browser.page().runJavaScript(script)

    def toggle_night_mode(self, checked):
        self.night_mode = checked

        if checked:
            self.browser.setStyleSheet("background-color: #000000;")
            self.apply_night_mode_to_web_page()  # Aplica o tema escuro na página web
            self.setStyleSheet(".night-mode " + self.styleSheet())
        else:
            self.browser.setStyleSheet("background-color: #ffffff; color: #000000;")
            self.setStyleSheet(self.styleSheet().replace(".night-mode ", ""))

    def add_new_tab(self):
        tab = Tab()
        self.browser = tab.web_view  # Agora, a variável de navegador é definida aqui
        index = self.tabs.addTab(tab, "Nova Aba")
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.tabs.currentWidget().web_view.setUrl(QUrl("about:blank"))

    def switch_to_next_tab(self):
        current_index = self.tabs.currentIndex()
        next_index = (current_index + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(next_index)

    def switch_to_prev_tab(self):
        current_index = self.tabs.currentIndex()
        prev_index = (current_index - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(prev_index)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    sys.exit(app.exec_())