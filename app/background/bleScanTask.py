import asyncio

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

from .bleConstants import *
from .bleNotificationHandler import BLENotificationHandler
from .uvicornLogger import create_uvicorn_logger

logger = create_uvicorn_logger("BLEScan")


async def wait_for_event(timeout: float, event: asyncio.Event | None = None, minimum_delay: float = 0.01) -> None:
    """
    指定した時間（timeout）だけ待機しますが、event がセットされた場合は即座に中断します。

    :param timeout: 待機する時間（秒）
    :param event: 中断を示すための `asyncio.Event`。指定がない場合は `None`。
    :param minimum_delay: 最小中断時間（秒）。指定がない場合は `0.01`。
    :type timeout: float
    :type event: asyncio.Event | None
    :type minimum_delay: float
    """
    if event:
        event_loop = asyncio.get_event_loop()
        end_time = event_loop.time() + timeout

        while not event.is_set():
            remaining = end_time - event_loop.time()

            if remaining <= 0:
                break

            await asyncio.sleep(min(remaining, minimum_delay))
    else:
        await asyncio.sleep(timeout)


async def find_device() -> BLEDevice | None:
    """
    BLEスキャンを行ってデバイス名 `BLE_DEVICE_NAME` と
    サービスデータUUID `BLE_SERVICE_DATA_UUID` にマッチするBLEデバイスを探索します。

    :return: デバイスを発見したとき `BLEDevice`、それ以外のとき `None`。
    :rtype: BLEDevice | None
    """
    advertisement_data_store = {}

    def callback(device, advertisement_data):
        if device.name == BLE_DEVICE_NAME:
            advertisement_data_store[device.address] = advertisement_data

    scanner = BleakScanner(detection_callback=callback)
    await scanner.start()
    device = await BleakScanner.find_device_by_name(BLE_DEVICE_NAME, timeout=5)
    await scanner.stop()

    if device:
        advertisement_data = advertisement_data_store.get(device.address)

        if advertisement_data:
            value = advertisement_data.service_data.get(str(BLE_SERVICE_DATA_UUID))

            if value:
                return device

    return None


def has_matched_service(client: BleakClient) -> bool:
    """
    指定された `BleakClient` が想定したサービスUUIDと特性に合致するかを判定します。

    :param client: 接続済みの `BleakClient`。
    :type client: BleakClient
    :return: 合致するとき `True`、それ以外のとき `False`。
    :rtype: bool
    """
    for service in client.services:
        logger.debug(f"[Service] {service.handle} {service}, {service.uuid}")

        for characteristic in service.characteristics:
            logger.debug(
                f"  - [Characteristic] {characteristic.handle} - {characteristic.description},"
                f" {characteristic.uuid} | props: {characteristic.properties}"
            )

    service = client.services.get_service(BLE_SERVICE_UUID)

    if service:
        characteristic_voltage = service.get_characteristic(BLE_CHARACTERISTIC_VOLTAGE_UUID)
        characteristic_freq = service.get_characteristic(BLE_CHARACTERISTIC_FREQ_UUID)

        if (
            characteristic_voltage
            and characteristic_freq
            and "notify" in characteristic_voltage.properties
            and "notify" in characteristic_freq.properties
        ):
            return True

    return False


async def bleScanTask(stop_event: asyncio.Event) -> None:
    logger.info("task started")

    while not stop_event.is_set():
        device = await find_device()

        if not device:
            await wait_for_event(30, stop_event)
            continue
        else:
            logger.info(f"device found: {device.name} ({device.address})")

        logger.info(f"connecting: {device.name} ({device.address})")

        def onDisconnectionDetected(client: BleakClient) -> None:
            logger.info(f"disconnection detected: {client.address}")

        async with BleakClient(
            device, timeout=10.0, winrt={"use_cached_services": False}, disconnected_callback=onDisconnectionDetected
        ) as client:
            if client.is_connected and has_matched_service(client):
                notification_handler = BLENotificationHandler()
                logger.info(f"connected: {device.name} ({device.address})")
                logger.info(f"start notify: {device.name} ({device.address})")
                await client.start_notify(BLE_CHARACTERISTIC_VOLTAGE_UUID, notification_handler.handle)
                await client.start_notify(BLE_CHARACTERISTIC_FREQ_UUID, notification_handler.handle)

                while not stop_event.is_set() and client.is_connected:
                    await wait_for_event(1, stop_event)

                if client.is_connected:
                    await client.stop_notify(BLE_CHARACTERISTIC_VOLTAGE_UUID)
                    await client.stop_notify(BLE_CHARACTERISTIC_FREQ_UUID)
                    logger.info(f"finished notify: {device.name} ({device.address})")

        logger.info(f"disconnected: {device.name} ({device.address})")

    logger.info("task finished")
