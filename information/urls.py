from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import ModifierObjetView, controler_objet
from .views import DashboardConsommationView, RapportPDFView

urlpatterns = [
    # URLs de base
    path('', views.home, name='home'),
    path('recherche/', views.recherche, name='recherche'),
    path('inscription/', views.inscription, name='inscription'),
    path('decouvrir/', views.decouvrir, name='decouvrir'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='logout'),
    path('profil/', views.profil, name='profil'),
    path('membres/', views.membres, name='membres'),
    path("admin-niveaux/", views.gestion_niveaux, name="gestion_niveaux"),
    
    # URLs avancées
    path('avance/', views.tableau_bord_avance, name='tableau-complexe'),
    path('avance/ajout/', views.demande_ajout, name='demande_ajout'),
    path('avance/suppression/<int:objet_id>/', views.demande_suppression, name='demande_suppression'),
    
    # URLs d'authentification
    path("mot-de-passe-oublie/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("mot-de-passe-oublie/envoye/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reinitialiser/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("mot-de-passe-complete/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('avance/', views.tableau_bord_avance, name='tableau-complexe'),
    path('avance/ajout/', views.demande_ajout, name='demande_ajout'),
    path('avance/suppression/<int:objet_id>/', views.demande_suppression, name='demande_suppression'),
    path('avance/demandes/<int:demande_id>/', views.details_demande, name='details_demande'),

    path('objets/<int:objet_id>/modifier/', views.modifier_objet, name='modifier-objet'),
    path('objets/<int:objet_id>/controler/', views.controler_objet, name='controler-objet'),  

    path('objets/<int:pk>/modifier/', ModifierObjetView.as_view(), name='modifier-objet'),
    path('objets/<int:objet_id>/controler/', controler_objet, name='controler-objet'),

    path('objets/<int:pk>/affecter/', AffecterObjetView.as_view(), name='affecter-objet'),
    
    path('objets/<int:objet_id>/services/', views.ConfigurerServicesView.as_view(), name='configurer-services'),
    path('objets/<int:objet_id>/services/ajouter/', views.AjouterServiceView.as_view(), name='ajouter-service'),
    path('services/<int:pk>/editer/', views.EditerServiceView.as_view(), name='editer-service'),

    path('objets/<int:pk>/configurer/', views.ConfigurerObjetView.as_view(), name='configurer-objet'),
    path('objets/<int:pk>/programmes/creer/', views.CreerProgrammeView.as_view(), name='creer-programme'),
    path('programmes/<int:pk>/modifier/', views.ModifierProgrammeView.as_view(), name='modifier-programme'),
    path('programmes/<int:pk>/supprimer/', views.SupprimerProgrammeView.as_view(), name='supprimer-programme'),

    path('dashboard/', DashboardConsommationView.as_view(), name='dashboard-consommation'),
    path('rapport/', RapportPDFView.as_view(), name='generer-rapport'),

]

# Ajout pour les médias en développement
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
