import RPi.GPIO as GPIO
import time

# Kasutame BCM nummerdust (veendu, et see vastab sinu juhtmetele)
# Kui kasutad füüsilisi viigunumbreid, muuda see GPIO.BOARD-iks
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --- Seadistused ---
# LED pinid (BCM numbrid)
CAR_RED = 2
CAR_YELLOW = 3
CAR_GREEN = 4
PED_RED = 20
PED_GREEN = 21
WHITE = 27
BUTTON = 26

# LEDid -> OUTPUT
led_pins = [CAR_RED, CAR_YELLOW, CAR_GREEN, PED_RED, PED_GREEN, WHITE]
GPIO.setup(led_pins, GPIO.OUT)

# Nupp -> INPUT (pull up takistiga: vaikimisi HIGH, vajutades LOW)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Algolekud ---
GPIO.output(CAR_RED, True)     # Alustame punasega
GPIO.output(CAR_YELLOW, False)
GPIO.output(CAR_GREEN, False)
GPIO.output(PED_RED, True)     # Jalakäija punane
GPIO.output(PED_GREEN, False)
GPIO.output(WHITE, False)

# Muutujad oleku hoidmiseks
ped_wait = False
last_button_state = GPIO.input(BUTTON)

# --- Abifunktsioonid ---

def check_button():
    """Kontrollib nupu olekut ja uuendab ped_wait muutujat."""
    global ped_wait, last_button_state
    current_state = GPIO.input(BUTTON)

    # Tuvastame "Falling edge" (HIGH -> LOW) ehk nupuvajutuse hetke
    if last_button_state == GPIO.HIGH and current_state == GPIO.LOW:
        if not ped_wait: # Ainult siis, kui juba ei oota
            ped_wait = True
            GPIO.output(WHITE, True) # Valge näitab, et soov on salvestatud
            print("NUPP VAJUTATUD -> Soov salvestatud, ootan järgmist tsüklit.")
    
    last_button_state = current_state

def wait_and_poll(duration):
    """Ootab antud aja (sekundites), kontrollides pidevalt nuppu."""
    # Jagame ooteaja väikesteks 0.05s juppideks, et nuppu tihti kontrollida
    steps = int(duration / 0.05)
    for _ in range(steps):
        check_button()
        time.sleep(0.05)

# --- Põhiprogramm ---

try:
    print("Valgusfoor käivitatud! (Ctrl+C lõpetamiseks)")

    while True:
        # ==========================================
        # 🔴 1. AUTO PUNANE (5s)
        # ==========================================
        GPIO.output(CAR_RED, True)

        # KONTROLL: Kas jalakäija ootab? 
        # See juhtub AINULT punase tsükli alguses.
        if ped_wait:
            # Vahetame jalakäija tuled
            GPIO.output(PED_RED, False)
            GPIO.output(PED_GREEN, True)
            
            # Soov täidetud -> kustutame valge ja nullime ootejärjekorra
            GPIO.output(WHITE, False)
            ped_wait = False 
            print("Jalakäija: ROHELINE")
        else:
            # Kui keegi ei oota, on jalakäijal punane
            GPIO.output(PED_GREEN, False)
            GPIO.output(PED_RED, True)

        # Ootame 5 sekundit (samal ajal nuppu kontrollides)
        # Kui siin vajutatakse nuppu, läheb ped_wait True-ks ja White põlema,
        # aga jalakäija tuli ei muutu roheliseks enne järgmist ringi.
        wait_and_poll(5)

        # Punase tsükli lõpp -> Jalakäija kindlasti punaseks tagasi
        GPIO.output(PED_GREEN, False)
        GPIO.output(PED_RED, True)
        
        # NB! Me EI nulli siin ped_wait muutujat ega WHITE tuld!
        # See tagabki, et kui nuppu vajutati punase ajal, jääb valge põlema 
        # kuni tsükkel teeb ringi ära ja jõuab uuesti algusesse.

        GPIO.output(CAR_RED, False)

        # ==========================================
        # 🟡 2. AUTO KOLLANE (1s)
        # ==========================================
        GPIO.output(CAR_YELLOW, True)
        wait_and_poll(1)
        GPIO.output(CAR_YELLOW, False)

        # ==========================================
        # 🟢 3. AUTO ROHELINE (5s)
        # ==========================================
        GPIO.output(CAR_GREEN, True)
        wait_and_poll(5)
        GPIO.output(CAR_GREEN, False)

        # ==========================================
        # 🟡 4. AUTO KOLLANE VILGUB (3x)
        # ==========================================
        # PDF ütles: vilgub 2s jooksul 3 korda. 
        # Teeme tsükli, aga kasutame ka siin poll'imist
        for _ in range(3):
            GPIO.output(CAR_YELLOW, True)
            wait_and_poll(0.33) # ca 1/3 sekundit sees
            GPIO.output(CAR_YELLOW, False)
            wait_and_poll(0.33) # ca 1/3 sekundit väljas

except KeyboardInterrupt:
    print("\nProgrammi peatamine...")

finally:
    GPIO.cleanup()
    print("GPIO puhastatud. Head aega!")