import RPi.GPIO as G
import time

dac = [8, 11, 7, 1, 0, 5, 12, 6]
comp = 14
troyka = 13
leds = [2, 3, 4, 17, 27, 22, 10, 9]

G.setmode(G.BCM)

G.setup(dac, G.OUT)
G.setup(troyka, G.OUT, initial=G.HIGH)
G.setup(comp, G.IN)
G.setup(leds, G.OUT)

def dec2bin(x):
    return [ int(bit) for bit in bin(x)[2:].zfill(8) ]

def adc():
    value = [0]*8
    for bit in range(8):
        value[bit] = 1
        G.output(dac, value)
        time.sleep(0.05)
        comp_res = G.input(comp)
        if comp_res:
            value[bit] = 0
    print(value)
    return int("".join( list( map(str, value) ) ), base=2)



'''def adc():
    for i in range(255):
        G.output(dac, dec2bin(i))
        comp_res = G.input(comp)
        time.sleep(0.01)
        if comp_res:
            print("comp_res", comp_res)
            return i
    return 0'''

try:
    while True:
        x = adc()
        print("digital value: " + str(x) + ", voltage: " + str( x * 3.3 / 256 ))
        G.output(leds, dec2bin(x))
finally:
    G.output(dac, 0)
    G.output(leds, 0)
    G.cleanup()
