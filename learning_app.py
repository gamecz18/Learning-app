#!/usr/bin/env python3
"""
Learning App - Aplikace pro učení pomocí otázek
Podporuje otázky typu ABCD (multiple choice) a otevřené otázky.
Formáty souborů:
  - name.single.txt - jedna otázka v souboru
  - name.multi.txt - více otázek v souboru (oddělené ---)
"""

import os
import random
import glob
from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    """Reprezentace jedné otázky."""
    text: str
    options: dict[str, str]  # {"A": "text", "B": "text", ...}
    correct_answer: str
    is_open: bool = False  # True pro otevřené otázky
    source_file: str = ""
    note: str = ""  # Poznámka k otázce (zobrazí se po odpovědi)


def parse_question_block(block: str, source_file: str = "") -> Optional[Question]:
    """
    Parsuje blok textu s otázkou.

    Formát pro ABCD otázky:
        Otázka: Text otázky?
        A) První možnost
        B) Druhá možnost
        C) Třetí možnost
        D) Čtvrtá možnost
        Odpověď: B
        Poznámka: Doplňující informace

    Formát pro otevřené otázky:
        Otázka: Text otázky?
        Odpověď: Správná odpověď
        Poznámka: Doplňující informace
    """
    lines = [line.strip() for line in block.strip().split('\n') if line.strip()]

    if not lines:
        return None

    question_text = ""
    options = {}
    correct_answer = ""
    note = ""

    for line in lines:
        # Otázka
        if line.lower().startswith("otázka:") or line.lower().startswith("otazka:"):
            question_text = line.split(":", 1)[1].strip()
        # Možnosti A-D
        elif len(line) >= 2 and line[0].upper() in "ABCD" and line[1] in ").:":
            letter = line[0].upper()
            option_text = line[2:].strip()
            options[letter] = option_text
        # Odpověď
        elif line.lower().startswith("odpověď:") or line.lower().startswith("odpoved:"):
            correct_answer = line.split(":", 1)[1].strip()
        # Poznámka
        elif line.lower().startswith("poznámka:") or line.lower().startswith("poznamka:"):
            note = line.split(":", 1)[1].strip()

    if not question_text or not correct_answer:
        return None

    # Pokud nejsou žádné možnosti, je to otevřená otázka
    is_open = len(options) == 0

    return Question(
        text=question_text,
        options=options,
        correct_answer=correct_answer,
        is_open=is_open,
        source_file=source_file,
        note=note
    )


def load_single_file(filepath: str) -> list[Question]:
    """Načte single.txt soubor - jedna otázka."""
    questions = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        question = parse_question_block(content, filepath)
        if question:
            questions.append(question)
    except Exception as e:
        print(f"Chyba při načítání {filepath}: {e}")
    return questions


def load_multi_file(filepath: str) -> list[Question]:
    """Načte multi.txt soubor - více otázek oddělených ---."""
    questions = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Rozdělení podle --- nebo prázdných řádků
        blocks = content.split('---')

        for block in blocks:
            question = parse_question_block(block, filepath)
            if question:
                questions.append(question)
    except Exception as e:
        print(f"Chyba při načítání {filepath}: {e}")
    return questions


def load_all_questions(directory: str = "questions") -> list[Question]:
    """Načte všechny otázky z adresáře."""
    questions = []

    if not os.path.exists(directory):
        print(f"Adresář '{directory}' neexistuje. Vytvořte ho a přidejte soubory s otázkami.")
        return questions

    # Načtení single souborů
    for filepath in glob.glob(os.path.join(directory, "*.single.txt")):
        questions.extend(load_single_file(filepath))

    # Načtení multi souborů
    for filepath in glob.glob(os.path.join(directory, "*.multi.txt")):
        questions.extend(load_multi_file(filepath))

    return questions


def ask_abcd_question(question: Question) -> bool:
    """Položí ABCD otázku a vrátí True pokud je odpověď správná."""
    print(f"\n{'='*50}")
    print(f"📚 {question.text}")
    print("-" * 50)

    # Zobrazení možností
    for letter in sorted(question.options.keys()):
        print(f"  {letter}) {question.options[letter]}")

    print("-" * 50)

    while True:
        answer = input("Tvá odpověď (A/B/C/D): ").strip().upper()
        if answer in question.options:
            break
        print("Neplatná odpověď. Zadej A, B, C nebo D.")

    correct = answer == question.correct_answer.upper()

    if correct:
        print("✅ Správně!")
    else:
        print(f"❌ Špatně. Správná odpověď je: {question.correct_answer}")
        if question.correct_answer.upper() in question.options:
            print(f"   → {question.options[question.correct_answer.upper()]}")

    # Zobrazení poznámky
    if question.note:
        print(f"\n📌 Poznámka: {question.note}")

    return correct


