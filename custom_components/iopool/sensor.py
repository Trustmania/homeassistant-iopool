from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_UNIT_TEMP
from .model import Pool
from .coordinator import IopoolCoordinator

SENSOR_TYPES = {
    "temperature": {"unit": "°C", "translation_key": "temperature"},
    "ph": {"unit": "pH", "translation_key": "ph"},
    "orp": {"unit": "mV", "translation_key": "orp"},
    "filtrationDuration": {"unit": "h", "translation_key": "filtrationDuration"},
    "measuredAt": {"unit": None, "translation_key": "measuredAt"},
    "mode": {"unit": None, "translation_key": "mode"},
    "measure_mode": {"unit": None, "translation_key": "measure_mode"},
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: IopoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    unit_pref = entry.data.get(CONF_UNIT_TEMP, "C")

    sensors = []

    for pool in coordinator.data:
        for key, props in SENSOR_TYPES.items():
            sensors.append(
                IopoolSensor(
                    pool=pool,
                    coordinator=coordinator,
                    sensor_type=key,
                    unit_override=props["unit"],
                    translation_key=props["translation_key"],
                    unit_pref=unit_pref,
                )
            )

    async_add_entities(sensors)


class IopoolSensor(SensorEntity):
    def __init__(self, pool: Pool, coordinator: IopoolCoordinator, sensor_type: str, unit_override: str, translation_key: str, unit_pref: str):
        self._pool = pool
        self._coordinator = coordinator
        self._type = sensor_type
        self._unit_pref = unit_pref

        self._attr_unique_id = f"iopool_{pool.id}_{sensor_type}"
        self._attr_translation_key = translation_key
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, pool.id)},
            name=f"iopool {pool.title}",
            manufacturer="iopool",
            model="Eco",
        )

        if sensor_type in ["mode", "measure_mode"]:
            self._attr_device_class = "enum"
            if sensor_type == "mode":
                self._attr_options = ["STANDARD", "OPENING", "WINTER", "INITIALIZATION"]
            else:
                self._attr_options = ["gateway", "live", "manual", "maintenance", "backup", "standard"]

        if sensor_type == "temperature":
            self._attr_native_unit_of_measurement = "°F" if unit_pref == "F" else unit_override
        elif sensor_type == "measuredAt":
            self._attr_device_class = "timestamp"
        else:
            self._attr_native_unit_of_measurement = unit_override

    @property
    def extra_state_attributes(self):
        if self._type == "orp":
            return {
                "rating_scale": [
                    {"from": 0, "to": 550, "level": "bad", "color": "red"},
                    {"from": 550, "to": 650, "level": "medium", "color": "yellow"},
                    {"from": 650, "to": 800, "level": "good", "color": "green"},
                    {"from": 800, "to": 1000, "level": "medium", "color": "yellow"},
                    {"from": 1000, "to": 2000, "level": "bad", "color": "red"},
                ]
            }
        elif self._type == "ph":
            return {
                "rating_scale": [
                    {"from": 0.0, "to": 6.8, "level": "bad", "color": "red"},
                    {"from": 6.8, "to": 7.1, "level": "medium", "color": "yellow"},
                    {"from": 7.1, "to": 7.7, "level": "good", "color": "green"},
                    {"from": 7.7, "to": 8.1, "level": "medium", "color": "yellow"},
                    {"from": 8.1, "to": 14.0, "level": "bad", "color": "red"},
                ]
            }
        return {}

    async def async_added_to_hass(self):
        """Register for coordinator updates."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    def _temperature(self, pool):
        temperature = pool.latestMeasure.temperature
        if self._unit_pref == "F":
            temperature = (temperature * 9 / 5 + 32)
        return round(temperature, 1)

    @property
    def native_value(self):
        pool = next((p for p in self._coordinator.data if p.id == self._pool.id), None)
        if not pool:
            return None

        lm = pool.latestMeasure

        match self._type:
            case "temperature":
                return self._temperature(pool) if lm else None
            case "ph":
                return round(lm.ph, 4) if lm else None
            case "orp":
                return int(lm.orp) if lm else None
            case "filtrationDuration":
                return pool.advice.filtrationDuration
            case "measuredAt":
                return lm.measuredAt if lm else None
            case "mode":
                return pool.mode
            case "measure_mode":
                return lm.mode if lm else None

        return None
