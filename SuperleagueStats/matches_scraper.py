"""
================================================================
 Super League Greece — Matches Scraper
 Βασισμένο στον αρχικό κώδικα + MariaDB αποθήκευση

 Χρήση:
   python matches_scraper.py              # Scrape + MariaDB + CSV
   python matches_scraper.py --csv-only  # Μόνο CSV
   python matches_scraper.py --dry-run   # Εμφάνιση χωρίς αποθήκευση

 Απαιτήσεις:
   pip install pandas requests lxml html5lib pymysql
================================================================
"""

import os
import re
import sys
import csv
import json
import time
import argparse
import datetime
from pathlib import Path
from io import StringIO

import requests
import pandas as pd

# ================================================================
# ΡΥΘΜΙΣΕΙΣ (από τον αρχικό κώδικα + βελτιωμένο User-Agent)
# ================================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.transfermarkt.com/",
}

COMPETITIONS = {
    "regular": "https://www.transfermarkt.com/super-league-1/gesamtspielplan/wettbewerb/GR1/saison_id/2025",
    "playoffs": "https://www.transfermarkt.com/super-league-1-play-off/startseite/wettbewerb/POGR/saison_id/2025",
    "fifth_place_playoff": "https://www.transfermarkt.com/super-league-5th-place-play-off/startseite/wettbewerb/GRPL/saison_id/2025",
    "playout": "https://www.transfermarkt.com/super-league-play-out/gesamtspielplan/wettbewerb/S1PO/saison_id/2025",
}

SEASON_NAME = "2025-2026"

OUTPUT_DIR = Path(__file__).parent / "scraper_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Αντιστοίχιση ονομάτων Transfermarkt → βάση δεδομένων
TEAM_NAME_MAP = {
    # Olympiacos
    "Olympiacos":              "Ολυμπιακός",
    "Olympiakos":              "Ολυμπιακός",
    "Olympiacos Piraeus":      "Ολυμπιακός",
    "Olympiakos Piraeus":      "Ολυμπιακός",
    # AEK
    "AEK Athens":              "ΑΕΚ",
    "AEK Athen":               "ΑΕΚ",
    "AEK":                     "ΑΕΚ",
    # PAOK
    "PAOK":                    "ΠΑΟΚ",
    "PAOK Thessaloniki":        "ΠΑΟΚ",
    # Panathinaikos
    "Panathinaikos":           "Παναθηναϊκός",
    "Panathinaikos Athens":    "Παναθηναϊκός",
    "Panathinaikos Athen":     "Παναθηναϊκός",
    # Aris
    "Aris":                    "Άρης",
    "Aris Thessaloniki":       "Άρης",
    "Aris Saloniki":           "Άρης",
    "Aris FC":                 "Άρης",
    # OFI
    "OFI Crete":               "ΟΦΗ",
    "OFI":                     "ΟΦΗ",
    "OFI Kreta":               "ΟΦΗ",
    # Asteras Tripolis
    "Asteras Tripolis":        "Αστέρας Τρίπολης",
    "Asteras Aktor":           "Αστέρας Τρίπολης",
    "Asteras":                 "Αστέρας Τρίπολης",
    # Lamia
    "Lamia":                   "Λαμία",
    "PAS Lamia":               "Λαμία",
    "PAS Lamia 1964":          "Λαμία",
    # Volos
    "Volos":                   "Βόλος",
    "Volos NFC":               "Βόλος",
    "Volos FC":                "Βόλος",
    # Panetolikos
    "Panetolikos":             "Παναιτωλικός",
    "Panetolikos GFS":         "Παναιτωλικός",
    # Atromitos
    "Atromitos":               "Ατρόμητος",
    "Atromitos Athens":        "Ατρόμητος",
    "Atromitos Athen":         "Ατρόμητος",
    # Kerkyra
    "Kerkyra":                 "Κέρκυρα",
    "AOK Kerkyra":             "Κέρκυρα",
    "Kerkyra FC":              "Κέρκυρα",
}


