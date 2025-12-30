#!/usr/bin/env python3
"""
Learning App GUI - Aplikace pro učení s grafickým rozhraním
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import os

# Import funkcí z původní aplikace
from learning_app import load_all_questions, Question


class LearningAppGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Learning App")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Data
        self.questions: list[Question] = []
        self.current_questions: list[Question] = []
        self.current_index = 0
        self.correct_count = 0
        self.answered = False

        # Styl
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        self.style.configure("Question.TLabel", font=("Arial", 14))
        self.style.configure("Option.TRadiobutton", font=("Arial", 12))
        self.style.configure("Big.TButton", font=("Arial", 12), padding=10)

        # Hlavní kontejner
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Načtení otázek
        self.load_questions()

        # Zobrazení menu
        self.show_menu()

    def load_questions(self):
        """Načte všechny otázky."""
        self.questions = load_all_questions("questions")

    def clear_frame(self):
        """Vyčistí hlavní frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_menu(self):
        """Zobrazí hlavní menu."""
        self.clear_frame()

        # Nadpis
        title = ttk.Label(self.main_frame, text="🎓 Learning App", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Statistiky
        abcd_count = sum(1 for q in self.questions if not q.is_open)
        open_count = sum(1 for q in self.questions if q.is_open)

        stats_text = f"Načteno {len(self.questions)} otázek ({abcd_count} ABCD, {open_count} otevřených)"
        stats = ttk.Label(self.main_frame, text=stats_text)
        stats.pack(pady=(0, 20))

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame,
            text="▶ Spustit kvíz (všechny otázky)",
            style="Big.TButton",
            command=lambda: self.start_quiz("all"),
            width=35
        ).pack(pady=5)

        ttk.Button(
            btn_frame,
            text="🔤 Spustit kvíz (pouze ABCD)",
            style="Big.TButton",
            command=lambda: self.start_quiz("abcd"),
            width=35
        ).pack(pady=5)

        ttk.Button(
            btn_frame,
            text="📝 Spustit kvíz (pouze otevřené)",
            style="Big.TButton",
            command=lambda: self.start_quiz("open"),
            width=35
        ).pack(pady=5)

        ttk.Button(
            btn_frame,
            text="🔄 Znovu načíst otázky",
            style="Big.TButton",
            command=self.reload_questions,
            width=35
        ).pack(pady=5)

        ttk.Button(
            btn_frame,
            text="❌ Konec",
            style="Big.TButton",
            command=self.root.quit,
            width=35
        ).pack(pady=5)

    def reload_questions(self):
        """Znovu načte otázky."""
        self.load_questions()
        messagebox.showinfo("Info", f"Načteno {len(self.questions)} otázek.")
        self.show_menu()

    def start_quiz(self, quiz_type: str):
        """Spustí kvíz."""
        if quiz_type == "all":
            self.current_questions = self.questions.copy()
        elif quiz_type == "abcd":
            self.current_questions = [q for q in self.questions if not q.is_open]
        else:  # open
            self.current_questions = [q for q in self.questions if q.is_open]

        if not self.current_questions:
            messagebox.showwarning("Upozornění", "Žádné otázky k dispozici!")
            return

        random.shuffle(self.current_questions)
        self.current_index = 0
        self.correct_count = 0
        self.show_question()

    def show_question(self):
        """Zobrazí aktuální otázku."""
        self.clear_frame()
        self.answered = False

        question = self.current_questions[self.current_index]

        # Progress
        progress_text = f"Otázka {self.current_index + 1} / {len(self.current_questions)}"
        progress = ttk.Label(self.main_frame, text=progress_text)
        progress.pack(anchor="e")

        # Progress bar
        progress_bar = ttk.Progressbar(
            self.main_frame,
            length=300,
            mode="determinate",
            value=(self.current_index / len(self.current_questions)) * 100
        )
        progress_bar.pack(anchor="e", pady=(0, 20))

        # Otázka
        q_type = "📝" if question.is_open else "🔤"
        q_label = ttk.Label(
            self.main_frame,
            text=f"{q_type} {question.text}",
            style="Question.TLabel",
            wraplength=600
        )
        q_label.pack(pady=(0, 20))

        # Odpověď
        if question.is_open:
            self.show_open_question(question)
        else:
            self.show_abcd_question(question)

    def show_abcd_question(self, question: Question):
        """Zobrazí ABCD otázku."""
        self.selected_option = tk.StringVar(value="")

        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.X, pady=10)

        for letter in sorted(question.options.keys()):
            rb = ttk.Radiobutton(
                options_frame,
                text=f"{letter}) {question.options[letter]}",
                value=letter,
                variable=self.selected_option,
                style="Option.TRadiobutton"
            )
            rb.pack(anchor="w", pady=5, padx=20)

        # Feedback label
        self.feedback_label = ttk.Label(self.main_frame, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=10)

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        self.check_btn = ttk.Button(
            btn_frame,
            text="✓ Zkontrolovat",
            command=lambda: self.check_abcd_answer(question),
            style="Big.TButton"
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(
            btn_frame,
            text="→ Další",
            command=self.next_question,
            style="Big.TButton",
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

    def show_open_question(self, question: Question):
        """Zobrazí otevřenou otázku."""
        # Vstupní pole
        self.answer_entry = ttk.Entry(self.main_frame, font=("Arial", 14), width=40)
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus()

        # Bind Enter key
        self.answer_entry.bind("<Return>", lambda e: self.check_open_answer(question))

        # Feedback label
        self.feedback_label = ttk.Label(self.main_frame, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=10)

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        self.check_btn = ttk.Button(
            btn_frame,
            text="✓ Zkontrolovat",
            command=lambda: self.check_open_answer(question),
            style="Big.TButton"
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)

        self.override_btn = ttk.Button(
            btn_frame,
            text="👍 Přijmout jako správné",
            command=self.override_answer,
            style="Big.TButton",
            state=tk.DISABLED
        )
        self.override_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(
            btn_frame,
            text="→ Další",
            command=self.next_question,
            style="Big.TButton",
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

    def check_abcd_answer(self, question: Question):
        """Zkontroluje ABCD odpověď."""
        if self.answered:
            return

        answer = self.selected_option.get()
        if not answer:
            messagebox.showwarning("Upozornění", "Vyber odpověď!")
            return

        self.answered = True
        correct = answer == question.correct_answer.upper()

        if correct:
            self.correct_count += 1
            self.feedback_label.config(text="✅ Správně!", foreground="green")
        else:
            correct_text = question.options.get(question.correct_answer.upper(), "")
            self.feedback_label.config(
                text=f"❌ Špatně. Správná odpověď: {question.correct_answer}) {correct_text}",
                foreground="red"
            )

        self.check_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)

    def check_open_answer(self, question: Question):
        """Zkontroluje otevřenou odpověď."""
        if self.answered:
            return

        answer = self.answer_entry.get().strip()
        if not answer:
            messagebox.showwarning("Upozornění", "Zadej odpověď!")
            return

        self.answered = True
        correct = answer.lower() == question.correct_answer.lower()

        if correct:
            self.correct_count += 1
            self.feedback_label.config(text="✅ Správně!", foreground="green")
            self.override_btn.config(state=tk.DISABLED)
        else:
            self.feedback_label.config(
                text=f"❌ Špatně. Správná odpověď: {question.correct_answer}",
                foreground="red"
            )
            self.override_btn.config(state=tk.NORMAL)

        self.check_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
        self.answer_entry.config(state=tk.DISABLED)

    def override_answer(self):
        """Přijme odpověď jako správnou."""
        self.correct_count += 1
        self.feedback_label.config(text="✅ Přijato jako správné!", foreground="green")
        self.override_btn.config(state=tk.DISABLED)

    def next_question(self):
        """Přejde na další otázku."""
        self.current_index += 1

        if self.current_index >= len(self.current_questions):
            self.show_results()
        else:
            self.show_question()

    def show_results(self):
        """Zobrazí výsledky kvízu."""
        self.clear_frame()

        total = len(self.current_questions)
        percentage = (self.correct_count / total) * 100 if total > 0 else 0

        # Nadpis
        title = ttk.Label(self.main_frame, text="📊 Výsledky", style="Title.TLabel")
        title.pack(pady=(0, 30))

        # Skóre
        score_text = f"Správné odpovědi: {self.correct_count} / {total}"
        score = ttk.Label(self.main_frame, text=score_text, font=("Arial", 18))
        score.pack(pady=10)

        # Procenta
        percent = ttk.Label(self.main_frame, text=f"{percentage:.1f}%", font=("Arial", 24, "bold"))
        percent.pack(pady=10)

        # Hodnocení
        if percentage >= 90:
            rating = "🏆 Výborně!"
            color = "green"
        elif percentage >= 70:
            rating = "👍 Dobrá práce!"
            color = "blue"
        elif percentage >= 50:
            rating = "📖 Ještě trochu procvičuj."
            color = "orange"
        else:
            rating = "💪 Nevzdávej to!"
            color = "red"

        rating_label = ttk.Label(self.main_frame, text=rating, font=("Arial", 16))
        rating_label.pack(pady=20)

        # Progress bar
        result_bar = ttk.Progressbar(
            self.main_frame,
            length=400,
            mode="determinate",
            value=percentage
        )
        result_bar.pack(pady=20)

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame,
            text="🔄 Znovu",
            command=lambda: self.start_quiz("all"),
            style="Big.TButton"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="🏠 Menu",
            command=self.show_menu,
            style="Big.TButton"
        ).pack(side=tk.LEFT, padx=10)


def main():
    """Spustí GUI aplikaci."""
    # Kontrola existence adresáře s otázkami
    if not os.path.exists("questions"):
        os.makedirs("questions")

    root = tk.Tk()
    app = LearningAppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
