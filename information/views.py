from django.shortcuts import render
from .models import Evenement
from datetime import datetime
from .forms import CustomUserForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfilUtilisateurForm
from .models import ProfilUtilisateur
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .forms import DemandeAjoutObjetForm, DemandeSuppressionObjetForm
from .models import ObjetConnecte
from django.views.generic import UpdateView
from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse


def home(request):
    return render(request, 'information/home.html')

# Vue pour la page de recherche (pas utilisée pour l’instant)
def recherche(request):
    return render(request, 'information/recherche.html')

# Vue pour la page d'inscription
def inscription(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()  # ✅ crée l’utilisateur dans la base
            # Récupération de l'email saisi
            destinataire = form.cleaned_data.get('email')
            # Envoi de l'e-mail
            send_mail(
                subject='Bienvenue chez Cowork Connect',
                message=(
                    "Bonjour,\n\n"
                    "Nous vous remercions pour votre inscription sur le site de Cowork Connect.\n"
                    "Nous serions ravis de vous accueillir bientôt au sein de nos locaux.\n"
                    "Afin de mieux faire connaissance, nous vous invitons à bien vouloir compléter votre profil utilisateur en vous connectant à votre compte.\n"
                    "Pour toute question, n'hésitez pas à nous contacter.\n\n"
                    "À bientôt,\n"
                    "L'équipe Cowork Connect"),
                from_email='coworkconnect2025@gmail.com',  # Mets ici l'email de ton application
                recipient_list=[destinataire],
                fail_silently=False,
            )

            return redirect('connexion') 

    else:
        form = CustomUserForm()

    return render(request, 'information/inscription.html', {'form': form})

# Vue pour la page Découvrir (photo, description, filtres, événements)
def decouvrir(request):
    domaine = request.GET.get('domaine')
    mois = request.GET.get('mois')

    evenements = Evenement.objects.all()

    if domaine and domaine != "tous":
        evenements = evenements.filter(domaine=domaine)

    if mois and mois != "tous":
        evenements = evenements.filter(date__month=int(mois))

    context = {
        'evenements': evenements,
        'mois_actuel': datetime.now().month,
    }

    return render(request, 'information/decouvrir.html', context)

def connexion(request):
    message = ''

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            message = "Identifiants incorrects"

    return render(request, 'information/connexion.html', {'message': message})

def deconnexion(request):
    logout(request)
    return redirect('home')

@login_required
def profil(request):
    # ✅ On récupère ou crée le profil lié à l’utilisateur connecté
    profil, created = ProfilUtilisateur.objects.get_or_create(user=request.user)

    message = ""

    if request.method == 'POST':
        # Formulaire envoyé : on traite la mise à jour
        form = ProfilUtilisateurForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            message = "Profil mis à jour avec succès ✅"
        else:
            message = "Erreur dans le formulaire ❌"
    else:
        # Première visite de la page : on pré-remplit le formulaire
        form = ProfilUtilisateurForm(instance=profil)

    context = {
        'form': form,
        'message': message,
        'pseudo': request.user.username,
        'niveau': profil.niveau,
        'points': profil.points,
    }
    return render(request, 'information/profil.html', context)

@login_required
def membres(request):
    societe_filtre = request.GET.get('societe')
    
    profils = ProfilUtilisateur.objects.all().select_related('user')

    if societe_filtre:
        profils = profils.filter(societe__icontains=societe_filtre)

    context = {
        'profils': profils,
        'societe_filtre': societe_filtre or '',
    }

    return render(request, 'information/membres.html', context)

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import ProfilUtilisateur
from .forms import NiveauForm

def est_superuser(user):
    return user.is_superuser

@user_passes_test(est_superuser)
def gestion_niveaux(request):
    profils = ProfilUtilisateur.objects.all()

    if request.method == "POST":
        profil_id = request.POST.get("profil_id")
        profil = get_object_or_404(ProfilUtilisateur, id=profil_id)
        form = NiveauForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
        return redirect('gestion_niveaux')

    context = {
        'profils': profils,
        'form': NiveauForm()
    }
    return render(request, "information/gestion_niveaux.html", context)


@login_required
def tableau_de_bord_complexe(request):
    if not hasattr(request.user, 'profil') or request.user.profil.niveau != 'avance':
        return redirect('home')  # ou une page d'erreur

    if request.method == 'POST':
        if 'ajout_objet' in request.POST:
            form_ajout = DemandeAjoutObjetForm(request.POST)
            if form_ajout.is_valid():
                form_ajout.save(utilisateur=request.user)
                return redirect('tableau_complexe')
        elif 'suppression_objet' in request.POST:
            form_suppression = DemandeSuppressionObjetForm(request.POST)
            if form_suppression.is_valid():
                form_suppression.save(utilisateur=request.user)
                return redirect('tableau_complexe')
    else:
        form_ajout = DemandeAjoutObjetForm()
        form_suppression = DemandeSuppressionObjetForm()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ObjetConnecte, DemandeObjet
from .forms import DemandeAjoutObjetForm, DemandeSuppressionObjetForm

def est_utilisateur_avance(user):
    """Vérifie si l'utilisateur a le niveau avancé ou expert"""
    return (user.is_authenticated and 
            hasattr(user, 'profilutilisateur') and 
            user.profilutilisateur.niveau in ['avance', 'expert'])

@login_required
@user_passes_test(est_utilisateur_avance)
def tableau_bord_avance(request):
    """Tableau de bord principal pour utilisateurs avancés"""
    objets = ObjetConnecte.objects.filter(actif=True)
    demandes = DemandeObjet.objects.filter(utilisateur=request.user).order_by('-date_demande')
    
    context = {
        'objets': objets,
        'demandes': demandes,
        'niveau_utilisateur': request.user.profilutilisateur.niveau
    }
    return render(request, 'tableau_bord_avance.html', context)


@login_required
@user_passes_test(est_utilisateur_avance)
def demande_ajout(request):
    """Gestion des demandes d'ajout d'objets"""
    if request.method == 'POST':
        form = DemandeAjoutObjetForm(request.POST)
        if form.is_valid():
            # Utilisation de la méthode save() améliorée du formulaire
            form.save(utilisateur=request.user)
            return redirect('tableau_bord_avance')
    else:
        form = DemandeAjoutObjetForm()
    
    return render(request, 'demande_ajout.html', {
        'form': DemandeAjoutObjetForm(),
        'action': 'Ajout'
    })

@login_required
@user_passes_test(est_utilisateur_avance)
def demande_suppression(request, objet_id):
    """Gestion des demandes de suppression d'objets"""
    objet = get_object_or_404(ObjetConnecte, id=objet_id, actif=True)
    
    if request.method == 'POST':
        form = DemandeSuppressionObjetForm(request.POST)
        if form.is_valid():
            # Utilisation de la méthode save() améliorée du formulaire
            demande = form.save(commit=False)
            demande.objet_connecte = objet
            demande.save(utilisateur=request.user)
            return redirect('tableau_bord_avance')
    else:
        form = DemandeSuppressionObjetForm(initial={'objet_connecte': objet})
    
    return render(request, 'demande_form.html', {
        'form': DemandeSuppressionObjetForm(),
        'objet': objet,
        'action': 'Suppression'
    })

@login_required
@user_passes_test(est_utilisateur_avance)
def details_demande(request, demande_id):
    """Visualisation des détails d'une demande"""
    demande = get_object_or_404(DemandeObjet, id=demande_id, utilisateur=request.user)
    return render(request, 'details_demande.html', {'demande': demande})

@login_required
@user_passes_test(lambda u: u.profil.niveau == 'avance')
def modifier_objet(request, objet_id):
    objet = get_object_or_404(ObjetConnecte, id=objet_id)
    
    if request.method == 'POST':
        form = ModificationObjetForm(request.POST, instance=objet)
        if form.is_valid():
            form.save()
            messages.success(request, "Objet modifié avec succès")
            return redirect('tableau-complexe')
    else:
        form = ModificationObjetForm(instance=objet)
    
    return render(request, 'modifier_objet.html', {'form': form, 'objet': objet})

@login_required
@user_passes_test(lambda u: u.profil.niveau == 'avance')
def controler_objet(request, objet_id):
    objet = get_object_or_404(ObjetConnecte, id=objet_id)
    
    if request.method == 'POST':
        form = ControleObjetForm(request.POST)
        if form.is_valid():
            objet.statut = form.cleaned_data['statut']
            objet.save()
            
            # Journalisation du changement
            JournalModification.objects.create(
                utilisateur=request.user,
                objet=objet,
                action=f"Statut changé à {objet.get_statut_display()}",
                details=form.cleaned_data['commentaire']
            )
            
            messages.success(request, "Statut mis à jour")
            return redirect('tableau-complexe')
    else:
        form = ControleObjetForm(initial={'statut': objet.statut})
    
    return render(request, 'controler_objet.html', {'form': form, 'objet': objet})

from django.views.generic import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ModifierObjetView(SuccessMessageMixin, UpdateView):
    model = ObjetConnecte
    form_class = ModificationObjetForm
    template_name = 'modifier_objet.html'
    success_message = "Objet modifié avec succès"
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit('submit', 'Enregistrer', css_class='btn-primary'))
        return form

    def get_success_url(self):
        return reverse('tableau-complexe')

