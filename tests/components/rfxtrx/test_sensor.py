"""The tests for the Rfxtrx sensor platform."""
import pytest

from homeassistant.components.rfxtrx.const import ATTR_EVENT
from homeassistant.const import TEMP_CELSIUS, UNIT_PERCENTAGE
from homeassistant.core import State
from homeassistant.setup import async_setup_component

from . import _signal_event

from tests.common import mock_restore_cache


async def test_default_config(hass, rfxtrx):
    """Test with 0 sensor."""
    await async_setup_component(
        hass, "sensor", {"sensor": {"platform": "rfxtrx", "devices": {}}}
    )
    await hass.async_block_till_done()

    assert len(hass.states.async_all()) == 0


async def test_one_sensor(hass, rfxtrx):
    """Test with 1 sensor."""
    assert await async_setup_component(
        hass,
        "rfxtrx",
        {"rfxtrx": {"device": "abcd", "devices": {"0a52080705020095220269": {}}}},
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_05_02_temperature")
    assert state
    assert state.state == "unknown"
    assert (
        state.attributes.get("friendly_name")
        == "WT260,WT260H,WT440H,WT450,WT450H 05:02 Temperature"
    )
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS


@pytest.mark.parametrize(
    "state,event",
    [["18.4", "0a520801070100b81b0279"], ["17.9", "0a52085e070100b31b0279"]],
)
async def test_state_restore(hass, rfxtrx, state, event):
    """State restoration."""

    entity_id = "sensor.wt260_wt260h_wt440h_wt450_wt450h_07_01_temperature"

    mock_restore_cache(hass, [State(entity_id, state, attributes={ATTR_EVENT: event})])

    assert await async_setup_component(
        hass,
        "rfxtrx",
        {"rfxtrx": {"device": "abcd", "devices": {"0a520801070100b81b0279": {}}}},
    )
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == state


async def test_one_sensor_no_datatype(hass, rfxtrx):
    """Test with 1 sensor."""
    assert await async_setup_component(
        hass,
        "rfxtrx",
        {"rfxtrx": {"device": "abcd", "devices": {"0a52080705020095220269": {}}}},
    )
    await hass.async_block_till_done()

    base_id = "sensor.wt260_wt260h_wt440h_wt450_wt450h_05_02"
    base_name = "WT260,WT260H,WT440H,WT450,WT450H 05:02"

    state = hass.states.get(f"{base_id}_temperature")
    assert state
    assert state.state == "unknown"
    assert state.attributes.get("friendly_name") == f"{base_name} Temperature"
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS

    state = hass.states.get(f"{base_id}_humidity")
    assert state
    assert state.state == "unknown"
    assert state.attributes.get("friendly_name") == f"{base_name} Humidity"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    state = hass.states.get(f"{base_id}_humidity_status")
    assert state
    assert state.state == "unknown"
    assert state.attributes.get("friendly_name") == f"{base_name} Humidity status"
    assert state.attributes.get("unit_of_measurement") == ""

    state = hass.states.get(f"{base_id}_rssi_numeric")
    assert state
    assert state.state == "unknown"
    assert state.attributes.get("friendly_name") == f"{base_name} Rssi numeric"
    assert state.attributes.get("unit_of_measurement") == "dBm"

    state = hass.states.get(f"{base_id}_battery_numeric")
    assert state
    assert state.state == "unknown"
    assert state.attributes.get("friendly_name") == f"{base_name} Battery numeric"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE


async def test_several_sensors(hass, rfxtrx):
    """Test with 3 sensors."""
    assert await async_setup_component(
        hass,
        "rfxtrx",
        {
            "rfxtrx": {
                "device": "abcd",
                "devices": {
                    "0a52080705020095220269": {},
                    "0a520802060100ff0e0269": {},
                },
            }
        },
    )
    await hass.async_block_till_done()
    await hass.async_start()

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_05_02_temperature")
    assert state
    assert state.state == "unknown"
    assert (
        state.attributes.get("friendly_name")
        == "WT260,WT260H,WT440H,WT450,WT450H 05:02 Temperature"
    )
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_06_01_temperature")
    assert state
    assert state.state == "unknown"
    assert (
        state.attributes.get("friendly_name")
        == "WT260,WT260H,WT440H,WT450,WT450H 06:01 Temperature"
    )
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_06_01_humidity")
    assert state
    assert state.state == "unknown"
    assert (
        state.attributes.get("friendly_name")
        == "WT260,WT260H,WT440H,WT450,WT450H 06:01 Humidity"
    )
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE


async def test_discover_sensor(hass, rfxtrx):
    """Test with discovery of sensor."""
    assert await async_setup_component(
        hass, "rfxtrx", {"rfxtrx": {"device": "abcd", "automatic_add": True}},
    )
    await hass.async_block_till_done()
    await hass.async_start()

    # 1
    await _signal_event(hass, "0a520801070100b81b0279")
    base_id = "sensor.wt260_wt260h_wt440h_wt450_wt450h_07_01"

    state = hass.states.get(f"{base_id}_humidity")
    assert state
    assert state.state == "27"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    state = hass.states.get(f"{base_id}_humidity_status")
    assert state
    assert state.state == "normal"
    assert state.attributes.get("unit_of_measurement") == ""

    state = hass.states.get(f"{base_id}_rssi_numeric")
    assert state
    assert state.state == "-64"
    assert state.attributes.get("unit_of_measurement") == "dBm"

    state = hass.states.get(f"{base_id}_temperature")
    assert state
    assert state.state == "18.4"
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS

    state = hass.states.get(f"{base_id}_battery_numeric")
    assert state
    assert state.state == "90"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    # 2
    await _signal_event(hass, "0a52080405020095240279")
    base_id = "sensor.wt260_wt260h_wt440h_wt450_wt450h_05_02"
    state = hass.states.get(f"{base_id}_humidity")

    assert state
    assert state.state == "36"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    state = hass.states.get(f"{base_id}_humidity_status")
    assert state
    assert state.state == "normal"
    assert state.attributes.get("unit_of_measurement") == ""

    state = hass.states.get(f"{base_id}_rssi_numeric")
    assert state
    assert state.state == "-64"
    assert state.attributes.get("unit_of_measurement") == "dBm"

    state = hass.states.get(f"{base_id}_temperature")
    assert state
    assert state.state == "14.9"
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS

    state = hass.states.get(f"{base_id}_battery_numeric")
    assert state
    assert state.state == "90"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    # 1 Update
    await _signal_event(hass, "0a52085e070100b31b0279")
    base_id = "sensor.wt260_wt260h_wt440h_wt450_wt450h_07_01"

    state = hass.states.get(f"{base_id}_humidity")
    assert state
    assert state.state == "27"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    state = hass.states.get(f"{base_id}_humidity_status")
    assert state
    assert state.state == "normal"
    assert state.attributes.get("unit_of_measurement") == ""

    state = hass.states.get(f"{base_id}_rssi_numeric")
    assert state
    assert state.state == "-64"
    assert state.attributes.get("unit_of_measurement") == "dBm"

    state = hass.states.get(f"{base_id}_temperature")
    assert state
    assert state.state == "17.9"
    assert state.attributes.get("unit_of_measurement") == TEMP_CELSIUS

    state = hass.states.get(f"{base_id}_battery_numeric")
    assert state
    assert state.state == "90"
    assert state.attributes.get("unit_of_measurement") == UNIT_PERCENTAGE

    assert len(hass.states.async_all()) == 10


async def test_update_of_sensors(hass, rfxtrx):
    """Test with 3 sensors."""
    assert await async_setup_component(
        hass,
        "rfxtrx",
        {
            "rfxtrx": {
                "device": "abcd",
                "devices": {
                    "0a52080705020095220269": {},
                    "0a520802060100ff0e0269": {},
                },
            }
        },
    )
    await hass.async_block_till_done()
    await hass.async_start()

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_05_02_temperature")
    assert state
    assert state.state == "unknown"

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_06_01_temperature")
    assert state
    assert state.state == "unknown"

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_06_01_humidity")
    assert state
    assert state.state == "unknown"

    await _signal_event(hass, "0a520802060101ff0f0269")
    await _signal_event(hass, "0a52080705020085220269")

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_05_02_temperature")
    assert state
    assert state.state == "13.3"

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_06_01_temperature")
    assert state
    assert state.state == "51.1"

    state = hass.states.get("sensor.wt260_wt260h_wt440h_wt450_wt450h_06_01_humidity")
    assert state
    assert state.state == "15"
