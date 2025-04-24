from django.db import models

class Parcelle(models.Model):
    nom = models.CharField(max_length=1)  # A, B, ou C

    def __str__(self):
        return f"Parcelle {self.nom}"

class CapteurData(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, default=1)
    date = models.DateTimeField(auto_now_add=True)
    humidite = models.FloatField()
    temperature = models.FloatField()
    salinite = models.FloatField()
    npk = models.CharField(max_length=50)
    eto = models.FloatField(null=True, blank=True)

class IrrigationDecision(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, default=1)
    date = models.DateTimeField(auto_now_add=True)
    strategie = models.CharField(max_length=20)
    dose_eau = models.FloatField()

class Mesure(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    humidite = models.FloatField()
    volume_eau = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.parcelle.nom} - H: {self.humidite}% | V: {self.volume_eau} L"
