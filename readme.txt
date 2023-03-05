Napisać program ilustrujący działanie algorytmu k-najbliższych sąsiadów. Program powinien pozwalać na wybór następujących parametrów:

liczby sąsiadów k (od 1 do 20),
rodzaju metryki (euklidesowa lub miejska),
rodzaju głosowania (proste lub ważone odwrotnością kwadratu odległości).
Użytkownik wczytuje z pliku tekstowego zbiór uczący. Program normalizuje zmienne i wyświetla obserwacje na ekranie w postaci okrągłych kolorowych punktów (należy zadbać o odpowiednie przeskalowanie, żeby punkty były dobrze widoczne i umieszczone centralnie). Obserwacje należące do poszczególnych kategorii powinny być oznaczone różnymi kolorami. Po ustawieniu parametrów klasyfikatora użytkownik klika w dowolne miejsce obszaru, na którym wyświetlane są obserwacje. Program zaznacza kliknięty punkt kwadratem, dokonuje klasyfikacji obserwacji odpowiadającej klikniętemu punktowi, oznacza go kolorem odpowiadającym wyznaczonej kategorii, wyróżnia sąsiadów, na podstawie których została dokonana klasyfikacja oraz pokazuje odległości do nich. Program pozwala na klikanie dowolną liczbę razy. (Wyróżniane są punkty i odległości tylko do ostatniego z klikniętych przez użytkownika punktów).

Każdy z wierszy pliku zawierającego zbiór uczący zawiera 3-elementowy ciąg liczb oddzielonych przecinkami. Pierwsze 2 elementy tego ciągu to liczby rzeczywiste oznaczające wartości zmiennych opisujących. Trzeci element to liczba naturalna z zakresu 0-5 oznaczająca wartość zmiennej celu - kategorię do której należy dana obserwacja.
Klasyfikacja nowych obserwacji powinna być dokonywana tylko na podstawie obserwacji ze zbioru uczącego. Wprowadzone wcześniej przez kliknięcie nowe punkty nie powinny być używane do klasyfikacji kolejnych.


Aby uruchomić projekt należy mieć skonfigurowanego pythona jako systemowa zmienna Path
Następnie należy zainstalować dodatkowe biblioteki za pomocą polecenia "pip install PySide6"
Po poprawnym doinstalowaniu bibliotek można uruchomić projekt poleceniem "python .\main.py"