import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import time

def dectobin(value):
    """Конвертирует десятичное число в восьмибитный двоичный код."""
    return [int(i) for i in bin(value)[2:].zfill(8)]

def adc():
    """Считывает аналоговый сигнал с датчика."""
    level = 0
    for i in range(bits - 1, -1, -1):
        # Постепенно увеличиваем уровень сигнала на ЦАП и считываем выходной сигнал компаратора
        level += 2**i
        GPIO.output(dac, dectobin(level))
        time.sleep(0.01)
        comp_val  = GPIO.input(comp)
        if (comp_val == 0):
            # Если выход компаратора = 0, значит, аналоговый сигнал меньше, чем уровень на ЦАП
            level -= 2**i
    return level

def num2_dac_leds(value):
    """Зажигает светодиоды в соответствии с двоичным кодом."""
    signal = dectobin(value)
    GPIO.output(dac, signal)
    return signal

dac = [26, 19, 13, 6, 5, 11, 9, 10]  # Номера GPIO для выводов ЦАП
leds = [24, 25, 8, 7, 12, 16, 20, 21]  # Номера GPIO для светодиодов
comp = 4  # Номер GPIO для компаратора
troyka = 17  # Номер GPIO для светодиода "тройка"
bits = len(dac)  # Количество битов ЦАП
levels = 2 ** bits  # Количество уровней квантования ЦАП
maxV = 3.3  # Максимальное напряжение на датчике

GPIO.setmode(GPIO.BCM)

# Настройка GPIO
GPIO.setup(troyka, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dac, GPIO.OUT)
GPIO.setup(comp, GPIO.IN)

# Включение питания на датчик
GPIO.output(troyka, 0)

data_volts = []  # Массив для хранения значений напряжения
data_times = []  # Массив для хранения времени считывания

try:
    start_time = time.time()  # Начало отсчета времени считывания
    val = 0  # Текущее значение напряжения
    while(val < 250):  # Цикл считывания и вывода напряжения от 0 до 250
        val = adc()  # Считываем напряжение с датчика
        print(" volts - {:3}".format(val / levels * maxV))  # Выводим значение напряжения в вольтах
        num2_dac_leds(val)  # Зажигаем светодиоды в соответствии с двоичным кодом
        data_volts.append(val)  # Добавляем значение напряжения в массив
        data_times.append(time.time() - start_time)  # Добавляем время считывания в массив

    GPIO.output(troyka, 1)  # Выключаем питание на датчик

    while(val > 64):  # Цикл считывания и вывода напряжения от 250 до 64
        val = adc()  # Считываем напряжение с датчика
        print(" volts - {:3}".format(val/levels * maxV))  # Выводим значение напряжения в вольтах
        num2_dac_leds(val)  # Зажигаем светодиоды в соответствии с двоичным кодом
        data_volts.append(val)  # Добавляем значение напряжения в массив
        data_times.append(time.time() - start_time)  # Добавляем время считывания в массив

    end_time = time.time()  # Конец отсчета времени считывания

    # Сохранение калибровочных коэффициентов в файл
    with open("./settings.txt", "w") as file:
        file.write(str((end_time - start_time) / len(data_volts)))  # Период преобразования АЦП
        file.write(("\n"))
        file.write(str(maxV / 256))  # Цена младшего разряда АЦП

    print(end_time - start_time, " secs\n", len(data_volts) / (end_time - start_time), "\n", maxV / 256)

finally:
    # Очистка GPIO
    GPIO.output(dac, GPIO.LOW)
    GPIO.output(troyka, GPIO.LOW)
    GPIO.cleanup()

data_times_str = [str(item) for item in data_times]  # Преобразование массива времени в массив строк
data_volts_str = [str(item) for item in data_volts]  # Преобразование массива напряжения в массив строк

# Сохранение данных в файл
with open("data.txt", "w") as file:
    file.write("\n".join(data_volts_str))

# Построение графика
plt.plot(data_times, data_volts)
plt.show()
