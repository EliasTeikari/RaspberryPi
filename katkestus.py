import RPi.GPIO as GPIO
import time

# Kasutame BCM nummerdust
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --- Seadistused ---
CAR_RED = 2
CAR_YELLOW = 3
CAR_GREEN = 4
PED_RED = 20
PED_GREEN = 21
WHITE = 27
BUTTON = 26

led_pins = [CAR_RED, CAR_YELLOW, CAR_GREEN, PED_RED, PED_GREEN, WHITE]
GPIO.setup(led_pins, GPIO.OUT)

# Nupp -> INPUT (pull up takistiga)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Algolekud ---
GPIO.output(CAR_RED, True)
GPIO.output(CAR_YELLOW, False)
GPIO.output(CAR_GREEN, False)
GPIO.output(PED_RED, True)
GPIO.output(PED_GREEN, False)
GPIO.output(WHITE, False)

# Muutuja oleku hoidmiseks
ped_wait = False

# --- KATKESTUSE FUNKTSIOON (Callback) ---
# Seda funktsiooni kutsutakse välja AINULT siis, kui nuppu vajutatakse.
# See toimub taustal, sõltumata sellest, mida peatsükkel parasjagu teeb.
def button_handler(channel):
    global ped_wait
    if not ped_wait:
        ped_wait = True
        GPIO.output(WHITE, True) # Süütame kohe valge tule
        print("KATKESTUS -> Nuppu vajutati! Soov salvestatud.")

# Registreerime sündmuse (Event Detect)
# Jälgime nuppu (BUTTON), reageerime langevale rindele (FALLING ehk HIGH -> LOW)
# bouncetime=200 tähendab, et 200ms jooksul uut vajutust ei loeta (välistab nupu värisemise)
GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_handler, bouncetime=200)


# --- Põhiprogramm ---
try:
    print("Valgusfoor käivitatud (Katkestuste režiim)")

    while True:
        # ==========================================
        # 🔴 1. AUTO PUNANE (5s)
        # ==========================================
        GPIO.output(CAR_RED, True)

        # Kontrollime tsükli alguses, kas katkestus on vahepeal toimunud
        if ped_wait:
            GPIO.output(PED_RED, False)
            GPIO.output(PED_GREEN, True)
            
            # Nullime ootejärjekorra
            GPIO.output(WHITE, False)
            ped_wait = False
            print("Jalakäija: ROHELINE")
        else:
            GPIO.output(PED_GREEN, False)
            GPIO.output(PED_RED, True)

        # SIIN ON SUUR ERINEVUS:
        # Me ei pea enam tegema tsüklit nupu kontrollimiseks.
        # Võime lihtsalt "magada", sest katkestus töötab taustal edasi.
        time.sleep(5)

        # Punase lõpus jalakäija punaseks (juhul kui oli roheline)
        GPIO.output(PED_GREEN, False)
        GPIO.output(PED_RED, True)
        
        GPIO.output(CAR_RED, False)

        # ==========================================
        # 🟡 2. AUTO KOLLANE (1s)
        # ==========================================
        GPIO.output(CAR_YELLOW, True)
        time.sleep(1) # Lihtne sleep, sest nuppu jälgitakse riistvaraliselt
        GPIO.output(CAR_YELLOW, False)

        # ==========================================
        # 🟢 3. AUTO ROHELINE (5s)
        # ==========================================
        GPIO.output(CAR_GREEN, True)
        time.sleep(5)
        GPIO.output(CAR_GREEN, False)

        # ==========================================
        # 🟡 4. AUTO KOLLANE VILGUB (3x)
        # ==========================================
        for _ in range(3):
            GPIO.output(CAR_YELLOW, True)
            time.sleep(0.33)
            GPIO.output(CAR_YELLOW, False)
            time.sleep(0.33)

except KeyboardInterrupt:
    print("\nProgrammi peatamine...")

finally:
    # Oluline: eemaldame sündmuste detekteerimise ja puhastame viigud
    GPIO.remove_event_detect(BUTTON)
    GPIO.cleanup()
    print("GPIO puhastatud.")