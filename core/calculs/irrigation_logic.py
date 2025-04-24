from calculs_irrigation import dose_et0, dose_humidite, dose_combinaison, duree_irrigation

# Simuler base de données
MAP_PARCELLES = {
    "esp32_A": {"nom": "A", "strategie": "ET0"},
    "esp32_B": {"nom": "B", "strategie": "HUMIDITE"},
    "esp32_C": {"nom": "C", "strategie": "COMBINE"},
}

def process_data(devEui, payload):
    parcelle = MAP_PARCELLES.get(devEui)
    if not parcelle:
        raise Exception("Parcelle inconnue")

    ET0 = float(payload.get("et0", 0))
    H = float(payload.get("hum", 0)) / 100  # ex: 28% → 0.28
    jours = int(payload.get("days", 10))

    # Paramètres fixes
    surface = 2.5
    profondeur = 0.2
    capacite_sol = 200
    goutteurs = 50
    debit_total = goutteurs * 1  # 1 L/h par goutteur

    # Kc selon le jour
    if jours <= 7:
        Kc = 0.6
    elif 8 <= jours <= 20:
        Kc = 0.8
    else:
        Kc = 0.7

    # Choix stratégie
    if parcelle["strategie"] == "ET0":
        dose = dose_et0(ET0, Kc, surface)
    elif parcelle["strategie"] == "HUMIDITE":
        dose = dose_humidite(0.35, H, profondeur, surface, capacite_sol)
    else:
        dose = dose_combinaison(ET0, Kc, surface, 0.35, H, profondeur, capacite_sol)

    duree = duree_irrigation(dose, debit_total)

    if dose > 0.5:
        envoyer_downlink(devEui, duree)
    return {"parcelle": parcelle["nom"], "dose": dose, "duree": duree}

# Envoie d'une commande vers ChirpStack
import requests
import base64
def envoyer_downlink(devEui, duree_minutes):
    payload = f"T{int(duree_minutes):02d}"
    base64_payload = base64.b64encode(payload.encode()).decode()
    
    downlink = {
        "deviceQueueItem": {
            "confirmed": True,
            "data": base64_payload,
            "fPort": 10,
            "devEui": devEui
        }
    }

    print(f"🚀 Envoi downlink à {devEui} : {payload}")
    
    # Remplace par ton endpoint API ChirpStack
    url = f"http://<chirpstack_host>:8080/api/devices/{devEui}/queue"
    headers = {"Grpc-Metadata-Authorization": "Bearer <API_KEY>"}
    
    response = requests.post(url, json=downlink, headers=headers)
    print("↩️ Réponse ChirpStack :", response.status_code, response.text)
