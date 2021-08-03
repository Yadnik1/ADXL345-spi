from machine import SPI,I2C,Pin
import utime
import sys
# ADXL345 constant
# ADXL345 register constant
REG_DEVID = 0x00  # 0x00- Device ID Register for Get Device ID 
REG_POWER_CTL = 0x2D  # 0x2d-power saving control register
REG_DATAX0 = 0x32 
# Other constants
DEVID = 0xE5  # 0xE5-ADXL345 device ID
SENSITIVITY_2G = 1.0/256    # (g/LSB)
EARTH_GRAVITY = 9.80665     # acceleration [m / (s * s)]

# Specify port A and pin21 to the program control slave selection CS
cs = Pin(("GPIO_0", 21), Pin.OUT)

# Initialize SPI
spi = SPI("SPI_0")
spi.init(baudrate=500000, polarity=1, phase=1, bits=8, firstbit=SPI.MSB)

#Function definition
def reg_write(spi, cs, reg, data):
    """
    Write bytes to the specified register
    """
    msg = bytearray()
    msg.append(0x00|reg)
    msg.append(data)
    cs.value(0)
    spi.write(msg)
    cs.value(1)
    
def reg_read(spi, cs, reg, nbytes=1):
    """
    Read bytes from the specified register; if NBYTES> 1 is read from a continuous register.
    """
    if nbytes < 1:
        return bytearray()
    elif nbytes == 1:
        mb = 0
    else:
        mb = 1
    msg = bytearray()
    msg.append(0x80|(mb<<6)|reg)
    cs.value(0)
    spi.write(msg)
    data = spi.read(nbytes)
    cs.value(1)
    return data

#      
cs.value(1)
reg_read(spi, cs, REG_DEVID)
# Read the device ID to determine if SPI communication with the ADXL345
data = reg_read(spi, cs, REG_DEVID)

test=bytearray((DEVID,))
if (data != bytearray((DEVID,))):
    print("Error: Pico can't communicate with ADXL345!")
    sys.exit()
data = reg_read(spi, cs, REG_POWER_CTL)
print(data)
data = int.from_bytes(data, "big")|(1<<3)
reg_write(spi, cs, REG_POWER_CTL, data)
data = reg_read(spi, cs, REG_POWER_CTL)
print(data)
utime.sleep(2.0)
while True:
    data = reg_read(spi, cs, REG_DATAX0, 6)
    acc_x = ustruct.unpack_from("<h", data, 0)[0]
    acc_y = ustruct.unpack_from("<h", data, 2)[0]
    acc_z = ustruct.unpack_from("<h", data, 4)[0]
    acc_x = acc_x * SENSITIVITY_2G * EARTH_GRAVITY
    acc_y = acc_y * SENSITIVITY_2G * EARTH_GRAVITY
    acc_z = acc_z * SENSITIVITY_2G * EARTH_GRAVITY
    print("X=", "{:.2f}".format(acc_x), \
          ", Y=", "{:.2f}".format(acc_y), \
          ", Z=", "{:.2f}".format(acc_z))
    utime.sleep(0.1)
