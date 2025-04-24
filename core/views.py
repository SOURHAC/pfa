from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from .models import Parcelle, Mesure, CapteurData
from .calculs.calculs_irrigation import dose_et0, dose_humidite, dose_combinaison, duree_irrigation
import json
import csv
from django.http import HttpResponse
from datetime import timedelta, datetime
from django.utils.timezone import now


# 🔧 API pour recevoir les données via POST (par ex. depuis ChirpStack)
@csrf_exempt
def receive_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Crée ou récupère une parcelle en fonction de son nom
        parcelle_obj, _ = Parcelle.objects.get_or_create(nom=data['parcelle'])

        # Enregistre les données reçues dans CapteurData
        CapteurData.objects.create(
            parcelle=parcelle_obj,
            humidite=data['humidite'],
            temperature=data['temperature'],
            salinite=data['salinite'],
            npk=data['npk'],
            eto=data.get('eto')
        )

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'error': 'Invalid method'}, status=405)

# 📊 Vue du tableau de bord avec les graphiques
def dashboard(request):
    parcelles = Parcelle.objects.all()
    parcelle_data = {}

    for parcelle in parcelles:
        mesures = Mesure.objects.filter(parcelle=parcelle).order_by('timestamp')
        humidite = [m.humidite for m in mesures]
        volume = [m.volume_eau for m in mesures]
        labels = [m.timestamp.strftime("%d/%m %H:%M") for m in mesures]

        # Dernières valeurs pour l'affichage dans la carte de chaque parcelle
        parcelle.humidite = humidite[-1] if humidite else None
        parcelle.volume = volume[-1] if volume else None

        parcelle_data[parcelle.id] = {
            'labels': labels,
            'humidite': humidite,
            'volume': volume,
        }

    context = {
        'parcelles': parcelles,
        'parcelle_data': json.dumps(parcelle_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'core/dashboard.html', context)

def calculs_irrigation(request):
    parcelles = Parcelle.objects.all()

    # Calculs d'irrigation pour chaque parcelle
    for parcelle in parcelles:
        mesures = Mesure.objects.filter(parcelle=parcelle).order_by('timestamp')
        humidite = [m.humidite for m in mesures]
        volume_eau = [m.volume_eau for m in mesures]

        if mesures.exists():
            dernier_humidite = humidite[-1]
            # Paramètres pour le calcul (exemple fictif)
            ET0 = 3.1  # Exemple de valeur d'ET0
            Kc = 1.2    # Exemple de coefficient de culture
            surface = 100  # Surface en m²
            Hopt = 60  # Humidité optimale en %
            capacite_sol = 0.2  # Capacité du sol en L/m²
            profondeur = 30  # Profondeur de sol en cm
            debit_total_lh = 10  # Débit total en L/h

            # Effectuer les calculs
            dose_eto = dose_et0(ET0, Kc, surface)
            dose_humidite_val = dose_humidite(Hopt, dernier_humidite, profondeur, surface, capacite_sol)
            dose_comb = dose_combinaison(ET0, Kc, surface, Hopt, dernier_humidite, profondeur, capacite_sol)
            duree_irrigation_val = duree_irrigation(dose_comb, debit_total_lh)

            # Tu peux enregistrer ou utiliser ces résultats selon ta logique, mais ne les passe pas dans le contexte ici
            # Par exemple, les enregistrer dans la base de données, envoyer un email, etc.

    return render(request, 'core/calculs_irrigation.html')  # Rendu d'une page vide ou d'un message de succès

# 🕰️ Vue historique des mesures CapteurData
def historique(request):
    data = CapteurData.objects.all().order_by('-date')
    return render(request, 'core/historique.html', {'data': data})

# ⚙️ Vue de la page de configuration
def config_view(request):
    return render(request, 'core/config.html')

def export_mesures_csv(request):
    # Date limite : 35 jours en arrière
    date_limite = now() - timedelta(days=35)

    # Création de la réponse HTTP avec type CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mesures_parcelles.csv"'

    writer = csv.writer(response)
    writer.writerow(['Parcelle', 'Timestamp', 'Humidité (%)', 'Volume Eau (L)'])

    mesures = Mesure.objects.filter(timestamp__gte=date_limite).select_related('parcelle').order_by('parcelle__nom', 'timestamp')

    for mesure in mesures:
        writer.writerow([
            mesure.parcelle.nom,
            mesure.timestamp.strftime('%Y-%m-%d %H:%M'),
            mesure.humidite,
            mesure.volume_eau
        ])

    return response