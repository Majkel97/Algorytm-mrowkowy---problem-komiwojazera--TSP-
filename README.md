# Algorytm mrówkowy do rozwiązania problemu komiwojażera

## Spis treści

1. [Wprowadzenie](#wprowadzenie)
2. [Sprawozdanie](#sprawozdanie)
   - [Cele i wymagania](#cele-i-wymagania)
   - [Wykorzystane narzędzia](#wykorzystane-narzędzia)
   - [Zobrazowanie działania aplikacji](#zobrazowanie-działania-aplikacji)
   - [Parametry algorytmu i ich wyjaśnienie](#parametry-algorytmu-i-ich-wyjaśnienie)
   - [Opis algorytmu optymalizacji](#opis-algorytmu-optymalizacji)
   - [Zrzuty ekranu z działania aplikacji](#zrzuty-ekranu-z-działania-aplikacji)
   - [Podsumowanie ](#podsumowanie)
3. [Dokumentacja techniczna](#dokumentacja-techniczna)
   - [Instalacja](#instalacja)
   - [Uruchomienie aplikacji](#uruchomienie-aplikacji)

## Wprowadzenie

W niniejszym sprawozdaniu opisano implementację algorytmu optymalizacji kolonii mrówek (Ant Colony Optimization) do rozwiązania problemu komiwojażera. Algorytm ten został zastosowany w kontekście planowania trasy między różnymi miastami, które użytkownik może wybrać za pomocą formularza. Poniżej przedstawiono cele, użyte narzędzia oraz przykład użycia algorytmu.

## Sprawozdanie

### Cele i wymagania

Celem projektu było zaimplementowanie algorytmu optymalizacji kolonii mrówek do rozwiązania problemu komiwojażera w kontekście trasy między różnymi miastami. Wymagania funkcjonalne obejmowały:

- Możliwość dodawania miast do listy.
- Konfigurowalne parametry algorytmu, takie jak liczba mrówek, liczba iteracji, współczynniki wpływu feromonu i odległości, oraz szybkość (Euclidean distance lub Haversine distance).
- Wizualizację trasy na mapie.
- Wyświetlanie logów i najlepszej znalezionej trasy.
- Działanie algorytmu w przeglądarce jako aplikacja webowa
- Interfejs powinien posiadać instrukcje dla użytkownika o tym jak działa program oraz za co odpowiadają poszczególne parametry.

### Wykorzystane narzędzia

Projekt został zaimplementowany w języku Python przy użyciu frameworka Django. Do obliczeń odległości między miastami wykorzystano bibliotekę NumPy oraz Geopy. Interfejs użytkownika został zrealizowany przy użyciu technologii HTML, CSS i JavaScript, z wykorzystaniem frameworka Django do renderowania szablonów. Projekt korzysta też z dwóch serwisów API - OpenStreetMap do wizualizacji wybranych lokalizacji na mapie oraz wyznaczania tras po wykonaniu algorytmu, natomiast drugie to https://countriesnow.space/ i służy do wyboru miast i zwraca geolokację.

### Zobrazowanie działania aplikacji

Poniżej znajduje się krótki opis funkcji kluczowych oraz sposób użycia algorytmu:

- **`distance`**: Funkcja obliczająca odległość między dwoma punktami, z możliwością wyboru miary (Euclidean lub Haversine). Algorytm posiada dwie funkcję do obliczania odległości pomiędzy punktami - szybszą, która pokazuje przybliżone odległości pomiędzy punktami oraz dokładną, która oblicza odległości z uwzględnieniem krzywizny Ziemi.
- **`ant_colony_optimization`**: Główna funkcja wykonująca algorytm optymalizacji kolonii mrówek. Przyjmuje parametry konfiguracyjne i zwraca znalezioną trasę oraz lokalizacje.
- **`generate_paths`**: Funkcja generująca ścieżki dla zadanej liczby mrówek z określonego punktu startowego.
- **`calculate_probabilities`**: Funkcja obliczająca prawdopodobieństwa wyboru kolejnego punktu na podstawie poziomu feromonu i odległości.
- **`update_pheromone`**: Funkcja aktualizująca poziomy feromonu na trasach na podstawie przejścia mrówek.

Dodatkowo istnieje kilka funkcji obsługujących interfejs użytkownika, takich jak dodawanie miast, konfiguracja algorytmu, wyświetlanie mapy, logów i parametrów.

### Parametry algorytmu i ich wyjaśnienie

**Liczba mrówek** - Liczbą całkowita większa od zera reprezentująca liczbę mrówek.
Możliwy zakres wartości w tym projekcie to od 1 do 100 mrówek.

**Liczba iteracji** - Liczba całkowita większa od zera reprezentująca ile razy algorytm przejdzie przez całą populację mrówek.
Możliwy zakres wartości w tym projekcie to od 1 do 250 iteracji.

**Alpha (waga feromonu)** - Liczba rzeczywista większa od zera, kontroluje, jak bardzo mrówki kierują się ilością feromonu na ścieżkach.
Możliwy zakres wartości w tym projekcie to od 0.1 do 2.0.

**Beta (waga heurystyki** - Liczba rzeczywista większa od zera, kontroluje, jak bardzo mrówki kierują się heurystyką, np. odległością między punktami.
Możliwy zakres wartości w tym projekcie to od 0.1 do 2.0.

**Parowanie feromonów** - Liczba rzeczywista w zakresie 0.0 - 1.0. Określa, jak szybko feromony parują z krawędzi. Im bliżej wartości 1, tym feromony parują szybciej.

**Pozostawiane feromony** - Liczba rzeczywista w zakresie 1.0 - 10.0. Określa, jak dużo feromonów pozostawiają mrówki na krawędziach.

**Dokładność obliczeń** - Do wyboru wartość szybka lub dokładna. Algorytm posiada dwie funkcję do oblicznia odległości pomiędzy punktami - szybszą, która pokazuje przybliżone odległości pomiędzy punktami oraz dokładną, która oblicza odległości z uwzględnieniem krzywizny Ziemi.

### Opis algorytmu optymalizacji

Algorytm optymalizacji kolonii mrówek jest metaheurystyką inspirowaną zachowaniami mrówek w poszukiwaniu żywności. Algorytm ten jest używany do rozwiązania problemu komiwojażera, czyli znalezienia najkrótszej trasy przechodzącej przez wszystkie lokalizacje dokładnie raz.

Kroki algorytmu:

**1. Inicjalizacja feromonów:**

Początkowo, feromony na wszystkich ścieżkach są ustawiane na równą wartość (w tym przypadku, wartość 1).

**2. Iteracje i mrówki**

Dla każdej lokalizacji początkowej, dla każdej iteracji, każda mrówka rozpoczyna trasę od danej lokalizacji. Mrówki poruszają się po grafie, wybierając kolejne lokalizacje zgodnie z prawdopodobieństwem, które zależy od ilości feromonów na ścieżce oraz atrakcyjności trasy (określonej przez parametry alpha i beta). Po przejściu trasy przez wszystkie lokalizacje, aktualizowane są feromony na poszczególnych ścieżkach. Im krótsza trasa, tym większa ilość feromonów jest pozostawiana.

**3. Aktualizacja feromonów**

Feromony są aktualizowane po każdej iteracji na podstawie długości tras przebytych przez mrówki. Krótsze trasy otrzymują większą ilość feromonów, co zwiększa szanse wybrania danej ścieżki przez kolejne mrówki.

**4. Rejestracja najlepszej trasy**

Algorytm śledzi najlepszą znalezioną trasę i jej długość w trakcie wszystkich iteracji i zapamiętuje te dane, aby porównać w kolejnych iteracjach.

**5. Wyniki**

Po zakończeniu wszystkich iteracji algorytm zwraca najlepszą znalezioną trasę i jej długość.

### Zrzuty ekranu z działania aplikacji

### Podsumowanie

Projekt został zrealizowany zgodnie z założeniami, umożliwiając użytkownikowi planowanie trasy między różnymi miastami przy użyciu algorytmu optymalizacji kolonii mrówek. Wizualizacja trasy na mapie oraz dostęp do logów i parametrów algorytmu wspierają zrozumienie procesu optymalizacji. Algorytm może być konfigurowany pod kątem liczby mrówek, liczby iteracji, współczynników wpływu feromonu i odległości, oraz szybkości obliczeń odległości.

## Dokumentacja techniczna

### Instalacja

1. Pobierz kod z tego repozytorium i otwórz go w edytorze kodu (np. Visual Studio Code).

2. Stwórz plik .env w folderze /app. Powinien zawierać następujące dane:

   ```
   # Replace variable values with your secrets / key / logins

   # Django settings
   DEBUG='TRUE_OR_FALSE'
   SECRET_KEY='YOUR_SECRET_KEY'

   # Database settings
   SQL_ENGINE=django.db.backends.postgresql
   POSTGRES_DB='DATABASE_NAME'
   POSTGRES_PASSWORD='DATABASE_PASSWORD'
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   ```

3. Upewnij się, że posiadasz zainstalowanego Dockera i jest on włączony.

4. Uruchom poniższe polecenia z poziomu katalogu głównego repozytorium:

   ```
   cd .docker
   docker compose build
   ```

### Uruchomienie aplikacji

1. Uruchom poniższe polecenia z poziomu katalogu głównego repozytorium:

   ```
   cd .docker
   docker compose build
   ```

2. Docker zainstaluje wszystkie wymagania, utworzy i zastosuje migracje, a następnie uruchomi serwer za pomocą następujących poleceń z Dockerfile i docker-compose.yaml

   ```
   bash -c "python manage.py makemigrations
   && python manage.py migrate --run-syncdb
   && python manage.py runserver 0.0.0.0:8000"
   ```

3. Utwórz konto superużytkownika, aby uzyskać dostęp do panelu administracyjnego Django (jeśli to konieczne):

   ```
   python manage.py createsuperuser
   ```

4. Uzyskaj dostęp do aplikacji w przeglądarce internetowej pod adresem `http://localhost:8000/`.
