# Home Assistant Integration: iopool

Diese Integration verbindet deine iopool Smart Pool Lösung mit Home Assistant.

## 🔧 Funktionen

- Verbindet einen oder mehrere Pools mit Home Assistant
- Erstellt ein Gerät pro Pool
- Liefert folgende Sensoren:
  - Wassertemperatur
  - pH-Wert
  - ORP (Redox)
  - Filterlaufzeit
  - Messzeitpunkt
  - Pool-Modus (z.B. Standard, Winter)
  - Messmodus (z.B. Gateway, Live)
- Binary Sensoren:
  - Messung gültig
  - Maßnahme erforderlich
- Unterstützt °C/°F Auswahl & benutzerdefiniertes Polling-Intervall

## 🧪 Visualisierung

ORP und pH werden mit einer Skala (gut/mittel/schlecht) als `extra_state_attributes` geliefert und lassen sich mit Gauge-Karten automatisch einfärben.

## 🛠️ Installation

1. [HACS](https://hacs.xyz) öffnen → `Benutzerdefinierte Repositories` → URL deines Repos hinzufügen → Kategorie: `Integration`
2. Integration „iopool“ installieren
3. Home Assistant neu starten
4. Integration über „Integrationen“ hinzufügen

## ⚙️ Konfiguration

Erfolgt über die Benutzeroberfläche (config_flow). Du gibst an:

- API Key (iopool)
- Polling-Intervall (Sekunden, min. 30)
- Temperatureinheit (°C oder °F)

## 📚 Beispiel Lovelace Gauge

```yaml
type: custom:mushroom-template-card
entity: sensor.iopool_<pool>_orp
primary: Redox (ORP)
secondary: "{{ states('sensor.iopool_<pool>_orp') }} mV"
icon: mdi:flash
icon_color: >
  {% set value = states('sensor.iopool_<pool>_orp') | float %}
  {% set scale = state_attr('sensor.iopool_<pool>_orp', 'rating_scale') %}
  {% for zone in scale %}
    {% if zone.from <= value < zone.to %}
      {{ zone.color }}
    {% endif %}
  {% endfor %}