from nose.tools import *
import math
import RPi.GPIO as GPIO
from hcsr04sensor.sensor import Measurement, basic_distance

TRIG_PIN = 17
ECHO_PIN = 27

# Uncomment the mode you are using to identify the GPIO pins.  Default is BCM
GPIO_MODE = GPIO.BCM
# GPIO_MODE = GPIO.BOARD


def raw_distance():
    value = Measurement(TRIG_PIN, ECHO_PIN)
    return value.raw_distance()


def test_measurement():
    """Test that object is being created properly."""
    value = Measurement(TRIG_PIN, ECHO_PIN, 25, "metric", gpio_mode=GPIO_MODE)
    value_defaults = Measurement(TRIG_PIN, ECHO_PIN)
    assert_equal(isinstance(value, Measurement), True)
    assert_equal(value.trig_pin, TRIG_PIN)
    assert_equal(value.echo_pin, ECHO_PIN)
    assert_equal(value.temperature, 25)
    assert_equal(value.unit, "metric")
    assert_equal(value_defaults.trig_pin, TRIG_PIN)
    assert_equal(value_defaults.echo_pin, ECHO_PIN)
    assert_equal(value_defaults.temperature, 20)
    assert_equal(value_defaults.unit, "metric")


def test_imperial_temperature_and_speed_of_sound():
    """Test that after Fahrenheit is converted to Celsius, that speed of sound is
    calculated correctly."""
    value = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial", gpio_mode=GPIO_MODE)
    raw_measurement = value.raw_distance()
    speed_of_sound = 331.3 * math.sqrt(1 + (value.temperature / 273.15))
    assert_equal(value.temperature, 20.0016)
    assert_equal(value.unit, "imperial")
    assert type(raw_measurement) == float
    assert_equal(speed_of_sound, 343.21555930656075)


def test_imperial_measurements():
    """Test that an imperial measurement is what you would expect with a precise
    raw_measurement."""
    value = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial", gpio_mode=GPIO_MODE)
    raw_measurement = 26.454564846
    hole_depth = 25

    imperial_distance = value.distance_imperial(raw_measurement)
    imperial_depth = value.depth_imperial(raw_measurement, hole_depth)

    assert type(imperial_distance) == float
    assert_equal(imperial_distance, 10.423098549324001)
    assert_equal(imperial_depth, 14.576901450675999)


def test_metric_measurements():
    """Test that a metric measurement is what you would expect with a precise
    raw_measurement."""
    value = Measurement(TRIG_PIN, ECHO_PIN, 20, "metric", gpio_mode=GPIO_MODE)
    raw_measurement = 48.80804985408
    hole_depth = 72

    metric_distance = value.distance_metric(raw_measurement)
    metric_depth = value.depth_metric(raw_measurement, hole_depth)

    assert_equal(metric_distance, 48.80804985408)
    assert_equal(metric_depth, 23.191950145920003)


def test_different_sample_size():
    """Test that a user defined sample_size works correctly."""
    value = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial", gpio_mode=GPIO_MODE)
    raw_measurement1 = value.raw_distance(sample_size=1)
    raw_measurement2 = value.raw_distance(sample_size=4)
    raw_measurement3 = value.raw_distance(sample_size=11)
    assert type(raw_measurement1) == float
    assert type(raw_measurement2) == float
    assert type(raw_measurement3) == float


def test_different_sample_wait():
    """Test that a user defined sample_wait time work correctly."""
    value = Measurement(TRIG_PIN, ECHO_PIN, gpio_mode=GPIO_MODE)
    raw_measurement1 = value.raw_distance(sample_wait=0.3)
    raw_measurement2 = value.raw_distance(sample_wait=0.1)
    raw_measurement3 = value.raw_distance(sample_wait=0.03)
    raw_measurement4 = value.raw_distance(sample_wait=0.01)
    assert type(raw_measurement1) == float
    assert type(raw_measurement2) == float
    assert type(raw_measurement3) == float
    assert type(raw_measurement4) == float