@login_required
def controler_objet(request, objet_id):
    objet = get_object_or_404(ObjetConnecte, id=objet_id)
    
    if request.method == 'POST':
        form = ControleObjetForm(request.POST)
        if form.is_valid():
            # Journalisation avant modification
            ancien_statut = objet.get_statut_display()
            
            objet.statut = form.cleaned_data['statut']
            objet.save()
            
            JournalModification.objects.create(
                utilisateur=request.user,
                objet=objet,
                action=f"Statut changé de {ancien_statut} à {objet.get_statut_display()}",
                details=form.cleaned_data['commentaire']
            )
            
            messages.success(request, f"Statut changé à {objet.get_statut_display()}")
            return redirect('tableau-complexe')
    else:
        form = ControleObjetForm(initial={'statut': objet.statut})
    
    # Configuration crispy pour le formulaire
    form.helper = FormHelper()
    form.helper.form_method = 'post'
    form.helper.add_input(Submit('submit', 
        'Confirmer le changement', 
        css_class='btn-danger' if objet.statut == 'ACTIF' else 'btn-success'))
    
    return render(request, 'controler_objet.html', {
        'form': form,
        'objet': objet
    })



class AffecterObjetView(UpdateView):
    model = ObjetConnecte
    form_class = AffectationForm
    template_name = 'affectation_objet.html'

    def form_valid(self, form):
        objet = form.save(commit=False)
        objet.affecte_par = self.request.user
        objet.date_affectation = timezone.now()
        objet.save()
        
        messages.success(
            self.request,
            f"Objet {objet.nom} affecté à {objet.zone} avec succès"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tableau-complexe')


class ConfigurerServicesView(ListView):
    model = Service
    template_name = 'configuration/services.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return Service.objects.filter(objet_id=self.kwargs['objet_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objet'] = get_object_or_404(ObjetConnecte, pk=self.kwargs['objet_id'])
        return context

class AjouterServiceView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'configuration/ajouter_service.html'
    
    def form_valid(self, form):
        form.instance.objet_id = self.kwargs['objet_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('configurer-services', kwargs={'objet_id': self.kwargs['objet_id']})

class EditerServiceView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'configuration/editer_service.html'
    
    def get_success_url(self):
        return reverse('configurer-services', kwargs={'objet_id': self.object.objet_id})


class ConfigurerObjetView(TemplateView):
    template_name = 'objets/configurer_objet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        objet = get_object_or_404(ObjetConnecte, pk=self.kwargs['pk'])
        
        # Sélection du formulaire selon le type d'objet
        if objet.type_objet == 'THERMOSTAT':
            context['form'] = ParametreThermostatForm(
                initial={
                    'temperature': objet.parametres.get(nom='temperature').valeur,
                    'mode': objet.parametres.get(nom='mode').valeur
                }
            )
        elif objet.type_objet == 'LUMIERE':
            context['form'] = ProgrammeLumiereForm()
        
        context['objet'] = objet
        context['programmes'] = objet.programmes.all()
        return context

    def post(self, request, *args, **kwargs):
        objet = get_object_or_404(ObjetConnecte, pk=kwargs['pk'])
        
        if objet.type_objet == 'THERMOSTAT':
            form = ParametreThermostatForm(request.POST)
            if form.is_valid():
                # Enregistrement des paramètres
                temperature = form.cleaned_data['temperature']
                mode = form.cleaned_data['mode']
                
                # Mise à jour avec historique
                param_temp = objet.parametres.get(nom='temperature')
                HistoriqueParametre.objects.create(
                    parametre=param_temp,
                    ancienne_valeur=param_temp.valeur,
                    nouvelle_valeur=temperature,
                    modifie_par=request.user
                )
                param_temp.valeur = temperature
                param_temp.save()
                
                param_mode = objet.parametres.get(nom='mode')
                param_mode.valeur = mode
                param_mode.save()
                
                messages.success(request, "Paramètres du thermostat mis à jour")
                return redirect('configurer-objet', pk=objet.pk)

        return self.render_to_response(self.get_context_data(form=form))

class CreerProgrammeView(CreateView):
    model = Programme
    form_class = ProgrammeLumiereForm
    template_name = 'objets/creer_programme.html'

    def form_valid(self, form):
        form.instance.objet_id = self.kwargs['pk']
        form.instance.parametres = self.get_parametres_objet()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('configurer-objet', kwargs={'pk': self.kwargs['pk']})

class ModifierProgrammeView(UpdateView):
    model = Programme
    form_class = ProgrammeLumiereForm
    template_name = 'objets/modifier_programme.html'

    def get_success_url(self):
        return reverse('configurer-objet', kwargs={'pk': self.object.objet.pk})

from django.views.generic import TemplateView
from django.db.models import Sum, Avg, F
from datetime import timedelta
from django.utils import timezone

class DashboardConsommationView(TemplateView):
    template_name = 'optimisation/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcul des consommations hebdomadaires
        date_debut = timezone.now() - timedelta(days=7)
        
        context['consommation_globale'] = MesureConsommation.objects.filter(
            date_debut__gte=date_debut
        ).aggregate(
            total=Sum('valeur'),
            moyenne=Avg('valeur')
        )
        
        # Top 5 des objets les plus consommateurs
        context['top_consommateurs'] = MesureConsommation.objects.filter(
            date_debut__gte=date_debut
        ).values(
            'objet__nom', 'objet__type_objet'
        ).annotate(
            total=Sum('valeur')
        ).order_by('-total')[:5]
        
        # Alertes non résolues
        context['alertes'] = AlerteOptimisation.objects.filter(
            resolue=False
        ).select_related('objet')
        
        return context

class RapportPDFView(View):
    def get(self, request, *args, **kwargs):
        # Génération de rapport PDF avec ReportLab
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rapport_consommation.pdf"'
        
        p = canvas.Canvas(response)
        # ... implémentation du rapport PDF ...
        p.save()
        
        return response