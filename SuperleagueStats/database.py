"""
Super League Greece - Database Module
Διαχείριση βάσης δεδομένων SQLite
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "superleague.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Δημιουργία όλων των πινάκων της βάσης δεδομένων."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        -- ================================================
        -- ΠΙΝΑΚΑΣ: Ομάδες
        -- ================================================
        CREATE TABLE IF NOT EXISTS teams (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            short_name  TEXT NOT NULL,
            city        TEXT,
            stadium     TEXT,
            founded     INTEGER,
            logo_path   TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Σεζόν
        -- ================================================
        CREATE TABLE IF NOT EXISTS seasons (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,  -- π.χ. "2024-2025"
            start_date  DATE,
            end_date    DATE,
            is_active   INTEGER DEFAULT 0
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Αγωνιστικές
        -- ================================================
        CREATE TABLE IF NOT EXISTS matchdays (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id   INTEGER NOT NULL,
            number      INTEGER NOT NULL,
            name        TEXT,
            FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
            UNIQUE(season_id, number)
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Διαιτητές
        -- ================================================
        CREATE TABLE IF NOT EXISTS referees (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            country     TEXT DEFAULT 'Ελλάδα',
            badge_level TEXT  -- π.χ. "FIFA", "UEFA", "Εθνική"
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Αγώνες
        -- ================================================
        CREATE TABLE IF NOT EXISTS matches (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id       INTEGER NOT NULL,
            matchday_id     INTEGER,
            home_team_id    INTEGER NOT NULL,
            away_team_id    INTEGER NOT NULL,
            match_date      DATETIME,
            stadium         TEXT,
            home_score      INTEGER DEFAULT 0,
            away_score      INTEGER DEFAULT 0,
            status          TEXT DEFAULT 'scheduled',  -- scheduled, played, postponed, cancelled
            referee_id      INTEGER,
            attendance      INTEGER,
            notes           TEXT,
            FOREIGN KEY (season_id)     REFERENCES seasons(id),
            FOREIGN KEY (matchday_id)   REFERENCES matchdays(id),
            FOREIGN KEY (home_team_id)  REFERENCES teams(id),
            FOREIGN KEY (away_team_id)  REFERENCES teams(id),
            FOREIGN KEY (referee_id)    REFERENCES referees(id)
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Παίκτες
        -- ================================================
        CREATE TABLE IF NOT EXISTS players (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT NOT NULL,
            nationality     TEXT,
            date_of_birth   DATE,
            position        TEXT,  -- GK, DEF, MID, FWD
            jersey_number   INTEGER,
            foot            TEXT,  -- Δεξί, Αριστερό, Αμφίδεξιο
            height_cm       INTEGER,
            weight_kg       INTEGER,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Ρόστερ (Παίκτης ανά ομάδα/σεζόν)
        -- ================================================
        CREATE TABLE IF NOT EXISTS rosters (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id         INTEGER NOT NULL,
            season_id       INTEGER NOT NULL,
            player_id       INTEGER NOT NULL,
            jersey_number   INTEGER,
            date_joined     DATE,
            date_left       DATE,
            loan            INTEGER DEFAULT 0,
            loan_from_team  TEXT,
            FOREIGN KEY (team_id)   REFERENCES teams(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (player_id) REFERENCES players(id),
            UNIQUE(team_id, season_id, player_id)
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Προπονητές
        -- ================================================
        CREATE TABLE IF NOT EXISTS coaches (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT NOT NULL,
            nationality     TEXT,
            date_of_birth   DATE,
            license_level   TEXT  -- UEFA Pro, UEFA A κτλ
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Ιστορικό Προπονητών ανά ομάδα/σεζόν
        -- ================================================
        CREATE TABLE IF NOT EXISTS team_coaches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id     INTEGER NOT NULL,
            season_id   INTEGER NOT NULL,
            coach_id    INTEGER NOT NULL,
            date_from   DATE,
            date_to     DATE,
            is_current  INTEGER DEFAULT 1,
            FOREIGN KEY (team_id)   REFERENCES teams(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id),
            FOREIGN KEY (coach_id)  REFERENCES coaches(id)
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Στατιστικά Παικτών ανά Αγώνα
        -- ================================================
        CREATE TABLE IF NOT EXISTS player_match_stats (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id        INTEGER NOT NULL,
            player_id       INTEGER NOT NULL,
            team_id         INTEGER NOT NULL,
            minutes_played  INTEGER DEFAULT 0,
            goals           INTEGER DEFAULT 0,
            assists         INTEGER DEFAULT 0,
            yellow_cards    INTEGER DEFAULT 0,
            red_cards       INTEGER DEFAULT 0,
            own_goals       INTEGER DEFAULT 0,
            shots           INTEGER DEFAULT 0,
            shots_on_target INTEGER DEFAULT 0,
            passes          INTEGER DEFAULT 0,
            key_passes      INTEGER DEFAULT 0,
            tackles         INTEGER DEFAULT 0,
            fouls_committed INTEGER DEFAULT 0,
            fouls_suffered  INTEGER DEFAULT 0,
            offsides        INTEGER DEFAULT 0,
            saves           INTEGER DEFAULT 0,  -- Για τερματοφύλακες
            rating          REAL,               -- 1.0-10.0
            FOREIGN KEY (match_id)  REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (team_id)   REFERENCES teams(id),
            UNIQUE(match_id, player_id)
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Γεγονότα Αγώνα (γκολ, κάρτες κτλ)
        -- ================================================
        CREATE TABLE IF NOT EXISTS match_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id    INTEGER NOT NULL,
            minute      INTEGER,
            extra_time  INTEGER DEFAULT 0,
            event_type  TEXT NOT NULL,  -- goal, yellow_card, red_card, substitution, own_goal, penalty
            player_id   INTEGER,
            player2_id  INTEGER,        -- Για αντικαταστάσεις: παίκτης που βγαίνει
            team_id     INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (match_id)  REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (team_id)   REFERENCES teams(id)
        );

        -- ================================================
        -- ΠΙΝΑΚΑΣ: Βαθμολογία (ενημερώνεται αυτόματα)
        -- ================================================
        CREATE TABLE IF NOT EXISTS standings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id       INTEGER NOT NULL,
            matchday_id     INTEGER,
            team_id         INTEGER NOT NULL,
            position        INTEGER,
            played          INTEGER DEFAULT 0,
            won             INTEGER DEFAULT 0,
            drawn           INTEGER DEFAULT 0,
            lost            INTEGER DEFAULT 0,
            goals_for       INTEGER DEFAULT 0,
            goals_against   INTEGER DEFAULT 0,
            goal_diff       INTEGER DEFAULT 0,
            points          INTEGER DEFAULT 0,
            form            TEXT,  -- π.χ. "WWDLW"
            FOREIGN KEY (season_id)  REFERENCES seasons(id),
            FOREIGN KEY (matchday_id) REFERENCES matchdays(id),
            FOREIGN KEY (team_id)    REFERENCES teams(id),
            UNIQUE(season_id, matchday_id, team_id)
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Βάση δεδομένων αρχικοποιήθηκε επιτυχώς!")


# ============================================================
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ CRUD
# ============================================================

class TeamDAO:
    @staticmethod
    def get_all():
        with get_connection() as conn:
            return conn.execute("SELECT * FROM teams ORDER BY name").fetchall()

    @staticmethod
    def insert(name, short_name, city="", stadium="", founded=None):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO teams (name, short_name, city, stadium, founded) VALUES (?,?,?,?,?)",
                (name, short_name, city, stadium, founded)
            )

    @staticmethod
    def update(team_id, name, short_name, city, stadium, founded):
        with get_connection() as conn:
            conn.execute(
                "UPDATE teams SET name=?, short_name=?, city=?, stadium=?, founded=? WHERE id=?",
                (name, short_name, city, stadium, founded, team_id)
            )

    @staticmethod
    def delete(team_id):
        with get_connection() as conn:
            conn.execute("DELETE FROM teams WHERE id=?", (team_id,))


class SeasonDAO:
    @staticmethod
    def get_all():
        with get_connection() as conn:
            return conn.execute("SELECT * FROM seasons ORDER BY name DESC").fetchall()

    @staticmethod
    def get_active():
        with get_connection() as conn:
            return conn.execute("SELECT * FROM seasons WHERE is_active=1").fetchone()

    @staticmethod
    def insert(name, start_date, end_date, is_active=0):
        with get_connection() as conn:
            if is_active:
                conn.execute("UPDATE seasons SET is_active=0")
            conn.execute(
                "INSERT INTO seasons (name, start_date, end_date, is_active) VALUES (?,?,?,?)",
                (name, start_date, end_date, is_active)
            )

    @staticmethod
    def set_active(season_id):
        with get_connection() as conn:
            conn.execute("UPDATE seasons SET is_active=0")
            conn.execute("UPDATE seasons SET is_active=1 WHERE id=?", (season_id,))


class MatchDAO:
    @staticmethod
    def get_all(season_id=None):
        query = """
            SELECT m.*, 
                   ht.name as home_team, at.name as away_team,
                   r.name as referee_name, r.country as referee_country,
                   md.number as matchday_number,
                   s.name as season_name
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams at ON m.away_team_id = at.id
            LEFT JOIN referees r ON m.referee_id = r.id
            LEFT JOIN matchdays md ON m.matchday_id = md.id
            LEFT JOIN seasons s ON m.season_id = s.id
        """
        params = ()
        if season_id:
            query += " WHERE m.season_id=?"
            params = (season_id,)
        query += " ORDER BY m.match_date DESC"
        with get_connection() as conn:
            return conn.execute(query, params).fetchall()

    @staticmethod
    def insert(season_id, matchday_id, home_team_id, away_team_id,
               match_date, stadium, home_score, away_score, status, referee_id, attendance, notes):
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO matches 
                (season_id, matchday_id, home_team_id, away_team_id, match_date, 
                 stadium, home_score, away_score, status, referee_id, attendance, notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (season_id, matchday_id, home_team_id, away_team_id, match_date,
                  stadium, home_score, away_score, status, referee_id, attendance, notes))

    @staticmethod
    def update_score(match_id, home_score, away_score, status="played"):
        with get_connection() as conn:
            conn.execute(
                "UPDATE matches SET home_score=?, away_score=?, status=? WHERE id=?",
                (home_score, away_score, status, match_id)
            )

    @staticmethod
    def delete(match_id):
        with get_connection() as conn:
            conn.execute("DELETE FROM matches WHERE id=?", (match_id,))


class PlayerDAO:
    @staticmethod
    def get_all():
        with get_connection() as conn:
            return conn.execute("SELECT * FROM players ORDER BY full_name").fetchall()

    @staticmethod
    def get_by_team_season(team_id, season_id):
        with get_connection() as conn:
            return conn.execute("""
                SELECT p.*, r.jersey_number as roster_number, r.loan, r.loan_from_team
                FROM players p
                JOIN rosters r ON p.id = r.player_id
                WHERE r.team_id=? AND r.season_id=?
                ORDER BY p.position, p.full_name
            """, (team_id, season_id)).fetchall()

    @staticmethod
    def insert(full_name, nationality, dob, position, jersey_number, foot, height, weight):
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO players (full_name, nationality, date_of_birth, position, 
                                     jersey_number, foot, height_cm, weight_kg)
                VALUES (?,?,?,?,?,?,?,?)
            """, (full_name, nationality, dob, position, jersey_number, foot, height, weight))
            return cursor.lastrowid

    @staticmethod
    def search(query):
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM players WHERE full_name LIKE ? ORDER BY full_name",
                (f"%{query}%",)
            ).fetchall()


