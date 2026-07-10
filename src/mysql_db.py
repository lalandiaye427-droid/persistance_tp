import mysql.connector
from mysql.connector import Error


class GestionMySQL:
    """Classe pour gérer la base de données relationnelle multi-tables avec MySQL."""

    def __init__(self, host, user, password, database):
        """Initialise les paramètres de connexion à MySQL."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connexion(self):
        """Établit la connexion et retourne le couple (connexion, curseur)."""
        conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return conn, conn.cursor()

    def fermer(self, conn, cursor):
        """Ferme proprement le curseur et la connexion (Exigence du TP)."""
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

    def creer_table(self):
        """Crée l'architecture multi-tables (Exercice 5)."""
        conn, cursor = None, None
        try:
            conn, cursor = self.connexion()

            # Désactivation temporaire pour éviter les conflits lors des recréations
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # Table 1 : Sites
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS sites
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               nom
                               VARCHAR
                           (
                               100
                           ),
                               ville VARCHAR
                           (
                               100
                           )
                               )
                           """)

            # Table 2 : Équipements (reliée à sites)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS equipements
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               nom
                               VARCHAR
                           (
                               100
                           ),
                               type VARCHAR
                           (
                               50
                           ),
                               ip VARCHAR
                           (
                               50
                           ),
                               actif INT DEFAULT 1,
                               id_site INT,
                               FOREIGN KEY
                           (
                               id_site
                           ) REFERENCES sites
                           (
                               id
                           ) ON DELETE CASCADE
                               )
                           """)

            # Table 3 : Interfaces (reliée à equipements)
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS interfaces
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               nom
                               VARCHAR
                           (
                               50
                           ),
                               ip VARCHAR
                           (
                               50
                           ),
                               masque VARCHAR
                           (
                               50
                           ),
                               id_equipement INT,
                               FOREIGN KEY
                           (
                               id_equipement
                           ) REFERENCES equipements
                           (
                               id
                           ) ON DELETE CASCADE
                               )
                           """)

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
        except Error as e:
            print(f"Erreur lors de la création des tables MySQL : {e}")
        finally:
            self.fermer(conn, cursor)

    # --- Exercice 4 : CRUD basique ---

    def ajouter(self, nom: str, type_eq: str, ip: str, id_site: int = None):
        """Insère un équipement dans MySQL."""
        conn, cursor = None, None
        try:
            conn, cursor = self.connexion()
            cursor.execute(
                "INSERT INTO equipements (nom, type, ip, actif, id_site) VALUES (%s, %s, %s, 1, %s)",
                (nom, type_eq, ip, id_site)
            )
            conn.commit()
        except Error as e:
            print(f"Erreur d'ajout MySQL : {e}")
        finally:
            self.fermer(conn, cursor)

    def lister(self) -> list:
        """Retourne tous les équipements."""
        conn, cursor = None, None
        resultats = []
        try:
            conn, cursor = self.connexion()
            cursor.execute("SELECT * FROM equipements")
            resultats = cursor.fetchall()
        except Error as e:
            print(f"Erreur de listage MySQL : {e}")
        finally:
            self.fermer(conn, cursor)
        return resultats

    def rechercher(self, ip: str) -> tuple:
        """Recherche un équipement par son IP."""
        conn, cursor = None, None
        resultat = None
        try:
            conn, cursor = self.connexion()
            cursor.execute("SELECT * FROM equipements WHERE ip = %s", (ip,))
            resultat = cursor.fetchone()
        except Error as e:
            print(f"Erreur de recherche MySQL : {e}")
        finally:
            self.fermer(conn, cursor)
        return resultat

    def desactiver(self, ip: str):
        """Désactive un équipement par son IP."""
        conn, cursor = None, None
        try:
            conn, cursor = self.connexion()
            cursor.execute("UPDATE equipements SET actif = 0 WHERE ip = %s", (ip,))
            conn.commit()
        except Error as e:
            print(f"Erreur de désactivation MySQL : {e}")
        finally:
            self.fermer(conn, cursor)

    # --- Exercice 5 : Gestion multi-tables ---

    def ajouter_site(self, nom: str, ville: str) -> int:
        """Insère un site et retourne son ID généré."""
        conn, cursor = None, None
        last_id = None
        try:
            conn, cursor = self.connexion()
            cursor.execute("INSERT INTO sites (nom, ville) VALUES (%s, %s)", (nom, ville))
            conn.commit()
            last_id = cursor.lastrowid
        except Error as e:
            print(f"Erreur lors de l'ajout du site : {e}")
        finally:
            self.fermer(conn, cursor)
        return last_id

    def ajouter_equipement(self, nom: str, type_eq: str, id_site: int) -> int:
        """Insère un équipement lié à un site et retourne son ID."""
        conn, cursor = None, None
        last_id = None
        try:
            conn, cursor = self.connexion()
            cursor.execute(
                "INSERT INTO equipements (nom, type, ip, actif, id_site) VALUES (%s, %s, '', 1, %s)",
                (nom, type_eq, id_site)
            )
            conn.commit()
            last_id = cursor.lastrowid
        except Error as e:
            print(f"Erreur lors de l'ajout de l'équipement lié : {e}")
        finally:
            self.fermer(conn, cursor)
        return last_id

    def ajouter_interface(self, nom: str, ip: str, masque: str, id_equipement: int):
        """Insère une interface réseau liée à un équipement."""
        conn, cursor = None, None
        try:
            conn, cursor = self.connexion()
            cursor.execute(
                "INSERT INTO interfaces (nom, ip, masque, id_equipement) VALUES (%s, %s, %s, %s)",
                (nom, ip, masque, id_equipement)
            )
            conn.commit()
        except Error as e:
            print(f"Erreur lors de l'ajout de l'interface : {e}")
        finally:
            self.fermer(conn, cursor)

    def topologie_site(self, id_site: int):
        """Affiche la topologie d'un site à l'aide d'un JOIN."""
        conn, cursor = None, None
        try:
            conn, cursor = self.connexion()
            query = """
                    SELECT e.nom AS equipement, e.type, i.nom AS interface, i.ip
                    FROM equipements e
                             LEFT JOIN interfaces i ON e.id = i.id_equipement
                    WHERE e.id_site = %s \
                    """
            cursor.execute(query, (id_site,))
            lignes = cursor.fetchall()
            print(f"\n--- Topologie du Site ID {id_site} ---")
            for eq_nom, eq_type, int_nom, int_ip in lignes:
                print(f"Équipement: {eq_nom} ({eq_type}) | Interface: {int_nom or 'N/A'} | IP: {int_ip or 'N/A'}")
        except Error as e:
            print(f"Erreur lors du calcul de la topologie : {e}")
        finally:
            self.fermer(conn, cursor)

    def rechercher_ip(self, ip: str):
        """Retrouve l'équipement et le site d'une adresse IP donnée."""
        conn, cursor = None, None
        try:
            conn, cursor = self.connexion()
            query = """
                    SELECT e.nom AS equipement, s.nom AS site, s.ville
                    FROM interfaces i
                             JOIN equipements e ON i.id_equipement = e.id
                             JOIN sites s ON e.id_site = s.id
                    WHERE i.ip = %s \
                    """
            cursor.execute(query, (ip,))
            res = cursor.fetchone()
            print(f"\n--- Recherche de l'IP : {ip} ---")
            if res:
                print(f"IP localisée sur '{res[0]}' au site '{res[1]}' ({res[2]}).")
            else:
                print("Adresse IP introuvable.")
        except Error as e:
            print(f"Erreur lors de la recherche IP : {e}")
        finally:
            self.fermer(conn, cursor)