"""
Super League Greece - Κεντρικό GUI
Εφαρμογή διαχείρισης στατιστικών Super League Ελλάδας
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from database import (
    init_database, get_connection,
    TeamDAO, SeasonDAO, MatchDAO, PlayerDAO,
    StandingsDAO, RefereeDAO, CoachDAO, ImportDAO
)

# ============================================================
# ΘΕΜΑ & ΧΡΩΜΑΤΑ
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark":      "#0A0E1A",
    "bg_card":      "#111827",
    "bg_header":    "#0F1F3D",
    "accent_blue":  "#1E40AF",
    "accent_gold":  "#F59E0B",
    "accent_green": "#10B981",
    "accent_red":   "#EF4444",
    "text_primary": "#F1F5F9",
    "text_muted":   "#94A3B8",
    "border":       "#1E293B",
    "highlight":    "#3B82F6",
}


# ============================================================
# ΒΟΗΘΗΤΙΚΑ WIDGETS
# ============================================================

def create_label(parent, text, font_size=13, color=None, bold=False, **kwargs):
    weight = "bold" if bold else "normal"
    color = color or COLORS["text_primary"]
    return ctk.CTkLabel(parent, text=text,
                        font=ctk.CTkFont(family="Helvetica", size=font_size, weight=weight),
                        text_color=color, **kwargs)


def create_button(parent, text, command, color="blue", width=120, **kwargs):
    fg = COLORS["accent_blue"] if color == "blue" else \
         COLORS["accent_gold"] if color == "gold" else \
         COLORS["accent_green"] if color == "green" else \
         COLORS["accent_red"]
    return ctk.CTkButton(parent, text=text, command=command,
                         fg_color=fg, hover_color=fg,
                         font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                         width=width, height=34, **kwargs)


def create_entry(parent, placeholder="", width=200):
    return ctk.CTkEntry(parent, placeholder_text=placeholder, width=width,
                        fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                        text_color=COLORS["text_primary"],
                        font=ctk.CTkFont(family="Helvetica", size=12))


def create_combobox(parent, values, width=200):
    return ctk.CTkComboBox(parent, values=values, width=width,
                           fg_color=COLORS["bg_card"], border_color=COLORS["border"],
                           text_color=COLORS["text_primary"],
                           button_color=COLORS["accent_blue"],
                           font=ctk.CTkFont(family="Helvetica", size=12))


# ============================================================
# ΚΥΡΙΑ ΕΦΑΡΜΟΓΗ
# ============================================================

class SuperLeagueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_database()
        self._seed_sample_data()

        self.title("⚽ Super League Greece — Διαχειριστής")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_dark"])

        self._build_layout()
        self._show_frame("dashboard")

    # --------------------------------------------------------
    def _seed_sample_data(self):
        """Εισαγωγή δειγματικών δεδομένων αν η βάση είναι κενή."""
        with get_connection() as conn:
            if conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0] > 0:
                return

        teams = [
            ("Ολυμπιακός", "ΟΛΥ", "Πειραιάς", "Γ. Καραϊσκάκης", 1925),
            ("ΑΕΚ", "ΑΕΚ", "Αθήνα", "OPAP Arena", 1924),
            ("ΠΑΟΚ", "ΠΑΟ", "Θεσσαλονίκη", "Τούμπα", 1926),
            ("Παναθηναϊκός", "ΠΑΝ", "Αθήνα", "Απόστολος Νικολαΐδης", 1908),
            ("Άρης", "ΑΡΗ", "Θεσσαλονίκη", "Κλεάνθης Βικελίδης", 1914),
            ("ΟΦΗ", "ΟΦΗ", "Ηράκλειο", "Θεόδωρος Βαρδινογιάννης", 1925),
            ("Αστέρας Τρίπολης", "ΑΣΤ", "Τρίπολη", "Θεόδωρος Κολοκοτρώνης", 1931),
            ("Λαμία", "ΛΑΜ", "Λαμία", "Αθανάσιος Διάκος", 1959),
            ("Βόλος", "ΒΟΛ", "Βόλος", "Παντελής Μαγουλάς", 1925),
            ("Παναιτωλικός", "ΠΑΝ", "Αγρίνιο", "Παναιτωλικό", 1926),
            ("Ατρόμητος", "ΑΤΡ", "Περιστέρι", "Νικηφόρος Λυτράς", 1923),
            ("Κέρκυρα", "ΚΕΡ", "Κέρκυρα", "Ευρωπαϊκό", 1994),
        ]
        for t in teams:
            TeamDAO.insert(*t)

        SeasonDAO.insert("2024-2025", "2024-09-01", "2025-05-31", is_active=1)

        refs = [
            ("Κυριάκος Παπαδόπουλος", "Ελλάδα", "UEFA"),
            ("Ανδρέας Τσόχος", "Ελλάδα", "FIFA"),
            ("Σωτήρης Βαρβέρης", "Ελλάδα", "Εθνική"),
        ]
        for r in refs:
            RefereeDAO.insert(*r)

    # --------------------------------------------------------
    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=COLORS["bg_header"],
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS["accent_blue"],
                                   corner_radius=0, height=80)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="⚽ SUPER LEAGUE",
                     font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
                     text_color="white").pack(expand=True)

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("🏠  Dashboard",   "dashboard"),
            ("📅  Αγώνες",      "matches"),
            ("🏆  Βαθμολογία",  "standings"),
            ("🏟️  Ομάδες",      "teams"),
            ("👤  Παίκτες",     "players"),
            ("🎽  Ρόστερ",      "rosters"),
            ("👔  Προπονητές",  "coaches"),
            ("🟨  Διαιτητές",   "referees"),
            ("📊  Στατιστικά",  "stats"),
            ("📥  Import",      "import_data"),
        ]
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                command=lambda k=key: self._show_frame(k),
                fg_color="transparent", hover_color=COLORS["accent_blue"],
                text_color=COLORS["text_primary"], anchor="w",
                font=ctk.CTkFont(family="Helvetica", size=13),
                height=44, corner_radius=0
            )
            btn.pack(fill="x", padx=0)
            self.nav_buttons[key] = btn

        # Main content area
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Build all frames
        self.frames = {}
        frame_classes = {
            "dashboard":   DashboardFrame,
            "matches":     MatchesFrame,
            "standings":   StandingsFrame,
            "teams":       TeamsFrame,
            "players":     PlayersFrame,
            "rosters":     RostersFrame,
            "coaches":     CoachesFrame,
            "referees":    RefereesFrame,
            "stats":       StatsFrame,
            "import_data": ImportFrame,
        }
        for key, cls in frame_classes.items():
            frame = cls(self.content, self)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[key] = frame

    def _show_frame(self, name):
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color=COLORS["accent_blue"] if key == name else "transparent")
        frame = self.frames[name]
        frame.lift()
        if hasattr(frame, "refresh"):
            frame.refresh()


# ============================================================
# DASHBOARD
# ============================================================
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        create_label(self, "📊 Dashboard", font_size=24, bold=True).pack(
            anchor="w", padx=30, pady=(25, 5))
        create_label(self, "Επισκόπηση Super League Greece", font_size=13,
                     color=COLORS["text_muted"]).pack(anchor="w", padx=30, pady=(0, 20))

        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=30)

        self.recent_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                          corner_radius=12)
        self.recent_frame.pack(fill="both", expand=True, padx=30, pady=20)

    def refresh(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        for w in self.recent_frame.winfo_children():
            w.destroy()

        with get_connection() as conn:
            n_teams   = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
            n_matches = conn.execute("SELECT COUNT(*) FROM matches WHERE status='played'").fetchone()[0]
            n_players = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
            season    = SeasonDAO.get_active()
            season_name = season['name'] if season else "—"

        cards = [
            ("🏟️", "Ομάδες", str(n_teams), COLORS["accent_blue"]),
            ("⚽", "Αγώνες", str(n_matches), COLORS["accent_green"]),
            ("👤", "Παίκτες", str(n_players), COLORS["accent_gold"]),
            ("📅", "Σεζόν", season_name, COLORS["accent_red"]),
        ]
        for icon, label, value, color in cards:
            card = ctk.CTkFrame(self.cards_frame, fg_color=COLORS["bg_card"],
                                corner_radius=12, width=200)
            card.pack(side="left", padx=8, pady=4)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=28)).pack(pady=(16, 2))
            ctk.CTkLabel(card, text=value,
                         font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
                         text_color=color).pack()
            ctk.CTkLabel(card, text=label,
                         font=ctk.CTkFont(family="Helvetica", size=12),
                         text_color=COLORS["text_muted"]).pack(pady=(0, 16))

        # Recent matches
        create_label(self.recent_frame, "  Τελευταίοι Αγώνες",
                     font_size=15, bold=True).pack(anchor="w", pady=(14, 4))

        with get_connection() as conn:
            recent = conn.execute("""
                SELECT ht.name as home, at.name as away,
                       m.home_score, m.away_score, m.match_date, m.status
                FROM matches m
                JOIN teams ht ON m.home_team_id=ht.id
                JOIN teams at ON m.away_team_id=at.id
                WHERE m.status='played'
                ORDER BY m.match_date DESC LIMIT 6
            """).fetchall()

        for m in recent:
            row = ctk.CTkFrame(self.recent_frame, fg_color=COLORS["bg_dark"],
                               corner_radius=8, height=40)
            row.pack(fill="x", padx=12, pady=3)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=f"{m['home']}  {m['home_score']} — {m['away_score']}  {m['away']}",
                         font=ctk.CTkFont(family="Helvetica", size=13),
                         text_color=COLORS["text_primary"]).pack(side="left", padx=14)
            ctk.CTkLabel(row, text=str(m['match_date'] or "")[:10],
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS["text_muted"]).pack(side="right", padx=14)


# ============================================================
# ΑΓΩΝΕΣ
# ============================================================
class MatchesFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "📅 Αγώνες", font_size=22, bold=True).pack(side="left")
        create_button(hdr, "+ Νέος Αγώνας", self._open_add_match,
                      color="green").pack(side="right")

        # Filter bar
        filter_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        filter_bar.pack(fill="x", padx=24, pady=10)
        create_label(filter_bar, "  Σεζόν:").pack(side="left", padx=(8, 4))
        self.season_combo = create_combobox(filter_bar, self._get_season_names(), width=160)
        self.season_combo.pack(side="left", padx=4)
        create_button(filter_bar, "🔍 Φίλτρο", self.refresh, width=100).pack(side="left", padx=8)
        create_button(filter_bar, "🗑️ Διαγραφή", self._delete_match,
                      color="red", width=110).pack(side="right", padx=8)
        create_button(filter_bar, "✏️ Αποτέλεσμα", self._update_score,
                      color="gold", width=130).pack(side="right", padx=4)

        # Table
        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SL.Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         rowheight=32, fieldbackground=COLORS["bg_card"],
                         font=("Helvetica", 12))
        style.configure("SL.Treeview.Heading",
                         background=COLORS["accent_blue"],
                         foreground="white", font=("Helvetica", 12, "bold"))
        style.map("SL.Treeview", background=[("selected", COLORS["highlight"])])

        cols = ("Αγ/κή", "Ημ/νία", "Γηπεδούχος", "Σκορ", "Φιλοξ.", "Διαιτητής", "Κατάσταση")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="SL.Treeview")
        widths = [60, 100, 180, 80, 180, 150, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def _get_season_names(self):
        season_names = SeasonDAO.get_all_names() or ["2024-2025"]
        return [s['name'] for s in seasons] if seasons else ["—"]

    def refresh(self):
        self.season_combo.configure(values=self._get_season_names())
        for item in self.tree.get_children():
            self.tree.delete(item)
        selected_season = self.season_combo.get()
        with get_connection() as conn:
            season = conn.execute("SELECT id FROM seasons WHERE name=?",
                                   (selected_season,)).fetchone()
            season_id = season['id'] if season else None

        matches = MatchDAO.get_all(season_id)
        for m in matches:
            score = f"{m['home_score']} — {m['away_score']}" if m['status'] == 'played' else "vs"
            self.tree.insert("", "end", iid=m['id'], values=(
                m['matchday_number'] or "—",
                str(m['match_date'] or "")[:10],
                m['home_team'],
                score,
                m['away_team'],
                f"{m['referee_name'] or '—'} ({m['referee_country'] or ''})",
                m['status']
            ))

    def _open_add_match(self):
        MatchDialog(self, self.app, on_save=self.refresh)

    def _update_score(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε αγώνα πρώτα!")
            return
        match_id = int(sel[0])
        ScoreDialog(self, match_id, on_save=self.refresh)

    def _delete_match(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Διαγραφή", "Να διαγραφεί ο αγώνας;"):
            MatchDAO.delete(int(sel[0]))
            self.refresh()


# --------------------------------------------------------
class MatchDialog(ctk.CTkToplevel):
    def __init__(self, parent, app, on_save=None):
        super().__init__(parent)
        self.app = app
        self.on_save = on_save
        self.title("Νέος Αγώνας")
        self.geometry("550x600")
        self.configure(fg_color=COLORS["bg_dark"])
        self._build()

    def _build(self):
        create_label(self, "➕ Καταχώρηση Αγώνα", font_size=18, bold=True).pack(pady=(20, 16))

        with get_connection() as conn:
            teams = [r['name'] for r in conn.execute("SELECT name FROM teams ORDER BY name").fetchall()]
            seasons = [r['name'] for r in conn.execute("SELECT name FROM seasons ORDER BY name DESC").fetchall()]
            refs = ["—"] + [r['name'] for r in conn.execute("SELECT name FROM referees ORDER BY name").fetchall()]
            matchdays = [str(i) for i in range(1, 35)]

        fields = [
            ("Σεζόν:", create_combobox(self, seasons, 360)),
            ("Αγωνιστική:", create_combobox(self, matchdays, 360)),
            ("Γηπεδούχος:", create_combobox(self, teams, 360)),
            ("Φιλοξενούμενος:", create_combobox(self, teams, 360)),
            ("Ημερομηνία (YYYY-MM-DD):", create_entry(self, "2025-01-15", 360)),
            ("Γήπεδο:", create_entry(self, "Γήπεδο...", 360)),
            ("Γκολ Γηπεδούχου:", create_entry(self, "0", 360)),
            ("Γκολ Φιλοξ.:", create_entry(self, "0", 360)),
            ("Διαιτητής:", create_combobox(self, refs, 360)),
            ("Κατάσταση:", create_combobox(self, ["scheduled", "played", "postponed"], 360)),
        ]
        self.widgets = {}
        for label, widget in fields:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=4)
            create_label(row, label, font_size=12, color=COLORS["text_muted"]).pack(anchor="w")
            widget.pack(fill="x")
            self.widgets[label] = widget

        create_button(self, "💾 Αποθήκευση", self._save, color="green", width=200).pack(pady=20)

    def _save(self):
        w = self.widgets
        with get_connection() as conn:
            season = conn.execute("SELECT id FROM seasons WHERE name=?",
                                   (w["Σεζόν:"].get(),)).fetchone()
            home = conn.execute("SELECT id FROM teams WHERE name=?",
                                 (w["Γηπεδούχος:"].get(),)).fetchone()
            away = conn.execute("SELECT id FROM teams WHERE name=?",
                                 (w["Φιλοξενούμενος:"].get(),)).fetchone()
            ref_name = w["Διαιτητής:"].get()
            ref = conn.execute("SELECT id FROM referees WHERE name=?",
                                (ref_name,)).fetchone() if ref_name != "—" else None
            md_number = int(w["Αγωνιστική:"].get() or 1)
            md = conn.execute("SELECT id FROM matchdays WHERE season_id=? AND number=?",
                               (season['id'], md_number)).fetchone()
            if not md:
                conn.execute("INSERT INTO matchdays (season_id, number) VALUES (?,?)",
                             (season['id'], md_number))
                md = conn.execute("SELECT id FROM matchdays WHERE season_id=? AND number=?",
                                   (season['id'], md_number)).fetchone()

        try:
            MatchDAO.insert(
                season_id=season['id'],
                matchday_id=md['id'],
                home_team_id=home['id'],
                away_team_id=away['id'],
                match_date=w["Ημερομηνία (YYYY-MM-DD):"].get(),
                stadium=w["Γήπεδο:"].get(),
                home_score=int(w["Γκολ Γηπεδούχου:"].get() or 0),
                away_score=int(w["Γκολ Φιλοξ.:"].get() or 0),
                status=w["Κατάσταση:"].get(),
                referee_id=ref['id'] if ref else None,
                attendance=None,
                notes=None
            )
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))


class ScoreDialog(ctk.CTkToplevel):
    def __init__(self, parent, match_id, on_save=None):
        super().__init__(parent)
        self.match_id = match_id
        self.on_save = on_save
        self.title("Ενημέρωση Αποτελέσματος")
        self.geometry("340x280")
        self.configure(fg_color=COLORS["bg_dark"])
        self._build()

    def _build(self):
        create_label(self, "⚽ Αποτέλεσμα", font_size=18, bold=True).pack(pady=20)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack()
        create_label(row, "Γηπεδούχος:", font_size=12).pack(side="left", padx=4)
        self.home_entry = create_entry(row, "0", 60)
        self.home_entry.pack(side="left", padx=4)
        create_label(row, "—", font_size=14).pack(side="left", padx=4)
        self.away_entry = create_entry(row, "0", 60)
        self.away_entry.pack(side="left", padx=4)
        create_label(row, "Φιλοξ.:", font_size=12).pack(side="left", padx=4)

        create_button(self, "✅ Αποθήκευση", self._save, color="green", width=160).pack(pady=24)

    def _save(self):
        try:
            MatchDAO.update_score(self.match_id,
                                   int(self.home_entry.get()),
                                   int(self.away_entry.get()),
                                   "played")
            # Ενημέρωση βαθμολογίας
            with get_connection() as conn:
                m = conn.execute("SELECT season_id FROM matches WHERE id=?",
                                  (self.match_id,)).fetchone()
            StandingsDAO.recalculate(m['season_id'])
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))


# ============================================================
# ΒΑΘΜΟΛΟΓΙΑ
# ============================================================
class StandingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "🏆 Βαθμολογία", font_size=22, bold=True).pack(side="left")

        self.season_combo = create_combobox(hdr, ["—"], width=160)
        self.season_combo.pack(side="right", padx=4)
        create_label(hdr, "Σεζόν:", color=COLORS["text_muted"]).pack(side="right")
        create_button(hdr, "🔄 Ανανέωση", self.refresh, color="blue").pack(side="right", padx=8)

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=14)

        style = ttk.Style()
        style.configure("Stand.Treeview",
                         background=COLORS["bg_card"], foreground=COLORS["text_primary"],
                         rowheight=34, fieldbackground=COLORS["bg_card"],
                         font=("Helvetica", 13))
        style.configure("Stand.Treeview.Heading",
                         background=COLORS["accent_gold"],
                         foreground="#1A1A1A", font=("Helvetica", 12, "bold"))
        style.map("Stand.Treeview", background=[("selected", COLORS["highlight"])])

        cols = ("#", "Ομάδα", "ΑΓ", "Ν", "Ι", "Η", "ΓΥ", "ΓΚ", "ΔΓ", "ΒΑΘ")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Stand.Treeview")
        widths = [40, 220, 50, 50, 50, 50, 60, 60, 60, 70]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        seasons = SeasonDAO.get_all()
        names = [s['name'] for s in seasons]
        self.season_combo.configure(values=names or ["—"])

        sel = self.season_combo.get()
        if not sel or sel == "—":
            active = SeasonDAO.get_active()
            if active:
                sel = active['name']
                self.season_combo.set(sel)

        with get_connection() as conn:
            season = conn.execute("SELECT id FROM seasons WHERE name=?", (sel,)).fetchone()
        if not season:
            return

        StandingsDAO.recalculate(season['id'])

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = StandingsDAO.get(season['id'])
        for r in rows:
            tag = "top3" if r['position'] <= 3 else "bottom3" if r['position'] >= len(rows) - 2 else ""
            self.tree.insert("", "end", tags=(tag,), values=(
                r['position'], r['team_name'],
                r['played'], r['won'], r['drawn'], r['lost'],
                r['goals_for'], r['goals_against'], r['goal_diff'],
                r['points']
            ))
        self.tree.tag_configure("top3", background="#14532D")
        self.tree.tag_configure("bottom3", background="#7F1D1D")


# ============================================================
# ΟΜΑΔΕΣ
# ============================================================
class TeamsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "🏟️ Ομάδες", font_size=22, bold=True).pack(side="left")
        create_button(hdr, "+ Νέα Ομάδα", self._add, color="green").pack(side="right")

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=14)

        style = ttk.Style()
        style.configure("T.Treeview", background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"], rowheight=32,
                         fieldbackground=COLORS["bg_card"], font=("Helvetica", 12))
        style.configure("T.Treeview.Heading", background=COLORS["accent_blue"],
                         foreground="white", font=("Helvetica", 12, "bold"))

        cols = ("Όνομα", "Συντ.", "Πόλη", "Γήπεδο", "Ίδρυση")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="T.Treeview")
        for col, w in zip(cols, [220, 70, 130, 200, 80]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

        create_button(self, "🗑️ Διαγραφή", self._delete, color="red", width=120).pack(pady=10)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in TeamDAO.get_all():
            self.tree.insert("", "end", iid=t['id'], values=(
                t['name'], t['short_name'], t['city'] or "", t['stadium'] or "", t['founded'] or ""))

    def _add(self):
        SimpleFormDialog(self, "Νέα Ομάδα",
            [("Όνομα", ""), ("Συντομογραφία", ""), ("Πόλη", ""), ("Γήπεδο", ""), ("Ίδρυση", "")],
            lambda v: (TeamDAO.insert(v[0], v[1], v[2], v[3], v[4] or None), self.refresh()))

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Διαγραφή", "Να διαγραφεί η ομάδα;"):
            TeamDAO.delete(int(sel[0]))
            self.refresh()


# ============================================================
# ΠΑΙΚΤΕΣ
# ============================================================
class PlayersFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "👤 Παίκτες", font_size=22, bold=True).pack(side="left")
        create_button(hdr, "+ Νέος Παίκτης", self._add, color="green").pack(side="right")

        search_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        search_frame.pack(fill="x", padx=24, pady=8)
        create_label(search_frame, "  🔍 Αναζήτηση:").pack(side="left", padx=4)
        self.search_entry = create_entry(search_frame, "Όνομα παίκτη...", 300)
        self.search_entry.pack(side="left", padx=4)
        create_button(search_frame, "Αναζήτηση", self._search, width=110).pack(side="left", padx=4)

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        style = ttk.Style()
        style.configure("P.Treeview", background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"], rowheight=30,
                         fieldbackground=COLORS["bg_card"], font=("Helvetica", 12))
        style.configure("P.Treeview.Heading", background=COLORS["accent_blue"],
                         foreground="white", font=("Helvetica", 12, "bold"))

        cols = ("Ονοματεπώνυμο", "Θέση", "Εθνικότητα", "Ημ. Γέννησης", "Ύψος", "Βάρος", "Πόδι")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="P.Treeview")
        widths = [220, 80, 130, 110, 70, 70, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in PlayerDAO.get_all():
            self.tree.insert("", "end", iid=p['id'], values=(
                p['full_name'], p['position'] or "—", p['nationality'] or "—",
                str(p['date_of_birth'] or "—"), p['height_cm'] or "—",
                p['weight_kg'] or "—", p['foot'] or "—"
            ))

    def _search(self):
        q = self.search_entry.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in PlayerDAO.search(q):
            self.tree.insert("", "end", iid=p['id'], values=(
                p['full_name'], p['position'] or "—", p['nationality'] or "—",
                str(p['date_of_birth'] or "—"), p['height_cm'] or "—",
                p['weight_kg'] or "—", p['foot'] or "—"
            ))

    def _add(self):
        PlayerDialog(self, on_save=self.refresh)


class PlayerDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Νέος Παίκτης")
        self.geometry("480x580")
        self.configure(fg_color=COLORS["bg_dark"])
        self._build()

    def _build(self):
        create_label(self, "👤 Νέος Παίκτης", font_size=18, bold=True).pack(pady=(20, 14))
        self.fields = {}
        combos = {
            "Θέση:": (["GK", "DEF", "MID", "FWD"], 360),
            "Πόδι:": (["Δεξί", "Αριστερό", "Αμφίδεξιο"], 360),
        }
        entries = [
            ("Ονοματεπώνυμο:", ""), ("Εθνικότητα:", ""), ("Ημ. Γέννησης (YYYY-MM-DD):", ""),
            ("Ύψος (cm):", ""), ("Βάρος (kg):", ""), ("Νούμερο Φανέλας:", ""),
        ]
        for label, val in entries:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=4)
            create_label(row, label, font_size=12, color=COLORS["text_muted"]).pack(anchor="w")
            w = create_entry(row, val, 360)
            w.pack(fill="x")
            self.fields[label] = w

        for label, (vals, width) in combos.items():
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=4)
            create_label(row, label, font_size=12, color=COLORS["text_muted"]).pack(anchor="w")
            w = create_combobox(row, vals, width)
            w.pack(fill="x")
            self.fields[label] = w

        create_button(self, "💾 Αποθήκευση", self._save, color="green", width=180).pack(pady=20)

    def _save(self):
        try:
            pid = PlayerDAO.insert(
                full_name=self.fields["Ονοματεπώνυμο:"].get(),
                nationality=self.fields["Εθνικότητα:"].get(),
                dob=self.fields["Ημ. Γέννησης (YYYY-MM-DD):"].get() or None,
                position=self.fields["Θέση:"].get(),
                jersey_number=int(self.fields["Νούμερο Φανέλας:"].get() or 0),
                foot=self.fields["Πόδι:"].get(),
                height=int(self.fields["Ύψος (cm):"].get() or 0),
                weight=int(self.fields["Βάρος (kg):"].get() or 0),
            )
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))


# ============================================================
# ΡΟΣΤΕΡ
# ============================================================
class RostersFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "🎽 Ρόστερ Ομάδας", font_size=22, bold=True).pack(side="left")
        create_button(hdr, "+ Προσθήκη Παίκτη", self._add, color="green").pack(side="right")

        filter_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        filter_frame.pack(fill="x", padx=24, pady=8)
        create_label(filter_frame, "  Ομάδα:").pack(side="left")
        self.team_combo = create_combobox(filter_frame, ["—"], width=200)
        self.team_combo.pack(side="left", padx=6)
        create_label(filter_frame, "Σεζόν:").pack(side="left")
        self.season_combo = create_combobox(filter_frame, ["—"], width=140)
        self.season_combo.pack(side="left", padx=6)
        create_button(filter_frame, "🔍 Εμφάνιση", self.refresh, width=120).pack(side="left", padx=8)

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        style = ttk.Style()
        style.configure("R.Treeview", background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"], rowheight=30,
                         fieldbackground=COLORS["bg_card"], font=("Helvetica", 12))
        style.configure("R.Treeview.Heading", background=COLORS["accent_green"],
                         foreground="white", font=("Helvetica", 12, "bold"))

        cols = ("#", "Παίκτης", "Θέση", "Εθνικότητα", "Δανεικός")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="R.Treeview")
        widths = [50, 220, 80, 130, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        with get_connection() as conn:
            teams = conn.execute("SELECT id, name FROM teams ORDER BY name").fetchall()
            seasons = conn.execute("SELECT id, name FROM seasons ORDER BY name DESC").fetchall()

        team_names = [t['name'] for t in teams]
        season_names = [s['name'] for s in seasons]
        self.team_combo.configure(values=team_names or ["—"])
        self.season_combo.configure(values=season_names or ["—"])

        sel_team = self.team_combo.get()
        sel_season = self.season_combo.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        with get_connection() as conn:
            team = conn.execute("SELECT id FROM teams WHERE name=?", (sel_team,)).fetchone()
            season = conn.execute("SELECT id FROM seasons WHERE name=?", (sel_season,)).fetchone()
        if not team or not season:
            return

        players = PlayerDAO.get_by_team_season(team['id'], season['id'])
        for p in players:
            self.tree.insert("", "end", values=(
                p['roster_number'] or "—",
                p['full_name'],
                p['position'] or "—",
                p['nationality'] or "—",
                "Ναι" if p['loan'] else "Όχι"
            ))

    def _add(self):
        RosterAddDialog(self, on_save=self.refresh)


class RosterAddDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Προσθήκη στο Ρόστερ")
        self.geometry("420x380")
        self.configure(fg_color=COLORS["bg_dark"])
        self._build()

    def _build(self):
        create_label(self, "🎽 Προσθήκη Παίκτη στο Ρόστερ", font_size=16, bold=True).pack(pady=(20, 14))

        with get_connection() as conn:
            players = [r['full_name'] for r in conn.execute("SELECT full_name FROM players ORDER BY full_name")]
            teams = [r['name'] for r in conn.execute("SELECT name FROM teams ORDER BY name")]
            seasons = [r['name'] for r in conn.execute("SELECT name FROM seasons ORDER BY name DESC")]

        self.fields = {}
        for label, vals in [("Ομάδα:", teams), ("Σεζόν:", seasons), ("Παίκτης:", players)]:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=6)
            create_label(row, label, font_size=12, color=COLORS["text_muted"]).pack(anchor="w")
            w = create_combobox(row, vals, 360)
            w.pack(fill="x")
            self.fields[label] = w

        for label in ["Νούμερο Φανέλας:", "Ημ. Ένταξης (YYYY-MM-DD):"]:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=30, pady=4)
            create_label(row, label, font_size=12, color=COLORS["text_muted"]).pack(anchor="w")
            w = create_entry(row, "", 360)
            w.pack(fill="x")
            self.fields[label] = w

        self.loan_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self, text="Δανεικός παίκτης", variable=self.loan_var,
                         text_color=COLORS["text_primary"]).pack(pady=6)
        create_button(self, "💾 Αποθήκευση", self._save, color="green", width=160).pack(pady=16)

    def _save(self):
        with get_connection() as conn:
            team = conn.execute("SELECT id FROM teams WHERE name=?",
                                 (self.fields["Ομάδα:"].get(),)).fetchone()
            season = conn.execute("SELECT id FROM seasons WHERE name=?",
                                   (self.fields["Σεζόν:"].get(),)).fetchone()
            player = conn.execute("SELECT id FROM players WHERE full_name=?",
                                   (self.fields["Παίκτης:"].get(),)).fetchone()
            if not (team and season and player):
                messagebox.showerror("Σφάλμα", "Επιλέξτε όλα τα πεδία!")
                return
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO rosters 
                    (team_id, season_id, player_id, jersey_number, date_joined, loan)
                    VALUES (?,?,?,?,?,?)
                """, (team['id'], season['id'], player['id'],
                      int(self.fields["Νούμερο Φανέλας:"].get() or 0),
                      self.fields["Ημ. Ένταξης (YYYY-MM-DD):"].get() or None,
                      1 if self.loan_var.get() else 0))
                if self.on_save:
                    self.on_save()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Σφάλμα", str(e))


