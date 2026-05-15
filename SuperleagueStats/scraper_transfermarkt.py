"""
================================================================
 Super League Greece — Transfermarkt Scraper
 Τραβάει ρόστερ + αξίες παικτών για όλες τις ομάδες
 Αποθηκεύει: MariaDB + CSV

 Απαιτήσεις:
   pip install selenium webdriver-manager beautifulsoup4 lxml cloudscraper pymysql

 Χρήση:
   python scraper_transfermarkt.py
   python scraper_transfermarkt.py --team "Olympiacos"
   python scraper_transfermarkt.py --csv-only
================================================================
"""

import os
import sys
import csv
import json
import time
import random
import argparse
import datetime
from pathlib import Path

# ── Transfermarkt URLs ───────────────────────────────────────────
TM_BASE = "https://www.transfermarkt.com"
TM_LEAGUE_URL = f"{TM_BASE}/super-league/startseite/wettbewerb/GR1"

# Hardcoded ομάδες Super League 2024-2025 με Transfermarkt IDs
# (για αποφυγή scraping της league page που μπλοκάρεται)
SUPERLEAGUE_TEAMS = {
    "Olympiacos":        {"tm_id": 1039,  "tm_slug": "olympiacos-piräus"},
    "AEK Athens":        {"tm_id": 5955,  "tm_slug": "aek-athen"},
    "PAOK":              {"tm_id": 5941,  "tm_slug": "paok-thessaloniki"},
    "Panathinaikos":     {"tm_id": 1031,  "tm_slug": "panathinaikos-athen"},
    "Aris":              {"tm_id": 5958,  "tm_slug": "aris-thessaloniki"},
    "OFI Crete":         {"tm_id": 5945,  "tm_slug": "ofi-kreta"},
    "Asteras Tripolis":  {"tm_id": 11337, "tm_slug": "asteras-tripolis"},
    "Lamia":             {"tm_id": 16424, "tm_slug": "pas-lamia-1964"},
    "Volos":             {"tm_id": 12471, "tm_slug": "volos-nfc"},
    "Panetolikos":       {"tm_id": 11395, "tm_slug": "panetolikos-gfs"},
    "Atromitos":         {"tm_id": 5954,  "tm_slug": "atromitos-athen"},
    "Kerkyra":           {"tm_id": 11399, "tm_slug": "aok-kerkyra"},
}

OUTPUT_DIR = Path(__file__).parent / "scraper_output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ================================================================
# CONFIG
# ================================================================
def load_db_config():
    config_path = Path(__file__).parent / "db_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {"engine": "sqlite"}


