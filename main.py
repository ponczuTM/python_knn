from PySide6.QtQuick import QQuickView

from PySide6.QtCore import QSize, QUrl, qInstallMessageHandler

from PySide6.QtGui import QGuiApplication
from pathlib import Path
import sys
from controller import controller

#dodaj logowanie na konsoli
def qt_message_handler(mode, context, message):
    print(mode, context, message)

qInstallMessageHandler(qt_message_handler)
app = QGuiApplication([])

view = QQuickView()

view.setResizeMode(QQuickView.SizeRootObjectToView)

# Load the QML file

qml_file = Path(__file__).parent / "view.qml"

if not qml_file.exists():
    print("No qml file")

view.rootContext().setContextProperty("controller", controller)#dodaj kontroler do gui
view.setSource(QUrl.fromLocalFile(qml_file.resolve()))

# Show the window

if view.status() == QQuickView.Error:
    for e in view.errors():
        print("error: " + e.toString())
    sys.exit(-1)


view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
#ustaw szytwne wymiary okna, canva nie ma zaimplementowanej oblsugi zmiany okna, wiec rozmiar okna jest sztywny
view.setMaximumSize(QSize(1024, 650))
view.setMinimumSize(QSize(1024, 650))
view.show()

app.exec()

del view
