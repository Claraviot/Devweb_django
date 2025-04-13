from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProfilUtilisateur
from .models import DemandeObjet, ObjetConnecte, Zone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field

class CustomUserForm(UserCreationForm):
    username = forms.CharField(label="Pseudonyme", max_length=30)
    email = forms.EmailField(label="Adresse mail", required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfilUtilisateurForm(forms.ModelForm):
    class Meta:
        model = ProfilUtilisateur
        fields = [
            'prenom', 'nom', 'date_naissance', 'sexe', 'photo',
            'poste', 'societe',  # ✅ ici on utilise le bon champ
            'show_prenom', 'show_nom', 'show_date_naissance', 'show_sexe', 'show_photo'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'prenom': 'Prénom',
            'nom': 'Nom',
            'date_naissance': 'Date de naissance',
            'sexe': 'Sexe',
            'photo': 'Photo',
            'poste': 'Intitulé du poste',  # ✅ le bon label
            'societe': 'Société',
            'show_prenom': 'Afficher le prénom',
            'show_nom': 'Afficher le nom',
            'show_date_naissance': 'Afficher la date de naissance',
            'show_sexe': 'Afficher le sexe',
            'show_photo': 'Afficher la photo',
        }


class NiveauForm(forms.ModelForm):
    class Meta:
        model = ProfilUtilisateur
        fields = ['niveau']


class DemandeAjoutObjetForm(forms.Form):
    nom = forms.CharField(max_length=100, label="Nom de l'objet")
    modele = forms.CharField(max_length=100, label="Modèle")
    type_objet = forms.CharField(max_length=50, label="Type d'objet")
    fonction = forms.CharField(widget=forms.Textarea, label="Fonction principale")
    emplacement = forms.CharField(max_length=100, label="Emplacement suggéré")
    parametres = forms.JSONField(label="Paramètres techniques")
    raison = forms.CharField(widget=forms.Textarea, label="Pourquoi cet objet serait utile?")
    commentaires = forms.CharField(widget=forms.Textarea, required=False, label="Commentaires supplémentaires")

class DemandeSuppressionObjetForm(forms.Form):
    raison = forms.CharField(widget=forms.Textarea, label="Raison de la suppression")
    commentaires = forms.CharField(widget=forms.Textarea, required=False, label="Commentaires supplémentaires")

class ModificationObjetForm(forms.ModelForm):
    class Meta:
        model = ObjetConnecte
        fields = ['nom', 'nom_temporaire', 'description', 'parametres', 'version']
        widgets = {
            'parametres': forms.Textarea(attrs={'class': 'json-editor'}),
        }

class ControleObjetForm(forms.Form):
    statut = forms.ChoiceField(choices=ObjetConnecte.STATUT_CHOICES)
    commentaire = forms.CharField(widget=forms.Textarea, required=False)


class AffectationForm(forms.ModelForm):
    class Meta:
        model = ObjetConnecte
        fields = ['zone', 'nom_temporaire']
        widgets = {
            'zone': forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zone'].queryset = Zone.objects.all().order_by('batiment', 'etage', 'nom')


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom', 'protocole', 'endpoint', 'port', 'actif', 'configuration']
        widgets = {
            'configuration': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nom', css_class='col-md-6'),
                Column('protocole', css_class='col-md-6'),
            ),
            Row(
                Column('endpoint', css_class='col-md-8'),
                Column('port', css_class='col-md-4'),
            ),
            'actif',
            Fieldset(
                'Configuration avancée',
                'configuration',
                css_class='mt-4'
            )
        )

class RegleServiceForm(forms.ModelForm):
    class Meta:
        model = RegleService
        fields = ['nom', 'condition', 'action', 'priorite']


class ParametreThermostatForm(forms.Form):
    temperature = forms.FloatField(
        label="Température cible (°C)",
        min_value=10,
        max_value=30,
        widget=forms.NumberInput(attrs={'step': '0.5'})
    )
    mode = forms.ChoiceField(
        choices=[('AUTO', 'Automatique'), ('MANUEL', 'Manuel')],
        widget=forms.RadioSelect
    )

class ProgrammeLumiereForm(forms.ModelForm):
    JOURS_CHOICES = [
        (1, 'Lundi'),
        (2, 'Mardi'),
        (3, 'Mercredi'),
        (4, 'Jeudi'),
        (5, 'Vendredi'),
        (6, 'Samedi'),
        (7, 'Dimanche')
    ]
    
    jours = forms.MultipleChoiceField(
        choices=JOURS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Programme
        fields = ['nom', 'heure_debut', 'heure_fin', 'actif']
        widgets = {
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nom',
            Div(
                Field('jours', css_class='form-check-inline'),
                css_class='mb-3'
            ),
            Div(
                Field('heure_debut', wrapper_class='col-md-6'),
                Field('heure_fin', wrapper_class='col-md-6'),
                css_class='row'
            ),
            'actif'
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['heure_debut'] >= cleaned_data['heure_fin']:
            raise forms.ValidationError("L'heure de fin doit être après l'heure de début")
        return cleaned_data