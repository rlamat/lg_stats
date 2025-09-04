from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class VerificationStatus(models.TextChoices):
    PENDING = "pending", _("En attente")
    APPROVED = "approved", _("Approuvée")
    REJECTED = "rejected", _("Refusée")

class Role(models.TextChoices):
    # Camp du Village — Rôles à information
    ANALYSTE = "analyste", "Analyste"
    ASTRONOME = "astronome", "Astronome"
    AUBERGISTE = "aubergiste", "Aubergiste"
    BOHEMIENNE = "bohemienne", "Bohémienne"
    CHAMAN = "chaman", "Chaman"
    CONTEUSE = "conteuse", "Conteuse"
    DETECTIVE = "detective", "Détective"
    DRUIDE = "druide", "Druide"
    ESPION = "espion", "Espion"
    FOSSOYEUR = "fossoyeur", "Fossoyeur"
    INTERPRETE = "interprete", "Interprète"
    JUMEAUX = "jumeaux", "Jumeaux"
    MONTREUR_D_OURS = "montreur_d_ours", "Montreur d'Ours"
    ORACLE = "oracle", "Oracle"
    PRETRESSE = "pretresse", "Prêtresse"
    PROPHETESSE = "prophetessse", "Prophétesse"  # (attention: 3 s si tu veux coller au slug choisi)
    RENARD = "renard", "Renard"
    VAUDOUISTE = "vaudouiste", "Vaudouiste"
    VIEUX_SAGE = "vieux_sage", "Vieux Sage"
    VOYANTE = "voyante", "Voyante"

    # Camp du Village — Autres rôles
    ANCIEN = "ancien", "Ancien"
    AVOCAT = "avocat", "Avocat"
    BIENFAITEUR = "bienfaiteur", "Bienfaiteur"
    BOUC_EMISSAIRE = "bouc_emissaire", "Bouc Émissaire"
    BRACONNIER = "braconnier", "Braconnier"
    CHASSEUR = "chasseur", "Chasseur"
    CITOYEN = "citoyen", "Citoyen"
    CORBEAU = "corbeau", "Corbeau"
    ERMITE = "ermite", "Ermite"
    GARDE = "garde", "Garde"
    IDIOT_DU_VILLAGE = "idiot_du_village", "Idiot du Village"
    LAPIN = "lapin", "Lapin"
    MIRE = "mire", "Mire"
    PETITE_FILLE = "petite_fille", "Petite Fille"
    REBOUTEUX = "rebouteux", "Rebouteux"
    SALVATEUR = "salvateur", "Salvateur"
    SERVITEUR = "serviteur", "Serviteur"
    SIMPLE_VILLAGEOIS = "simple_villageois", "Simple Villageois"
    SOEURS = "soeurs", "Soeurs"
    SORCIERE = "sorciere", "Sorcière"

    # Camp des Loups
    LOUP_GAROU = "loup_garou", "Loup-Garou"
    GRAND_MECHANT_LOUP = "grand_mechant_loup", "Grand Méchant Loup"
    INFECT_PERE_DES_LOUPS = "infect_pere_des_loups", "Infect Père des Loups"
    LOUP_GAROU_AMNESIQUE = "loup_garou_amnesique", "Loup-Garou Amnésique"
    LOUP_GAROU_CRAINTIF = "loup_garou_craintif", "Loup-Garou Craintif"
    LOUP_GAROU_DELOYAL = "loup_garou_deloyal", "Loup-Garou Déloyal"
    LOUP_GAROU_FAUSSAIRE = "loup_garou_faussaire", "Loup-Garou Faussaire"
    LOUP_GAROU_FEUTRE = "loup_garou_feutre", "Loup-Garou Feutré"
    LOUP_GAROU_GRIMEUR = "loup_garou_grimeur", "Loup-Garou Grimeur"
    LOUP_GAROU_HURLEUR = "loup_garou_hurleur", "Loup-Garou Hurleur"
    LOUP_GAROU_MYSTIQUE = "loup_garou_mystique", "Loup-Garou Mystique"
    LOUP_GAROU_PERFIDE = "loup_garou_perfide", "Loup-Garou Perfide"
    LOUP_GAROU_SANGUINAIRE = "loup_garou_sanguinaire", "Loup-Garou Sanguinaire"
    LOUP_GAROU_TENEBREUX = "loup_garou_tenebreux", "Loup-Garou Ténébreux"
    LOUP_GAROU_VENGEUR = "loup_garou_vengeur", "Loup-Garou Vengeur"
    VILAIN_PETIT_LOUP = "vilain_petit_loup", "Vilain Petit Loup"
    LOUP_GAROU_BLANC = "loup_garou_blanc", "Loup-Garou Blanc"

    # Rôles solitaires
    ANGE = "ange", "Ange"
    ASSASSIN = "assassin", "Assassin"
    FEU_FOLLET = "feu_follet", "Feu Follet"
    IMITATEUR = "imitateur", "Imitateur"
    JOUEUR_DE_FLUTE = "joueur_de_flute", "Joueur de Flûte"
    NECROMANCIEN = "necromancien", "Nécromancien"
    PYROMANE = "pyromane", "Pyromane"
    RIVAL = "rival", "Rival"
    RONIN = "ronin", "Ronin"
    VOYOU = "voyou", "Voyou"

    # Rôles hybrides
    CHIEN_LOUP = "chien_loup", "Chien-Loup"
    CUPIDON = "cupidon", "Cupidon"
    ENFANT_SAUVAGE = "enfant_sauvage", "Enfant Sauvage"
    RENEGAT = "renegat", "Renégat"
    TRUBLION = "trublion", "Trublion"
    VOLEUR = "voleur", "Voleur"

    AUTRE = "autre", "Autre"


class Camp(models.TextChoices):
    VILLAGE = "village", "Village"
    LOUP = "loup", "Loups"
    SOLO = "solo", "Solo/Neutre"
    Couple = "couple", "Couple"

class GameEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_entries")
    played_at = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.AUTRE)
    camp = models.CharField(max_length=16, choices=Camp.choices, default=Camp.VILLAGE)
    kills = models.PositiveIntegerField(default=0)
    won = models.BooleanField(default=False)
    killed_players = models.TextField(blank=True, help_text="Optionnel: pseudos tués, séparés par des virgules")
    notes = models.TextField(blank=True)
    proof_image = models.ImageField(upload_to='proofs/%Y/%m/%d/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=16,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_entries')
    verified_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ["-played_at"]

    def killed_list(self):
        return [p.strip() for p in self.killed_players.split(",") if p.strip()]

    def __str__(self):
        return f"{self.user.username} - {self.played_at:%Y-%m-%d} ({self.role})"
