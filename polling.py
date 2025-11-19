import RPi.GPIO as GPIO
import time

# Kasutame BCM nummerdust (GPIO numbrid)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

AUTO_PUNANE = 2
AUTO_KOLLANE = 3
AUTO_ROHELINE = 4
JALA_PUNANE = 20
JALA_ROHELINE = 21
VALGE = 27
NUPP = 26

tulid = [AUTO_PUNANE, AUTO_KOLLANE, AUTO_ROHELINE, JALA_PUNANE, JALA_ROHELINE, VALGE]
GPIO.setup(tulid, GPIO.OUT)

# Nupp sisend sisseehitatud pull-up takistiga
GPIO.setup(NUPP, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Algolekud
GPIO.output(AUTO_PUNANE, True) 
GPIO.output(JALA_PUNANE, True)  
GPIO.output(VALGE, False)     

# Jalakäija ootamise muutujad
jalakaija_ootab = False
eelmine_nupu_seisund = GPIO.input(NUPP)

def kontrolli_nuppu():
    """Kontrollib nupu olekut ja märgib, et jalakäija tahab üle minna."""
    global jalakaija_ootab, eelmine_nupu_seisund
    praegune = GPIO.input(NUPP)

    # Tuvastame nupuvajutuse (HIGH, mis läheb LOW)
    if eelmine_nupu_seisund == GPIO.HIGH and praegune == GPIO.LOW:
        if not jalakaija_ootab:
            jalakaija_ootab = True
            GPIO.output(VALGE, True)
            print("Nupp vajutatud")

    eelmine_nupu_seisund = praegune


def oota_ja_kontrolli(sekundid):
    """Ootab määratud aja, kontrollides samal ajal nuppu."""
    sammud = int(sekundid / 0.05)
    for _ in range(sammud):
        kontrolli_nuppu()
        time.sleep(0.05)


try:
    print("Valgusfoor käivitatud")

    while True:

        # Auto foor punane
        GPIO.output(AUTO_PUNANE, True)
        GPIO.output(AUTO_KOLLANE, False)
        GPIO.output(AUTO_ROHELINE, False)

        if jalakaija_ootab:
            GPIO.output(JALA_PUNANE, False)
            GPIO.output(JALA_ROHELINE, True)
            GPIO.output(VALGE, False)
            jalakaija_ootab = False
            print("Jalakäija ROHELINE")
        else:
            GPIO.output(JALA_ROHELINE, False)
            GPIO.output(JALA_PUNANE, True)

        oota_ja_kontrolli(5)

        # Punase lõpus jalakäija jälle punaseks
        GPIO.output(JALA_ROHELINE, False)
        GPIO.output(JALA_PUNANE, True)
        GPIO.output(AUTO_PUNANE, False)

        # Auto foor kollane
        GPIO.output(AUTO_KOLLANE, True)
        oota_ja_kontrolli(1)
        GPIO.output(AUTO_KOLLANE, False)

        # Auto foor roheline
        GPIO.output(AUTO_ROHELINE, True)
        oota_ja_kontrolli(5)
        GPIO.output(AUTO_ROHELINE, False)

        # Kollane auto foor vilgub 3 korda
        for _ in range(3):
            GPIO.output(AUTO_KOLLANE, True)
            oota_ja_kontrolli(0.33)
            GPIO.output(AUTO_KOLLANE, False)
            oota_ja_kontrolli(0.33)

except KeyboardInterrupt:
    print("\n Programm peatatud")

finally:
    GPIO.cleanup()
    print("GPIO puhastatud")