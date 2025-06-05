import board
import analogio
import digitalio

class Battery:
    def __init__(self, adc_pin, charge_detect_pin, v_full=12.4, v_half=11.5, v_empty=10.2, charge_threshold=12.8):
        self.adc = analogio.AnalogIn(adc_pin)
        self.charge_detect = digitalio.DigitalInOut(charge_detect_pin)
        self.charge_detect.direction = digitalio.Direction.INPUT
        self.v_full = v_full
        self.v_half = v_half
        self.v_empty = v_empty
        self.charge_threshold = charge_threshold

    def get_voltage(self):
        adc_value = self.adc.value
        voltage_out = adc_value * 3.3 / 65536  # 将 ADC 值转换为电压（假设参考电压为 3.3V）
        voltage_in = voltage_out * 5  # 根据分压比计算原始电压
        return voltage_in

    def get_soc(self):
        voltage_in = self.get_voltage()
        is_charging = self.is_charging()

        if is_charging:
            if voltage_in > self.charge_threshold:
                return 100
            elif voltage_in > self.v_full:
                return 100
            elif voltage_in > self.v_half:
                return ((voltage_in - self.v_half) / (self.v_full - self.v_half)) * 50 + 50
            elif voltage_in > self.v_empty:
                return ((voltage_in - self.v_empty) / (self.v_half - self.v_empty)) * 50
            else:
                return 0
        else:
            if voltage_in > self.v_full:
                return 100
            elif voltage_in > self.v_half:
                return ((voltage_in - self.v_half) / (self.v_full - self.v_half)) * 50 + 50
            elif voltage_in > self.v_empty:
                return ((voltage_in - self.v_empty) / (self.v_half - self.v_empty)) * 50
            else:
                return 0

    def is_charging(self):
        return self.charge_detect.value