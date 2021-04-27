# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.utils.translation import ugettext as _
from core.utils import utils_infos_individus, utils_dates, utils_resolveur_formule
from core.models import ModeleDocument, Organisateur
import json, os, datetime
from django.conf import settings
from django.core.cache import cache
from reportlab.lib.units import mm as mmPDF
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from reportlab.graphics.barcode.common import Codabar, Code11, I2of5, MSI
from reportlab.graphics.barcode.code128 import Code128
from reportlab.graphics.barcode.code39 import Extended39, Standard39
from reportlab.graphics.barcode.code93 import Extended93, Standard93
from reportlab.graphics.barcode.usps import FIM, POSTNET
from reportlab.graphics.barcode import createBarcodeDrawing


class Categorie():
    nom = ""
    code = ""
    photosIndividuelles = False
    champs = []
    codesbarres = []
    speciaux = []

    def As_dict(self):
        return {"nom": self.nom, "code": self.code, "photosIndividuelles": self.photosIndividuelles,
                "champs": self.champs, "codesbarres": self.codesbarres, "speciaux": self.speciaux}

    def As_Json(self):
        return json.dumps(self.As_dict())


class Fond(Categorie):
    def __init__(self):
        self.nom = _(u"Fond")
        self.code = "fond"
        self.photosIndividuelles = False
        self.champs = [(_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"), ]
        self.codesbarres = []
        self.speciaux = []


class Facture(Categorie):
    def __init__(self):
        self.nom = _(u"Facture")
        self.code = "facture"

        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires de dossier"), _(u"M. DUPOND Gérard"), "{FAMILLE_NOM}"),
            (_(u"Rue de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"Individus concernés"), _(u"Kévin ALLIBERT"), "{INDIVIDUS_CONCERNES}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Numéro de facture"), u"1234567", "{NUM_FACTURE}"),
            (_(u"Code-barres - Numéro de facture"), u"F123456", "{CODEBARRES_NUM_FACTURE}"),
            (_(u"Nom du lot"), _(u"Mars 2014"), "{NOM_LOT}"),
            (_(u"Date d'échéance de paiement (long)"), _(u"Lundi 10 janvier 2011"), "{DATE_ECHEANCE_LONG}"),
            (_(u"Date d'échéance de paiement (court)"), u"10/01/2011", "{DATE_ECHEANCE_COURT}"),
            (_(u"Texte échéance de paiement"), _(u"Date d'échéance : 10/01/2011"), "{TEXTE_ECHEANCE}"),
            (_(u"Date d'édition de la facture (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition de la facture (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            (_(u"Date du prélèvement si facture prélevée"), u"15/10/2011", "{DATE_PRELEVEMENT}"),

            (_(u"Total des prestations de la période"), u"10.00 €", "{TOTAL_PERIODE}"),
            (_(u"Total déjà réglé pour la période"), u"6.00 €", "{TOTAL_REGLE}"),
            (_(u"Solde dû pour la période"), u"4.00 €", "{SOLDE_DU}"),
            (_(u"Total des reports des périodes précédentes"), u"134.50 €", "{TOTAL_REPORTS}"),
            (_(u"Solde avec reports"), u"138.50 €", "{SOLDE_AVEC_REPORTS}"),
            (_(u"Solde du compte"), u"-35.80 €", "{SOLDE_COMPTE}"),
            (_(u"Total des déductions"), u"20.50 €", "{TOTAL_DEDUCTIONS}"),

            (_(u"PES ORMC ID de la pièce"), u"12345", "{PES_IDPIECE}"),
            (_(u"PES ORMC Nom du lot"), u"Cantine janv 2016", "{PES_NOM_LOT}"),
            (_(u"PES ORMC Exercice"), u"2016", "{PES_LOT_EXERCICE}"), (_(u"PES ORMC Mois"), u"12", "{PES_LOT_MOIS}"),
            (_(u"PES ORMC Objet du lot"), u"Accueil périscolaire", "{PES_LOT_OBJET}"),
            (_(u"PES ORMC ID Bordereau"), u"17", "{PES_LOT_ID_BORDEREAU}"),
            (_(u"PES ORMC Code produit"), u"87", "{PES_LOT_CODE_PRODUIT}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = [(_(u"Numéro de facture"), u"1234567", "{CODEBARRES_NUM_FACTURE}"), ]

        self.speciaux = [
            {"nom": _(u"Cadre principal"), "champ": _(u"cadre_principal"), "obligatoire": True, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False, },
            {"nom": _(u"Coupon-réponse vertical"), "champ": _(u"coupon_vertical"), "obligatoire": False, "x": None, "y": None, "largeur": 15, "hauteur": 70, "largeurModifiable": False, "hauteurModifiable": False, "verrouillageLargeur": True, "verrouillageHauteur": True, "interditModifProportions": True, },
            {"nom": _(u"Coupon-réponse horizontal"), "champ": _(u"coupon_horizontal"), "obligatoire": False, "x": None, "y": None, "largeur": 70, "hauteur": 15, "largeurModifiable": False, "hauteurModifiable": False, "verrouillageLargeur": True, "verrouillageHauteur": True, "interditModifProportions": True, },
        ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Attestation(Categorie):
    def __init__(self):
        self.nom = _(u"Attestation")
        self.code = "attestation"

        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),

            (_(u"Nom du destinataire"), _(u"M. DUPOND Gérard"), "{DESTINATAIRE_NOM}"),
            (_(u"Rue de l'adresse du destinataire"), _(u"10 rue des oiseaux"), "{DESTINATAIRE_RUE}"),
            (_(u"Ville de l'adresse du destinataire"), _(u"29000 QUIMPER"), "{DESTINATAIRE_VILLE}"),

            (_(u"Nom des individus concernés"), u"Xavier DUPOND et Lucie DUPOND", "{NOMS_INDIVIDUS}"),
            (_(u"Date de début de la période"), u"01/01/2011", "{DATE_DEBUT}"),
            (_(u"Date de fin de la période"), u"31/01/2011", "{DATE_FIN}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Numéro de l'attestation"), u"1234567", "{NUM_ATTESTATION}"),
            (_(u"Date d'édition de l'attestation (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition de l'attestation (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),

            (_(u"Total des prestations de la période"), u"10.00 €", "{TOTAL_PERIODE}"),
            (_(u"Total déjà réglé pour la période"), u"6.00 €", "{TOTAL_REGLE}"),
            (_(u"Solde dû pour la période"), u"4.00 €", "{SOLDE_DU}"),
            (_(u"Total des déductions"), u"20.50 €", "{TOTAL_DEDUCTIONS}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = []

        self.speciaux = [
            {"nom": _(u"Cadre principal"), "champ": _(u"cadre_principal"), "obligatoire": True, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False, }
        ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Rappel(Categorie):
    def __init__(self):
        self.nom = _(u"Rappel")
        self.code = "rappel"

        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires de dossier"), _(u"M. DUPOND Gérard"), "{FAMILLE_NOM}"),
            (_(u"Rue de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Numéro de rappel"), u"1234567", "{NUM_RAPPEL}"),
            (_(u"Code-barres - Numéro de rappel"), u"F123456", "{CODEBARRES_NUM_RAPPEL}"),
            (_(u"Nom du lot"), _(u"Mars 2014"), "{NOM_LOT}"),
            (_(u"Date d'édition du rappel (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition du rappel (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            (_(u"Date de début"), u"10/07/2011", "{DATE_DEBUT}"), (_(u"Date de fin"), u"21/12/2011", "{DATE_FIN}"),

            (_(u"Solde"), u"12.00 €", "{SOLDE}"), (_(u"Solde en lettres"), _(u"Douze Euros"), "{SOLDE_LETTRES}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = [(_(u"Numéro de rappel"), u"1234567", "{CODEBARRES_NUM_RAPPEL}"), ]

        self.speciaux = [
            {"nom": _(u"Cadre principal"), "champ": _(u"cadre_principal"), "obligatoire": True, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False, },
            {"nom": _(u"Coupon-réponse vertical"), "champ": _(u"coupon_vertical"), "obligatoire": False, "x": None, "y": None, "largeur": 15, "hauteur": 70, "largeurModifiable": False, "hauteurModifiable": False, "verrouillageLargeur": True, "verrouillageHauteur": True, "interditModifProportions": True, },
            {"nom": _(u"Coupon-réponse horizontal"), "champ": _(u"coupon_horizontal"), "obligatoire": False, "x": None, "y": None, "largeur": 70, "hauteur": 15, "largeurModifiable": False, "hauteurModifiable": False, "verrouillageLargeur": True, "verrouillageHauteur": True, "interditModifProportions": True, },
        ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Reglement(Categorie):
    def __init__(self):
        self.nom = _(u"Règlement")
        self.code = "reglement"

        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),

            (_(u"Nom du destinataire"), _(u"M. DUPOND Gérard"), "{DESTINATAIRE_NOM}"),
            (_(u"Rue de l'adresse du destinataire"), _(u"10 rue des oiseaux"), "{DESTINATAIRE_RUE}"),
            (_(u"Ville de l'adresse du destinataire"), _(u"29000 QUIMPER"), "{DESTINATAIRE_VILLE}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Numéro du reçu"), u"1234567", "{NUM_RECU}"),
            (_(u"Date d'édition du reçu (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition du reçu (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),

            (_(u"ID du règlement"), u"11234567", "{IDREGLEMENT}"),
            (_(u"Date du règlement"), u"21/03/2011", "{DATE_REGLEMENT}"),
            (_(u"Mode de règlement"), _(u"Chèque"), "{MODE_REGLEMENT}"),
            (_(u"Nom de l'émetteur"), _(u"Caisse d'épargne"), "{NOM_EMETTEUR}"),
            (_(u"Numéro de pièce"), u"0001243", "{NUM_PIECE}"),
            (_(u"Montant du règlement"), u"10.00 €", "{MONTANT_REGLEMENT}"),
            (_(u"Nom du payeur"), _(u"DUPOND Gérard"), "{NOM_PAYEUR}"),
            (_(u"Numéro de quittancier"), u"246", "{NUM_QUITTANCIER}"),
            (_(u"Date de saisie du règlement"), u"23/03/2011", "{DATE_SAISIE}"),
            (_(u"Date d'encaissement différé"), u"24/04/2011", "{DATE_DIFFERE}"),
            (_(u"Observations"), _(u"Observations"), "{OBSERVATIONS}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = []

        self.speciaux = [
            {"nom": _(u"Cadre principal"), "champ": _(u"cadre_principal"), "obligatoire": True, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False}
        ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ---------------------------------------------------------------------------------------------------------------------------------------

class Individu(Categorie):
    def __init__(self):
        self.nom = _(u"Individu")
        self.code = "individu"
        self.photosIndividuelles = True

        self.champs = [(_(u"Numéro ID de l'individu"), u"2582", "{IDINDIVIDU}"),
            (_(u"Civilité de l'individu (long)"), _(u"Mademoiselle"), "{INDIVIDU_CIVILITE_LONG}"),
            (_(u"Civilité de l'individu (court)"), _(u"Melle"), "{INDIVIDU_CIVILITE_COURT}"),
            (_(u"Genre de l'individu (M ou F)"), u"M", "{INDIVIDU_GENRE}"),
            (_(u"Nom de l'individu"), _(u"DUPOND"), "{INDIVIDU_NOM}"),
            (_(u"Prénom de l'individu"), _(u"Lucie"), "{INDIVIDU_PRENOM}"),
            (_(u"Date de naissance de l'individu"), u"12/04/1998", "{INDIVIDU_DATE_NAISS}"),
            (_(u"Age de l'individu"), u"12", "{INDIVIDU_AGE}"),
            (_(u"Code postal de la ville de naissance"), u"29200", "{INDIVIDU_CP_NAISS}"),
            (_(u"Nom de la ville de naissance"), _(u"BREST"), "{INDIVIDU_VILLE_NAISS}"),
            (_(u"Rue de l'adresse de l'individu"), _(u"10 rue des oiseaux"), "{INDIVIDU_RUE}"),
            (_(u"Code postal de l'adresse de l'individu"), u"29200", "{INDIVIDU_CP}"),
            (_(u"Ville de l'adresse de l'individu"), _(u"BREST"), "{INDIVIDU_VILLE}"),
            (_(u"Profession de l'individu"), _(u"Menuisier"), "{INDIVIDU_PROFESSION}"),
            (_(u"Employeur de l'individu"), _(u"SARL DUPOND"), "{INDIVIDU_EMPLOYEUR}"),
            (_(u"Téléphone fixe de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_TEL_DOMICILE}"),
            (_(u"Téléphone mobile de l'individu"), u"06.01.02.03.04.", "{INDIVIDU_TEL_MOBILE}"),
            (_(u"Fax de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_FAX}"),
            (_(u"Adresse internet de l'individu"), _(u"moi@test.com"), "{INDIVIDU_EMAIL}"),
            (_(u"Téléphone fixe pro de l'individu"), u"01.04.05.04.05.", "{INDIVIDU_TEL_PRO}"),
            (_(u"Fax pro de l'individu"), u"06.03.04.05.04.", "{INDIVIDU_FAX_PRO}"),
            (_(u"Adresse internet pro"), _(u"montravail@test.com"), "{INDIVIDU_EMAIL_PRO}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="individu"))

        self.codesbarres = [(_(u"ID de l'individu"), u"1234567", "{CODEBARRES_ID_INDIVIDU}"), ]

        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("individu"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("individu"))


# ---------------------------------------------------------------------------------------------------------------------------------------

class Famille(Categorie):
    def __init__(self):
        self.nom = _(u"famille")
        self.code = "famille"
        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND Gérard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"Régime social de la famille"), _(u"Régime général"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Numéro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = [(_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"), ]

        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ---------------------------------------------------------------------------------------------------------------------------------------

class Inscription(Categorie):
    def __init__(self):
        self.nom = _(u"Inscription")
        self.code = "inscription"
        self.photosIndividuelles = True

        self.champs = [(_(u"Numéro ID de l'individu"), u"2582", "{IDINDIVIDU}"),
            (_(u"Civilité de l'individu (long)"), _(u"Mademoiselle"), "{INDIVIDU_CIVILITE_LONG}"),
            (_(u"Civilité de l'individu (court)"), _(u"Melle"), "{INDIVIDU_CIVILITE_COURT}"),
            (_(u"Genre de l'individu (M ou F)"), u"M", "{INDIVIDU_GENRE}"),
            (_(u"Nom de l'individu"), _(u"DUPOND"), "{INDIVIDU_NOM}"),
            (_(u"Prénom de l'individu"), _(u"Lucie"), "{INDIVIDU_PRENOM}"),
            (_(u"Date de naissance de l'individu"), u"12/04/1998", "{INDIVIDU_DATE_NAISS}"),
            (_(u"Age de l'individu"), u"12", "{INDIVIDU_AGE}"),
            (_(u"Code postal de la ville de naissance"), u"29200", "{INDIVIDU_CP_NAISS}"),
            (_(u"Nom de la ville de naissance"), _(u"BREST"), "{INDIVIDU_VILLE_NAISS}"),
            (_(u"Rue de l'adresse de l'individu"), _(u"10 rue des oiseaux"), "{INDIVIDU_RUE}"),
            (_(u"Code postal de l'adresse de l'individu"), u"29200", "{INDIVIDU_CP}"),
            (_(u"Ville de l'adresse de l'individu"), _(u"BREST"), "{INDIVIDU_VILLE}"),
            (_(u"Profession de l'individu"), _(u"Menuisier"), "{INDIVIDU_PROFESSION}"),
            (_(u"Employeur de l'individu"), _(u"SARL DUPOND"), "{INDIVIDU_EMPLOYEUR}"),
            (_(u"Téléphone fixe de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_TEL_DOMICILE}"),
            (_(u"Téléphone mobile de l'individu"), u"06.01.02.03.04.", "{INDIVIDU_TEL_MOBILE}"),
            (_(u"Fax de l'individu"), u"01.02.03.04.05.", "{INDIVIDU_FAX}"),
            (_(u"Adresse internet de l'individu"), _(u"moi@test.com"), "{INDIVIDU_EMAIL}"),
            (_(u"Téléphone fixe pro de l'individu"), u"01.04.05.04.05.", "{INDIVIDU_TEL_PRO}"),
            (_(u"Fax pro de l'individu"), u"06.03.04.05.04.", "{INDIVIDU_FAX_PRO}"),
            (_(u"Adresse internet pro"), _(u"montravail@test.com"), "{INDIVIDU_EMAIL_PRO}"),

            (_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND Gérard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"Régime social de la famille"), _(u"Régime général"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Numéro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Numéro ID de l'inscription"), u"003", "{IDINSCRIPTION}"),
            (_(u"Date de l'inscription"), u"01/01/2013", "{DATE_INSCRIPTION}"),
            (_(u"Est parti"), _(u"Oui"), "{EST_PARTI}"),

            (_(u"Numéro ID de l'activité"), u"003", "{IDACTIVITE}"),
            (_(u"Nom de l'activité (long)"), _(u"Accueil de Loisirs"), "{ACTIVITE_NOM_LONG}"),
            (_(u"Nom de l'activité (abrégé)"), _(u"ALSH"), "{ACTIVITE_NOM_COURT}"),

            (_(u"Numéro ID du groupe"), u"001", "{IDGROUPE}"),
            (_(u"Nom du groupe (long)"), _(u"Accueil de Loisirs"), "{GROUPE_NOM_LONG}"),
            (_(u"Nom du groupe (abrégé)"), _(u"ALSH"), "{GROUPE_NOM_COURT}"),

            (_(u"Numéro ID de la catégorie de tarif"), u"004", "{IDCATEGORIETARIF}"),
            (_(u"Nom de la catégorie de tarif"), _(u"Hors commune"), "{NOM_CATEGORIE_TARIF}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="individu+famille"))

        self.codesbarres = [(_(u"ID de l'individu"), u"1234567", "{CODEBARRES_ID_INDIVIDU}"), ]

        self.speciaux = [
            {"nom": _(u"Cadre principal"), "champ": _(u"cadre_principal"), "obligatoire": False, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False}
        ]

        # Questionnaires
        self.champs.extend(GetQuestions("individu"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("individu"))

        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))

        self.champs.extend(GetQuestions("inscription"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("inscription"))


# ---------------------------------------------------------------------------------------------------------------------------------------

class Cotisation(Categorie):
    def __init__(self):
        self.nom = _(u"Cotisation")
        self.code = "cotisation"
        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la cotisation"), u"13215", "{IDCOTISATION}"),
            (_(u"Numéro ID du type d'adhésion"), u"034", "{IDTYPE_COTISATION}"),
            (_(u"Numéro ID de l'unité d'adhésion"), u"31", "{IDUNITE_COTISATION}"),
            (_(u"Numéro ID de l'utilisateur qui a saisi l'adhésion"), u"023", "{IDUTILISATEUR}"),
            (_(u"Date de saisie de l'adhésion"), u"01/01/2014", "{DATE_SAISIE}"),
            (_(u"Date de création de la carte"), u"10/01/2014", "{DATE_CREATION_CARTE}"),
            (_(u"Numéro de la carte"), u"0123321", "{NUMERO_CARTE}"),
            (_(u"Numéro ID du dépôt de l'adhésion"), u"064", "{IDDEPOT_COTISATION}"),
            (_(u"Date de début de validité"), u"01/01/2014", "{DATE_DEBUT}"),
            (_(u"Date de fin de validité"), u"31/12/2014", "{DATE_FIN}"),
            (_(u"Numéro ID de la prestation"), u"31211", "{IDPRESTATION}"),
            (_(u"Nom du type d'adhésion"), _(u"Carte d'adhérent"), "{NOM_TYPE_COTISATION}"),
            (_(u"Nom de l'unité de l'adhésion"), u"2014", "{NOM_UNITE_COTISATION}"),
            (_(u"Adhésion familiale ou individuelle"), _(u"Cotisation familiale"), "{COTISATION_FAM_IND}"),
            (_(u"Nom de l'adhésion (Type + unité)"), _(u"Carte d'adhérent - 2014"), "{NOM_COTISATION}"),
            (_(u"Nom de dépôt d'adhésions"), _(u"Dépôt Janvier 2014"), "{NOM_DEPOT}"),
            (_(u"Montant facturé"), u"20.00 €", "{MONTANT_FACTURE}"),
            (_(u"Montant réglé"), u"20.00 €", "{MONTANT_REGLE}"), (_(u"Solde actuel"), u"20.00 €", "{SOLDE_ACTUEL}"),
            (_(u"Activités associées"), u"Centre de loisirs, Cantine", "{ACTIVITES}"),
            (_(u"Notes"), u"Texte libre", "{NOTES}"),
            (_(u"Montant facturé en lettres"), _(u"Vingt Euros"), "{MONTANT_FACTURE_LETTRES}"),
            (_(u"Montant réglé en lettres"), _(u"Vingt Euros"), "{MONTANT_REGLE_LETTRES}"),
            (_(u"Solde actuel en lettres"), _(u"Vingt Euros"), "{SOLDE_ACTUEL_LETTRES}"),
            (_(u"Date du règlement"), u"01/01/2014", "{DATE_REGLEMENT}"),
            (_(u"Mode de règlement"), _(u"Chèque"), "{MODE_REGLEMENT}"),

            (_(u"Numéro ID de l'individu bénéficiaire"), u"4654", "{IDINDIVIDU}"),
            (_(u"Numéro ID de la famille bénéficiare"), u"13211", "{BENEFICIAIRE_NOM}"),
            (_(u"Adresse du bénéficiaire - Rue"), _(u"10 rue des oiseaux"), "{BENEFICIAIRE_RUE}"),
            (_(u"Adresse du bénéficiaire - CP"), u"29200", "{BENEFICIAIRE_CP}"),
            (_(u"Adresse du bénéficiaire - Ville"), _(u"BREST"), "{BENEFICIAIRE_VILLE}"),

            (_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND Gérard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"Régime social de la famille"), _(u"Régime général"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Numéro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Date d'édition (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="individu+famille"))

        self.codesbarres = [(_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"), ]

        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Attestation_fiscale(Categorie):
    def __init__(self):
        self.nom = _(u"Attestation fiscale")
        self.code = "attestation_fiscale"

        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires de dossier"), _(u"M. DUPOND Gérard"), "{FAMILLE_NOM}"),
            (_(u"Rue de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Date d'édition (long)"), _(u"Lundi 9 septembre 2011"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition (court)"), u"19/09/2011", "{DATE_EDITION_COURT}"),
            (_(u"Date de début"), u"10/07/2011", "{DATE_DEBUT}"), (_(u"Date de fin"), u"21/12/2011", "{DATE_FIN}"),

            (_(u"Montant facturé"), u"20.00 €", "{MONTANT_FACTURE}"),
            (_(u"Montant réglé"), u"20.00 €", "{MONTANT_REGLE}"),
            (_(u"Montant impayé"), u"20.00 €", "{MONTANT_IMPAYE}"),
            (_(u"Montant facturé en lettres"), _(u"Vingt Euros"), "{MONTANT_FACTURE_LETTRES}"),
            (_(u"Montant réglé en lettres"), _(u"Vingt Euros"), "{MONTANT_REGLE_LETTRES}"),
            (_(u"Montant impayé en lettres"), _(u"Vingt Euros"), "{MONTANT_IMPAYE_LETTRES}"),

            (_(u"Texte d'introduction"), _(u"Veuillez trouver ici le montant..."), "{INTRO}"),

            (_(u"Détail enfant 1"), _(u"10.00 € pour Lucie DUPOND née le 01/02/2005"), "{TXT_ENFANT_1}"),
            (_(u"Détail enfant 2"), _(u"10.00 € pour Lucie DUPOND née le 01/02/2005"), "{TXT_ENFANT_2}"),
            (_(u"Détail enfant 3"), _(u"10.00 € pour Lucie DUPOND née le 01/02/2005"), "{TXT_ENFANT_3}"),
            (_(u"Détail enfant 4"), _(u"10.00 € pour Lucie DUPOND née le 01/02/2005"), "{TXT_ENFANT_4}"),
            (_(u"Détail enfant 5"), _(u"10.00 € pour Lucie DUPOND née le 01/02/2005"), "{TXT_ENFANT_5}"),
            (_(u"Détail enfant 6"), _(u"10.00 € pour Lucie DUPOND née le 01/02/2005"), "{TXT_ENFANT_6}"),

        ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.speciaux = [
            {"nom": _(u"Cadre principal"), "champ": _(u"cadre_principal"), "obligatoire": False, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False, }
        ]

        self.codesbarres = [(_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"), ]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))


# ---------------------------------------------------------------------------------------------------------------------------------------

class Location(Categorie):
    def __init__(self):
        self.nom = _(u"Location")
        self.code = "location"
        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la location"), u"13215", "{IDLOCATION}"),
            (_(u"Numéro ID du produit"), u"034", "{IDPRODUIT}"),
            (_(u"Date de début de la location"), u"01/01/2017", "{DATE_DEBUT}"),
            (_(u"Date de fin de la location"), u"31/12/2017", "{DATE_FIN}"),
            (_(u"Heure de début de la location"), u"01/01/2014", "{HEURE_DEBUT}"),
            (_(u"Heure de fin de la location"), u"10/01/2014", "{HEURE_FIN}"),
            (_(u"Nom du produit"), u"0123321", "{NOM_PRODUIT}"), (_(u"Nom de la catégorie"), u"064", "{NOM_CATEGORIE}"),
            (_(u"Notes sur la location"), u"01/01/2014", "{NOTES}"),

            (_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND Gérard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"Régime social de la famille"), _(u"Régime général"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Numéro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Date d'édition (long)"), _(u"Lundi 9 septembre 2017"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition (court)"), u"19/09/2017", "{DATE_EDITION_COURT}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = [(_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"), ]

        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))

        self.champs.extend(GetQuestions("location"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("location"))

        self.champs.extend(GetQuestions("produit"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("produit"))


# ----------------------------------------------------------------------------------------------------------------------------------


class Location_demande(Categorie):
    def __init__(self):
        self.nom = _(u"Demande de location")
        self.code = "location_demande"
        self.photosIndividuelles = False

        self.champs = [(_(u"Numéro ID de la demande"), u"13215", "{IDDEMANDE}"),
            (_(u"Date de la demande"), u"01/01/2017", "{DATE}"), (_(u"Heure de la demande"), u"01/01/2014", "{HEURE}"),
            (_(u"Catégories demandées"), u"Catégorie 1, catégorie 2", "{CATEGORIES}"),
            (_(u"Produits demandés"), u"Produit 1, produit 2", "{PRODUITS}"),
            (_(u"Notes sur la demande"), u"01/01/2014", "{NOTES}"),

            (_(u"Numéro ID de la famille"), u"2582", "{IDFAMILLE}"),
            (_(u"Noms des titulaires"), _(u"DUPOND Gérard et Lucie"), "{FAMILLE_NOM}"),
            (_(u"Rue de l'adresse de la famille"), _(u"10 rue des oiseaux"), "{FAMILLE_RUE}"),
            (_(u"Code postal de l'adresse de la famille"), u"29200", "{FAMILLE_CP}"),
            (_(u"Ville de l'adresse de la famille"), _(u"BREST"), "{FAMILLE_VILLE}"),
            (_(u"Régime social de la famille"), _(u"Régime général"), "{FAMILLE_REGIME}"),
            (_(u"Caisse de la famille"), _(u"C.A.F."), "{FAMILLE_CAISSE}"),
            (_(u"Numéro d'allocataire de la famille"), u"0123456X", "{FAMILLE_NUMALLOC}"),

            (_(u"Nom de l'organisateur"), _(u"Association Noethys"), "{ORGANISATEUR_NOM}"),
            (_(u"Rue de l'organisateur"), _(u"Avenue des Lilas"), "{ORGANISATEUR_RUE}"),
            (_(u"Code postal de l'organisateur"), u"29870", "{ORGANISATEUR_CP}"),
            (_(u"Ville de l'organisateur"), _(u"LANNILIS"), "{ORGANISATEUR_VILLE}"),
            (_(u"Téléphone de l'organisateur"), u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            (_(u"Fax de l'organisateur"), u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            (_(u"Mail de l'organisateur"), _(u"noethys") + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            (_(u"Site internet de l'organisateur"), u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            (_(u"Numéro d'agrément de l'organisateur"), u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            (_(u"Numéro SIRET de l'organisateur"), u"123456789123", "{ORGANISATEUR_SIRET}"),
            (_(u"Code APE de l'organisateur"), _(u"NO123"), "{ORGANISATEUR_APE}"),

            (_(u"Date d'édition (long)"), _(u"Lundi 9 septembre 2017"), "{DATE_EDITION_LONG}"),
            (_(u"Date d'édition (court)"), u"19/09/2017", "{DATE_EDITION_COURT}"), ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = [(_(u"ID de la famille"), u"1234567", "{CODEBARRES_ID_FAMILLE}"), ]

        self.speciaux = []

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))

        self.champs.extend(GetQuestions("location_demande"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("location_demande"))


# ----------------------------------------------------------------------------------------------------------------------------------

class Devis(Categorie):
    def __init__(self):
        self.nom = "Devis"
        self.code = "devis"

        self.photosIndividuelles = False

        self.champs = [
            ("Numéro ID de la famille", u"2582", "{IDFAMILLE}"),

            ("Nom du destinataire", "M. DUPOND Gérard", "{DESTINATAIRE_NOM}"),
            ("Rue de l'adresse du destinataire", "10 rue des oiseaux", "{DESTINATAIRE_RUE}"),
            ("Ville de l'adresse du destinataire", "29000 QUIMPER", "{DESTINATAIRE_VILLE}"),

            ("Nom des individus concernés", u"Xavier DUPOND et Lucie DUPOND", "{NOMS_INDIVIDUS}"),
            ("Date de début de la période", u"01/01/2011", "{DATE_DEBUT}"),
            ("Date de fin de la période", u"31/01/2011", "{DATE_FIN}"),

            ("Nom de l'organisateur", "Association Noethys", "{ORGANISATEUR_NOM}"),
            ("Rue de l'organisateur", "Avenue des Lilas", "{ORGANISATEUR_RUE}"),
            ("Code postal de l'organisateur", u"29870", "{ORGANISATEUR_CP}"),
            ("Ville de l'organisateur", "LANNILIS", "{ORGANISATEUR_VILLE}"),
            ("Téléphone de l'organisateur", u"01.98.01.02.03", "{ORGANISATEUR_TEL}"),
            ("Fax de l'organisateur", u"01.04.05.06.", "{ORGANISATEUR_FAX}"),
            ("Mail de l'organisateur", "noethys" + u"@gmail.com", "{ORGANISATEUR_MAIL}"),
            ("Site internet de l'organisateur", u"www.noethys.com", "{ORGANISATEUR_SITE}"),
            ("Numéro d'agrément de l'organisateur", u"0256ORG234", "{ORGANISATEUR_AGREMENT}"),
            ("Numéro SIRET de l'organisateur", u"123456789123", "{ORGANISATEUR_SIRET}"),
            ("Code APE de l'organisateur", "NO123", "{ORGANISATEUR_APE}"),

            ("Numéro du devis", u"1234567", "{NUM_DEVIS}"),
            ("Date d'édition du devis (long)", "Lundi 9 septembre 2011", "{DATE_EDITION_LONG}"),
            ("Date d'édition du devis (court)", u"19/09/2011", "{DATE_EDITION_COURT}"),

            ("Total des prestations de la période", u"10.00 €", "{TOTAL_PERIODE}"),
            ("Total déjà réglé pour la période", u"6.00 €", "{TOTAL_REGLE}"),
            ("Solde dû pour la période", u"4.00 €", "{SOLDE_DU}"),
            ("Total des déductions", u"20.50 €", "{TOTAL_DEDUCTIONS}"),
             ]

        self.champs.extend(utils_infos_individus.GetNomsChampsPossibles(mode="famille"))

        self.codesbarres = []

        self.speciaux = [{"nom": "Cadre principal", "champ": "cadre_principal", "obligatoire": True, "nbreMax": 1, "x": None, "y": None, "verrouillageX": False, "verrouillageY": False, "Xmodifiable": True, "Ymodifiable": True, "largeur": 100, "hauteur": 150, "largeurModifiable": True, "hauteurModifiable": True, "largeurMin": 80, "largeurMax": 1000, "hauteurMin": 80, "hauteurMax": 1000, "verrouillageLargeur": False, "verrouillageHauteur": False, "verrouillageProportions": False, "interditModifProportions": False, }]

        # Questionnaires
        self.champs.extend(GetQuestions("famille"))
        self.codesbarres.extend(GetCodesBarresQuestionnaires("famille"))



def GetQuestions(type):
    return []
    # Q = UTILS_Questionnaires.Questionnaires()
    # listeQuestions = Q.GetQuestions(type)
    # listeTemp = []
    # for dictQuestion in listeQuestions :
    #     defaut = Q.FormatageReponse(dictQuestion["defaut"], dictQuestion["controle"])
    #     listeTemp.append((dictQuestion["label"], defaut, "{QUESTION_%d}" % dictQuestion["IDquestion"]))
    # return listeTemp


def GetCodesBarresQuestionnaires(type="individu"):
    return []
    # DB = GestionDB.DB()
    # req = """SELECT IDquestion, questionnaire_questions.label, questionnaire_questions.options
    # FROM questionnaire_questions
    # LEFT JOIN questionnaire_categories ON questionnaire_categories.IDcategorie = questionnaire_questions.IDcategorie
    # WHERE controle='codebarres' AND type='%s'
    # ORDER BY questionnaire_questions.ordre;""" % type
    # DB.ExecuterReq(req)
    # listeDonnees = DB.ResultatReq()
    # DB.Close()
    # listeCodes = []
    # for IDquestion, label, options in listeDonnees :
    #     listeCodes.append((label, u"1234567", "{CODEBARRES_QUESTION_%d}" % IDquestion))
    # return listeCodes


def ConvertTailleModeleEnPx(taille):
    return (taille[0] * mmPDF, taille[1] * mmPDF)


class Modele_doc():
    """ Importation d'un modèle pour un PDF """

    def __init__(self, IDmodele=None):
        self.IDmodele = IDmodele

        # Importation des infos sur ce modèle
        self.modele = ModeleDocument.objects.select_related("fond").get(pk=IDmodele)

        # Importation des objets
        self.objets = json.loads(self.modele.objets)

    def FindObjet(self, champ=""):
        for objet in self.objets:
            if objet.get("champ") == champ:
                return ObjetPDF(objet)
        return None

    def GetCoordsObjet(self, objet=None):
        """ Modifie Y pour inverser l'objet """
        coords = objet.GetCoords()
        taille_page = ConvertTailleModeleEnPx((self.modele.largeur, self.modele.hauteur))
        coords[1] = taille_page[1] - coords[3] - coords[1]
        return coords

    def DessineFond(self, canvas, dict_valeurs={}, options={}):
        """ Dessine les objets du fond """
        if self.modele.fond:
            # fond = ModeleDocument.objects.get(pk=self.modele.fond_id)
            for objet in json.loads(self.modele.fond.objets):
                valeur = self.GetValeur(objet, dict_valeurs)
                if valeur is not False:
                    ObjetPDF(objet, canvas, valeur=valeur, options=options)

    def DessineTousObjets(self, canvas, dict_valeurs={}, options={}):
        """ Dessine tous les objets """
        for objet in self.objets:
            valeur = self.GetValeur(objet, dict_valeurs)
            if valeur is not False:
                etat = ObjetPDF(objet, canvas, valeur=valeur, options=options)
                if etat == False:
                    return False

    def GetValeur(self, objet=None, dict_valeurs={}):
        valeur = None
        # -------- CODE-BARRES -------
        if objet.get("categorie") == "barcode":
            if objet.get("champ") in dict_valeurs:
                valeur = dict_valeurs[objet["champ"]]
                if len(valeur) == 0:
                    valeur = None

        # -------- TEXTE ----------
        if "texte" in objet.get("categorie", ""):
            texte = objet.get("text")
            for nomChamp, valeur in dict_valeurs.items():
                # Traitement d'une formule
                texte = utils_resolveur_formule.ResolveurTexte(texte=texte, listeChamps=list(dict_valeurs.keys()), dictValeurs=dict_valeurs)

                # Remplacement des mos-clés par les valeurs
                if type(nomChamp) == str and nomChamp.startswith("{"):
                    if not valeur: valeur = ""
                    if type(valeur) == int: valeur = str(valeur)
                    if type(valeur) == float: valeur = u"%.02f €" % valeur
                    if type(valeur) == datetime.date: valeur = utils_dates.ConvertDateToFR(valeur)
                    if nomChamp in texte:
                        texte = texte.replace(nomChamp, valeur)
            # Remplace également les mots-clés non utilisés par des chaînes vides
            # texte = re.sub(r"\{[A-Za-z0-9_-]*?\}", "", texte)

            valeur = texte

        # -------- IMAGE -------
        # if objet.categorie == "image":
        #     if objet.typeImage == "logo":
        #         # Type Logo
        #         if objet.exists == False:
        #             valeur = False
        #     elif objet.typeImage == "photo":
        #         # Type Photo
        #         if "{IDINDIVIDU}" in dictChamps:
        #             IDindividu = dictChamps["{IDINDIVIDU}"]
        #             DB = GestionDB.DB(suffixe="PHOTOS")
        #             req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%s;" % IDindividu
        #             DB.ExecuterReq(req)
        #             listeDonnees = DB.ResultatReq()
        #             DB.Close()
        #             if len(listeDonnees) > 0:
        #                 IDphoto, bufferPhoto = listeDonnees[0]
        #                 io = six.BytesIO(bufferPhoto)
        #                 if 'phoenix' in wx.PlatformInfo:
        #                     img = wx.Image(io, wx.BITMAP_TYPE_ANY)
        #                 else:
        #                     img = wx.ImageFromStream(io, wx.BITMAP_TYPE_ANY)
        #                 valeur = img
        #             else:
        #                 # Image par défaut
        #                 if "nomImage" in dictChamps:
        #                     nomImage = dictChamps["nomImage"]
        #                     bmp = wx.Bitmap(Chemins.GetStaticPath("Images/128x128/%s" % nomImage), wx.BITMAP_TYPE_ANY)
        #                     img = bmp.ConvertToImage()
        #                     valeur = img
        #     else:
        #         valeur = None

        return valeur

    def DessineFormes(self, canvas):
        """ Dessine les formes """
        for objet in self.objets:
            if objet.get("categorie") in ("rectangle", "ligne", "ellipse", "polygone"):
                ObjetPDF(objet, canvas)

    def DessineCodesBarres(self, canvas, dict_valeurs={}):
        """ Dessine les codes-barres """
        for objet in self.objets:
            if objet.get("categorie") == "barcode":
                valeur = self.GetValeur(objet, dict_valeurs)
                if valeur:
                    ObjetPDF(objet, canvas, valeur=valeur)

    def DessineTextes(self, canvas, dict_valeurs={}):
        """ Dessine les textes """
        for objet in self.objets:
            if "texte" in objet.get("categorie"):
                valeur = self.GetValeur(objet, dict_valeurs)
                ObjetPDF(objet, canvas, valeur=valeur)

    def DessineImages(self, canvas, dict_valeurs={}):
        """ Dessine les images """
        for objet in self.objets:
            if objet.get("categorie") in ("image", "logo"):
                valeur = self.GetValeur(objet, dict_valeurs)
                if True:#valeur:
                    ObjetPDF(objet, canvas, valeur=valeur)


# ------------------------------------------------------------------------------------------------------------------------------


class ObjetPDF():
    """ objet = objet Json | canvas = canvas Reportlab """
    def __init__(self, objet, canvas=None, valeur=None, options={}):
        self.canvas = canvas
        self.valeur = valeur
        self.categorie = None

        for key, value in objet.items():
            if key in ("left", "top", "width", "height", "strokeWidth", "lineHeight", "x1", "y1", "x2", "y2"):
                if not value: value = 0
                value = value * mmPDF
            setattr(self, key, value)

        self.width *= getattr(self, 'scaleX', 1)
        self.height *= getattr(self, 'scaleY', 1)

        if canvas:

            canvas.saveState()

            largeur_canvas, hauteur_canvas = canvas._pagesize
            if "translate" not in options or options["translate"]:
                canvas.scale(1, -1)
                canvas.translate(0, -hauteur_canvas)

            # Rotation
            if hasattr(self, "angle") and self.angle:
                canvas.translate(self.left, self.top)
                canvas.rotate(self.angle)
                canvas.translate(-self.left, -self.top)

            # ------- RECTANGLE ------
            if self.categorie == "rectangle":
                canvas.rect(self.left, self.top, self.width, self.height, self.SetTrait(), self.SetRemplissage())

            # ------- ELLIPSE ------
            if self.categorie == "cercle":
                canvas.ellipse(self.left, self.top, self.left + self.width, self.top + self.height, self.SetTrait(), self.SetRemplissage())

            # ------- LIGNE ------
            if self.type == "line":
                trait = self.SetTrait()
                canvas.line(self.left, self.top, self.left + self.width, self.top)

            # ------- POLYGONE ------
            # if self.categorie == "polygone":
            #     listePoints = objet.Points
            #     trait = GetTrait(objet)
            #     remplissage = GetRemplissage(objet)
            #     p = canvas.beginPath()
            #     p.moveTo(listePoints[0][0] * mmPDF, listePoints[0][1] * mmPDF)
            #     for x, y in listePoints[1:]:
            #         p.lineTo(x * mmPDF, y * mmPDF)
            #     p.lineTo(listePoints[0][0] * mmPDF, listePoints[0][1] * mmPDF)
            #     canvas.drawPath(p, trait, remplissage)

            # ------- TEXTE ------
            if self.categorie == "texte":
                if valeur == None:
                    valeur = self.text
                taillePolice = self.fontSize
                textObject = canvas.beginText()
                textObject.setFont(self.GetPolice(), taillePolice)
                canvas.scale(1, -1)
                textObject.setTextOrigin(self.left, -self.top - taillePolice)# - taillePolice + (taillePolice * 0.1))  # textObject._leading * 0.5)
                self.SetCouleurPolice()

                # Si largeur fixe, on wrap le texte
                from reportlab.platypus import Paragraph
                from reportlab.lib.styles import ParagraphStyle

                # para = Paragraph(valeur.replace("\\n", "<br/>"), ParagraphStyle(name="A", fontName="Helvetica", fontSize=taillePolice))
                # para.wrap(self.width, 100) # paragraph.wrap(A4_TRANSVERSE[0] - 50, A4_TRANSVERSE[1] - 50)
                # print(para)
                # # print(para.blPara.lines)
                # para.drawOn(self.canvas, self.left, -self.top - taillePolice)

                # if objet.largeurTexte != None:
                #     dc = wx.MemoryDC()
                #     dc.SetFont(wx.Font(taillePolice, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
                #     valeur = wordwrap(valeur, objet.largeurTexte * 3.7, dc, breakLongWords=True)

                textObject.textLines(valeur)
                canvas.drawText(textObject)


            # ------- IMAGE ------
            if self.categorie in ("image", "logo", "photo"):
                # s = BytesIO()
                #
                # if self.categorie == "image":
                #     match = re.match(r"^data:image/(jpeg|png);base64", self.src)
                #     if match:
                #         img_format = match.groups()[0]
                #         img_data = base64.b64decode(self.src[(match.span(0)[1] + 1):])
                #         s.write(img_data)
                #
                # if self.categorie in ("logo", "photo"):
                #     u = urllib.request.urlopen(self.src)
                #     s.write(u.read())
                #     s = self.src
                #
                # s.seek(0)

                # Récupère l'URL du logo de l'organisateur en cours
                if self.categorie == "logo":
                    organisateur = cache.get('organisateur')
                    if not organisateur:
                        organisateur = Organisateur.objects.filter(pk=1).first()
                    self.src = organisateur.logo.url

                # Si c'est une URL vers image
                if "data:" not in self.src:
                    if self.categorie == "photo" and "static/" in self.src:
                        url = os.path.join(settings.STATIC_ROOT, self.src[self.src.find("images/"):])
                    else:
                        url = settings.MEDIA_ROOT + self.src.replace("media/", "")

                # Si c'est une image au format base64
                if "data:" in self.src:
                    url = self.src

                # Chargement de l'image
                img = ImageReader(url)
                self.canvas.translate(0, self.top * 2)
                self.canvas.scale(1, -1)

                # Ajustement du ratio du logo
                if self.categorie == "logo":
                    self.width = img._image.size[0] / img._image.size[1] * self.height

                # Dessin de l'image
                self.canvas.drawImage(img, self.left, self.top, self.width, -self.height, mask="auto")


            # ------- BARCODE ------
            if self.categorie == "barcode":
                largeur, hauteur = self.width, self.height
                valeur = "123456"
                if valeur != None:
                    # Vérifie que uniquement des chiffres dans certains codes-barres
                    if self.cb_norme in ("EAN8", "EAN13"):
                        for caract in valeur:
                            if caract not in "0123456789":
                                return False

                    if self.cb_norme == None: objet.norme = "Extended39"
                    if self.cb_norme == "Codabar": barcode = Codabar(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "Code11": barcode = Code11(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "I2of5": barcode = I2of5(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "MSI": barcode = MSI(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "Code128": barcode = Code128(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "EAN13": barcode = createBarcodeDrawing("EAN13", value="{:0>12}".format(valeur), barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "EAN8": barcode = createBarcodeDrawing("EAN8", value="{:0>7}".format(valeur), barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "Extended39": barcode = Extended39(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "Standard39": barcode = Standard39(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "Extended93": barcode = Extended93(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "Standard93": barcode = Standard93(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)
                    if self.cb_norme == "POSTNET": barcode = POSTNET(valeur, barHeight=hauteur, humanReadable=self.cb_affiche_numero)

                    canvas.scale(1, -1)
                    barcode.drawOn(canvas, self.left - 18, -self.top - self.height)

            # ------- SPECIAL ------
            if self.categorie == "special":
                canvas.rect(self.left, self.top, self.width, self.height, self.SetTrait(), self.SetRemplissage())
                canvas.setFillColorRGB(0, 0, 0)
                canvas.setFont("Helvetica", 9)
                canvas.scale(1, -1)
                canvas.drawString(self.left + 6, -self.top -12, self.nom)

            canvas.restoreState()

    def SetTrait(self):
        if self.strokeWidth:
            self.canvas.setStrokeColor(self.ConvertCouleur(self.stroke))
            self.canvas.setLineWidth(self.strokeWidth)
            if self.strokeDashArray:
                self.canvas.setDash(self.strokeDashArray)
            return 1
        else:
            return 0

    def SetRemplissage(self):
        if not self.fill:
            return 0
        else:
            self.canvas.setFillColor(self.ConvertCouleur(self.fill))
            return 1

    def SetCouleurPolice(self):
        self.canvas.setFillColor(self.ConvertCouleur(self.fill))

    def GetPolice(self):
        police = "Helvetica"
        if hasattr(self, "fontWeight") and self.fontWeight == "bold" : police = "Helvetica-Bold"
        if hasattr(self, "fontStyle") and self.fontStyle == "italic" : police = "Helvetica-Bold"
        if hasattr(self, "fontWeight") and self.fontWeight == "bold" and self.fontStyle == "italic" : police = "Helvetica-BoldOblique"
        return police

    def ConvertCouleur(self, couleur=""):
        if couleur and couleur.startswith('rgba'):
            temp = couleur[5:-1].split(",")
            return Color(float(temp[0])/255, float(temp[1])/255, float(temp[2])/255, float(temp[3]))
        return Color(0, 0, 0, 1)

    def GetCoords(self):
        return [self.left, self.top, self.width, self.height]