# ================================================================
# SCRAPER — Selenium (παρακάμπτει το Cloudflare protection)
# ================================================================
def get_driver():
    """Δημιουργεί Chrome WebDriver σε headless mode."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"  [WARN] Selenium δεν είναι διαθέσιμο: {e}")
        return None


def scrape_team_roster_selenium(driver, team_name, team_info, season="2024"):
    """Scrape ρόστερ ομάδας από Transfermarkt με Selenium."""
    from bs4 import BeautifulSoup

    tm_id   = team_info["tm_id"]
    tm_slug = team_info["tm_slug"]
    url = f"{TM_BASE}/{tm_slug}/kader/verein/{tm_id}/saison_id/{season}/plus/1"

    print(f"  Scraping: {url}")
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # Respect rate limiting

    soup = BeautifulSoup(driver.page_source, "lxml")
    players = []

    # Εύρεση πίνακα ρόστερ
    table = soup.select_one("table.items")
    if not table:
        print(f"  [WARN] Δεν βρέθηκε πίνακας για {team_name}")
        return players

    rows = table.select("tr.odd, tr.even")
    for row in rows:
        try:
            # Όνομα παίκτη
            name_cell = row.select_one("td.hauptlink a")
            if not name_cell:
                continue
            name = name_cell.text.strip()

            # Transfermarkt player ID
            player_url = name_cell.get("href", "")
            tm_player_id = player_url.split("/")[-1] if player_url else ""

            # Θέση
            pos_cell = row.select_one("td.posrela table td")
            position = pos_cell.text.strip() if pos_cell else ""

            # Ηλικία
            age_cells = row.select("td.zentriert")
            age = ""
            dob = ""
            for cell in age_cells:
                text = cell.text.strip()
                if text.isdigit() and 15 <= int(text) <= 45:
                    age = text
                # DOB format: DD.MM.YYYY (Age)
                if "(" in text and ")" in text:
                    dob_part = text.split("(")[0].strip()
                    dob = dob_part

            # Εθνικότητα (σημαία)
            nationality_img = row.select_one("td.zentriert img.flaggenrahmen")
            nationality = nationality_img.get("title", "") if nationality_img else ""

            # Αξία αγοράς
            value_cell = row.select_one("td.rechts.hauptlink")
            market_value_raw = value_cell.text.strip() if value_cell else "-"
            market_value_eur = parse_market_value(market_value_raw)

            # Νούμερο φανέλας
            number_cell = row.select_one("div.rn_nummer")
            jersey = number_cell.text.strip() if number_cell else ""

            players.append({
                "team":          team_name,
                "name":          name,
                "position":      position,
                "age":           age,
                "date_of_birth": dob,
                "nationality":   nationality,
                "jersey_number": jersey,
                "market_value":  market_value_raw,
                "market_value_eur": market_value_eur,
                "tm_player_id":  tm_player_id,
                "season":        season,
                "scraped_at":    datetime.datetime.now().isoformat()
            })
        except Exception as e:
            continue

    print(f"  ✅ {team_name}: {len(players)} παίκτες")
    return players


def parse_market_value(value_str):
    """Μετατρέπει '€5.00m' → 5000000, '€500Th.' → 500000."""
    if not value_str or value_str in ["-", "?"]:
        return 0
    v = value_str.replace("€", "").replace(",", ".").strip()
    try:
        if "m" in v.lower():
            return int(float(v.lower().replace("m", "")) * 1_000_000)
        elif "th" in v.lower() or "k" in v.lower():
            return int(float(v.lower().replace("th.", "").replace("k", "")) * 1_000)
        else:
            return int(float(v))
    except:
        return 0


# ================================================================
# FALLBACK — Mock δεδομένα για testing χωρίς internet/selenium
# ================================================================
def get_mock_roster(team_name, season="2024"):
    """Επιστρέφει δείγμα δεδομένων για testing."""
    mock_players = [
        {"name": "Τεστ Παίκτης 1", "position": "GK", "age": "28",
         "nationality": "Greece", "jersey_number": "1",
         "market_value": "€1.00m", "market_value_eur": 1000000},
        {"name": "Τεστ Παίκτης 2", "position": "CB", "age": "25",
         "nationality": "Greece", "jersey_number": "4",
         "market_value": "€500Th.", "market_value_eur": 500000},
        {"name": "Τεστ Παίκτης 3", "position": "MF", "age": "22",
         "nationality": "Brazil", "jersey_number": "8",
         "market_value": "€2.50m", "market_value_eur": 2500000},
    ]
    return [{**p, "team": team_name, "season": season,
             "date_of_birth": "", "tm_player_id": "",
             "scraped_at": datetime.datetime.now().isoformat()}
            for p in mock_players]


# ================================================================
# SAVE TO CSV
# ================================================================
def save_to_csv(all_players, season="2024"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = OUTPUT_DIR / f"superleague_rosters_{season}_{timestamp}.csv"

    if not all_players:
        print("  [WARN] Δεν υπάρχουν δεδομένα για CSV.")
        return None

    fieldnames = [
        "team", "name", "position", "age", "date_of_birth",
        "nationality", "jersey_number", "market_value",
        "market_value_eur", "tm_player_id", "season", "scraped_at"
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_players)

    print(f"\n  📄 CSV αποθηκεύτηκε: {filename}")
    print(f"     {len(all_players)} παίκτες σε {len(set(p['team'] for p in all_players))} ομάδες")
    return str(filename)


# ================================================================
# SAVE TO MARIADB / SQLITE
# ================================================================
def save_to_database(all_players, season_name="2024-2025"):
    config = load_db_config()

    if config.get("engine") == "mariadb":
        return _save_mariadb(all_players, season_name, config)
    else:
        return _save_sqlite(all_players, season_name)


def _save_mariadb(players, season_name, config):
    try:
        import pymysql
        conn = pymysql.connect(
            host=config.get("host", "localhost"),
            port=config.get("port", 3306),
            user=config.get("user", "superleague"),
            password=config.get("password", "nano1545"),
            database=config.get("database", "superleague_greece"),
            charset="utf8mb4",
            autocommit=True
        )

        # Προσθήκη στήλης market_value αν δεν υπάρχει
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    ALTER TABLE players
                    ADD COLUMN IF NOT EXISTS market_value_eur BIGINT DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS tm_player_id VARCHAR(20),
                    ADD COLUMN IF NOT EXISTS market_value_str VARCHAR(20)
                """)
            except:
                pass  # Ήδη υπάρχουν

        saved = _insert_players(conn, players, season_name, db_type="mariadb")
        conn.close()
        return saved
    except Exception as e:
        print(f"  [ERROR] MariaDB: {e}")
        return 0


