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

## Funkce GUI

### Responzivní design
- **Dynamické scalování**: Aplikace se automaticky přizpůsobuje velikosti okna
- **Scrollování**: Pokud obsah přesahuje velikost okna, můžete scrollovat kolečkem myši
- **Minimální velikost**: 700x500 pixelů
- **Doporučená velikost**: 900x650 pixelů

### Funkce
- **Quiz mode**: Procházení otázek s kontrolou odpovědí
- **Focus mode**: Zaměření na špatně zodpovězené otázky
- **Browse mode**: Prohlížení všech otázek se správnými odpověďmi
- **Review mode**: Přehled odpovědí po dokončení kvízu
- **Navigace**: Možnost procházet otázky vpřed i vzad během kvízu

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
Poznámka: Praha má přibližně 1,3 milionu obyvatel.
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

### Poznámky (volitelné)
Ke každé otázce lze přidat poznámku, která se zobrazí po odpovědi:

```
Otázka: Text otázky?
Odpověď: B
Poznámka: Doplňující informace k otázce.
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
