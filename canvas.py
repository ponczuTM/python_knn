from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtQml import QmlElement
from PySide6.QtGui import QPainter, QBrush
from PySide6.QtCore import Slot, Qt
from knn import Data

#zmienne Qt - do view.qml
QML_IMPORT_NAME = "com.knn.components"
QML_IMPORT_MAJOR_VERSION = 1

# klasa reprezentująca pole robocze
@QmlElement
class Canvas(QQuickPaintedItem):#pozwala rysowac uzywajac QPainter

    def __init__(self):
        super(Canvas, self).__init__()
        self.input_data = None # dane wczytane do knn
        self.margin = 5 #margines od kazdego z brzegów (maly, zeby uzytkownik nie myslal ze moze klikac na granicy)
        self.points = [] # punkty, ktore wprowadza uzytkownik klikajac
        self.scaled = None #punkty reprezentujace knn po przeskalowaniu x,y (w px)
        self.draw_axis = True #wartosci
        self.draw_lines = True #linie
        self.draw_distances = False #odleglosci
        self.last_result = None #ostatni klikniety punkt
        self.v_colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, Qt.GlobalColor.magenta, Qt.GlobalColor.darkYellow, Qt.GlobalColor.cyan] #kolorki
    #wyswietlanie wartosci
    def _draw_axis(self, painter: QPainter):
        min_x = self.input_data.min_x
        max_x = self.input_data.max_x
        min_y = self.input_data.min_y
        max_y = self.input_data.max_y
        x_range = max_x - min_x
        y_range = max_y - min_y
        steps = 20 #ile wartosci, mozna sobie zmienic
        step_x = x_range / steps
        step_y = y_range / steps

        for i in range(1, steps):
            x, y = min_x + step_x * i, min_y + step_y * i #wyznacz wspolzedne z pliku
            x_scaled, _ = self._to_gui_coords(x, min_y) #przeksztalc wspolzedne na px, _ to stala
            _, y_scaled = self._to_gui_coords(min_x, y)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(x_scaled, self.height(), "{:.2f}".format(x)) #wyswietl wartosci
            painter.drawText(0, y_scaled, "{:.2f}".format(y))

    #metoda wywolywana przez qt, za kazdym razem jak trzeba przemalować okno
    def paint(self, painter: QPainter):
        painter.setBrush(QBrush(Qt.GlobalColor.black)) #wypelnienie
        painter.setPen(Qt.GlobalColor.black) #kolor ramki
        painter.drawRect(0, 0, self.width(), self.height()) #narysowanie obszaru

        if not self.scaled: #nie ma danych, nie rysuj
            return

        if self.draw_axis:
            self._draw_axis(painter)

        for data in self.scaled: #narysuj punkty wczytane z pliku
            painter.setBrush(QBrush(self.v_colors[data.v]))
            painter.setPen(self.v_colors[data.v])
            painter.drawEllipse(data.x - 2, data.y - 2, 4, 4)

        if self.last_result: #narysuj sasiadow i oznacz ostatni punkt klikniety przez uzytkownika
            last_x, last_y, last_v = self.points[-1]
            for neighbour in self.last_result.neighbours:
                painter.setPen(Qt.GlobalColor.yellow)
                painter.setBrush(QBrush(Qt.GlobalColor.yellow, Qt.BrushStyle.NoBrush)) #oznaczenie sasiadow
                x, y = self._to_gui_coords(neighbour.x, neighbour.y)
                if self.draw_lines:
                    painter.drawLine(last_x, last_y, x, y)
                if self.draw_distances:
                    middle_x = min(x, last_x) + abs(x - last_x) / 2
                    middle_y = min(y, last_y) + abs(y - last_y) / 2
                    painter.drawText(middle_x, middle_y, "{:.2f}".format(neighbour.distance))
                painter.drawRect(x - 3, y - 3, 6, 6)

        for x, y, v in self.points: #punkty klikniete
            painter.setPen(self.v_colors[v])
            painter.setBrush(self.v_colors[v])
            painter.drawRoundedRect(x - 3, y - 3, 6, 6, 0.3, 0.3) #zaokraglenie

    # metoda przeksztalca wspolzedne wczytane z csv na wspozledne wykresu (w px)
    def _to_gui_coords(self, x, y):
        min_x = self.input_data.min_x
        max_x = self.input_data.max_x
        min_y = self.input_data.min_y
        max_y = self.input_data.max_y
        #wykres bedzie sie zaczynal w punkcie min_x, min_y
        reduced_x = max_x - min_x
        reduced_y = max_y - min_y
        w_multi = (self.width() - self.margin) / float(reduced_x) #proporcja do przeksztalcenia wspolzednych
        h_multi = (self.height() - self.margin) / float(reduced_y)
        reverse_y = self.height() - self.margin
        x, y = (x - min_x) * w_multi + self.margin / 2, reverse_y - (y - min_y) * h_multi + self.margin / 2 #margines
        return x, y

    #odwrotność funkcji _to_gui_coords, przeksztalca wspolzedne wyrazone w pikselach na wspolzedne z csv
    def from_gui_coords(self, x, y):
        min_x = self.input_data.min_x
        max_x = self.input_data.max_x
        min_y = self.input_data.min_y
        max_y = self.input_data.max_y
        w_multi = (self.width() - self.margin) / float(max_x - min_x)
        h_multi = (self.height() - self.margin) / float(max_y - min_y)
        reverse_y = self.height() - self.margin
        y = reverse_y - y
        x, y = (x - self.margin / 2) / w_multi + min_x, (y + self.margin / 2) / h_multi + min_y
        return x, y

    def _scale_input(self, input_data):
        scaled = []
        for data in input_data:
            x, y = self._to_gui_coords(data.x, data.y)
            scaled.append(Data(x, y, data.v))
        return scaled

    def update_knn(self, input_data): #wywolywane za kazdym razem jak uzytkownik wczyta nowe dane z csv
        self.input_data = input_data
        self.scaled = self._scale_input(input_data.data.copy())
        self.points = []
        self.last_result = None
        self.update() #przerysuj wykres

    def add_point(self, x, y, knn_result): #funkcja dodjaca punkt klikniety przez uzytkownika, przeskalowany na px
        self.last_result = knn_result
        self.points.append([x, y, self.last_result.v])
        self.update()

    #dekorator z qt, aby qml byl w stanie wywolac metode
    @Slot(bool)
    def show_axis(self, show):
        self.draw_axis = show
        self.update()

    @Slot(bool)
    def show_distances(self, show):
        self.draw_distances = show
        self.update()

    @Slot(bool)
    def show_connections(self, show):
        self.draw_lines = show
        self.update()

    @Slot()
    def clear(self):
        self.last_result = None
        self.scaled = None
        self.points = None
        self.update()

    #czy uzytkonik kliknal wewnatrz kanwy i nie w margines
    def in_canvas(self, point):
        if point.x() < self.margin/2 or point.y() < self.margin/2:
            return False
        if point.x() > self.width() - self.margin/2 or point.y() > self.height() - self.margin/2:
            return False
        return True

