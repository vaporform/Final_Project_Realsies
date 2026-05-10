import tkinter as tk
import csv
import os

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd

BG_COLOR = "#f4f6f8"
ACCENT = "#4a7fc1"

def apply_chart_style(ax, title, x_label, y_label):
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel(x_label, fontsize=9)
    ax.set_ylabel(y_label, fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_facecolor("white")

def log_to_csv(filename, data_list):
    if not os.path.exists(filename):
        # hackiest way to do this lol
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        filename_dir = filename.split('/')
        child_name = filename_dir[-1]
        header = []
        match child_name:
            case 'helper_cards.csv':
                header = ["card_name", "times_played"]
            case 'board_cards.csv':
                header = ["turn", "player_cards", "demon_cards"]
            case 'points_diff.csv':
                header = ["points_diff"]
            case 'points_gained.csv':
                header = ["points_gained"]
            case 'board_values.csv':
                header = ['board_value_range']
            case _:
                header = ['something']
        create_csv(filename,header)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data_list)

def create_csv(filename, headers):
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
        
        try:
            df = pd.read_csv(csv_path)
            card_counts = df.groupby("card_name").size()
            
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            card_counts.plot(kind="bar", ax=ax, color=ACCENT)
            apply_chart_style(ax, "Helper Card Usage", "Card Name", "Times Played")
            
            ax.tick_params(axis='x', rotation=45)
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except:
            label = tk.Label(self, text="No data yet", bg="white", fg="gray")
            label.pack(pady=20)

class BoardControlView(tk.Frame):
    def __init__(self, parent, csv_path):
        super().__init__(parent, bg="white")
        
        try:
            self.df = pd.read_csv(csv_path)
            if self.df.empty:
                raise ValueError("Empty Data")
                
            # Create session IDs based on turn == 0
            self.df['session'] = (self.df['turn'] == 0).cumsum()
            self.sessions = ["All"] + self.df['session'].unique().tolist()
            
            # Select 'All' session by default
            self.session_var = tk.StringVar(value="All")
            
            # Top row selector
            control_frame = tk.Frame(self, bg="white")
            control_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(control_frame, text="Session:", bg="white").pack(side="left")
            session_menu = tk.OptionMenu(control_frame, self.session_var, *self.sessions, command=self.update_chart)
            session_menu.pack(side="left", padx=10)
            
            # Sub-frame for chart
            self.chart_frame = tk.Frame(self, bg="white")
            self.chart_frame.pack(fill="both", expand=True)
            
            self.canvas = None
            self.update_chart(self.session_var.get())
            
        except Exception as e:
            label = tk.Label(self, text="No data yet", bg="white", fg="gray")
            label.pack(pady=20)

    def update_chart(self, session_id):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            
        if session_id == "All":
            df_sess = self.df.copy()
            x_values = range(len(df_sess))
            title = "Board Control (All Sessions)"
            xlabel = "Total Turns Across All Sessions"
        else:
            session_id = int(session_id)
            df_sess = self.df[self.df['session'] == session_id].copy()
            x_values = df_sess["turn"]
            title = f"Board Control (Session {session_id})"
            xlabel = "Turn"
        
        # Calculate percentages
        df_sess["total"] = df_sess["player_cards"] + df_sess["demon_cards"]
        df_sess["player_pct"] = (df_sess["player_cards"] / df_sess["total"] * 100).fillna(0)
        df_sess["demon_pct"] = (df_sess["demon_cards"] / df_sess["total"] * 100).fillna(0)
        df_sess["spooky_pct"] = 100 - df_sess["player_pct"] - df_sess["demon_pct"]
        
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        bar_width = 1.0 if session_id == "All" else 0.8
        
        ax.bar(x_values, df_sess["demon_pct"], label="Demon", color="red", width=bar_width)
        ax.bar(x_values, df_sess["player_pct"], bottom=df_sess["demon_pct"], label="Player", color=ACCENT, width=bar_width)
        ax.bar(x_values, df_sess["spooky_pct"], 
               bottom=df_sess["demon_pct"] + df_sess["player_pct"], label="Spooky", color="purple", width=bar_width)
        
        apply_chart_style(ax, title, xlabel, "Percentage (%)")
        ax.set_ylim(0, 100)
        ax.legend()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

class BoardValueView(tk.Frame):
    def __init__(self, parent, csv_path):
        super().__init__(parent, bg="white")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Count frequency of each value
            freq = df.iloc[:, 0].value_counts().sort_index()
            
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            freq.plot(kind="bar", ax=ax, color=ACCENT)
            apply_chart_style(ax, "Board Value Distribution", "Board Value", "Frequency")
            
            ax.tick_params(axis='x', rotation=0)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except:
            label = tk.Label(self, text="No data yet", bg="white", fg="gray")
            label.pack(pady=20)

class Application:
    def __init__(self, root, data_dir):
        self.root = root
        self.root.title("Devil's Gambit Statistics")
        self.root.geometry("1000x600")
        self.root.configure(bg=BG_COLOR)
        self.data_dir = data_dir
        
        # Get available demons
        self.demons = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        
        self.current_demon = self.demons[0] if self.demons else None

        # Top: Demon selector
        selector_frame = tk.Frame(self.root, bg=BG_COLOR)
        selector_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(selector_frame, text="Demon:", bg=BG_COLOR).pack(side="left")
        self.demon_var = tk.StringVar(value=self.current_demon)
        demon_menu = tk.OptionMenu(selector_frame, self.demon_var, *self.demons, command=self.on_demon_change)
        demon_menu.pack(side="left", padx=10)

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
    
    def on_demon_change(self, demon_name):
        self.current_demon = demon_name
        # Refresh current view
        if hasattr(self, 'current_cmd'):
            self.current_cmd()
    
    def get_demon_path(self):
        return os.path.join(self.data_dir, self.current_demon)

    def clear_view(self):
        if self.current_view:
            self.current_view.destroy()

    def show_helper(self):
        self.current_cmd = self.show_helper
        self.clear_view()
        self.current_view = HelperCardView(self.main_container, os.path.join(self.get_demon_path(), "helper_cards.csv"))
        self.current_view.pack(fill="both", expand=True)

    def show_control(self):
        self.current_cmd = self.show_control
        self.clear_view()
        self.current_view = BoardControlView(self.main_container, os.path.join(self.get_demon_path(), "board_cards.csv"))
        self.current_view.pack(fill="both", expand=True)

    def show_value(self):
        self.current_cmd = self.show_value
        self.clear_view()
        self.current_view = BoardValueView(self.main_container, os.path.join(self.get_demon_path(), "board_values.csv"))
        self.current_view.pack(fill="both", expand=True)

    def show_points_summary(self):
        self.current_cmd = self.show_points_summary
        self.clear_view()
        self.current_view = PointsSummaryView(
            self.main_container,
            os.path.join(self.get_demon_path(), "points_gained.csv"),
            os.path.join(self.get_demon_path(), "points_diff.csv")
        )
        self.current_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    '''
    nuke_csv("data/helper_cards.csv", ["card_name", "times_played"])
    nuke_csv("data/board_cards.csv", ["turn", "player_cards", "demon_cards"])
    nuke_csv("data/board_values.csv", ["board_value_range", "frequency"])
    nuke_csv("data/points_diff.csv", ["points_diff"])
    nuke_csv("data/points_gained.csv", ["points_gained"])
    '''
    
    root = tk.Tk()
    app = Application(root, data_dir="data")
    root.mainloop()