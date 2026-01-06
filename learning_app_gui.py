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


class QuizResult:
    """Výsledek jedné otázky v kvízu."""
    def __init__(self, question: Question, user_answer: str, is_correct: bool):
        self.question = question
        self.user_answer = user_answer
        self.is_correct = is_correct


class LearningAppGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Learning App")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        # Data
        self.questions: list[Question] = []
        self.current_questions: list[Question] = []
        self.current_index = 0
        self.correct_count = 0
        self.answered = False

        # Review a Focus mode
        self.quiz_results: list[QuizResult] = []  # Výsledky aktuálního kvízu
        self.wrong_questions: list[Question] = []  # Špatně zodpovězené otázky pro focus mode
        self.focus_mode_enabled = False  # Toggle pro focus mode
        self.review_index = 0  # Index pro review mode
        self.browse_index = 0  # Index pro browse mode (prohlížení všech otázek)

        # Styl
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Arial", 18, "bold"))
        self.style.configure("Question.TLabel", font=("Arial", 13))
        self.style.configure("Option.TRadiobutton", font=("Arial", 11))
        self.style.configure("Big.TButton", font=("Arial", 11), padding=10)

        # Hlavní kontejner s scrollable frame
        self.main_canvas = tk.Canvas(root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack scrollbar a canvas
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Bind mouse wheel
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Bind window resize pro update canvas width
        self.root.bind("<Configure>", self._on_window_resize)

        # Main frame uvnitř scrollable frame
        self.main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Načtení otázek
        self.load_questions()

        # Zobrazení menu
        self.show_menu()

    def _on_mousewheel(self, event):
        """Zpracování scroll wheel."""
        if event.num == 4 or event.delta > 0:
            self.main_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.main_canvas.yview_scroll(1, "units")

    def _on_window_resize(self, event):
        """Aktualizace canvas při změně velikosti okna."""
        if event.widget == self.root:
            self.main_canvas.itemconfig("frame", width=event.width - self.scrollbar.winfo_width())

    def _reset_scroll(self):
        """Reset scrollování na začátek."""
        self.main_canvas.yview_moveto(0)

    def _get_wraplength(self):
        """Vypočítá optimální wraplength podle šířky okna."""
        return max(400, self.root.winfo_width() - 150)

    def load_questions(self):
        """Načte všechny otázky."""
        self.questions = load_all_questions("questions")

    def clear_frame(self):
        """Vyčistí hlavní frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self._reset_scroll()

    def show_menu(self):
        """Zobrazí hlavní menu."""
        self.clear_frame()

        # Centrální kontejner pro lepší vycentrování
        center_frame = ttk.Frame(self.main_frame)
        center_frame.pack(expand=True, fill=tk.BOTH)

        # Nadpis
        title = ttk.Label(center_frame, text="🎓 Learning App", style="Title.TLabel")
        title.pack(pady=(20, 30))

        # Statistiky
        abcd_count = sum(1 for q in self.questions if not q.is_open)
        open_count = sum(1 for q in self.questions if q.is_open)

        stats_text = f"Načteno {len(self.questions)} otázek ({abcd_count} ABCD, {open_count} otevřených)"
        stats = ttk.Label(center_frame, text=stats_text, font=("Arial", 11))
        stats.pack(pady=(0, 20))

        # Focus mode toggle
        focus_frame = ttk.Frame(center_frame)
        focus_frame.pack(pady=10)

        self.focus_var = tk.BooleanVar(value=self.focus_mode_enabled)
        focus_check = ttk.Checkbutton(
            focus_frame,
            text="🎯 Focus mode (zaměřit se na špatné otázky)",
            variable=self.focus_var,
            command=self.toggle_focus_mode
        )
        focus_check.pack()

        if self.wrong_questions:
            wrong_count = len(self.wrong_questions)
            focus_info = ttk.Label(
                focus_frame,
                text=f"({wrong_count} otázek k procvičení)",
                foreground="gray"
            )
            focus_info.pack()
        elif self.focus_mode_enabled:
            focus_info = ttk.Label(
                focus_frame,
                text="(žádné špatné otázky - focus mode bude vypnut)",
                foreground="orange"
            )
            focus_info.pack()

        # Tlačítka
        btn_frame = ttk.Frame(center_frame)
        btn_frame.pack(pady=20)

        buttons = [
            ("▶ Spustit kvíz (všechny otázky)", lambda: self.start_quiz("all")),
            ("🔤 Spustit kvíz (pouze ABCD)", lambda: self.start_quiz("abcd")),
            ("📝 Spustit kvíz (pouze otevřené)", lambda: self.start_quiz("open")),
            ("📖 Procházet všechny otázky", self.start_browse),
            ("🔄 Znovu načíst otázky", self.reload_questions),
            ("❌ Konec", self.root.quit)
        ]

        for text, command in buttons:
            btn = ttk.Button(
                btn_frame,
                text=text,
                style="Big.TButton",
                command=command
            )
            btn.pack(pady=5, fill=tk.X, padx=20)

    def reload_questions(self):
        """Znovu načte otázky."""
        self.load_questions()
        messagebox.showinfo("Info", f"Načteno {len(self.questions)} otázek.")
        self.show_menu()

    def toggle_focus_mode(self):
        """Přepne focus mode."""
        self.focus_mode_enabled = self.focus_var.get()

    def start_quiz(self, quiz_type: str):
        """Spustí kvíz."""
        # Resetování výsledků kvízu
        self.quiz_results = []
        self.quiz_answers = {}  # Slovník pro ukládání odpovědí podle indexu

        # Výběr otázek podle typu a focus mode
        if self.focus_mode_enabled and self.wrong_questions:
            # Focus mode - použij špatně zodpovězené otázky
            base_questions = self.wrong_questions.copy()
            if quiz_type == "abcd":
                self.current_questions = [q for q in base_questions if not q.is_open]
            elif quiz_type == "open":
                self.current_questions = [q for q in base_questions if q.is_open]
            else:
                self.current_questions = base_questions
        else:
            # Normální mód
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

        # Progress header
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 15))

        progress_text = f"Otázka {self.current_index + 1} / {len(self.current_questions)}"
        progress = ttk.Label(progress_frame, text=progress_text, font=("Arial", 11))
        progress.pack(side=tk.TOP, anchor="e")

        # Progress bar
        progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            value=(self.current_index / len(self.current_questions)) * 100
        )
        progress_bar.pack(fill=tk.X, pady=(5, 0))

        # Otázka
        q_type = "📝" if question.is_open else "🔤"
        q_label = ttk.Label(
            self.main_frame,
            text=f"{q_type} {question.text}",
            style="Question.TLabel",
            wraplength=self._get_wraplength()
        )
        q_label.pack(pady=(10, 20), fill=tk.X)

        # Odpověď
        if question.is_open:
            self.show_open_question(question)
        else:
            self.show_abcd_question(question)

    def show_abcd_question(self, question: Question):
        """Zobrazí ABCD otázku."""
        # Zkontroluj, jestli už byla otázka zodpovězena
        prev_answer = self.quiz_answers.get(self.current_index)

        self.selected_option = tk.StringVar(value=prev_answer["answer"] if prev_answer else "")

        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        for letter in sorted(question.options.keys()):
            option_frame = ttk.Frame(options_frame)
            option_frame.pack(fill=tk.X, pady=5, padx=20)

            rb = ttk.Radiobutton(
                option_frame,
                text=f"{letter}) {question.options[letter]}",
                value=letter,
                variable=self.selected_option,
                style="Option.TRadiobutton"
            )
            rb.pack(anchor="w", fill=tk.X)
            # Pokud už bylo zodpovězeno, zakázat změnu
            if prev_answer:
                rb.config(state=tk.DISABLED)

        # Feedback label
        self.feedback_label = ttk.Label(self.main_frame, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=10)

        # Zobrazení předchozí odpovědi
        if prev_answer:
            self.answered = True
            if prev_answer["correct"]:
                self.feedback_label.config(text="✅ Správně!", foreground="green")
            else:
                correct_text = question.options.get(question.correct_answer.upper(), "")
                self.feedback_label.config(
                    text=f"❌ Špatně. Správná odpověď: {question.correct_answer}) {correct_text}",
                    foreground="red",
                    wraplength=self._get_wraplength()
                )

        # Note label (pro poznámky)
        self.note_label = ttk.Label(
            self.main_frame,
            text="",
            font=("Arial", 11, "italic"),
            foreground="gray",
            wraplength=self._get_wraplength()
        )
        self.note_label.pack(pady=5)

        # Zobrazit poznámku pokud už bylo zodpovězeno
        if prev_answer and question.note:
            self.note_label.config(text=f"📌 {question.note}")

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        # Tlačítko zpět
        self.prev_btn = ttk.Button(
            btn_frame,
            text="← Zpět",
            command=self.prev_question,
            style="Big.TButton",
            state=tk.NORMAL if self.current_index > 0 else tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.check_btn = ttk.Button(
            btn_frame,
            text="✓ Zkontrolovat",
            command=lambda: self.check_abcd_answer(question),
            style="Big.TButton",
            state=tk.DISABLED if prev_answer else tk.NORMAL
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(
            btn_frame,
            text="→ Další",
            command=self.next_question,
            style="Big.TButton",
            state=tk.NORMAL if prev_answer else tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

    def show_open_question(self, question: Question):
        """Zobrazí otevřenou otázku."""
        # Zkontroluj, jestli už byla otázka zodpovězena
        prev_answer = self.quiz_answers.get(self.current_index)

        # Vstupní pole - responzivní šířka
        entry_frame = ttk.Frame(self.main_frame)
        entry_frame.pack(fill=tk.X, pady=10, padx=40)

        self.answer_entry = ttk.Entry(entry_frame, font=("Arial", 14))
        self.answer_entry.pack(fill=tk.X, expand=True)

        if prev_answer:
            self.answer_entry.insert(0, prev_answer["answer"])
            self.answer_entry.config(state=tk.DISABLED)
            self.answered = True
        else:
            self.answer_entry.focus()
            # Bind Enter key
            self.answer_entry.bind("<Return>", lambda e: self.check_open_answer(question))

        # Feedback label
        self.feedback_label = ttk.Label(self.main_frame, text="", font=("Arial", 12))
        self.feedback_label.pack(pady=10)

        # Zobrazení předchozí odpovědi
        if prev_answer:
            if prev_answer["correct"]:
                self.feedback_label.config(text="✅ Správně!", foreground="green")
            else:
                self.feedback_label.config(
                    text=f"❌ Špatně. Správná odpověď: {question.correct_answer}",
                    foreground="red",
                    wraplength=self._get_wraplength()
                )

        # Note label (pro poznámky)
        self.note_label = ttk.Label(
            self.main_frame,
            text="",
            font=("Arial", 11, "italic"),
            foreground="gray",
            wraplength=self._get_wraplength()
        )
        self.note_label.pack(pady=5)

        # Zobrazit poznámku pokud už bylo zodpovězeno
        if prev_answer and question.note:
            self.note_label.config(text=f"📌 {question.note}")

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        # Tlačítko zpět
        self.prev_btn = ttk.Button(
            btn_frame,
            text="← Zpět",
            command=self.prev_question,
            style="Big.TButton",
            state=tk.NORMAL if self.current_index > 0 else tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.check_btn = ttk.Button(
            btn_frame,
            text="✓ Zkontrolovat",
            command=lambda: self.check_open_answer(question),
            style="Big.TButton",
            state=tk.DISABLED if prev_answer else tk.NORMAL
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
            state=tk.NORMAL if prev_answer else tk.DISABLED
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

        # Uložení výsledku
        result = QuizResult(question, answer, correct)
        self.quiz_results.append(result)

        # Uložení do quiz_answers pro navigaci
        self.quiz_answers[self.current_index] = {"answer": answer, "correct": correct}

        if correct:
            self.correct_count += 1
            self.feedback_label.config(text="✅ Správně!", foreground="green")
        else:
            correct_text = question.options.get(question.correct_answer.upper(), "")
            self.feedback_label.config(
                text=f"❌ Špatně. Správná odpověď: {question.correct_answer}) {correct_text}",
                foreground="red",
                wraplength=self._get_wraplength()
            )

        # Zobrazení poznámky
        if question.note:
            self.note_label.config(text=f"📌 {question.note}")

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
        self.current_open_answer = answer  # Uložení pro případný override
        correct = answer.lower() == question.correct_answer.lower()

        # Uložení výsledku
        result = QuizResult(question, answer, correct)
        self.quiz_results.append(result)

        # Uložení do quiz_answers pro navigaci
        self.quiz_answers[self.current_index] = {"answer": answer, "correct": correct}

        if correct:
            self.correct_count += 1
            self.feedback_label.config(text="✅ Správně!", foreground="green")
            self.override_btn.config(state=tk.DISABLED)
        else:
            self.feedback_label.config(
                text=f"❌ Špatně. Správná odpověď: {question.correct_answer}",
                foreground="red",
                wraplength=self._get_wraplength()
            )
            self.override_btn.config(state=tk.NORMAL)

        # Zobrazení poznámky
        if question.note:
            self.note_label.config(text=f"📌 {question.note}")

        self.check_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL)
        self.answer_entry.config(state=tk.DISABLED)

    def override_answer(self):
        """Přijme odpověď jako správnou."""
        self.correct_count += 1
        self.feedback_label.config(text="✅ Přijato jako správné!", foreground="green")
        self.override_btn.config(state=tk.DISABLED)
        # Aktualizace posledního výsledku jako správného
        if self.quiz_results:
            self.quiz_results[-1].is_correct = True
        # Aktualizace v quiz_answers
        if self.current_index in self.quiz_answers:
            self.quiz_answers[self.current_index]["correct"] = True

    def prev_question(self):
        """Přejde na předchozí otázku."""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

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

        # Aktualizace špatně zodpovězených otázek pro focus mode
        new_wrong = [r.question for r in self.quiz_results if not r.is_correct]
        # Přidání nových špatných otázek (bez duplicit)
        existing_texts = {q.text for q in self.wrong_questions}
        for q in new_wrong:
            if q.text not in existing_texts:
                self.wrong_questions.append(q)
                existing_texts.add(q.text)
        # Odebrání otázek, které byly tentokrát správně (z focus mode)
        correct_texts = {r.question.text for r in self.quiz_results if r.is_correct}
        self.wrong_questions = [q for q in self.wrong_questions if q.text not in correct_texts]

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
        elif percentage >= 70:
            rating = "👍 Dobrá práce!"
        elif percentage >= 50:
            rating = "📖 Ještě trochu procvičuj."
        else:
            rating = "💪 Nevzdávej to!"

        rating_label = ttk.Label(self.main_frame, text=rating, font=("Arial", 16))
        rating_label.pack(pady=10)

        # Progress bar - responzivní
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=10, padx=40)

        result_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            value=percentage
        )
        result_bar.pack(fill=tk.X, expand=True)

        # Info o focus mode
        if self.wrong_questions:
            wrong_info = ttk.Label(
                self.main_frame,
                text=f"🎯 {len(self.wrong_questions)} otázek k procvičení ve focus mode",
                foreground="gray"
            )
            wrong_info.pack(pady=5)

        # Tlačítka
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(
            btn_frame,
            text="📋 Projít otázky",
            command=self.start_review,
            style="Big.TButton"
        ).pack(side=tk.LEFT, padx=10)

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

    def start_review(self):
        """Spustí review mode pro procházení otázek."""
        if not self.quiz_results:
            messagebox.showinfo("Info", "Žádné otázky k zobrazení.")
            return
        self.review_index = 0
        self.show_review()

    def show_review(self):
        """Zobrazí aktuální otázku v review mode."""
        self.clear_frame()

        result = self.quiz_results[self.review_index]
        question = result.question
        total = len(self.quiz_results)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame,
            text=f"📋 Přehled otázek ({self.review_index + 1}/{total})",
            style="Title.TLabel"
        ).pack(side=tk.LEFT)

        # Status ikona
        status_icon = "✅" if result.is_correct else "❌"
        status_text = "Správně" if result.is_correct else "Špatně"
        status_color = "green" if result.is_correct else "red"

        status_label = ttk.Label(
            header_frame,
            text=f"{status_icon} {status_text}",
            font=("Arial", 14),
            foreground=status_color
        )
        status_label.pack(side=tk.RIGHT)

        # Progress bar - responzivní
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 20), padx=40)

        progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            value=((self.review_index + 1) / total) * 100
        )
        progress_bar.pack(fill=tk.X, expand=True)

        # Otázka
        q_type = "📝" if question.is_open else "🔤"
        q_label = ttk.Label(
            self.main_frame,
            text=f"{q_type} {question.text}",
            style="Question.TLabel",
            wraplength=self._get_wraplength()
        )
        q_label.pack(pady=(0, 15), fill=tk.X)

        # Odpovědi
        if question.is_open:
            # Otevřená otázka
            answer_frame = ttk.Frame(self.main_frame)
            answer_frame.pack(fill=tk.X, pady=5, padx=20)

            ttk.Label(
                answer_frame,
                text=f"Tvá odpověď: {result.user_answer}",
                font=("Arial", 12),
                foreground="blue" if result.is_correct else "red"
            ).pack(anchor="w")

            ttk.Label(
                answer_frame,
                text=f"Správná odpověď: {question.correct_answer}",
                font=("Arial", 12),
                foreground="green"
            ).pack(anchor="w", pady=(5, 0))
        else:
            # ABCD otázka
            options_frame = ttk.Frame(self.main_frame)
            options_frame.pack(fill=tk.X, pady=5, padx=20)

            for letter in sorted(question.options.keys()):
                is_correct = letter == question.correct_answer.upper()
                is_user_answer = letter == result.user_answer

                # Určení barvy
                if is_correct:
                    color = "green"
                    prefix = "✓ "
                elif is_user_answer and not is_correct:
                    color = "red"
                    prefix = "✗ "
                else:
                    color = "black"
                    prefix = "  "

                option_text = f"{prefix}{letter}) {question.options[letter]}"
                if is_user_answer:
                    option_text += " (tvá odpověď)"

                ttk.Label(
                    options_frame,
                    text=option_text,
                    font=("Arial", 12),
                    foreground=color
                ).pack(anchor="w", pady=2)

        # Poznámka
        if question.note:
            note_label = ttk.Label(
                self.main_frame,
                text=f"📌 {question.note}",
                font=("Arial", 11, "italic"),
                foreground="gray",
                wraplength=self._get_wraplength()
            )
            note_label.pack(pady=15)

        # Navigační tlačítka
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(pady=20)

        prev_btn = ttk.Button(
            nav_frame,
            text="← Předchozí",
            command=self.prev_review,
            style="Big.TButton",
            state=tk.NORMAL if self.review_index > 0 else tk.DISABLED
        )
        prev_btn.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            nav_frame,
            text="🏠 Zpět na výsledky",
            command=self.show_results,
            style="Big.TButton"
        ).pack(side=tk.LEFT, padx=10)

        next_btn = ttk.Button(
            nav_frame,
            text="Další →",
            command=self.next_review,
            style="Big.TButton",
            state=tk.NORMAL if self.review_index < total - 1 else tk.DISABLED
        )
        next_btn.pack(side=tk.LEFT, padx=10)

        # Quick navigation - špatné otázky
        wrong_indices = [i for i, r in enumerate(self.quiz_results) if not r.is_correct]
        if wrong_indices:
            wrong_frame = ttk.Frame(self.main_frame)
            wrong_frame.pack(pady=10)

            ttk.Label(
                wrong_frame,
                text="Přeskočit na špatnou otázku:",
                foreground="gray"
            ).pack(side=tk.LEFT, padx=5)

            for idx in wrong_indices:
                btn = ttk.Button(
                    wrong_frame,
                    text=str(idx + 1),
                    command=lambda i=idx: self.goto_review(i),
                    width=3
                )
                btn.pack(side=tk.LEFT, padx=2)

    def prev_review(self):
        """Přejde na předchozí otázku v review."""
        if self.review_index > 0:
            self.review_index -= 1
            self.show_review()

    def next_review(self):
        """Přejde na další otázku v review."""
        if self.review_index < len(self.quiz_results) - 1:
            self.review_index += 1
            self.show_review()

    def goto_review(self, index: int):
        """Přejde na konkrétní otázku v review."""
        self.review_index = index
        self.show_review()

    def start_browse(self):
        """Spustí procházení všech otázek."""
        if not self.questions:
            messagebox.showinfo("Info", "Žádné otázky k zobrazení.")
            return
        self.browse_index = 0
        self.show_browse()

    def show_browse(self):
        """Zobrazí aktuální otázku v browse mode."""
        self.clear_frame()

        question = self.questions[self.browse_index]
        total = len(self.questions)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame,
            text=f"📖 Procházení otázek ({self.browse_index + 1}/{total})",
            style="Title.TLabel"
        ).pack(side=tk.LEFT)

        # Typ otázky
        q_type_text = "Otevřená" if question.is_open else "ABCD"
        q_type_icon = "📝" if question.is_open else "🔤"
        ttk.Label(
            header_frame,
            text=f"{q_type_icon} {q_type_text}",
            font=("Arial", 12),
            foreground="gray"
        ).pack(side=tk.RIGHT)

        # Progress bar - responzivní
        progress_frame_browse = ttk.Frame(self.main_frame)
        progress_frame_browse.pack(fill=tk.X, pady=(0, 20), padx=40)

        progress_bar = ttk.Progressbar(
            progress_frame_browse,
            mode="determinate",
            value=((self.browse_index + 1) / total) * 100
        )
        progress_bar.pack(fill=tk.X, expand=True)

        # Otázka
        q_label = ttk.Label(
            self.main_frame,
            text=f"❓ {question.text}",
            style="Question.TLabel",
            wraplength=self._get_wraplength()
        )
        q_label.pack(pady=(0, 15))

        # Odpovědi
        if question.is_open:
            # Otevřená otázka
            answer_frame = ttk.Frame(self.main_frame)
            answer_frame.pack(fill=tk.X, pady=5, padx=20)

            ttk.Label(
                answer_frame,
                text=f"✓ Správná odpověď: {question.correct_answer}",
                font=("Arial", 12),
                foreground="green"
            ).pack(anchor="w")
        else:
            # ABCD otázka
            options_frame = ttk.Frame(self.main_frame)
            options_frame.pack(fill=tk.X, pady=5, padx=20)

            for letter in sorted(question.options.keys()):
                is_correct = letter == question.correct_answer.upper()
                color = "green" if is_correct else "black"
                prefix = "✓ " if is_correct else "  "

                ttk.Label(
                    options_frame,
                    text=f"{prefix}{letter}) {question.options[letter]}",
                    font=("Arial", 12),
                    foreground=color
                ).pack(anchor="w", pady=2)

        # Poznámka
        if question.note:
            note_label = ttk.Label(
                self.main_frame,
                text=f"📌 {question.note}",
                font=("Arial", 11, "italic"),
                foreground="gray",
                wraplength=self._get_wraplength()
            )
            note_label.pack(pady=15)

        # Zdrojový soubor
        if question.source_file:
            import os
            source_label = ttk.Label(
                self.main_frame,
                text=f"📁 {os.path.basename(question.source_file)}",
                font=("Arial", 10),
                foreground="lightgray"
            )
            source_label.pack(pady=5)

        # Navigační tlačítka
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(pady=20)

        prev_btn = ttk.Button(
            nav_frame,
            text="← Předchozí",
            command=self.prev_browse,
            style="Big.TButton",
            state=tk.NORMAL if self.browse_index > 0 else tk.DISABLED
        )
        prev_btn.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            nav_frame,
            text="🏠 Menu",
            command=self.show_menu,
            style="Big.TButton"
        ).pack(side=tk.LEFT, padx=10)

        next_btn = ttk.Button(
            nav_frame,
            text="Další →",
            command=self.next_browse,
            style="Big.TButton",
            state=tk.NORMAL if self.browse_index < total - 1 else tk.DISABLED
        )
        next_btn.pack(side=tk.LEFT, padx=10)

        # Rychlá navigace
        jump_frame = ttk.Frame(self.main_frame)
        jump_frame.pack(pady=10)

        ttk.Label(jump_frame, text="Přejít na otázku:", foreground="gray").pack(side=tk.LEFT, padx=5)

        self.jump_entry = ttk.Entry(jump_frame, width=5)
        self.jump_entry.pack(side=tk.LEFT, padx=5)
        self.jump_entry.bind("<Return>", lambda e: self.jump_to_browse())

        ttk.Button(
            jump_frame,
            text="Přejít",
            command=self.jump_to_browse
        ).pack(side=tk.LEFT, padx=5)

    def prev_browse(self):
        """Přejde na předchozí otázku v browse mode."""
        if self.browse_index > 0:
            self.browse_index -= 1
            self.show_browse()

    def next_browse(self):
        """Přejde na další otázku v browse mode."""
        if self.browse_index < len(self.questions) - 1:
            self.browse_index += 1
            self.show_browse()

    def jump_to_browse(self):
        """Přejde na konkrétní otázku v browse mode."""
        try:
            idx = int(self.jump_entry.get()) - 1
            if 0 <= idx < len(self.questions):
                self.browse_index = idx
                self.show_browse()
            else:
                messagebox.showwarning("Upozornění", f"Zadej číslo 1-{len(self.questions)}")
        except ValueError:
            messagebox.showwarning("Upozornění", "Zadej platné číslo")


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
