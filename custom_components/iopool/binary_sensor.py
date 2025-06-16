from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .model import Pool
from .coordinator import IopoolCoordinator

BINARY_SENSORS = {
    "isValid": {"translation_key": "isValid"},
    "hasAnActionRequired": {"translation_key": "hasAnActionRequired"},
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: IopoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for pool in coordinator.data:
        for key, props in BINARY_SENSORS.items():
            sensors.append(
                IopoolBinarySensor(
                    pool=pool,
                    coordinator=coordinator,
                    sensor_type=key,
                    translation_key=props["translation_key"],
                )
            )

    async_add_entities(sensors)


class IopoolBinarySensor(BinarySensorEntity):
    def __init__(self, pool: Pool, coordinator: IopoolCoordinator, sensor_type: str, translation_key: str):
        self._pool = pool
        self._coordinator = coordinator
        self._type = sensor_type

        self._attr_unique_id = f"iopool_{pool.id}_{sensor_type}"
        self._attr_translation_key = translation_key
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, pool.id)},
            name=f"iopool {pool.title}",
            manufacturer="iopool",
            model="Eco",
        )

        if sensor_type == "hasAnActionRequired":
            self._attr_icon = "mdi:alert-circle"
        elif sensor_type == "isValid":
            self._attr_icon = "mdi:check-decagram"

    async def async_added_to_hass(self):
        """Register for coordinator updates."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    @property
    def is_on(self) -> bool | None:
        pool = next((p for p in self._coordinator.data if p.id == self._pool.id), None)
        if not pool:
            return None

        lm = pool.latestMeasure

        match self._type:
            case "isValid":
                return lm.isValid if lm else None
            case "hasAnActionRequired":
                return pool.hasAnActionRequired

        return None