class StandingsDAO:
    @staticmethod
    def recalculate(season_id):
        """Επαναϋπολογισμός βαθμολογίας από τα αποτελέσματα."""
        with get_connection() as conn:
            # Παίρνουμε όλες τις ομάδες που έχουν αγωνιστεί
            matches = conn.execute("""
                SELECT home_team_id, away_team_id, home_score, away_score
                FROM matches
                WHERE season_id=? AND status='played'
            """, (season_id,)).fetchall()

            stats = {}

            for m in matches:
                for team_id, goals_for, goals_against in [
                    (m['home_team_id'], m['home_score'], m['away_score']),
                    (m['away_team_id'], m['away_score'], m['home_score'])
                ]:
                    if team_id not in stats:
                        stats[team_id] = dict(played=0, won=0, drawn=0, lost=0,
                                               gf=0, ga=0, pts=0)
                    s = stats[team_id]
                    s['played'] += 1
                    s['gf'] += goals_for
                    s['ga'] += goals_against
                    if goals_for > goals_against:
                        s['won'] += 1; s['pts'] += 3
                    elif goals_for == goals_against:
                        s['drawn'] += 1; s['pts'] += 1
                    else:
                        s['lost'] += 1

            # Ταξινόμηση
            sorted_teams = sorted(stats.items(),
                key=lambda x: (-x[1]['pts'], -(x[1]['gf']-x[1]['ga']), -x[1]['gf']))

            # Ενημέρωση βαθμολογίας
            conn.execute("DELETE FROM standings WHERE season_id=? AND matchday_id IS NULL", (season_id,))
            for pos, (team_id, s) in enumerate(sorted_teams, 1):
                conn.execute("""
                    INSERT INTO standings 
                    (season_id, team_id, position, played, won, drawn, lost,
                     goals_for, goals_against, goal_diff, points)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (season_id, team_id, pos, s['played'], s['won'], s['drawn'],
                      s['lost'], s['gf'], s['ga'], s['gf']-s['ga'], s['pts']))

    @staticmethod
    def get(season_id):
        with get_connection() as conn:
            return conn.execute("""
                SELECT s.position, t.name as team_name, t.short_name,
                       s.played, s.won, s.drawn, s.lost,
                       s.goals_for, s.goals_against, s.goal_diff, s.points
                FROM standings s
                JOIN teams t ON s.team_id = t.id
                WHERE s.season_id=? AND s.matchday_id IS NULL
                ORDER BY s.position
            """, (season_id,)).fetchall()


class RefereeDAO:
    @staticmethod
    def get_all():
        with get_connection() as conn:
            return conn.execute("SELECT * FROM referees ORDER BY name").fetchall()

    @staticmethod
    def insert(name, country="Ελλάδα", badge="Εθνική"):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO referees (name, country, badge_level) VALUES (?,?,?)",
                (name, country, badge)
            )


class CoachDAO:
    @staticmethod
    def get_all():
        with get_connection() as conn:
            return conn.execute("SELECT * FROM coaches ORDER BY full_name").fetchall()

    @staticmethod
    def insert(full_name, nationality, dob, license_level):
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO coaches (full_name, nationality, date_of_birth, license_level) VALUES (?,?,?,?)",
                (full_name, nationality, dob, license_level)
            )
            return cursor.lastrowid

    @staticmethod
    def assign_to_team(team_id, season_id, coach_id, date_from):
        with get_connection() as conn:
            # Τερματισμός προηγούμενου προπονητή
            conn.execute("""
                UPDATE team_coaches SET is_current=0, date_to=?
                WHERE team_id=? AND season_id=? AND is_current=1
            """, (date_from, team_id, season_id))
            conn.execute("""
                INSERT INTO team_coaches (team_id, season_id, coach_id, date_from, is_current)
                VALUES (?,?,?,?,1)
            """, (team_id, season_id, coach_id, date_from))


class ImportDAO:
    @staticmethod
    def import_csv_matches(filepath, season_id):
        """Import αγώνων από CSV."""
        import csv
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with get_connection() as conn:
                for row in reader:
                    try:
                        # Εύρεση ομάδων
                        home = conn.execute("SELECT id FROM teams WHERE name LIKE ?",
                                            (f"%{row['home_team']}%",)).fetchone()
                        away = conn.execute("SELECT id FROM teams WHERE name LIKE ?",
                                            (f"%{row['away_team']}%",)).fetchone()
                        if not home or not away:
                            results.append(f"❌ Δεν βρέθηκε ομάδα: {row['home_team']} ή {row['away_team']}")
                            continue
                        conn.execute("""
                            INSERT OR IGNORE INTO matches
                            (season_id, home_team_id, away_team_id, match_date, 
                             home_score, away_score, status)
                            VALUES (?,?,?,?,?,?,?)
                        """, (season_id, home['id'], away['id'],
                              row.get('date'), row.get('home_score', 0),
                              row.get('away_score', 0), row.get('status', 'played')))
                        results.append(f"✅ {row['home_team']} - {row['away_team']}")
                    except Exception as e:
                        results.append(f"❌ Σφάλμα: {e}")
        return results

