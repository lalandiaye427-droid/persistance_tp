import sqlite3
from datetime import datetime


class GestionSQLite:
    """Classe pour gérer l'inventaire des équipements et les logs avec SQLite."""

    def __init__(self, db_name: str):
        """Initialise le nom de la base de données."""
        self.db_name = db_name

    def creer_table(self):
        """Crée les tables equipements et logs si elles n'existent pas."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Table Equipements (Exercice 1)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS equipements
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               nom
                               TEXT,
                               type
                               TEXT,
                               ip
                               TEXT,
                               actif
                               INTEGER
                           )
                           """)

            # Table Logs (Exercice 2)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS logs
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               equipement
                               TEXT,
                               niveau
                               TEXT,
                               message
                               TEXT,
                               horodatage
                               TEXT
                           )
                           """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la création des tables SQLite : {e}")
        finally:
            if conn:
                conn.close()

    # --- Exercice 1 : Gestion des équipements ---

    def ajouter(self, nom: str, type_eq: str, ip: str):
        """Insère un équipement réseau, actif=1 par défaut."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO equipements (nom, type, ip, actif) VALUES (?, ?, ?, 1)",
                (nom, type_eq, ip)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de l'équipement : {e}")
        finally:
            if conn:
                conn.close()

    def lister(self) -> list:
        """Retourne et affiche tous les équipements."""
        conn = None
        resultats = []
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipements")
            resultats = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors du listage des équipements : {e}")
        finally:
            if conn:
                conn.close()
        return resultats

    def rechercher(self, ip: str) -> tuple:
        """Retourne l'équipement correspondant à l'IP donnée."""
        conn = None
        resultat = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipements WHERE ip = ?", (ip,))
            resultat = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la recherche de l'IP {ip} : {e}")
        finally:
            if conn:
                conn.close()
        return resultat

    def desactiver(self, ip: str):
        """Met actif=0 pour l'équipement dont l'adresse IP est fournie."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE equipements SET actif = 0 WHERE ip = ?", (ip,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la désactivation de l'équipement {ip} : {e}")
        finally:
            if conn:
                conn.close()

    # --- Exercice 2 : Gestion des logs ---

    def ajouter_log(self, equipement: str, niveau: str, message: str):
        """Insère un log avec la date et heure courante comme horodatage."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO logs (equipement, niveau, message, horodatage) VALUES (?, ?, ?, ?)",
                (equipement, niveau, message, horodatage)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du log : {e}")
        finally:
            if conn:
                conn.close()

    def statistiques(self):
        """Affiche le nombre de logs par niveau (COUNT + GROUP BY)."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT niveau, COUNT(*) FROM logs GROUP BY niveau")
            stats = cursor.fetchall()
            print("\n--- Statistiques des Logs ---")
            for niveau, total in stats:
                print(f"Niveau : {niveau} | Total : {total}")
        except sqlite3.Error as e:
            print(f"Erreur lors du calcul des statistiques : {e}")
        finally:
            if conn:
                conn.close()

    def afficher_logs_tries(self) -> list:
        """Affiche et retourne les logs triés par horodatage décroissant."""
        conn = None
        resultats = []
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM logs ORDER BY horodatage DESC")
            resultats = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des logs triés : {e}")
        finally:
            if conn:
                conn.close()
        return resultats

    # --- Exercice 3 : Requêtes avancées et jointures ---

    def rapport_equipement(self, nom: str):
        """Affiche pour un équipement son statut ET ses 5 derniers logs."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Récupération du statut
            cursor.execute("SELECT actif FROM equipements WHERE nom = ?", (nom,))
            statut_res = cursor.fetchone()

            if statut_res is None:
                print(f"\nL'équipement '{nom}' n'existe pas.")
                return

            statut = "Actif" if statut_res[0] == 1 else "Inactif"
            print(f"\n=== Rapport pour l'équipement : {nom} (Statut : {statut}) ===")

            # Jointure pour récupérer les 5 derniers logs
            cursor.execute("""
                           SELECT l.niveau, l.message, l.horodatage
                           FROM logs l
                                    JOIN equipements e ON e.nom = l.equipement
                           WHERE e.nom = ?
                           ORDER BY l.horodatage DESC LIMIT 5
                           """, (nom,))

            logs = cursor.fetchall()
            if not logs:
                print("Aucun log trouvé pour cet équipement.")
            for niveau, msg, date in logs:
                print(f"[{date}] {niveau} : {msg}")

        except sqlite3.Error as e:
            print(f"Erreur lors de la génération du rapport : {e}")
        finally:
            if conn:
                conn.close()