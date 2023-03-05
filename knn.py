import csv
import math
from pathlib import Path

#liczenie odleglosci euklidesowej
class EuclideanMetric:
    def calc(self, x1, y1, x2, y2):
        a = pow(x2 - x1, 2)
        b = pow(y2 - y1, 2)
        return math.sqrt(a + b)


#liczenie odleglosci miejskiej
class CityMetric:
    def calc(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

#funkcja utworząca na podstawie danych obiekt wlasciwej klasy
def create_metric(metric):
    if metric == "Euklidesowa":
        return EuclideanMetric()
    if metric == "Miejska":
        return CityMetric()
    return None

#reprezentuje dane do glosowania
class VotingData:
    def __init__(self, neighbour):
        self.neighbours = [neighbour]
        self.distance_sum = neighbour.distance
        self.weight = 1 / pow(neighbour.distance, 2)
        self.v = neighbour.v

    def add(self, neighbour):
        if neighbour.v != self.v:
            raise Exception("Wrong v class")
        self.neighbours.append(neighbour)
        self.distance_sum += neighbour.distance  #suma odleglosci do prostego glosowania
        self.weight += 1 / neighbour.distance #wazenie odwrotnoscia kwadratu odleglosci

    def __len__(self):
        return len(self.neighbours)

    def __str__(self):
        return f"Voting data: {len(self.neighbours)}, distance_sum: {self.distance_sum}, weight: {self.weight}, v: {self.v}"

#klasa bazowa do glosowania
class Voting:
    def group_classes(self, distances, k):
        voting_data = sorted(distances, key=lambda data: (data.distance, data.v)) #sortowanie sasiadow
        print(";".join([str(s) for s in voting_data]))
        k_neighbours = voting_data[:k] #wybierz k najblizszych sasiadow
        statistic = {} #pogrupuj
        for neighbour in k_neighbours:
            if neighbour.v not in statistic:
                statistic[neighbour.v] = VotingData(neighbour)
            else:
                statistic[neighbour.v].add(neighbour)
        return statistic


class SimpleVoting(Voting):
    def vote(self, distances, k):
        statistic = self.group_classes(distances, k)
        #posortuj po sumie odlegosci sasiadow
        statistic = sorted(sorted(statistic.values(), key=lambda voting_data: voting_data.distance_sum),
                           key=lambda voting_data: len(voting_data), reverse=True)
        print(";".join([str(s) for s in statistic]))
        print(statistic[0])
        return statistic[0], statistic[1:]

#reprezentuje wazone glosowanie
class WeightedVoting(Voting):
    def vote(self, distances, k):
        statistic = self.group_classes(distances, k)
        #sortuje po wadze od najwiekszej, do najmniejszej
        statistic = sorted(statistic.values(), key=lambda voting_data: voting_data.weight, reverse=True)
        print(";".join([str(s) for s in statistic]))
        print(statistic[0])
        return statistic[0], statistic[1:]

#funkcja dla typu glosowania
def create_voting(voting):
    if voting == "Proste":
        return SimpleVoting()
    if voting == "Ważone":
        return WeightedVoting()
    return None

#reprezentuje dane wczytane z csv
class Data:
    def __init__(self, x, y, v, distance=None, normalized_x=None, normalized_y=None):
        self.x = x #pierwsza kolumna, os x na wykresie
        self.y = y #druga kolumna, os y na wykresie
        self.v = v #trzecia kolumna, klasa danych
        self.distance = distance #dystans policzony zgodnie z wybrana metryka
        # znormalizowane wartosci x i y
        self.normalized_x = normalized_x
        self.normalized_y = normalized_y

    def __str__(self):
        return f"Data x: {self.x}, y: {self.y}, v: {self.v}, distance: {self.distance}, n_x: {self.normalized_x}, n_y:{self.normalized_y}"

#przetrzymywanie csv, wyznacza min i max
class KnnData:
    def __init__(self):
        self.data = []
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.v = set()

    def add(self, data_entry):
        self.v.add(data_entry.v)
        if len(self.data) > 0:
            self.min_x = min([self.min_x, data_entry.x])
            self.max_x = max([self.max_x, data_entry.x])
            self.min_y = min([self.min_y, data_entry.y])
            self.max_y = max([self.max_y, data_entry.y])
        else:
            self.min_y = data_entry.y
            self.min_x = data_entry.x
            self.max_y = data_entry.y
            self.max_x = data_entry.x
        self.data.append(data_entry)

#klasa reprezentujaca funkcjonalnosc knn
class Knn:
    def __init__(self, knn_path):
        self.knn_path = Path(knn_path)
        self.input_data = None

    #normalizuj wartosc wedlug, aby kazda była w zakresie od 0 do 1
    def _normalize_value(self, value, variable_min, variable_max):
        n = (value - variable_min) / float(variable_max - variable_min)
        print(value, variable_min, variable_max, n)
        return (value - variable_min) / float(variable_max - variable_min)

    def _normalize(self, data):
        try:
            for entry in data.data:
                entry.normalized_x = self._normalize_value(entry.x, data.min_x, data.max_x)
                entry.normalized_y = self._normalize_value(entry.y, data.min_y, data.max_y)
            return True, data
        except ZeroDivisionError:
            return False, "Minimalna wartość dla jednej ze zmiennych to 0 lub min (max analogicznie)"

    def _read_data(self, path):
        if not path.exists():
            return False, "brak KNN"
        input_data = KnnData()
        try:
            with open(path, "r") as file:
                csv_data = csv.reader(file, delimiter=",")
                for row in csv_data:
                    try:
                        x = float(row[0])
                        y = float(row[1])
                        v = int(row[2])
                        if v < 0 or v > 5:
                            raise ValueError
                        input_data.add(Data(x, y, v))
                    #walidacja pliku
                    except ValueError:
                        return False, f"Nieprawidłowa wartość liczbowa lub poza zakresem: {row[0]}, {row[1]}, {row[2]}"
                    except IndexError:
                        return False, f"Źle skonstruowany plik: {row}"
            self.input_data = input_data
            return True, input_data
        except:
            return False, "Błąd podczas analizowania danych wejściowych knn"

    #metoda wywolywana przez kontroler, na wczytanie pliku csv
    def prepare(self):
        print(self.knn_path)
        self.input_data = []
        status, result = self._read_data(self.knn_path)
        if not status:
            return status, result
        status, result = self._normalize(result)
        if not status:
            return status, result
        self.input_data = result
        return True, self.input_data
#metoda wywolywana przez kontroler na klikniecie przez uzytkownika w wykres
    #funkcja do obliczenia knn
    def exec(self, new_x, new_y, metric, voting, k):
        metric = create_metric(metric)
        voting = create_voting(voting)
        distances = []
        #wartosc podana nie powinna byc poza min max wczytanym z pliku, ale gdyby jednak, to policz
        min_x = min([self.input_data.min_x, new_x])
        max_x = max([self.input_data.max_x, new_x])
        min_y = min([self.input_data.min_y, new_y])
        max_y = max([self.input_data.max_y, new_y])
        normalized_x = self._normalize_value(new_x, min_x, max_x)
        normalized_y = self._normalize_value(new_y, min_y, max_y)
        #wez wszystkie punkty z csv i policz dla nich odleglosci do nowego punktu, zgodnie z wybrana metoda
        for data in self.input_data.data:
            distances.append(Data(data.x, data.y, data.v,
                                  metric.calc(data.normalized_x, data.normalized_y, normalized_x, normalized_y),
                                  data.normalized_x, data.normalized_y))
        #znajdz klase zgodnie z wybrana metoda i liczba sasiadow
        return voting.vote(distances, k)
