import tkinter as tk
from tkinter import ttk
import csv
import os
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BG_COLOR = "#f4f6f8"
ACCENT = "#4a7fc1"

def apply_chart_style(ax, title, x_label, y_label):
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel(x_label, fontsize=9)
    ax.set_ylabel(y_label, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_facecolor("white")

class HelperCardView(tk.Frame):
    def __init__(self, parent, csv_path):
        super().__init__(parent, bg="white")
        
        # 1. Load Data
        names, counts = [], []
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                names.append(row["card_name"])
                counts.append(int(row["times_played"]))

        # 2. Create Plot
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(names, counts, color=ACCENT)
        apply_chart_style(ax, "Helper Card Usage", "Card Name", "Times Played")

        # 3. Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)

class BoardControlView(tk.Frame):
    def __init__(self, parent, csv_path):
        super().__init__(parent, bg="white")
        
        turns, player, demon = [], [], []
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                turns.append(int(row["turn"]))
                player.append(int(row["player_cards"]))
                demon.append(int(row["demon_cards"]))

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        # Stacked Bar Chart
        ax.bar(turns, demon, color="#1a3a5c", label="Demon")
        ax.bar(turns, player, bottom=demon, color="#7fb3d3", label="Player")
        
        apply_chart_style(ax, "Board Control", "Turn", "Card Count")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)

class BoardValueView(tk.Frame):
    def __init__(self, parent, csv_path):
        super().__init__(parent, bg="white")
        
        labels, freqs = [], []
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                labels.append(row["board_value_range"])
                freqs.append(int(row["frequency"]))

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(labels, freqs, color=ACCENT)
        apply_chart_style(ax, "Board Value Range", "Range", "Frequency")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)

class Application:
    def __init__(self, root, data_dir):
        self.root = root
        self.root.title("Devil's Gambit Statistics")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_COLOR)
        self.data_dir = data_dir

        # Container for the graphs
        self.main_container = tk.Frame(self.root, bg=BG_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Bottom Nav
        nav_frame = tk.Frame(self.root, bg=BG_COLOR)
        nav_frame.pack(fill="x", pady=10)

        buttons = [
            ("Helper Cards", self.show_helper),
            ("Board Control", self.show_control),
            ("Board Value", self.show_value)
        ]

        for text, cmd in buttons:
            tk.Button(nav_frame, text=text, command=cmd, width=15).pack(side="left", padx=10, expand=True)

        # Default View
        self.current_view = None
        self.show_helper()

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()

    def show_helper(self):
        self.clear_view()
        self.current_view = HelperCardView(self.main_container, os.path.join(self.data_dir, "helper_cards.csv"))
        self.current_view.pack(fill="both", expand=True)

    def show_control(self):
        self.clear_view()
        self.current_view = BoardControlView(self.main_container, os.path.join(self.data_dir, "board_cards.csv"))
        self.current_view.pack(fill="both", expand=True)

    def show_value(self):
        self.clear_view()
        self.current_view = BoardValueView(self.main_container, os.path.join(self.data_dir, "board_values.csv"))
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root, data_dir="data")
    root.mainloop()