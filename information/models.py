from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class Evenement(models.Model):
    DOMAINE_CHOICES = [
        ('science', 'Science'),
        ('art', 'Art'),
        ('finance', 'Finance'),
        ('business', 'Business'),
        ('cinema', 'Cinéma'),
        ('maths', 'Maths'),
        ('informatique', 'Informatique'),
        ('ia', 'Intelligence Artificielle'),
    ]

    titre = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    domaine = models.CharField(max_length=30, choices=DOMAINE_CHOICES)
    lieu = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.titre} ({self.domaine})"

class StatistiquesUtilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    connexions = models.IntegerField(default=0)
    consultations = models.IntegerField(default=0)

    def total_points(self):
        return self.connexions * 0.25 + self.consultations * 0.50


class ProfilUtilisateur(models.Model):
    NIVEAUX = [
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
        ('expert', 'Expert'),
    ]

    SEXES = [
        ('H', 'Homme'),
        ('F', 'Femme'),
        ('A', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    niveau = models.CharField(max_length=20, choices=NIVEAUX, default='debutant')
    points = models.FloatField(default=0.0)
    
    # Infos personnelles
    prenom = models.CharField(max_length=100, blank=True)
    nom = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXES, null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    societe = models.CharField(max_length=100, blank=True)
    poste = models.CharField("Intitulé du poste", max_length=100, blank=True)

    # Visibilité
    show_prenom = models.BooleanField(default=True)
    show_nom = models.BooleanField(default=False)
    show_date_naissance = models.BooleanField(default=True)
    show_sexe = models.BooleanField(default=True)
    show_photo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    
def update_niveau(self):
    if self.points < 100:
        self.niveau = 'debutant'
    elif self.points < 300:
        self.niveau = 'intermediaire'
    elif self.points < 600:
        self.niveau = 'avance'
    else:
        self.niveau = 'expert'

def save(self, *args, **kwargs):
    self.update_niveau()
    super().save(*args, **kwargs)


class ObjetConnecte(models.Model):
    TYPES_OBJETS = [
        ('capteur', 'Capteur'),
        ('actionneur', 'Actionneur'),
        ('affichage', 'Affichage'),
        ('autre', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('MAINTENANCE', 'Maintenance'),
    ]
    
    nom = models.CharField(max_length=100)
    type_objet = models.CharField(max_length=20, choices=TYPES_OBJETS)
    description = models.TextField()
    emplacement = models.CharField(max_length=100)
    parametres = models.JSONField(default=dict)
    date_ajout = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    createur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    nom_temporaire = models.CharField(max_length=100, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    version = models.CharField(max_length=50, default='1.0')
    salle = models.ForeignKey(Salle, on_delete=models.SET_NULL, null=True)
    createur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    date_affectation = models.DateTimeField(null=True, blank=True)
    affecte_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='affectations')

class DemandeObjet(models.Model):
    TYPE_DEMANDE = [
        ('ajout', 'Demande d\'ajout'),
        ('suppression', 'Demande de suppression'),
    ]
    
    nom = models.CharField(max_length=100)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    type_demande = models.CharField(max_length=20, choices=TYPE_DEMANDE)
    objet_connecte = models.ForeignKey(ObjetConnecte, on_delete=models.CASCADE, null=True, blank=True)
    modele = models.CharField(max_length=100, blank=True)
    type_objet = models.CharField(max_length=20, choices=ObjetConnecte.TYPES_OBJETS)
    fonction = models.TextField()
    emplacement = models.CharField(max_length=100)
    parametres = models.JSONField(default=dict)
    raison = models.TextField(blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    traitee = models.BooleanField(default=False)

class JournalModification(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    objet = models.ForeignKey(ObjetConnecte, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

class Zone(models.Model):
    nom = models.CharField(max_length=100)
    batiment = models.CharField(max_length=50)
    etage = models.IntegerField()
    capacite_max = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.batiment} - {self.nom} (Étage {self.etage})"

class Service(models.Model):
    PROTOCOLES = [
        ('HTTP', 'HTTP'),
        ('MQTT', 'MQTT'),
        ('CoAP', 'CoAP'),
        ('WebSocket', 'WebSocket'),
    ]
    
    nom = models.CharField(max_length=100)
    objet = models.ForeignKey(ObjetConnecte, on_delete=models.CASCADE, related_name='services')
    protocole = models.CharField(max_length=20, choices=PROTOCOLES)
    endpoint = models.URLField()
    port = models.PositiveIntegerField()
    actif = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} ({self.protocole})"

class RegleService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    condition = models.JSONField()
    action = models.JSONField()
    priorite = models.IntegerField(default=0)

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ObjetConnecte(models.Model):
    TYPES_OBJET = [
        ('THERMOSTAT', 'Thermostat'),
        ('LUMIERE', 'Lumière'),
        ('PRISE', 'Prise intelligente'),
        ('AUTRE', 'Autre équipement')
    ]
    
    nom = models.CharField(max_length=100)
    type_objet = models.CharField(max_length=20, choices=TYPES_OBJET)
    piece = models.ForeignKey('Piece', on_delete=models.SET_NULL, null=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

class Piece(models.Model):
    nom = models.CharField(max_length=100)
    etage = models.IntegerField()
    batiment = models.CharField(max_length=50)

class Parametre(models.Model):
    objet = models.ForeignKey(ObjetConnecte, on_delete=models.CASCADE, related_name='parametres')
    nom = models.CharField(max_length=100)
    valeur = models.JSONField()
    modifiable = models.BooleanField(default=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['objet', 'nom'], name='parametre_unique_par_objet')
        ]

class Programme(models.Model):
    objet = models.ForeignKey(ObjetConnecte, on_delete=models.CASCADE, related_name='programmes')
    nom = models.CharField(max_length=100)
    jours = models.JSONField()  # Ex: [1,3,5] pour Lun, Mer, Ven
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    actif = models.BooleanField(default=True)
    parametres = models.JSONField(default=dict)  # Ex: {"temperature": 21}

class HistoriqueParametre(models.Model):
    parametre = models.ForeignKey(Parametre, on_delete=models.CASCADE)
    ancienne_valeur = models.JSONField()
    nouvelle_valeur = models.JSONField()
    modifie_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_modification = models.DateTimeField(auto_now_add=True)


class MesureConsommation(models.Model):
    objet = models.ForeignKey('ObjetConnecte', on_delete=models.CASCADE)
    valeur = models.FloatField()  # kWh ou autre unité
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    type_mesure = models.CharField(max_length=50)  # 'energie', 'eau', etc.

class AlerteOptimisation(models.Model):
    SEUIL_TYPES = [
        ('CONSO_ANORMALE', 'Consommation anormale'),
        ('USAGE_INEFFICACE', 'Usage inefficace'),
        ('MAINTENANCE', 'Maintenance requise')
    ]
    
    objet = models.ForeignKey('ObjetConnecte', on_delete=models.CASCADE)
    type_alerte = models.CharField(max_length=50, choices=SEUIL_TYPES)
    gravite = models.CharField(max_length=20, choices=[('LOW', 'Faible'), ('MED', 'Moyenne'), ('HIGH', 'Haute')])
    message = models.TextField()
    parametres = models.JSONField()  # Ex: {"seuil": 10, "valeur_actuelle": 15}
    date_detection = models.DateTimeField(auto_now_add=True)
    resolue = models.BooleanField(default=False)