def _save_sqlite(players, season_name):
    try:
        import sqlite3
        db_path = Path(__file__).parent / "superleague.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        # Προσθήκη στηλών αν δεν υπάρχουν
        for col in ["market_value_eur INTEGER DEFAULT 0",
                    "tm_player_id TEXT",
                    "market_value_str TEXT"]:
            try:
                conn.execute(f"ALTER TABLE players ADD COLUMN {col}")
            except:
                pass
        conn.commit()

        saved = _insert_players(conn, players, season_name, db_type="sqlite")
        conn.close()
        return saved
    except Exception as e:
        print(f"  [ERROR] SQLite: {e}")
        return 0


def _insert_players(conn, players, season_name, db_type="sqlite"):
    """Εισαγωγή παικτών στη βάση — κοινή λογική για MariaDB & SQLite."""
    ph = "%s" if db_type == "mariadb" else "?"
    saved = 0

    # Εύρεση season_id
    if db_type == "mariadb":
        with conn.cursor() as cur:
            cur.execute(f"SELECT id FROM seasons WHERE name={ph}", (season_name,))
            row = cur.fetchone()
            season_id = row[0] if row else None
    else:
        cur = conn.execute("SELECT id FROM seasons WHERE name=?", (season_name,))
        row = cur.fetchone()
        season_id = row[0] if row else None

    if not season_id:
        print(f"  [WARN] Σεζόν '{season_name}' δεν βρέθηκε στη βάση. Δημιουργία...")
        if db_type == "mariadb":
            with conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO seasons (name, is_active) VALUES ({ph},{ph})",
                    (season_name, 0)
                )
                season_id = cur.lastrowid
            conn.commit()
        else:
            cur = conn.execute(
                "INSERT INTO seasons (name, is_active) VALUES (?,?)", (season_name, 0))
            season_id = cur.lastrowid
            conn.commit()

    for p in players:
        try:
            # Εύρεση team_id από βάση (αντιστοίχιση ονόματος)
            team_name = p["team"]
            if db_type == "mariadb":
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT id FROM teams WHERE name LIKE {ph}",
                        (f"%{team_name.split()[0]}%",)
                    )
                    row = cur.fetchone()
                    team_id = row[0] if row else None
            else:
                cur = conn.execute(
                    "SELECT id FROM teams WHERE name LIKE ?",
                    (f"%{team_name.split()[0]}%",)
                )
                row = cur.fetchone()
                team_id = row[0] if row else None

            # Εισαγωγή ή ενημέρωση παίκτη
            if db_type == "mariadb":
                with conn.cursor() as cur:
                    cur.execute(f"""
                        INSERT INTO players
                            (full_name, nationality, position, jersey_number,
                             market_value_eur, market_value_str, tm_player_id)
                        VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph})
                        ON DUPLICATE KEY UPDATE
                            market_value_eur = VALUES(market_value_eur),
                            market_value_str = VALUES(market_value_str)
                    """, (
                        p["name"], p.get("nationality",""),
                        p.get("position",""), p.get("jersey_number","") or None,
                        p.get("market_value_eur", 0),
                        p.get("market_value",""),
                        p.get("tm_player_id","")
                    ))
                    player_id = cur.lastrowid
                conn.commit()
            else:
                cur = conn.execute("""
                    INSERT OR IGNORE INTO players
                        (full_name, nationality, position, jersey_number,
                         market_value_eur, market_value_str, tm_player_id)
                    VALUES (?,?,?,?,?,?,?)
                """, (
                    p["name"], p.get("nationality",""),
                    p.get("position",""), p.get("jersey_number","") or None,
                    p.get("market_value_eur", 0),
                    p.get("market_value",""),
                    p.get("tm_player_id","")
                ))
                player_id = cur.lastrowid
                conn.commit()

            # Εισαγωγή στο roster
            if team_id and player_id and season_id:
                jersey = p.get("jersey_number", "") or None
                try:
                    jersey = int(jersey) if jersey else None
                except:
                    jersey = None

                if db_type == "mariadb":
                    with conn.cursor() as cur:
                        cur.execute(f"""
                            INSERT IGNORE INTO rosters
                                (team_id, season_id, player_id, jersey_number)
                            VALUES ({ph},{ph},{ph},{ph})
                        """, (team_id, season_id, player_id, jersey))
                    conn.commit()
                else:
                    conn.execute("""
                        INSERT OR IGNORE INTO rosters
                            (team_id, season_id, player_id, jersey_number)
                        VALUES (?,?,?,?)
                    """, (team_id, season_id, player_id, jersey))
                    conn.commit()

            saved += 1
        except Exception as e:
            print(f"    [WARN] {p.get('name','?')}: {e}")
            continue

    return saved


