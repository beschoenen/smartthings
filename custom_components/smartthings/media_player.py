from collections.abc import Sequence
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pysmartthings import DeviceEntity, Capability

from . import SmartThingsEntity
from .const import DATA_BROKERS, DOMAIN

from homeassistant.components.media_player import (
    ATTR_MEDIA_ENQUEUE,
    MediaPlayerDeviceClass,
    MediaPlayerEnqueue,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add fans for a config entry."""
    broker = hass.data[DOMAIN][DATA_BROKERS][config_entry.entry_id]
    async_add_entities(
        [
            SmartThingsMediaPlayer(device)
            for device in broker.devices.values()
            if broker.any_assigned(device.device_id, "media_player")
        ]
    )


def get_capabilities(capabilities: Sequence[str]) -> Sequence[str] | None:
    """Return all capabilities supported if minimum required are present."""
    supported = [
        Capability.switch,
        Capability.media_input_source,
        Capability.media_playback,
        Capability.media_playback_repeat,
        Capability.media_playback_shuffle,
        Capability.audio_mute,
        Capability.audio_volume,
        Capability.tv_channel,
        Capability.power_meter,
        Capability.power_consumption_report,
        Capability.power_source,
    ]

    if all(capability in capabilities for capability in supported):
        return supported
    return None


class SmartThingsMediaPlayer(SmartThingsEntity, MediaPlayerEntity):
    """Define a SmartThings Media Player."""

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self._device.switch_on(set_status=True)
        # State is set optimistically in the command above, therefore update
        # the entity state ahead of receiving the confirming push updates
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the media player off."""
        await self._device.switch_off(set_status=True)
        # State is set optimistically in the command above, therefore update
        # the entity state ahead of receiving the confirming push updates
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """Return true if media player is on."""
        return self._device.status.switch

    @property
    def volume_level(self):
        return self._device.status.volume
