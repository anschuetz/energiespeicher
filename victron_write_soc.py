#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript von Jesko Anschütz, Mai 2019
 Beispiel-Skript zum Beschreiben des Registers, welchen den 
 Ladezustand des Akkus enthält.
 Vorsicht bei der Benutzung! Ich weiß nicht, was passiert,
 wenn man mutwillig einen falschen Wert einträgt.
#######################################################
### Schäden verantwortet jeder selbst! ################
#######################################################
"""
# Hier den gewünschten SOC einstellen
soc_gewuenscht = 44 # in Prozent 


import os, time
from pymodbus.client.sync import ModbusTcpClient
# MODBUS-Modul vorher ggf. mit pip install installieren...

wechselrichter = ModbusTcpClient("10.0.0.200", 502)
wechselrichter.connect()
# Erstmal auslesen, was vorher drin stand...

antwortvebus = wechselrichter.read_holding_registers(30, 1, unit=246)
#   hier Register-Nummer 30 und nur 1 auslesen -------^           ^---- Unit-ID vom VEBus

registerinhalt = antwortvebus.registers
soc_vorher = registerinhalt[0] / 10


soc_zu_schreiben = soc_gewuenscht * 10

writerequest = wechselrichter.write_registers(30,[soc_zu_schreiben],unit=246)

assert(writerequest.function_code < 0x80)     # Sicherstellen, dass der write-Request fehlerfrei war.

time.sleep(2) # kurz warten, bis alles geschrieben ist...

# auslesen und zeigen, dass es geklappt hat...

antwortvebus = wechselrichter.read_holding_registers(30, 1, unit=246)
register=antwortvebus.registers
soc_nachher=register[0]/10

print("Der SOC war vorher {}% und jetzt ist er {}%".format(soc_vorher, soc_nachher))
