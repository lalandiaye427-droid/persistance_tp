import random
from faker import Faker
from src.sqlite_db import GestionSQLite
from src.mysql_db import GestionMySQL

# Constantes obligatoires (Noms des bases de données)
DB_NAME_SQLITE = 'reseau.db'
DB_NAME_MYSQL = 'reseau_db'


def tester_sqlite():
    print("=========================================")
    print("   TEST DE LA BASE DE DONNÉES SQLITE")
    print("=========================================")
    fake = Faker()
    db_sqlite = GestionSQLite(DB_NAME_SQLITE)
    db_sqlite.creer_table()

    # --- Exercice 1 : Gestion des équipements ---
    print("\n[SQLite] Insertion des équipements...")
    db_sqlite.ajouter("Routeur-Principal", "routeur", "192.168.1.1")
    db_sqlite.ajouter("Routeur-Secondaire", "routeur", "192.168.1.2")
    db_sqlite.ajouter("Switch-Etage1", "switch", "192.168.1.10")
    db_sqlite.ajouter("Switch-Etage2", "switch", "192.168.1.11")

    print("\nListe initiale des équipements :")
    for eq in db_sqlite.lister():
        print(eq)

    print("\nRecherche de l'IP 192.168.1.10 :")
    print(db_sqlite.rechercher("192.168.1.10"))

    print("\nDésactivation du Switch-Etage1 (192.168.1.10)...")
    db_sqlite.desactiver("192.168.1.10")

    # --- Exercice 2 : Gestion des logs réseau avec Faker ---
    print("\n[SQLite] Génération de 20 logs fictifs avec Faker...")
    equipements_exemples = ["Routeur-Principal", "Routeur-Secondaire", "Switch-Etage1", "Switch-Etage2"]
    niveaux_exemples = ["INFO", "WARNING", "ERROR"]

    for _ in range(20):
        eq_aleatoire = random.choice(equipements_exemples)
        niv_aleatoire = random.choice(niveaux_exemples)
        msg_fictif = fake.sentence(nb_words=6)
        db_sqlite.ajouter_log(eq_aleatoire, niv_aleatoire, msg_fictif)

    # Affichage des statistiques de logs
    db_sqlite.statistiques()

    print("\nAffichage des 5 logs les plus récents (triés décroissant) :")
    logs_tries = db_sqlite.afficher_logs_tries()
    for log in logs_tries[:5]:
        print(log)

    # --- Exercice 3 : Requêtes avancées ---
    print("\n[SQLite] Génération du rapport complet pour 'Routeur-Principal' :")
    db_sqlite.rapport_equipement("Routeur-Principal")


def tester_mysql():
    print("\n=========================================")
    print("   TEST DE LA BASE DE DONNÉES MYSQL")
    print("=========================================")

    # Paramètres par défaut (Ajustez le mot de passe si vous en avez un sur XAMPP/Wamp)
    db_mysql = GestionMySQL(host="localhost", user="root", password="", database=DB_NAME_MYSQL)

    try:
        db_mysql.creer_table()
    except Exception as e:
        print(f"Erreur de connexion MySQL : {e}")
        print(f"⚠️ Assurez-vous d'avoir créé la base vide '{DB_NAME_MYSQL}' sur votre serveur local.")
        return

    # Exercice 4 : Ajout de données basiques
    db_mysql.ajouter("Routeur-Core-MySQL", "routeur", "10.0.0.1")
    print("\nListe des équipements simples dans MySQL :")
    for eq in db_mysql.lister():
        print(eq)

    # Exercice 5 : Topologie Multi-tables complexe
    print("\nInsertion de la topologie multi-tables (Sites, Équipements, Interfaces)...")

    # Création de 2 sites distants
    id_site_dakar = db_mysql.ajouter_site("Campus Dakar", "Dakar")
    id_site_thies = db_mysql.ajouter_site("Extension Thies", "Thies")

    if id_site_dakar and id_site_thies:
        # Site de Dakar - 3 Équipements dotés de 2 interfaces chacun
        for i in range(1, 4):
            id_eq = db_mysql.ajouter_equipement(f"DK-Equipement-{i}", random.choice(["routeur", "switch"]),
                                                id_site_dakar)
            db_mysql.ajouter_interface("eth0", f"10.1.1.{i}1", "255.255.255.0", id_eq)
            db_mysql.ajouter_interface("eth1", f"10.1.1.{i}2", "255.255.255.0", id_eq)

        # Site de Thiès - 3 Équipements dotés de 2 interfaces chacun
        for i in range(1, 4):
            id_eq = db_mysql.ajouter_equipement(f"TH-Equipement-{i}", random.choice(["routeur", "switch"]),
                                                id_site_thies)
            db_mysql.ajouter_interface("eth0", f"10.2.2.{i}1", "255.255.255.0", id_eq)
            db_mysql.ajouter_interface("eth1", f"10.2.2.{i}2", "255.255.255.0", id_eq)

        # Affichage de la topologie du site de Dakar (via la jointure)
        db_mysql.topologie_site(id_site_dakar)

        # Recherche de la localisation géographique d'une IP
        db_mysql.rechercher_ip("10.1.1.21")


if __name__ == '__main__':
    tester_sqlite()
    tester_mysql()