# ================================================================
# CONFIG — db_config.json
# ================================================================
def load_db_config():
    """Ψάχνει το db_config.json σε πολλές τοποθεσίες."""
    search_paths = [
        Path(__file__).parent / "db_config.json",
        Path("C:/Program Files/SuperLeagueGreece/db_config.json"),
        Path(os.environ.get("APPDATA", "")) / "SuperLeagueGreece/db_config.json",
    ]
    for path in search_paths:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                cfg = json.load(f)
            print(f"  [CONFIG] Φορτώθηκε από: {path}")
            return cfg

    # Default αν δεν βρεθεί
    print("  [CONFIG] db_config.json δεν βρέθηκε — χρήση default τιμών")
    return {
        "engine": "mariadb",
        "host": "localhost",
        "port": 3306,
        "database": "superleague_greece",
        "user": "superleague",
        "password": "nano1545"
    }


def get_connection(config):
    """Επιστρέφει MariaDB σύνδεση."""
    import pymysql
    return pymysql.connect(
        host=config.get("host", "localhost"),
        port=config.get("port", 3306),
        user=config.get("user", "superleague"),
        password=config.get("password", "nano1545"),
        database=config.get("database", "superleague_greece"),
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor
    )


# ================================================================
# SCRAPING (αρχικός κώδικας + βελτιώσεις)
# ================================================================
def clean_columns(df):
    df.columns = [
        " ".join(map(str, col)).strip() if isinstance(col, tuple)
        else str(col).strip()
        for col in df.columns
    ]
    return df


