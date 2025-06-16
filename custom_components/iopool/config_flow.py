from homeassistant import config_entries
import voluptuous as vol
import requests

from .const import DOMAIN, CONF_API_KEY, CONF_INTERVAL, CONF_UNIT_TEMP, API_URL, DEFAULT_INTERVAL, DEFAULT_UNIT_TEMP


class IopoolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            interval = user_input.get(CONF_INTERVAL, DEFAULT_INTERVAL)
            unit = user_input.get(CONF_UNIT_TEMP, DEFAULT_UNIT_TEMP)

            if await self._validate_api_key(api_key):
                return self.async_create_entry(
                    title="iopool",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_INTERVAL: interval,
                        CONF_UNIT_TEMP: unit,
                    }
                )
            else:
                errors["base"] = "invalid_api_key"

        schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.All(int, vol.Range(min=30, max=3600)),
            vol.Optional(CONF_UNIT_TEMP, default=DEFAULT_UNIT_TEMP): vol.In({
                "C": "°C",
                "F": "°F"
            }),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _validate_api_key(self, api_key: str) -> bool:
        try:
            resp = await self.hass.async_add_executor_job(
                lambda: requests.get(API_URL, headers={"x-api-key": api_key}, timeout=10)
            )
            return resp.status_code == 200
        except Exception:
            return False
