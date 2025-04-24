def dose_et0(ET0, Kc, surface):
    return ET0 * Kc * surface

def dose_humidite(Hopt, Hactuelle, profondeur, surface, capacite_sol):
    deficit = max(0, Hopt - Hactuelle)
    return deficit * profondeur * surface * capacite_sol

def dose_combinaison(ET0, Kc, surface, Hopt, Hactuelle, profondeur, capacite_sol):
    d1 = dose_et0(ET0, Kc, surface)
    d2 = dose_humidite(Hopt, Hactuelle, profondeur, surface, capacite_sol)
    return min(d1, d2)

def duree_irrigation(dose_l, debit_total_lh):
    return dose_l / (debit_total_lh / 60)  # minutes
