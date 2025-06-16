import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from datetime import timedelta
import requests

from .const import CONF_API_KEY, CONF_INTERVAL, DEFAULT_INTERVAL, API_URL
from .model import Pool

LOGGER = logging.getLogger(__name__)


class IopoolCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.api_key = config[CONF_API_KEY]
        self.poll_interval = config.get(CONF_INTERVAL, DEFAULT_INTERVAL)
        self._last_measured_at = {}

        super().__init__(
            hass,
            logger=LOGGER,
            name="iopool",
            update_interval=timedelta(seconds=self.poll_interval),
        )

    def _get_headers(self):
        return {
            "x-api-key": self.api_key,
            "Accept": "application/json"
        }

    async def _async_update_data(self):
        try:
            response = await self.hass.async_add_executor_job(
                lambda: requests.get(API_URL, headers=self._get_headers(), timeout=10)
            )
            response.raise_for_status()

            raw_data = response.json()
            return [Pool(**item) for item in raw_data]

        except Exception as err:
            raise UpdateFailed(f"Some error on fetching the iopool data: {err}")
