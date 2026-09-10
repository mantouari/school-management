"""Vues publiques : page d'accueil, tableau de bord, sonde de santé."""
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.academic.models import AnneeScolaire, Classe
from apps.attendance.models import Presence
from apps.communication.models import Annonce
from apps.finance.models import Paiement
from apps.students.models import Eleve
from apps.users.models import User

from .models import Etablissement


def home(request):
    """Page publique de présentation de l'établissement."""
    etablissement = Etablissement.get_solo()
    annee = AnneeScolaire.objects.filter(active=True).first()
    return render(
        request,
        "home.html",
        {
            "etablissement": etablissement,
            "annee": annee,
            "nb_eleves": Eleve.objects.count(),
            "nb_classes": Classe.objects.count(),
        },
    )


@login_required
def dashboard(request):
    """Tableau de bord : indicateurs clés de l'année scolaire active."""
    annee = AnneeScolaire.objects.filter(active=True).first()
    classes = Classe.objects.filter(annee_scolaire=annee) if annee else Classe.objects.none()
    today = timezone.localdate()

    context = {
        "annee": annee,
        "nb_eleves": Eleve.objects.count(),
        "nb_enseignants": User.objects.filter(role=User.Role.ENSEIGNANT).count(),
        "nb_classes": classes.count(),
        "total_encaisse": (
            Paiement.objects.filter(frais__annee_scolaire=annee).aggregate(
                total=Sum("montant")
            )["total"]
            or 0
        )
        if annee
        else 0,
        "absences_du_jour": Presence.objects.filter(
            date=today, statut__in=[Presence.Statut.ABSENT, Presence.Statut.RETARD]
        ).count(),
        "annonces": Annonce.objects.order_by("-date_publication")[:5],
        "etablissement": Etablissement.get_solo(),
    }
    return render(request, "dashboard.html", context)


def health_check(request):
    """Sonde utilisée par Render pour vérifier que l'application répond."""
    return JsonResponse({"status": "ok"})
