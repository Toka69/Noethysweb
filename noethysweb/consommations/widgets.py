# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe
from core.models import Activite, Groupe, Unite, UniteRemplissage, Evenement, Ecole, Classe
from core.utils import utils_dates
import json


class SelectionGroupesWidget(Widget):
    template_name = 'core/widgets/checktree.html'

    def get_context(self, name, value, attrs=None):
        context = dict(self.attrs.items())
        if attrs is not None:
            context.update(attrs)
        context['name'] = name

        # Récupère les sélections initiales
        context['selections'] = []
        if value:
            context['selections'] = [int(id) for id in value.split(";")]

        # Récupération des dates
        liste_dates = context.get("dates", [])

        # Branches 1
        liste_activites = Activite.objects.filter(ouverture__date__in=liste_dates).order_by("-date_fin").distinct()
        context['liste_branches1'] = [{"pk": activite.pk, "label": activite.nom} for activite in liste_activites]

        # Branches 2
        context['dict_branches2'] = {}
        for groupe in Groupe.objects.select_related('activite').filter(activite_id__in=liste_activites).order_by("ordre"):
            context['dict_branches2'].setdefault(groupe.activite_id, [])
            context['dict_branches2'][groupe.activite_id].append({"pk": groupe.pk, "label": groupe.nom})

        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(loader.render_to_string(self.template_name, context))

    def value_from_datadict(self, data, files, name):
        selections = data.getlist(name, [])
        return ";".join(selections)



class SelectionUnitesWidget(Widget):
    template_name = 'consommations/widgets/selection_unites.html'

    def get_context(self, name, value, attrs=None):
        context = dict(self.attrs.items())
        if attrs is not None:
            context.update(attrs)
        context['name'] = name
        if value is not None:
            context['value'] = value

        # Récupération de la valeur
        dict_valeurs = {}
        if value:
            for idactivite, liste_valeurs in json.loads(value).items():
                for index, valeur in enumerate(liste_valeurs):
                    categorie, idunite, affichage = valeur.split("_")
                    dict_valeurs["%s_%s_%s" % (idactivite, categorie, idunite)] = {"ordre": index, "affichage": affichage}

        # Récupération des dates
        liste_dates = context.get("dates", [])

        # Importation des activités
        liste_activites = Activite.objects.filter(ouverture__date__in=liste_dates).order_by("-date_fin").distinct()

        # Importation des unités
        dict_unites = {}

        def save_unite(unite=None, categorie=None, affichage=None):
            unite.categorie = categorie
            unite.affichage = affichage
            if unite.categorie == "remplissage":
                unite.ordre = unite.ordre + 100
            dict_unites.setdefault(unite.activite, [])
            dict_valeur = dict_valeurs.get("%s_%s_%s" % (unite.activite_id, unite.categorie, unite.pk))
            if dict_valeur:
                unite.affichage = dict_valeur["affichage"]
                unite.ordre = dict_valeur["ordre"]
            dict_unites[unite.activite].append(unite)

        for unite in Unite.objects.filter(activite__in=liste_activites).order_by("ordre"):
            save_unite(unite, categorie="consommation", affichage="afficher")

        for unite in UniteRemplissage.objects.filter(activite__in=liste_activites).order_by("ordre"):
            save_unite(unite, categorie="remplissage", affichage="masquer")

        # Tri par ordre
        for idactivite, liste_valeurs in dict_unites.items():
            dict_unites[idactivite] = sorted(liste_valeurs, key=lambda x: x.ordre)

        context["liste_activites"] = liste_activites
        context["dict_unites"] = dict_unites
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(loader.render_to_string(self.template_name, context))


class ColonnesPersoWidget(Widget):
    template_name = 'consommations/widgets/colonnes_perso.html'

    def get_context(self, name, value, attrs=None):
        context = dict(self.attrs.items())
        if attrs is not None:
            context.update(attrs)
        context['name'] = name
        if value is not None:
            context['value'] = value
        else:
            context['value'] = "[]"

        # Importation du form de saisie d'une colonne
        from consommations.forms.colonne_personnalisee import Formulaire
        context['form'] = Formulaire()

        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(loader.render_to_string(self.template_name, context))


class SelectionEvenementsWidget(Widget):
    template_name = 'core/widgets/checktree.html'

    def get_context(self, name, value, attrs=None):
        context = dict(self.attrs.items())
        if attrs is not None:
            context.update(attrs)
        context['name'] = name

        # Récupère les sélections initiales
        context['selections'] = []
        if value:
            context['selections'] = [int(id) for id in value.split(";")]

        # Récupération des dates
        liste_dates = context.get("dates", [])

        # Branches 1
        liste_activites = Activite.objects.filter(ouverture__date__in=liste_dates).order_by("-date_fin").distinct()
        context['liste_branches1'] = [{"pk": activite.pk, "label": activite.nom} for activite in liste_activites]

        # Branches 2
        context['dict_branches2'] = {}
        for evenement in Evenement.objects.select_related('activite').filter(activite_id__in=liste_activites, date__in=liste_dates).order_by("date", "heure_debut"):
            context['dict_branches2'].setdefault(evenement.activite_id, [])
            context['dict_branches2'][evenement.activite_id].append({"pk": evenement.pk, "label": "%s : %s" % (utils_dates.ConvertDateToFR(evenement.date), evenement.nom)})

        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(loader.render_to_string(self.template_name, context))

    def value_from_datadict(self, data, files, name):
        selections = data.getlist(name, [])
        return ";".join(selections)



class SelectionEcolesWidget(Widget):
    template_name = 'core/widgets/checklist.html'

    def get_context(self, name, value, attrs=None):
        context = dict(self.attrs.items())
        if attrs is not None:
            context.update(attrs)
        context['name'] = name

        # Récupère les sélections initiales
        context['selections'] = []
        if value:
            context['selections'] = [int(id) for id in value.split(";")]

        # Items
        liste_ecoles = Ecole.objects.all().order_by("nom")
        context['items'] = [{"pk": ecole.pk, "label": ecole.nom} for ecole in liste_ecoles]

        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(loader.render_to_string(self.template_name, context))

    def value_from_datadict(self, data, files, name):
        selections = data.getlist(name, [])
        return ";".join(selections)


class SelectionClassesWidget(Widget):
    template_name = 'core/widgets/checktree.html'

    def get_context(self, name, value, attrs=None):
        context = dict(self.attrs.items())
        if attrs is not None:
            context.update(attrs)
        context['name'] = name

        # Récupère les sélections initiales
        context['selections'] = []
        if value:
            context['selections'] = [int(id) for id in value.split(";")]

        # Récupération des dates
        liste_dates = context.get("dates", [])
        liste_dates.sort()

        # Branches 2
        context['dict_branches2'] = {}
        if liste_dates:
            for classe in Classe.objects.select_related('ecole').filter(date_debut__lte=max(liste_dates), date_fin__gte=min(liste_dates)).order_by("date_debut"):
                context['dict_branches2'].setdefault(classe.ecole_id, [])
                context['dict_branches2'][classe.ecole_id].append({"pk": classe.pk, "label": classe.nom})

        # Branches 1
        liste_ecoles = Ecole.objects.filter(pk__in=context['dict_branches2'].keys()).order_by("nom")
        context['liste_branches1'] = [{"pk": ecole.pk, "label": ecole.nom} for ecole in liste_ecoles]

        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(loader.render_to_string(self.template_name, context))

    def value_from_datadict(self, data, files, name):
        selections = data.getlist(name, [])
        return ";".join(selections)