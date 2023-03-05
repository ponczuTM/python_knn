from PySide6.QtCore import Signal, QObject, Slot, QUrl, QPoint
from PySide6.QtGui import QColor
from concurrent.futures import ThreadPoolExecutor
from knn import Knn
from canvas import Canvas

def prepare_knn(knn_path):
    knn = Knn(knn_path)
    status, result = knn.prepare()
    if status:
        return status, knn
    return status, result

#spawdz wynik i poinforuj gui o stanie
def knn_prepared(future):
    status, result = future.result()
    if not status:
        controller.knn_error.emit("<b style='color:red'>" + result + "</b>")
        return
    controller.knn = result
    controller.update_input_data()

#model-widok-kontroler
class Controller(QObject):
    # sygnaly do informowania gui o zmianach
    knn_prepared = Signal() #wczytano dane csv
    knn_error = Signal(str) #blad
    knn_status_updated = Signal(str) #wyznaczono nowa klase, poinformuj gui

    def __init__(self):
        super(Controller, self).__init__()
        self.executor = ThreadPoolExecutor()
        self.knn = None
        self.canvas = None

    def __del__(self):
        self.executor.shutdown()

    #wczytano dane z csv, zbuduj wykres na gui oraz pokaz legende
    def update_input_data(self):
        if self.canvas:
            self.canvas.update_knn(self.knn.input_data)
        self.knn_prepared.emit()
        report = self._build_report()
        self.knn_status_updated.emit(report)

    #wczytaj plik csv
    @Slot(str)
    def prepare_knn(self, path):
        path = QUrl(path).toLocalFile() #sciezka to katalog z projektem
        future = self.executor.submit(prepare_knn, path) #odpal wczytywanie danych
        future.add_done_callback(knn_prepared)
    @Slot(Canvas)
    def set_canvas(self, canvas):
        self.canvas = canvas
    def _build_report(self, knn_result=None, knn_discarded=None, x=None, y=None):
        report = "<h3>Oliwer Mroczkowski<br></b></h3><b>Legenda:<b/><br/>"
        for v in self.knn.input_data.v:
            report += f"<i style='color:{QColor(self.canvas.v_colors[v]).name()}'>klasyfikacja {v}</i><br/>"

        if knn_result:
            report += f"<br/><b>Kliknięty punkt: </b>({x:.2f},{y:.2f})<br/> " \
                      f"Klasa Dominująca: " \
                      f"<i style='color:{QColor(self.canvas.v_colors[knn_result.v]).name()}'>{knn_result.v}</i><br/><br/>"
            for result in knn_result.neighbours:
                report += f"<b>Punkt </b>({result.x:.2f},{result.y:.2f}) klasy <i style='color:{QColor(self.canvas.v_colors[knn_result.v]).name()}'>{knn_result.v}</i>,<br/>Odległość: {result.distance:.2f}<br/>"
        if knn_discarded:
            for discarded in knn_discarded:
                report += "<br/><br/>"
                report += f"<b>Klasa Odrzucona:</b> {discarded.v}<br/>"
                for result in discarded.neighbours:
                    report += f"<b>Odrzucony punkt: </b>({result.x:.2f},{result.y:.2f}),<br/>odległość: {result.distance:.2f}<br/>"
        return report

    #klik -> wyznacz klase, odmaluj wykres, pokaz nowy raport
    @Slot(QPoint, str, str, int)
    def add_point(self, point, metric, voting, k) -> None:
        if not self.canvas.in_canvas(point):
            return
        x, y = self.canvas.from_gui_coords(point.x(), point.y())
        result, discarded = self.knn.exec(x, y, metric, voting, k)
        self.canvas.add_point(point.x(), point.y(), result)
        report = self._build_report(result, discarded, x, y)
        self.knn_status_updated.emit(report)


controller = Controller()
