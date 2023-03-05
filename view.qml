import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml
//Import kanwy napisanej w pythonie w ramach zadania
import com.knn.components

//uloz kontrolki okna w kolumnie(od gory do dolu)
ColumnLayout {
    function enableKnn() {
        //czy mozna akceptowac klikniecia w wykres? Tak, jezeli wszystkie parametry sa wybrane i sa w wlasciwym zakresie(k)
        var kVal = parseInt(k.text)
        console.debug(kVal)
        if (kVal < 1 || kVal > 20 || isNaN(kVal)) {
            mouseArea.enabled = false
            knnStatus.text = "<b style='color:red'>Podaj prawidłowe dane</b>"
            return
        }
        knnStatus.text = ""
        mouseArea.enabled = true
    }
    property string csv: "" //sciezka do pliku csv

    //komunikacja z kontrolerem, python wysyla sygnal, tutaj jest on odbierany
    Connections {
        target: controller
        function onKnn_done() {
            message.text = "OK"
        }
        function onKnn_prepared() {
            k.enabled = true
            metric.enabled = true
            voting.enabled = true
            console.log("knn prepared")
            enableKnn()
        }
        function onKnn_status_updated(status) {
            knnStatus.text = status
        }
        function onKnn_error(error) {
            knnStatus.text = error
            knnView.clear()
        }
    }

    FileDialog {
        id: fileDialog
        currentFolder: ""

        onAccepted: {
            message.text = selectedFile
            csv = selectedFile
            controller.prepare_knn(csv)
        }
        fileMode: FileDialog.OpenFile
        nameFilters: ["Csv (*.csv)"]
    }
    anchors.fill: parent
    Text {
        id: message
        text: "<h3><b>Program ilustrujący działanie algorytmu k-najbliższych sąsiadów<br>   Oliwer Mroczkowski</b></h3>"
        Layout.fillWidth: true
    }
    Text {
        text: "   "
    }
    ToolBar {
        Layout.fillWidth: true
        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "Wybierz plik tekstowy"
                onClicked: {
                    fileDialog.visible = true
                }
            }
            Text {
                text: "        "
            }
            Text {
                text: "K:"
            }
            TextField {
                enabled: false
                placeholderText: "1-20"
                text: "3"
                color: "green"
                validator: IntValidator {
                    //sprawdzenie liczby k
                    top: 20
                    bottom: 1
                }
                onTextChanged: {
                    if (acceptableInput) {
                        k.color = "green"
                    } else {
                        k.color = "red"
                    }
                    enableKnn()
                }
                id: k
            }
            Text {
                text: "        "
            }
            Text {
                text: "Rodzaj metryki:"
            }
            ComboBox {
                enabled: false
                id: metric
                model: ["Euklidesowa", "Miejska"]
            }
            Text {
                text: "        "
            }
            Text {
                text: "Rodzaj głosowania:"
            }
            ComboBox {
                enabled: false
                id: voting
                model: ["Proste", "Ważone"]
            }
        }
    }
    RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        MouseArea {
            id: mouseArea
            enabled: false
            Layout.fillWidth: true
            Layout.fillHeight: true
            Canvas {
                id: knnView
                anchors.fill: parent
            }
            onClicked: function (mouse) {
                controller.add_point(mapToItem(knnView, mouse.x, mouse.y),
                                     metric.currentText, voting.currentText,
                                     parseInt(k.text))
            }
            Component.onCompleted: {
                //przekazanie obiektu kanwy do kontrolera
                controller.set_canvas(knnView)
            }
        }
        ScrollView {
            Layout.fillHeight: true
            implicitWidth: 200
            TextArea {
                anchors.fill: parent
                id: knnStatus
                readOnly: true
                textFormat: Text.RichText
            }
        }
    }
    RowLayout {
        Layout.fillWidth: true
        CheckBox {
            text: " pokaż wartości na osiach             "
            checked: true
            onCheckedChanged: {
                knnView.show_axis(checked)
            }
        }
        CheckBox {
            text: " pokaż linie łączące punkty             "
            checked: true
            onCheckedChanged: {
                knnView.show_connections(checked)
            }
        }
        CheckBox {
            text: " pokaż odległości do punktu"
            checked: false
            onCheckedChanged: {
                knnView.show_distances(checked)
            }
        }
    }
}
