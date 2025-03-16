'''connecting libraries'''
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import time
import numpy as np
from scipy.interpolate import make_interp_spline

GPIO.setwarnings(False)

''' объявление портов на малинке '''
comp = 14
dac = [8, 11, 7, 1, 0, 5, 12, 6]
led = [2, 3, 4, 17, 27, 22, 10, 9]
troyka = 13


GPIO.setmode(GPIO.BCM)

''' input output settings '''
GPIO.setup(dac, GPIO.OUT)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(troyka, GPIO.OUT, initial = 1)
GPIO.setup(comp, GPIO.IN)

'''function of transferring from record 10 to record 2'''
def num_to_bin(num):
    return [int(i) for i in bin(num)[2:].zfill(8)]

'''adc get function'''
def adc():
    num = 0
    for i in range(7, -1, -1):
        num += 2**i
        GPIO.output(dac, num_to_bin(num))
        time.sleep(0.005)
        comp_val = GPIO.input(comp)
        if (comp_val == 1):
            num -= 2**i
    return num

# function of outputting voltage to dac and returning its representation in 2 ss line
def comp_to_disco(num):
    str = num_to_bin(num)
    GPIO.output(dac, str)
    return str

# list of volt measurements
data_volts = []

val = 0


# three = high
GPIO.output(troyka, 1)

# start time
time_start = time.time()

# charging
print("Зарядка")
while(val < 203):
    val = adc()
    print(val)
    comp_to_disco(val)
    data_volts.append(val)

# тройка = low
GPIO.output(troyka, 0)

# разрядка
print("Разрядка")
while (val > 173):
    print(val)
    val = adc()
    comp_to_disco(val)
    data_volts.append(val)

# end time
time_end = time.time()


# time array
data_times = []
for i in range(0, len(data_volts)):
    t = (time_end - time_start)/len(data_volts)
    data_times.append(i * t)

# record volt measurements
data_volts_str = [str(i) for i in data_volts]
with open("data.txt", "w") as file:
    file.write("\n".join(data_volts_str))

# write average time and division in settings.txt
with open("settings.txt", "w") as file:
    file.write(str((time_end - time_start)/len(data_volts)))
    file.write("\n")
    file.write(str(3.3/256))


# show graph

xy_spline = make_interp_spline(data_times, data_volts)
x = np.linspace(min(data_times), max(data_times), 70)
y = xy_spline(x)

plt.minorticks_on()
plt.grid(which='minor', linestyle = ':')
plt.xlabel("x")
plt.ylabel("y")
plt.plot(x, y)
plt.show()
