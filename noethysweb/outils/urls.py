# -*- coding: utf-8 -*-
#  Copyright (c) 2019-2021 Ivan LUCAS.
#  Noethysweb, application de gestion multi-activités.
#  Distribué sous licence GNU GPL.

from django.urls import include, path
from core.views import toc
from core.decorators import secure_ajax
from outils.views import editeur_emails, editeur_emails_express, historique, update, sauvegarde_creer, statistiques, contacts, \
                        editeur_emails_familles, editeur_emails_individus, editeur_emails_contacts, editeur_emails_listes_diffusion, \
                        editeur_emails_saisie_libre, emails, notes_versions, messages_portail, messagerie_portail, notes, calendrier_annuel, \
                        demandes_portail, liste_conso_sans_presta, statistiques_portail, correcteur, editeur_sms, editeur_sms_familles, \
                        editeur_sms_individus, editeur_sms_saisie_libre, sms

urlpatterns = [

    # Table des matières
    path('outils/', toc.Toc.as_view(menu_code="outils_toc"), name='outils_toc'),

    # Statistiques
    path('outils/statistiques', statistiques.View.as_view(), name='statistiques'),
    path('outils/statistiques_portail', statistiques_portail.View.as_view(), name='statistiques_portail'),

    # Carnets de contacts
    path('outils/contacts/liste', contacts.Liste.as_view(), name='contacts_liste'),
    path('outils/contacts/ajouter', contacts.Ajouter.as_view(), name='contacts_ajouter'),
    path('outils/contacts/modifier/<int:pk>', contacts.Modifier.as_view(), name='contacts_modifier'),
    path('outils/contacts/supprimer/<int:pk>', contacts.Supprimer.as_view(), name='contacts_supprimer'),

    # Editeur d'emails
    path('outils/editeur_emails', editeur_emails.Ajouter.as_view(), name='editeur_emails'),
    path('outils/editeur_emails/<int:pk>', editeur_emails.Modifier.as_view(), name='editeur_emails'),
    path('outils/editeur_emails/familles/<int:idmail>', editeur_emails_familles.Liste.as_view(), name='editeur_emails_familles'),
    path('outils/editeur_emails/individus/<int:idmail>', editeur_emails_individus.Liste.as_view(), name='editeur_emails_individus'),
    path('outils/editeur_emails/contacts/<int:idmail>', editeur_emails_contacts.Liste.as_view(), name='editeur_emails_contacts'),
    path('outils/editeur_emails/listes_diffusion/<int:idmail>', editeur_emails_listes_diffusion.Liste.as_view(), name='editeur_emails_listes_diffusion'),
    path('outils/editeur_emails/saisie_libre/<int:idmail>', editeur_emails_saisie_libre.Liste.as_view(), name='editeur_emails_saisie_libre'),

    path('outils/emails/liste', emails.Liste.as_view(), name='emails_liste'),
    path('outils/emails/supprimer/<int:pk>', emails.Supprimer.as_view(), name='emails_supprimer'),
    path('outils/emails/supprimer_plusieurs/<str:listepk>', emails.Supprimer_plusieurs.as_view(), name='emails_supprimer_plusieurs'),

    # Editeur de SMS
    path('outils/editeur_sms', editeur_sms.Ajouter.as_view(), name='editeur_sms'),
    path('outils/editeur_sms/<int:pk>', editeur_sms.Modifier.as_view(), name='editeur_sms'),
    path('outils/editeur_sms/familles/<int:idsms>', editeur_sms_familles.Liste.as_view(), name='editeur_sms_familles'),
    path('outils/editeur_sms/individus/<int:idsms>', editeur_sms_individus.Liste.as_view(), name='editeur_sms_individus'),
    path('outils/editeur_sms/saisie_libre/<int:idsms>', editeur_sms_saisie_libre.Liste.as_view(), name='editeur_sms_saisie_libre'),

    path('outils/sms/liste', sms.Liste.as_view(), name='sms_liste'),
    path('outils/sms/supprimer/<int:pk>', sms.Supprimer.as_view(), name='sms_supprimer'),
    path('outils/sms/supprimer_plusieurs/<str:listepk>', sms.Supprimer_plusieurs.as_view(), name='sms_supprimer_plusieurs'),

    path('outils/historique', historique.Liste.as_view(), name='historique'),
    path('outils/update', update.View.as_view(), name='update'),
    path('outils/notes_versions', notes_versions.View.as_view(), name='notes_versions'),
    path('outils/calendrier_annuel', calendrier_annuel.View.as_view(), name='calendrier_annuel'),

    # Notes
    path('outils/notes/liste', notes.Liste.as_view(), name='notes_liste'),
    path('outils/notes/ajouter', notes.Ajouter.as_view(), name='notes_ajouter'),
    path('outils/notes/modifier/<int:pk>', notes.Modifier.as_view(), name='notes_modifier'),
    path('outils/notes/supprimer/<int:pk>', notes.Supprimer.as_view(), name='notes_supprimer'),

    # Sauvegarde
    path('outils/sauvegarde/creer', sauvegarde_creer.View.as_view(), name='sauvegarde_creer'),

    # Portail
    path('outils/portail/messages/liste', messages_portail.Liste.as_view(), name='messages_portail_liste'),
    path('outils/portail/messages/supprimer/<int:pk>', messages_portail.Supprimer.as_view(), name='messages_portail_supprimer'),

    path('outils/portail/messagerie', messagerie_portail.Ajouter.as_view(), name='messagerie_portail'),
    path('outils/portail/messagerie/<int:idstructure>/<int:idfamille>', messagerie_portail.Ajouter.as_view(), name='messagerie_portail'),

    path('outils/portail/renseignements/liste', demandes_portail.Liste.as_view(), name='demandes_portail_liste'),

    # Dépannage
    path('outils/correcteur', correcteur.View.as_view(), name='correcteur'),
    path('outils/liste_conso_sans_presta', liste_conso_sans_presta.Liste.as_view(), name='liste_conso_sans_presta'),
    path('outils/liste_conso_sans_presta_supprimer_plusieurs/<str:listepk>', liste_conso_sans_presta.Supprimer_plusieurs.as_view(), name='liste_conso_sans_presta_supprimer_plusieurs'),

    # AJAX
    path('outils/get_modele_email', secure_ajax(editeur_emails.Get_modele_email), name='ajax_get_modele_email'),
    path('outils/get_signature_email', secure_ajax(editeur_emails.Get_signature_email), name='ajax_get_signature_email'),
    path('outils/get_view_editeur_email', secure_ajax(editeur_emails_express.Get_view_editeur_email), name='ajax_get_view_editeur_email'),
    path('outils/envoyer_email_express', secure_ajax(editeur_emails_express.Envoyer_email), name='ajax_envoyer_email_express'),
    path('outils/get_calendrier_annuel', secure_ajax(calendrier_annuel.Get_calendrier_annuel), name='ajax_get_calendrier_annuel'),
    path('outils/portail/demandes/', secure_ajax(demandes_portail.Appliquer_modification), name='ajax_appliquer_modification_portail'),
    path('outils/sauvegarder_db/', secure_ajax(sauvegarde_creer.Sauvegarder_db), name='ajax_sauvegarder_db'),
    path('outils/sauvegarder_media/', secure_ajax(sauvegarde_creer.Sauvegarder_media), name='ajax_sauvegarder_media'),
    path('outils/sauvegarder_liste/', secure_ajax(sauvegarde_creer.Get_liste_sauvegardes), name='ajax_get_liste_sauvegardes'),
    path('outils/messages/marquer_lu/', secure_ajax(messagerie_portail.Marquer_lu), name='ajax_message_marquer_lu'),


]