def test_basic_distancei_bcm():
    """Test that float returned with default, positive and negative temps"""
    GPIO.setmode(GPIO.BCM)
    basic_reading = basic_distance(TRIG_PIN, ECHO_PIN)
    basic_reading2 = basic_distance(TRIG_PIN, ECHO_PIN, celsius=10)
    basic_reading3 = basic_distance(TRIG_PIN, ECHO_PIN, celsius=0)
    basic_reading4 = basic_distance(TRIG_PIN, ECHO_PIN, celsius=-100)
    assert type(basic_reading) == float
    assert type(basic_reading2) == float
    assert type(basic_reading3) == float
    assert type(basic_reading4) == float
    GPIO.cleanup((TRIG_PIN, ECHO_PIN))


def test_raises_exception_unit():
    """Test that a ValueError is raised if user passes invalid unit type"""
    value = Measurement(TRIG_PIN, ECHO_PIN, unit="Fahrenheit")
    assert_raises(ValueError, value.raw_distance)


def test_raises_exception_no_pulse():
    """Test that SystemError raised if echo pulse not received.
       Using the wrong echo pin but typically this error gets raised
       with a faulty cable.  Wrong echo pin simulates that condition"""
    wrong_echo_pin = ECHO_PIN - 1
    value = Measurement(TRIG_PIN, wrong_echo_pin)
    assert_raises(SystemError, value.raw_distance)


def test_depth():
    """Test the depth of a liquid in cm and inches"""

    value = Measurement(TRIG_PIN, ECHO_PIN, 20, "metric", gpio_mode=GPIO_MODE)
    raw_measurement = 48.80804985408
    hole_depth = 72

    metric_depth = value.depth(raw_measurement, hole_depth)

    assert_equal(metric_depth, 23.191950145920003)

    value2 = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial", gpio_mode=GPIO_MODE)
    hole_depth_inches = hole_depth * 0.394

    imperial_depth = value2.depth(raw_measurement, hole_depth_inches)
    assert_equal(imperial_depth, 9.137628357492481)


def test_distance():
    """Test the distance measurement in cm and inches"""

    value = Measurement(TRIG_PIN, ECHO_PIN, 20, "metric", gpio_mode=GPIO_MODE)
    raw_measurement = 48.80804985408

    metric_distance = value.distance(raw_measurement)
    assert_equal(metric_distance, 48.80804985408)

    value2 = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial", gpio_mode=GPIO_MODE)
    imperial_distance = value2.distance(raw_measurement)
    assert_equal(imperial_distance, 19.23037164250752)


def test_cylinder_volume_side():
    """Test the volume of liquid in a cylinder resting on its side in both
    litres and gallons"""

    value = Measurement(TRIG_PIN, ECHO_PIN, 20, "metric", gpio_mode=GPIO_MODE)
    depth = 20
    height = 120
    radius = 45

    cylinder_volume = value.cylinder_volume_side(depth, height, radius)
    assert_equal(cylinder_volume, 126.31926004538707)

    value2 = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial", gpio_mode=GPIO_MODE)
    depthi = 17
    heighti = 27
    radiusi = 18
    cylinder_volume_g = value2.cylinder_volume_side(depthi, heighti, radiusi)
    assert_equal(cylinder_volume_g, 55.28063419280857)


def test_cylinder_volume_standing():
    """Test the volume of a liquid in a standing cylinder in litres and gallons"""

    depth = 50
    radius = 30
    value = Measurement(TRIG_PIN, ECHO_PIN)
    cylinder_volume = value.cylinder_volume_standing(depth, radius)
    assert_equal(cylinder_volume, 141.3716694115407)

    depthi = 24
    radiusi = 12
    value2 = Measurement(TRIG_PIN, ECHO_PIN, 68, "imperial")
    cylinder_volume_g = value2.cylinder_volume_standing(depthi, radiusi)
    assert_equal(cylinder_volume_g, 47.00149009007067)


def test_box_volume():
    pass


def test_elliptical_cylinder_volume():
    pass
