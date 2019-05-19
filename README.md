# Energie-Management
Skripte zum Auslesen der Energiedaten von PV-Anlage, Stromspeicher und Übergabezähler
Vielleicht lässt sich damit irgendwann auch eine intelligente Steuerung realisieren :)

## victron_write_soc.py
Demo-Skript: SOC wird ausgelesen, neu geschrieben, wieder ausgelesen und anschließend vorher/nachher verglichen.

## momentanverbrauch.py
Die Daten von PV-Anlage (Solarlog) und Victron-Wechselrichter (Akku/Speicher) werden ausgelesen und verrechnet, so dass der Momentanverbrauch im Haus ermittelt werden kann. Ein kleiner Microcontroller könnte jetzt bunt anzeigen, ob die genutzte Energie vom eigenen Dach kommt :) 
