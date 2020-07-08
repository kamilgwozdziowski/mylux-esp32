import bluetooth
from ble_advertising import advertising_payload

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_UART_UUID = bluetooth.UUID("fdd80d88-c091-11ea-b3de-0242ac130004")
_AMPS_UUID = (
    bluetooth.UUID("ec15783c-c092-11ea-b3de-0242ac130004"),
    bluetooth.FLAG_NOTIFY,
)
_MAH_UUID = (
    bluetooth.UUID("05dcf540-c09a-11ea-b3de-0242ac130004"),
    bluetooth.FLAG_NOTIFY,
)
_UART_SERVICE = (
    _UART_UUID,
    (_AMPS_UUID, _MAH_UUID),
)

_AMPS = 0
_MAH = 1

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

class BleConnector:
    def __init__(self, name, config):
        self._config = config
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(handler=self._irq)
        services = self.constructUUIDList()
        ((self._variables),) = self._ble.gatts_register_services(services)
        self._connections = set()
        self._handler = None
        #...
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        self._payload = advertising_payload(name=name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._advertise()

    def irq(self, handler):
        self._handler = handler

    def constructUUIDList(self):
        return ((
            bluetooth.UUID(self._config["wattmeter"]["service"]),
            (
                (bluetooth.UUID(self._config["wattmeter"]["amps"]), bluetooth.FLAG_NOTIFY,),
                (bluetooth.UUID(self._config["wattmeter"]["mah"]), bluetooth.FLAG_NOTIFY,)
            )
        ),)

    
    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            print('_irq IRQ_CENTRAL_CONNECT')
            conn_handle, _, _, = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            print('_irq _IRQ_CENTRAL_DISCONNECT')
            conn_handle, _, _, = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            print('_irq __IRQ_GATTS_WRITE')
            conn_handle, value_handle, = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

    def write(self, i, data):
        for conn_handle in self._connections:
            print('Write!')
            self._ble.gatts_notify(conn_handle, self._variables[i], data)

    def close(self):
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()
    
    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)