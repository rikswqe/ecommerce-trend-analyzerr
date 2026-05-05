import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

produkty = []

with open("produkty.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=";")
    next(reader)

    for row in reader:
        #  zabezpieczenie
        if len(row) < 3:
            continue

        nazwa = row[0]
        cena = row[1]
        kupilo = row[2]

        #  czyszczenie danych
        cena = cena.replace("zł", "").replace(",", ".").strip()
        kupilo = kupilo.replace(" ", "").strip()

        try:
            cena = float(cena)
            kupilo = int(kupilo)
        except:
            continue

        #  tylko zapis danych
        produkty.append({
            "nazwa": nazwa,
            "cena": cena,
            "kupilo": kupilo
        })

print(f"Wczytano produktów: {len(produkty)}")