# ================================================================
# ΚΥΡΙΑ ΣΥΝΑΡΤΗΣΗ
# ================================================================
def run_scraper(teams=None, season="2024", season_name="2024-2025",
                csv_only=False, mock=False):

    target_teams = {k: v for k, v in SUPERLEAGUE_TEAMS.items()
                    if not teams or any(t.lower() in k.lower() for t in teams)}

    if not target_teams:
        print("❌ Δεν βρέθηκαν ομάδες. Έλεγξε το όνομα.")
        return

    print(f"\n🔍 Super League Greece — Transfermarkt Scraper")
    print(f"   Σεζόν: {season_name}")
    print(f"   Ομάδες: {len(target_teams)}")
    print(f"   Mode: {'MOCK (testing)' if mock else 'LIVE'}")
    print("=" * 50)

    all_players = []
    driver = None

    if not mock:
        print("\n  Εκκίνηση Chrome (headless)...")
        driver = get_driver()
        if not driver:
            print("  [WARN] Selenium δεν βρέθηκε. Χρήση mock δεδομένων.")
            mock = True

    try:
        for team_name, team_info in target_teams.items():
            print(f"\n⚽ {team_name}")
            if mock:
                players = get_mock_roster(team_name, season)
            else:
                players = scrape_team_roster_selenium(driver, team_name, team_info, season)
                time.sleep(random.uniform(2, 4))  # Rate limiting

            all_players.extend(players)

    finally:
        if driver:
            driver.quit()

    print(f"\n{'=' * 50}")
    print(f"✅ Σύνολο: {len(all_players)} παίκτες από {len(target_teams)} ομάδες")

    # ── Αποθήκευση CSV ──────────────────────────────────────────
    csv_file = save_to_csv(all_players, season)

    # ── Αποθήκευση βάση ─────────────────────────────────────────
    if not csv_only:
        print("\n  💾 Αποθήκευση στη βάση δεδομένων...")
        saved = save_to_database(all_players, season_name)
        print(f"  ✅ {saved}/{len(all_players)} παίκτες αποθηκεύτηκαν στη βάση")

    return all_players


# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfermarkt Scraper — Super League Greece"
    )
    parser.add_argument(
        "--team", nargs="+",
        help="Όνομα ομάδας (π.χ. --team Olympiacos PAOK)"
    )
    parser.add_argument(
        "--season", default="2024",
        help="Σεζόν Transfermarkt (default: 2024)"
    )
    parser.add_argument(
        "--season-name", default="2024-2025",
        help="Όνομα σεζόν στη βάση (default: 2024-2025)"
    )
    parser.add_argument(
        "--csv-only", action="store_true",
        help="Αποθήκευση μόνο σε CSV (όχι βάση)"
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Χρήση mock δεδομένων (για testing χωρίς internet)"
    )
    parser.add_argument(
        "--list-teams", action="store_true",
        help="Εμφάνιση διαθέσιμων ομάδων"
    )

    args = parser.parse_args()

    if args.list_teams:
        print("\nΔιαθέσιμες ομάδες Super League:")
        for name, info in SUPERLEAGUE_TEAMS.items():
            print(f"  {name:<25} (TM ID: {info['tm_id']})")
        sys.exit(0)

    run_scraper(
        teams=args.team,
        season=args.season,
        season_name=args.season_name,
        csv_only=args.csv_only,
        mock=args.mock
    )
