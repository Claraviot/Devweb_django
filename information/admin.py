

from django.contrib import admin
from .models import ProfilUtilisateur
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ProfilUtilisateur, Evenement, DemandeObjet

# Configuration pour Evenement (déjà bien configurée)
@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'domaine', 'date')
    list_filter = ('domaine', 'date')
    search_fields = ('titre', 'description')

# Configuration avancée pour ProfilUtilisateur
@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_username', 'niveau', 'points', 'prenom', 'nom', 'societe')
    list_filter = ('niveau', 'sexe', 'show_photo')
    search_fields = ('user__username', 'prenom', 'nom', 'societe', 'poste')
    list_editable = ('niveau', 'points')  # Permet de modifier directement dans la liste
    fieldsets = (
        (None, {
            'fields': ('user', 'niveau', 'points')
        }),
        ('Informations personnelles', {
            'fields': ('prenom', 'nom', 'date_naissance', 'sexe', 'photo'),
            'classes': ('collapse',)
        }),
        ('Profession', {
            'fields': ('societe', 'poste'),
            'classes': ('collapse',)
        }),
        ('Paramètres de visibilité', {
            'fields': ('show_prenom', 'show_nom', 'show_date_naissance', 'show_sexe', 'show_photo'),
            'classes': ('collapse',)
        }),
    )

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

# Ajout du profil inline dans l'admin User
class ProfilUtilisateurInline(admin.StackedInline):
    model = ProfilUtilisateur
    can_delete = False
    verbose_name_plural = 'Profile Utilisateur'
    fieldsets = (
        (None, {
            'fields': ('niveau', 'points', 'photo')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('prenom', 'nom', 'date_naissance', 'sexe', 'societe', 'poste'),
        }),
    )

class CustomUserAdmin(UserAdmin):
    inlines = (ProfilUtilisateurInline,)
    list_display = ('username', 'email', 'get_niveau', 'is_staff')
    
    def get_niveau(self, obj):
        if hasattr(obj, 'profilutilisateur'):
            return obj.profilutilisateur.niveau
        return "Non défini"
    get_niveau.short_description = 'Niveau'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(DemandeObjet)
class DemandeObjetAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'type_demande', 'objet_connecte', 'date_demande', 'traitee')
    list_filter = ('type_demande', 'traitee', 'date_demande')
    actions = ['marquer_comme_traitee']

    def marquer_comme_traitee(self, request, queryset):
        queryset.update(traitee=True)
    marquer_comme_traitee.short_description = "Marquer comme traitée"