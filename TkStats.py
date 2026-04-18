import tkinter as tk
import csv
import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
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

def log_to_csv(filename, data_list):
    '''
    Appends a single row of data to the specified CSV.
    data_list should match the columns.

    board_cards.csv: turn_n, player_cards, demon_cards
    helper_cards.csv: card_name, times_played
    board_values.csv: turn, scale_value
    '''
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data_list)

def nuke_csv(filename, headers):
    '''
    Wipes the csv, and write only headers...
    '''
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

class PointsSummaryView(tk.Frame):
    def __init__(self, parent, gained_path, diff_path):
        super().__init__(parent, bg="white")

        def read_csv_col(path):
            values = []
            with open(path) as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    return values
                col = reader.fieldnames[0]
                for row in reader:
                    try:
                        values.append(float(row[col]))
                    except ValueError:
                        pass
            return values

        def calc_stats(values):
            if not values:
                return ["N/A", "N/A", "N/A", "N/A"]
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            return [f"{mean:.2f}", f"{std_dev:.2f}", f"{min(values):.2f}", f"{max(values):.2f}"]

        try:
            gained_vals = read_csv_col(gained_path)
            diff_vals = read_csv_col(diff_path)

            if not gained_vals and not diff_vals:
                raise ValueError("No valid data")

            gained_stats = calc_stats(gained_vals)
            diff_stats = calc_stats(diff_vals)

            fig = Figure(figsize=(6, 3), dpi=100)
            ax = fig.add_subplot(111)
            ax.axis('tight')
            ax.axis('off')

            table_data = [
                ["Mean", gained_stats[0], diff_stats[0]],
                ["Std Dev", gained_stats[1], diff_stats[1]],
                ["Min", gained_stats[2], diff_stats[2]],
                ["Max", gained_stats[3], diff_stats[3]]
            ]

            table = ax.table(
                cellText=table_data,
                colLabels=["Metric", "Points Gained", "Points Diff"],
                cellLoc='center',
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2.3)

            for i in range(3):
                table[(0, i)].set_facecolor(ACCENT)
                table[(0, i)].set_text_props(weight='bold', color='white')

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except (FileNotFoundError, ValueError):
            label = tk.Label(self, text="No data yet", bg="white", fg="gray")
            label.pack(pady=20)
            
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
            for idx, row in enumerate(csv.DictReader(f)):
                turns.append(idx)  # use index, not turn value
                player.append(int(row["player_cards"]))
                demon.append(int(row["demon_cards"]))

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(turns, demon, color="#ff0000", label="Demon")
        ax.bar(turns, player, bottom=demon, color="#4a7fc1", label="Player")
        
        apply_chart_style(ax, "Board Control", "Turn Index", "Card Count")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)

class BoardValueView(tk.Frame):
    def __init__(self, parent, csv_path):
        super().__init__(parent, bg="white")
        
        turns, values = [], []
        with open(csv_path) as f:
            for idx, row in enumerate(csv.DictReader(f)):
                turns.append(idx)
                values.append(int(row["board_value"]))

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(turns, values, color=ACCENT)
        apply_chart_style(ax, "Board Value Over Time", "Turn Index", "Total Board Value")

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
            ("Board Value", self.show_value),
            ("Points Summary", self.show_points_summary)
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

    def show_points_summary(self):
        self.clear_view()
        self.current_view = PointsSummaryView(
            self.main_container,
            os.path.join(self.data_dir, "points_gained.csv"),
            os.path.join(self.data_dir, "points_diff.csv")
        )
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    '''
        nuke_csv("data/helper_cards.csv", ["card_name", "times_played"])
        nuke_csv("data/board_cards.csv", ["turn", "player_cards", "demon_cards"])
        nuke_csv("data/board_values.csv", ["board_value_range", "frequency"])
    '''
    root = tk.Tk()
    app = Application(root, data_dir="data")
    root.mainloop()