def scrape_url(name, url):
    print(f"  Scraping {name}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return pd.DataFrame()

    try:
        tables = pd.read_html(StringIO(r.text))
    except Exception as e:
        print(f"  [ERROR] pandas: {e}")
        return pd.DataFrame()

    matches = []
    for i, table in enumerate(tables):
        table = clean_columns(table)
        cols = " ".join(table.columns).lower()
        if "result" not in cols or "home" not in cols or "away" not in cols:
            continue
        table["competition_part"] = name
        table["source_url"]       = url
        table["table_index"]      = i
        matches.append(table)

    if not matches:
        print(f"  [WARN] Δεν βρέθηκε πίνακας για {name}")
        return pd.DataFrame()

    result = pd.concat(matches, ignore_index=True)
    print(f"  ✅ {name}: {len(result)} γραμμές")
    return result


# ================================================================
# ΒΟΗΘΗΤΙΚΕΣ — parsing
# ================================================================
def parse_score(result_str):
    """'2:1' → (2, 1), '-' → (None, None)"""
    if not result_str or str(result_str).strip() in ["-", "nan", "", "?"]:
        return None, None
    m = re.search(r"(\d+)\s*[:\-]\s*(\d+)", str(result_str))
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def parse_date(date_str):
    """Διάφορα formats → YYYY-MM-DD"""
    if not date_str or str(date_str).strip() in ["nan", "", "-"]:
        return None
    for fmt in ["%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d", "%m/%d/%Y"]:
        try:
            return datetime.datetime.strptime(str(date_str).strip(), fmt).strftime("%Y-%m-%d")
        except:
            continue
    return None


def map_team_name(name):
    """Μετατρέπει Transfermarkt όνομα → όνομα βάσης."""
    if not name or str(name).strip() in ["nan", ""]:
        return None
    name = str(name).strip()
    return TEAM_NAME_MAP.get(name, name)


def detect_columns(df):
    """
    Εντοπίζει αυτόματα στήλες date/home/away/result.
    Χειρίζεται το Transfermarkt format όπου υπάρχουν
    διπλές στήλες: 'Home team', 'Home team.1', 'Home', 'Home.1' κτλ
    Παίρνει πάντα την ΠΡΩΤΗ εμφάνιση (χωρίς .1, .2 suffix).
    """
    cols = list(df.columns)
    result = {}

    def first_match(keywords):
        """Επιστρέφει την πρώτη στήλη που ταιριάζει — χωρίς .N suffix αν υπάρχει."""
        # Πρώτα: ακριβής αντιστοίχιση χωρίς suffix
        for kw in keywords:
            for col in cols:
                col_clean = col.lower().strip()
                # Αγνόησε στήλες με .1, .2 suffix
                if col_clean == kw and not any(col.endswith(f".{i}") for i in range(1,10)):
                    return col
        # Μετά: μερική αντιστοίχιση χωρίς suffix
        for kw in keywords:
            for col in cols:
                col_clean = col.lower().strip()
                if kw in col_clean and not any(col.endswith(f".{i}") for i in range(1,10)):
                    return col
        # Τελευταία: οτιδήποτε ταιριάζει
        for kw in keywords:
            for col in cols:
                if kw in col.lower().strip():
                    return col
        return None

    result["date"]     = first_match(["date", "datum", "day"])
    result["home"]     = first_match(["home team", "home", "heim"])
    result["away"]     = first_match(["away team", "away", "gast"])
    result["result"]   = first_match(["result", "ergebnis", "score"])
    result["matchday"] = first_match(["matchday", "round", "spieltag"])

    # Καθάρισε None values
    result = {k: v for k, v in result.items() if v is not None}
    return result


# ================================================================
# ΑΠΟΘΗΚΕΥΣΗ CSV
# ================================================================
def save_csv(df):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = OUTPUT_DIR / f"superleague_matches_{SEASON_NAME}_{timestamp}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"\n  📄 CSV: {filename}")
    print(f"     {len(df)} γραμμές")
    return str(filename)


# ================================================================
# ΑΠΟΘΗΚΕΥΣΗ MARIADB
# ================================================================
def save_to_mariadb(df, config):
    """
    Αποθηκεύει τους αγώνες στον πίνακα matches της MariaDB.
    Αντιστοιχεί ομάδες και σεζόν αυτόματα.
    """
    try:
        conn = get_connection(config)
    except Exception as e:
        print(f"  [ERROR] Σύνδεση MariaDB απέτυχε: {e}")
        return 0

    saved    = 0
    skipped  = 0
    errors   = 0

    with conn:
        with conn.cursor() as cur:

            # ── Εύρεση / δημιουργία season ──────────────────────
            cur.execute("SELECT id FROM seasons WHERE name=%s", (SEASON_NAME,))
            row = cur.fetchone()
            if row:
                season_id = row["id"]
            else:
                cur.execute(
                    "INSERT INTO seasons (name, is_active) VALUES (%s, %s)",
                    (SEASON_NAME, 0)
                )
                season_id = cur.lastrowid
                conn.commit()
                print(f"  [DB] Νέα σεζόν δημιουργήθηκε: {SEASON_NAME} (id={season_id})")

            # ── Cache ομάδων ─────────────────────────────────────
            cur.execute("SELECT id, name FROM teams")
            teams_in_db = {r["name"]: r["id"] for r in cur.fetchall()}

            # ── Εντοπισμός στηλών ────────────────────────────────
            col_map = detect_columns(df)
            print(f"  [DB] Στήλες: {col_map}")

            # ── Εισαγωγή αγώνων ──────────────────────────────────
            for _, row in df.iterrows():
                try:
                    # Ημερομηνία
                    match_date = parse_date(
                        row.get(col_map.get("date", ""), None)
                    ) if "date" in col_map else None

                    # Ομάδες
                    home_col  = col_map.get("home")
                    away_col  = col_map.get("away")

                    if not home_col or not away_col:
                        # Fallback: ψάξε απευθείας
                        home_col = next((c for c in row.index if "home" in str(c).lower()), None)
                        away_col = next((c for c in row.index if "away" in str(c).lower()), None)

                    home_raw  = row.get(home_col) if home_col else None
                    away_raw  = row.get(away_col) if away_col else None
                    home_name = map_team_name(home_raw)
                    away_name = map_team_name(away_raw)

                    if not home_name or not away_name:
                        skipped += 1
                        continue

                    home_id = teams_in_db.get(home_name)
                    away_id = teams_in_db.get(away_name)

                    if not home_id or not away_id:
                        print(f"  [WARN] Ομάδα δεν βρέθηκε: '{home_name}' ή '{away_name}'")
                        skipped += 1
                        continue

                    # Αποτέλεσμα
                    result_raw         = row.get(col_map.get("result", ""), None)
                    home_score, away_score = parse_score(result_raw)
                    status = "played" if home_score is not None else "scheduled"

                    # Αγωνιστική
                    matchday_num = None
                    if "matchday" in col_map:
                        try:
                            matchday_num = int(row.get(col_map["matchday"], 0))
                        except:
                            pass

                    # Φάση (competition_part)
                    competition = str(row.get("competition_part", "regular")).strip()

                    # Matchday record
                    matchday_id = None
                    if matchday_num:
                        cur.execute(
                            "SELECT id FROM matchdays WHERE season_id=%s AND number=%s",
                            (season_id, matchday_num)
                        )
                        md = cur.fetchone()
                        if md:
                            matchday_id = md["id"]
                        else:
                            cur.execute(
                                "INSERT INTO matchdays (season_id, number, name) VALUES (%s,%s,%s)",
                                (season_id, matchday_num, f"Αγ. {matchday_num}")
                            )
                            matchday_id = cur.lastrowid

                    # Έλεγχος αν υπάρχει ήδη ο αγώνας
                    cur.execute("""
                        SELECT id FROM matches
                        WHERE season_id=%s
                          AND home_team_id=%s
                          AND away_team_id=%s
                    """, (season_id, home_id, away_id))

                    existing = cur.fetchone()

                    if existing:
                        # Ενημέρωση μόνο αν έχει αποτέλεσμα
                        if status == "played":
                            cur.execute("""
                                UPDATE matches
                                SET home_score=%s, away_score=%s,
                                    status=%s, match_date=%s
                                WHERE id=%s
                            """, (home_score, away_score, status,
                                  match_date, existing["id"]))
                            saved += 1
                        else:
                            skipped += 1
                    else:
                        # Νέος αγώνας
                        cur.execute("""
                            INSERT INTO matches
                                (season_id, matchday_id, home_team_id, away_team_id,
                                 match_date, home_score, away_score, status, notes)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            season_id, matchday_id, home_id, away_id,
                            match_date,
                            home_score if home_score is not None else 0,
                            away_score if away_score is not None else 0,
                            status,
                            competition
                        ))
                        saved += 1

                except Exception as e:
                    print(f"  [ERROR] Γραμμή: {e}")
                    errors += 1
                    continue

            conn.commit()

    print(f"\n  💾 MariaDB:")
    print(f"     ✅ Νέοι αγώνες:    {saved}")
    print(f"     🔄 Ενημερώθηκαν:  {skipped}")
    print(f"     ❌ Σφάλματα:       {errors}")
    return saved



# ================================================================
# MOCK DATA — για testing χωρίς internet
# ================================================================
def get_mock_data():
    """Επιστρέφει δειγματικούς αγώνες για testing."""
    data = [
        # Regular Season
        {"Date": "12/09/2025", "Home Team": "Olympiacos",    "Result": "2:1", "Away Team": "PAOK",             "Matchday": 1,  "competition_part": "regular"},
        {"Date": "12/09/2025", "Home Team": "AEK Athens",    "Result": "1:1", "Away Team": "Panathinaikos",    "Matchday": 1,  "competition_part": "regular"},
        {"Date": "13/09/2025", "Home Team": "Aris",          "Result": "0:2", "Away Team": "OFI Crete",        "Matchday": 1,  "competition_part": "regular"},
        {"Date": "13/09/2025", "Home Team": "Asteras Tripolis","Result": "3:0","Away Team": "Lamia",           "Matchday": 1,  "competition_part": "regular"},
        {"Date": "13/09/2025", "Home Team": "Volos",         "Result": "1:0", "Away Team": "Panetolikos",      "Matchday": 1,  "competition_part": "regular"},
        {"Date": "14/09/2025", "Home Team": "Atromitos",     "Result": "2:2", "Away Team": "Kerkyra",          "Matchday": 1,  "competition_part": "regular"},
        {"Date": "19/09/2025", "Home Team": "PAOK",          "Result": "3:1", "Away Team": "AEK Athens",       "Matchday": 2,  "competition_part": "regular"},
        {"Date": "19/09/2025", "Home Team": "Panathinaikos", "Result": "0:0", "Away Team": "Olympiacos",       "Matchday": 2,  "competition_part": "regular"},
        {"Date": "20/09/2025", "Home Team": "OFI Crete",     "Result": "1:1", "Away Team": "Asteras Tripolis", "Matchday": 2,  "competition_part": "regular"},
        {"Date": "20/09/2025", "Home Team": "Lamia",         "Result": "2:1", "Away Team": "Volos",            "Matchday": 2,  "competition_part": "regular"},
        {"Date": "21/09/2025", "Home Team": "Panetolikos",   "Result": "-",   "Away Team": "Aris",             "Matchday": 3,  "competition_part": "regular"},
        {"Date": "21/09/2025", "Home Team": "Kerkyra",       "Result": "-",   "Away Team": "Atromitos",        "Matchday": 3,  "competition_part": "regular"},
        # Playoffs
        {"Date": "10/05/2026", "Home Team": "Olympiacos",    "Result": "1:0", "Away Team": "AEK Athens",       "Matchday": 1,  "competition_part": "playoffs"},
        {"Date": "10/05/2026", "Home Team": "PAOK",          "Result": "2:1", "Away Team": "Panathinaikos",    "Matchday": 1,  "competition_part": "playoffs"},
        # Playout
        {"Date": "08/05/2026", "Home Team": "Lamia",         "Result": "0:1", "Away Team": "Kerkyra",          "Matchday": 1,  "competition_part": "playout"},
        {"Date": "08/05/2026", "Home Team": "Panetolikos",   "Result": "2:0", "Away Team": "Volos",            "Matchday": 1,  "competition_part": "playout"},
    ]
    return pd.DataFrame(data)

# ================================================================
# ΚΥΡΙΑ ΣΥΝΑΡΤΗΣΗ (αρχικός κώδικας + MariaDB)
# ================================================================
def main(args):
    print("\n" + "="*55)
    print("  Super League Greece — Matches Scraper")
    print(f"  Σεζόν: {SEASON_NAME}")
    print("="*55)

    # Φόρτωση config
    config = load_db_config()

    # Επιλογή competitions
    competitions = COMPETITIONS
    if args.part:
        competitions = {k: v for k, v in COMPETITIONS.items() if k == args.part}
        if not competitions:
            print(f"❌ Άγνωστο part: {args.part}. Επιλογές: {list(COMPETITIONS.keys())}")
            sys.exit(1)

    # ── Scraping ────────────────────────────────────────────────
    if args.mock:
        print("  [MOCK] Χρήση δειγματικών δεδομένων (χωρίς internet)")
        results = get_mock_data()
    else:
        all_matches = []
        for name, url in competitions.items():
            df = scrape_url(name, url)
            all_matches.append(df)
            time.sleep(2)  # ευγενικό scraping

        results = pd.concat(all_matches, ignore_index=True)
        results = results.dropna(how="all")

        # ── Καθαρισμός: αφαίρεση duplicate header rows ──────────
        # Το Transfermarkt επιστρέφει γραμμές όπου Date == Time
        # (duplicate headers που παράγει το pandas read_html)
        col_map = detect_columns(results)
        date_col = col_map.get("date")
        home_col = col_map.get("home")
        away_col = col_map.get("away")

        if date_col and home_col:
            # Κρατάμε μόνο γραμμές που έχουν πραγματικό home team
            results = results[results[home_col].notna()]
            results = results[results[home_col].astype(str).str.strip() != "nan"]
            results = results[results[home_col].astype(str).str.strip() != ""]
            # Αφαίρεση γραμμών όπου date == home (header repetition)
            if date_col != home_col:
                results = results[
                    results[date_col].astype(str) != results[home_col].astype(str)
                ]
        results = results.reset_index(drop=True)

        if home_col and away_col:
            print("  [MAPPING] Μετατροπή ονομάτων ομάδων στα Ελληνικά...")
            results[home_col] = results[home_col].map(TEAM_NAME_MAP).fillna(results[home_col])
            results[away_col] = results[away_col].map(TEAM_NAME_MAP).fillna(results[away_col])
        # ───────────────────────────────────────────────────────────────

    if results.empty:
        print("\n❌ Δεν βρέθηκαν αγώνες.")
        return

    print(f"\n{'='*55}")
    print(f"  Σύνολο γραμμών: {len(results)}")
    print(f"  Στήλες: {list(results.columns)}")
    print(results.head(3).to_string())

    if args.dry_run:
        print("\n  [DRY RUN] Δεν αποθηκεύτηκε τίποτα.")
        return

    # ── CSV (πάντα) ──────────────────────────────────────────────
    csv_file = save_csv(results)

    # ── MariaDB ──────────────────────────────────────────────────
    if not args.csv_only:
        print("\n  Αποθήκευση στη MariaDB...")
        save_to_mariadb(results, config)

    print("\n✅ Ολοκληρώθηκε!")


# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Super League Matches Scraper — Transfermarkt → MariaDB + CSV"
    )
    parser.add_argument(
        "--part",
        choices=["regular", "playoffs", "fifth_place_playoff", "playout"],
        help="Scrape μόνο συγκεκριμένη φάση"
    )
    parser.add_argument(
        "--csv-only", action="store_true",
        help="Αποθήκευση μόνο σε CSV (όχι MariaDB)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Εμφάνιση δεδομένων χωρίς αποθήκευση"
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Χρήση mock δεδομένων για testing (χωρίς internet)"
    )
    args = parser.parse_args()
    main(args)
