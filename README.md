# Learning App

Aplikace pro učení pomocí otázek v Pythonu.

## Spuštění

### Terminálová verze
```bash
python3 learning_app.py
```

### GUI verze (grafické rozhraní)
```bash
python3 learning_app_gui.py
```

> GUI vyžaduje tkinter (součást standardní instalace Pythonu)

## Typy otázek

- **ABCD otázky** - výběr z možností A, B, C, D
- **Otevřené otázky** - volná textová odpověď

## Formát souborů

### Single soubor (name.single.txt)
Obsahuje jednu otázku:

```
Otázka: Jaké je hlavní město České republiky?
A) Brno
B) Praha
C) Ostrava
D) Plzeň
Odpověď: B
```

### Multi soubor (name.multi.txt)
Obsahuje více otázek oddělených `---`:

```
Otázka: Ve kterém roce vznikla ČSR?
A) 1914
B) 1918
C) 1920
D) 1938
Odpověď: B
---
Otázka: Kdo byl první prezident?
A) Edvard Beneš
B) Klement Gottwald
C) Tomáš Garrigue Masaryk
D) Václav Havel
Odpověď: C
```

### Otevřené otázky
Bez možností A-D:

```
Otázka: Jak se jmenuje nejdelší řeka v ČR?
Odpověď: Vltava
```

## Struktura

```
Learning-app/
├── learning_app.py      # Terminálová verze
├── learning_app_gui.py  # GUI verze
├── questions/           # Složka s otázkami
│   ├── *.single.txt     # Soubory s jednou otázkou
│   └── *.multi.txt      # Soubory s více otázkami
└── README.md
```
