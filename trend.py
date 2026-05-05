import csv
from collections import defaultdict
from datetime import datetime
import statistics

produkty = defaultdict(list)
trend_list = []

# === WCZYTANIE DANYCH ===
with open("produkty.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=";")
    next(reader)

    for row in reader:
        if len(row) < 5:
            continue

        nazwa = row[0]
        cena = row[1]
        kupilo = row[2]
        data = row[3]
        link = row[4]

        cena = cena.replace("zł", "").replace(",", ".").strip()
        kupilo = kupilo.replace(" ", "").strip()

        try:
            cena = float(cena)
            kupilo = int(kupilo)
            data = datetime.strptime(data, "%Y-%m-%d")
        except:
            continue

        produkty[link].append((data, kupilo, cena, nazwa))


# === ANALIZA ===
for link, dane in produkty.items():

    if len(dane) < 5:  
        continue

    dane.sort(key=lambda x: x[0])

    # === DEDUPLIKACJA
    unikalne = {}
    for d, k, c, n in dane:
        if d not in unikalne or k > unikalne[d][1]:
            unikalne[d] = (d, k, c, n)

    dane = list(unikalne.values())
    dane.sort(key=lambda x: x[0])

    if len(dane) < 5:
        continue

    last = dane[-1]
    cena = last[2]
    nazwa = last[3]

    # === ŚREDNIA SPRZEDAŻ
    ostatnie = dane[-3:]   
    srednia = sum(x[1] for x in ostatnie) / len(ostatnie)

    # === STARSZE DANE
    starsze = dane[:-3]
    if len(starsze) > 0:
        srednia_stara = sum(x[1] for x in starsze) / len(starsze)
    else:
        srednia_stara = srednia

    # === MOMENTUM (luźniejsze)
    momentum = srednia / (srednia_stara + 0.1)

    # === ZMIANY
    wzrosty = []
    for i in range(1, len(ostatnie)):
        diff = ostatnie[i][1] - ostatnie[i-1][1]
        wzrosty.append(diff)

    if len(wzrosty) == 0:
        continue

    sredni_wzrost = sum(wzrosty) / len(wzrosty)

    # === PRZYSPIESZENIE
    if len(wzrosty) >= 2:
        przyspieszenie = wzrosty[-1] - wzrosty[-2]
    else:
        przyspieszenie = 0

    # === STABILNOŚĆ (luźniej)
    if len(wzrosty) > 2:
        odchylenie = statistics.stdev(wzrosty)
    else:
        odchylenie = 0

    if odchylenie > 15:   
        continue

    # === KLASYFIKACJA
    if srednia > 3000:
        typ = "BESTSELLER"
    elif srednia > 500:
        typ = "MID"
    else:
        typ = "TREND"

    # === SCORE
    score = (srednia * momentum * (1 + max(przyspieszenie, 0))) / (1 + cena/50)

    # === DECYZJA (NOWA LOGIKA)
    decyzja = " IGNORUJ"

    if typ == "BESTSELLER":
        decyzja = " PEWNIAK"

    elif typ == "TREND" and momentum > 1.3:
        decyzja = " KUP TERAZ"

    elif typ == "TREND" and momentum > 1.1:
        decyzja = " TESTUJ"

    elif typ == "MID" and momentum > 1.05:
        decyzja = " OBSERWUJ"

    # === KONKURENCJA
    ceny = [x[2] for x in dane]

    min_cena = min(ceny)
    avg_cena = sum(ceny) / len(ceny)

    if cena <= min_cena * 1.02:
        pozycja = " TOP CENA"
    elif cena <= avg_cena:
        pozycja = " OK"
    else:
        pozycja = " DROGO"

    # === FINALNA DECYZJA
    final = " ODPUSC"

    if decyzja == " KUP TERAZ" and pozycja == " TOP CENA":
        final = " BIERZ I SPRZEDAWAJ"

    elif decyzja == " KUP TERAZ":
        final = " TREND ALE DROGO"

    elif decyzja == " TESTUJ" and pozycja != " DROGO":
        final = " TESTUJ"

    elif decyzja == " PEWNIAK" and pozycja != " DROGO":
        final = " STABILNY"

    elif decyzja == " OBSERWUJ":
        final = " OBSERWUJ"

    # === ZAPIS
    trend_list.append((
        nazwa,
        round(srednia, 1),
        round(momentum, 2),
        round(score, 2),
        cena,
        pozycja,
        final
    ))

    if final == " BIERZ I SPRZEDAWAJ":
        print(f" NOWY HIT: {nazwa}")


# === SORT
trend_list.sort(key=lambda x: x[3], reverse=True)

# === OUTPUT
print("\n=== TOP PRODUKTY ===\n")

for p in trend_list[:20]:
    print(p[0])
    print(f"Sprzedaż: {p[1]} | Momentum: {p[2]}")
    print(f"Cena: {p[4]} zł | Pozycja: {p[5]}")
    print(f"Decyzja: {p[6]}")
    print("------")