def ask_open_question(question: Question) -> bool:
    """Položí otevřenou otázku a vrátí True pokud je odpověď správná."""
    print(f"\n{'='*50}")
    print(f"📝 {question.text}")
    print("-" * 50)

    answer = input("Tvá odpověď: ").strip()

    # Porovnání bez ohledu na velikost písmen
    correct = answer.lower() == question.correct_answer.lower()

    if correct:
        print("✅ Správně!")
    else:
        print(f"❌ Špatně. Správná odpověď je: {question.correct_answer}")
        # Zeptáme se, jestli byla odpověď přeci jen správná (pro synonyma atd.)
        override = input("Byla tvá odpověď přeci jen správná? (a/n): ").strip().lower()
        if override == 'a':
            correct = True
            print("✅ Označeno jako správné.")

    # Zobrazení poznámky
    if question.note:
        print(f"\n📌 Poznámka: {question.note}")

    return correct


def run_quiz(questions: list[Question], shuffle: bool = True):
    """Spustí kvíz se všemi otázkami."""
    if not questions:
        print("Žádné otázky k dispozici!")
        return

    if shuffle:
        random.shuffle(questions)

    correct_count = 0
    total_count = len(questions)

    print(f"\n🎓 KVÍZ - {total_count} otázek")
    print("=" * 50)

    for i, question in enumerate(questions, 1):
        print(f"\n[Otázka {i}/{total_count}]")

        if question.is_open:
            if ask_open_question(question):
                correct_count += 1
        else:
            if ask_abcd_question(question):
                correct_count += 1

    # Výsledky
    percentage = (correct_count / total_count) * 100 if total_count > 0 else 0
    print(f"\n{'='*50}")
    print(f"📊 VÝSLEDKY")
    print(f"{'='*50}")
    print(f"Správné odpovědi: {correct_count}/{total_count} ({percentage:.1f}%)")

    if percentage >= 90:
        print("🏆 Výborně!")
    elif percentage >= 70:
        print("👍 Dobrá práce!")
    elif percentage >= 50:
        print("📖 Ještě trochu procvičuj.")
    else:
        print("💪 Nevzdávej to, příště to bude lepší!")


def show_menu():
    """Zobrazí hlavní menu."""
    print("\n" + "=" * 50)
    print("🎓 LEARNING APP - Aplikace pro učení")
    print("=" * 50)
    print("1) Spustit kvíz (všechny otázky)")
    print("2) Spustit kvíz (pouze ABCD)")
    print("3) Spustit kvíz (pouze otevřené)")
    print("4) Zobrazit statistiky otázek")
    print("5) Konec")
    print("-" * 50)


def main():
    """Hlavní funkce aplikace."""
    questions_dir = "questions"

    # Kontrola existence adresáře
    if not os.path.exists(questions_dir):
        print(f"Vytvářím adresář '{questions_dir}' pro otázky...")
        os.makedirs(questions_dir)
        print("Přidejte soubory s otázkami do tohoto adresáře.")
        print("Formát: name.single.txt nebo name.multi.txt")
        return

    while True:
        # Načtení otázek při každé iteraci (umožňuje přidávat otázky za běhu)
        all_questions = load_all_questions(questions_dir)

        show_menu()

        if not all_questions:
            print(f"⚠️  Žádné otázky nenalezeny v '{questions_dir}'")
        else:
            abcd_count = sum(1 for q in all_questions if not q.is_open)
            open_count = sum(1 for q in all_questions if q.is_open)
            print(f"📊 Načteno: {len(all_questions)} otázek ({abcd_count} ABCD, {open_count} otevřených)")

        choice = input("\nVyber možnost (1-5): ").strip()

        if choice == "1":
            run_quiz(all_questions)
        elif choice == "2":
            abcd_questions = [q for q in all_questions if not q.is_open]
            run_quiz(abcd_questions)
        elif choice == "3":
            open_questions = [q for q in all_questions if q.is_open]
            run_quiz(open_questions)
        elif choice == "4":
            print(f"\n📊 Statistiky:")
            print(f"   Celkem otázek: {len(all_questions)}")
            print(f"   ABCD otázky: {sum(1 for q in all_questions if not q.is_open)}")
            print(f"   Otevřené otázky: {sum(1 for q in all_questions if q.is_open)}")

            # Statistiky podle souborů
            files = set(q.source_file for q in all_questions)
            print(f"   Zdrojových souborů: {len(files)}")
            for f in sorted(files):
                count = sum(1 for q in all_questions if q.source_file == f)
                print(f"      - {os.path.basename(f)}: {count} otázek")
        elif choice == "5":
            print("\n👋 Nashledanou!")
            break
        else:
            print("Neplatná volba, zkus to znovu.")


if __name__ == "__main__":
    main()
