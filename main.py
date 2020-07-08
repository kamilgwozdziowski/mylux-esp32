import time
from lib import ble
from lib import config

def main():
    configObj = config.Config('../config.json')
    configAr = configObj.getAllConnfig()

    bleMylux = ble.BleConnector(configAr['bleName'], configAr['bleUUID'])
    nums = [4, 8, 15, 16, 23, 42]
    i = 0
    mah = 0

    try:
        while True:
            print(nums[i])
            print(mah)
            bleMylux.write(configAr['amps'], str(nums[i]) + "\n")
            bleMylux.write(configAr['mah'], str(mah) + "\n")
            i = (i + 1) % len(nums)
            mah += i
            time.sleep_ms(1000)
    except KeyboardInterrupt:
        pass

    uart.close()

if __name__ == "__main__":
    main()