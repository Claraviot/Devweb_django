from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ProfilUtilisateur
from .models import MesureConsommation, AlerteOptimisation

@receiver(post_save, sender=User)
def creer_profil_utilisateur(sender, instance, created, **kwargs):
    if created:
        ProfilUtilisateur.objects.create(user=instance)


@receiver(post_save, sender=MesureConsommation)
def detecter_anomalies(sender, instance, **kwargs):
    # Seuils prédéfinis (pourrait venir d'une config)
    SEUILS = {
        'THERMOSTAT': {'warning': 5, 'critical': 10},  # kWh/jour
        'LUMIERE': {'warning': 2, 'critical': 3},
    }
    
    if instance.objet.type_objet in SEUILS:
        seuil = SEUILS[instance.objet.type_objet]
        
        if instance.valeur > seuil['critical']:
            AlerteOptimisation.objects.create(
                objet=instance.objet,
                type_alerte='CONSO_ANORMALE',
                gravite='HIGH',
                message=f"Consommation anormalement élevée: {instance.valeur} kWh",
                parametres={
                    'seuil': seuil['critical'],
                    'valeur_actuelle': instance.valeur
                }
            )
        elif instance.valeur > seuil['warning']:
            AlerteOptimisation.objects.create(
                objet=instance.objet,
                type_alerte='USAGE_INEFFICACE',
                gravite='MED',
                message=f"Consommation élevée: {instance.valeur} kWh",
                parametres={
                    'seuil': seuil['warning'],
                    'valeur_actuelle': instance.valeur
                }
            )