# ============================================================
# ΠΡΟΠΟΝΗΤΕΣ
# ============================================================
class CoachesFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "👔 Προπονητές", font_size=22, bold=True).pack(side="left")
        create_button(hdr, "+ Νέος Προπονητής", self._add, color="green").pack(side="right")

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=14)

        style = ttk.Style()
        style.configure("C.Treeview", background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"], rowheight=30,
                         fieldbackground=COLORS["bg_card"], font=("Helvetica", 12))
        style.configure("C.Treeview.Heading", background="#7C3AED",
                         foreground="white", font=("Helvetica", 12, "bold"))

        cols = ("Ονοματεπώνυμο", "Εθνικότητα", "Ημ. Γέννησης", "Άδεια")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="C.Treeview")
        for col, w in zip(cols, [220, 130, 110, 120]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Assign coach
        assign_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        assign_frame.pack(fill="x", padx=24, pady=(0, 14))
        create_label(assign_frame, "  Ανάθεση σε Ομάδα:", bold=True).pack(side="left", padx=8)
        with get_connection() as conn:
            teams = [r['name'] for r in conn.execute("SELECT name FROM teams ORDER BY name")]
            seasons = [r['name'] for r in conn.execute("SELECT name FROM seasons ORDER BY name DESC")]
        self.assign_team = create_combobox(assign_frame, teams, 180)
        self.assign_team.pack(side="left", padx=4)
        self.assign_season = create_combobox(assign_frame, seasons, 140)
        self.assign_season.pack(side="left", padx=4)
        create_button(assign_frame, "Ανάθεση", self._assign, color="gold", width=100).pack(side="left", padx=6)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for c in CoachDAO.get_all():
            self.tree.insert("", "end", iid=c['id'], values=(
                c['full_name'], c['nationality'] or "—",
                str(c['date_of_birth'] or "—"), c['license_level'] or "—"
            ))

    def _add(self):
        SimpleFormDialog(self, "Νέος Προπονητής",
            [("Ονοματεπώνυμο", ""), ("Εθνικότητα", ""), ("Ημ. Γέννησης (YYYY-MM-DD)", ""),
             ("Επίπεδο Άδειας", "UEFA Pro")],
            lambda v: (CoachDAO.insert(v[0], v[1], v[2] or None, v[3]), self.refresh()))

    def _assign(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Προσοχή", "Επιλέξτε προπονητή!")
            return
        coach_id = int(sel[0])
        with get_connection() as conn:
            team = conn.execute("SELECT id FROM teams WHERE name=?",
                                 (self.assign_team.get(),)).fetchone()
            season = conn.execute("SELECT id FROM seasons WHERE name=?",
                                   (self.assign_season.get(),)).fetchone()
        if team and season:
            from datetime import date
            CoachDAO.assign_to_team(team['id'], season['id'], coach_id, str(date.today()))
            messagebox.showinfo("Επιτυχία", "Ο προπονητής ανατέθηκε!")


# ============================================================
# ΔΙΑΙΤΗΤΕΣ
# ============================================================
class RefereesFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        create_label(hdr, "🟨 Διαιτητές", font_size=22, bold=True).pack(side="left")
        create_button(hdr, "+ Νέος Διαιτητής", self._add, color="gold").pack(side="right")

        table_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=24, pady=14)

        style = ttk.Style()
        style.configure("Ref.Treeview", background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"], rowheight=30,
                         fieldbackground=COLORS["bg_card"], font=("Helvetica", 12))
        style.configure("Ref.Treeview.Heading", background=COLORS["accent_gold"],
                         foreground="#1A1A1A", font=("Helvetica", 12, "bold"))

        cols = ("Ονοματεπώνυμο", "Χώρα", "Επίπεδο Σήματος")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Ref.Treeview")
        for col, w in zip(cols, [250, 150, 150]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in RefereeDAO.get_all():
            self.tree.insert("", "end", iid=r['id'], values=(
                r['name'], r['country'] or "Ελλάδα", r['badge_level'] or "—"))

    def _add(self):
        SimpleFormDialog(self, "Νέος Διαιτητής",
            [("Ονοματεπώνυμο", ""), ("Χώρα", "Ελλάδα"), ("Σήμα", "Εθνική")],
            lambda v: (RefereeDAO.insert(v[0], v[1], v[2]), self.refresh()))


# ============================================================
# ΣΤΑΤΙΣΤΙΚΑ
# ============================================================
class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        create_label(self, "📊 Στατιστικά", font_size=22, bold=True).pack(
            anchor="w", padx=24, pady=(20, 4))
        create_label(self, "Επιλέξτε σεζόν για αναλυτικά στατιστικά",
                     color=COLORS["text_muted"]).pack(anchor="w", padx=24)

        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8)
        hdr.pack(fill="x", padx=24, pady=10)
        self.season_combo = create_combobox(hdr, ["—"], width=160)
        self.season_combo.pack(side="left", padx=8, pady=8)
        create_button(hdr, "📈 Φόρτωση", self.refresh, color="blue").pack(side="left", padx=4)

        self.text_box = ctk.CTkTextbox(self, fg_color=COLORS["bg_card"],
                                        text_color=COLORS["text_primary"],
                                        font=ctk.CTkFont(family="Courier", size=13),
                                        corner_radius=10)
        self.text_box.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        season_names = SeasonDAO.get_all_names() or ["2024-2025"]
        self.season_combo.configure(values=[s['name'] for s in seasons] or ["—"])
        sel = self.season_combo.get()
        with get_connection() as conn:
            season = conn.execute("SELECT id FROM seasons WHERE name=?", (sel,)).fetchone()
        if not season:
            return
        sid = season['id']
        with get_connection() as conn:
            top_scorers = conn.execute("""
                SELECT p.full_name, t.name as team, SUM(pms.goals) as goals
                FROM player_match_stats pms
                JOIN players p ON pms.player_id=p.id
                JOIN teams t ON pms.team_id=t.id
                JOIN matches m ON pms.match_id=m.id
                WHERE m.season_id=?
                GROUP BY p.id ORDER BY goals DESC LIMIT 10
            """, (sid,)).fetchall()

            top_assists = conn.execute("""
                SELECT p.full_name, t.name as team, SUM(pms.assists) as assists
                FROM player_match_stats pms
                JOIN players p ON pms.player_id=p.id
                JOIN teams t ON pms.team_id=t.id
                JOIN matches m ON pms.match_id=m.id
                WHERE m.season_id=?
                GROUP BY p.id ORDER BY assists DESC LIMIT 10
            """, (sid,)).fetchall()

            cards = conn.execute("""
                SELECT p.full_name, t.name as team,
                       SUM(pms.yellow_cards) as yellows,
                       SUM(pms.red_cards) as reds
                FROM player_match_stats pms
                JOIN players p ON pms.player_id=p.id
                JOIN teams t ON pms.team_id=t.id
                JOIN matches m ON pms.match_id=m.id
                WHERE m.season_id=?
                GROUP BY p.id 
                HAVING yellows > 0 OR reds > 0
                ORDER BY reds DESC, yellows DESC LIMIT 10
            """, (sid,)).fetchall()

            team_stats = conn.execute("""
                SELECT t.name,
                    SUM(CASE WHEN m.home_team_id=t.id THEN m.home_score
                             ELSE m.away_score END) as gf,
                    SUM(CASE WHEN m.home_team_id=t.id THEN m.away_score
                             ELSE m.home_score END) as ga
                FROM matches m
                JOIN teams t ON (t.id=m.home_team_id OR t.id=m.away_team_id)
                WHERE m.season_id=? AND m.status='played'
                GROUP BY t.id ORDER BY gf DESC LIMIT 8
            """, (sid,)).fetchall()

        output = []
        output.append(f"═══ ΣΤΑΤΙΣΤΙΚΑ ΣΕΖΟΝ {sel} ═══\n")
        output.append("🥇 ΚΟΡΥΦΑIΟΙ ΣΚΟΡΕΡ:")
        for i, r in enumerate(top_scorers, 1):
            output.append(f"  {i:2}. {r['full_name']:<25} {r['team']:<20} ⚽ {r['goals']}")
        output.append("\n🎯 ΚΟΡΥΦΑIΟΙ ΑΣΙΣΤ:")
        for i, r in enumerate(top_assists, 1):
            output.append(f"  {i:2}. {r['full_name']:<25} {r['team']:<20} 🅰️  {r['assists']}")
        output.append("\n🟨 ΚΑΡΤΕΣ:")
        for i, r in enumerate(cards, 1):
            output.append(f"  {i:2}. {r['full_name']:<25} 🟨 {r['yellows']}  🟥 {r['reds']}")
        output.append("\n⚽ ΓΚΟΛ ΑΝΑ ΟΜΑΔΑ:")
        for r in team_stats:
            output.append(f"  {r['name']:<25} ΓΥ:{r['gf'] or 0}  ΓΚ:{r['ga'] or 0}  ΔΓ:{(r['gf'] or 0)-(r['ga'] or 0)}")

        if not top_scorers and not cards:
            output.append("\n  (Δεν υπάρχουν ακόμη στατιστικά παικτών)")
            output.append("  Προσθέστε στατιστικά από τη διαχείριση αγώνων.")

        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", "\n".join(output))


# ============================================================
# IMPORT
# ============================================================
class ImportFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        create_label(self, "📥 Εισαγωγή Δεδομένων", font_size=22, bold=True).pack(
            anchor="w", padx=24, pady=(20, 4))
        create_label(self, "Import αγώνων από CSV ή JSON", color=COLORS["text_muted"]).pack(
            anchor="w", padx=24, pady=(0, 16))

        # CSV import
        csv_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        csv_frame.pack(fill="x", padx=24, pady=8)
        create_label(csv_frame, "  📄 Import Αγώνων από CSV", font_size=15, bold=True).pack(
            anchor="w", pady=(14, 4))
        create_label(csv_frame, "  Απαιτούμενες στήλες: home_team, away_team, date, home_score, away_score, status",
                     font_size=11, color=COLORS["text_muted"]).pack(anchor="w")

        row = ctk.CTkFrame(csv_frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=10)
        self.season_combo = create_combobox(row, self._get_seasons(), width=160)
        self.season_combo.pack(side="left", padx=4)
        create_button(row, "📂 Επιλογή CSV", self._pick_csv, color="blue", width=140).pack(side="left", padx=4)
        create_button(row, "⬇️ Δείγμα CSV", self._export_sample, color="gold", width=130).pack(side="left", padx=4)

        self.log_box = ctk.CTkTextbox(self, fg_color=COLORS["bg_card"],
                                       text_color=COLORS["text_primary"],
                                       font=ctk.CTkFont(family="Courier", size=12),
                                       corner_radius=10, height=300)
        self.log_box.pack(fill="both", expand=True, padx=24, pady=(8, 20))

    def _get_seasons(self):
        return [s['name'] for s in SeasonDAO.get_all()] or ["—"]

    def refresh(self):
        self.season_combo.configure(values=self._get_seasons())

    def _pick_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        sel = self.season_combo.get()
        with get_connection() as conn:
            season = conn.execute("SELECT id FROM seasons WHERE name=?", (sel,)).fetchone()
        if not season:
            messagebox.showerror("Σφάλμα", "Επιλέξτε έγκυρη σεζόν!")
            return
        results = ImportDAO.import_csv_matches(path, season['id'])
        self.log_box.delete("1.0", "end")
        self.log_box.insert("1.0", "\n".join(results))
        StandingsDAO.recalculate(season['id'])

    def _export_sample(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV", "*.csv")],
                                             initialfile="sample_matches.csv")
        if not path:
            return
        import csv
        rows = [
            {"home_team": "Ολυμπιακός", "away_team": "ΑΕΚ", "date": "2025-01-10",
             "home_score": "2", "away_score": "1", "status": "played"},
            {"home_team": "ΠΑΟΚ", "away_team": "Παναθηναϊκός", "date": "2025-01-11",
             "home_score": "0", "away_score": "0", "status": "played"},
        ]
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        messagebox.showinfo("Επιτυχία", f"Δείγμα CSV αποθηκεύτηκε:\n{path}")


# ============================================================
# GENERIC DIALOG
# ============================================================
class SimpleFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, fields, on_save):
        super().__init__(parent)
        self.on_save_cb = on_save
        self.title(title)
        self.geometry(f"420x{120 + len(fields)*70}")
        self.configure(fg_color=COLORS["bg_dark"])
        create_label(self, title, font_size=16, bold=True).pack(pady=(16, 10))
        self.entries = []
        for label, default in fields:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=4)
            create_label(row, label, font_size=12, color=COLORS["text_muted"]).pack(anchor="w")
            e = create_entry(row, default, 360)
            e.pack(fill="x")
            self.entries.append(e)
        create_button(self, "💾 Αποθήκευση", self._save, color="green", width=160).pack(pady=16)

    def _save(self):
        vals = [e.get() for e in self.entries]
        try:
            self.on_save_cb(vals)
            self.destroy()
        except Exception as ex:
            messagebox.showerror("Σφάλμα", str(ex))


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    app = SuperLeagueApp()
    app.mainloop()
