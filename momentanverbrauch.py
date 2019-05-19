#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript von Jesko Anschütz, Mai 2019
Klassen zum Auslesen der Energiedaten von Solarlog und Victron-Wechselrichter
zur Bestimmung des tatsächlichen momentanen Verbrauchs im Haus
"""
import os, time, paho.mqtt.client as mqtt, json, requests, threading
from pymodbus.client.sync import ModbusTcpClient
from pprint import pprint

class SolarLog(object):
   def __init__(self, ip='10.0.0.11', payload='{"801":{"170":null}}', interval=15):
      self.checked = False
      self.interval = interval
      self.ip = ip
      self.payload = payload
      self.pac = 0
      self.relpower = 0
      self.rawdata=''
      self.datum = ''
      thread = threading.Thread(target=self.run, args=())
      thread.daemon = True                            # Daemonize thread
      thread.start()                                  # Start the execution
      self.get_data_from_solarlog()

   def get_data_from_solarlog(self):
      self.rawdata = requests.post('http://'+self.ip+'/getjp', data=self.payload)
      daten = json.loads(self.rawdata.text)
      self.datum = daten['801']['170']['100'] 
      self.pac = daten['801']['170']['101']
      self.pdc = daten['801']['170']['102']
      self.uac = daten['801']['170']['103']
      self.udc = daten['801']['170']['104']
      self.ertrag_heute = daten['801']['170']['105']
      self.ertrag_gestern = daten['801']['170']['106']
      self.ertrag_monat = daten['801']['170']['107']
      self.ertrag_jahr = daten['801']['170']['108']
      self.ertrag_gesamt = daten['801']['170']['109']     
      self.kwp = daten['801']['170']['116']
      self.relpower = self.pac / self.kwp * 100
      self.checked=True

   def run(self):
      while True:
            self.get_data_from_solarlog()
            time.sleep(self.interval)

class Victron(object):
   def __init__(self, ip='10.0.0.200', port=502 , interval=5):

      #print('Victron Modbus initialisieren')
      self.checked = False
      self.interval = interval
      self.ip = ip
      self.port = port
      self.pac = 0
      self.pdc = 0
      self.soc = 0
      self.datum = ''
      thread = threading.Thread(target=self.run, args=())
      thread.daemon = True                            # Daemonize thread
      thread.start()                                  # Start the execution
      #print('fertig')
   def correct_power_value(self, power):
      if power > 32000:
         return power - 65536
      else:
         return power
   def run(self):
      VEBUS_FIRST_ADDRESS = 3
      VEBUS_LAST_ADDRESS = 59
      VEBUS_NUM_ADDRESSES = VEBUS_LAST_ADDRESS - VEBUS_FIRST_ADDRESS
      VEBUS_INPUT_POWER_PHASE_1 = 12 - 3  #(Register 12, aber wir fangen ja erst bei Reg.3 an...)
      VEBUS_STATE_OF_CHARGE = 30 - 3
      GRID_FIRST_ADDRESS = 2600  #Reg. 2600 - 2602 sind die drei Phasen am Übergabezähler 
      GRID_NUM_ADDRESSES = 3
      UID_VEBUS = 246
      UID_GRID = 30
      wechselrichter = ModbusTcpClient(self.ip, self.port)
      wechselrichter.connect()
      while True:
            vebus = wechselrichter.read_holding_registers(VEBUS_FIRST_ADDRESS, VEBUS_NUM_ADDRESSES, unit = UID_VEBUS)
            grid = wechselrichter.read_holding_registers(GRID_FIRST_ADDRESS, GRID_NUM_ADDRESSES, unit = UID_GRID)
            vebus_register = vebus.registers
            grid_register = grid.registers
            self.soc = vebus_register[VEBUS_STATE_OF_CHARGE] / 10
            self.pac = vebus_register[VEBUS_INPUT_POWER_PHASE_1]*10
            self.pgrid1 = self.correct_power_value(grid_register[0])
            self.pgrid2 = self.correct_power_value(grid_register[1])
            self.pgrid3 = self.correct_power_value(grid_register[2])
            self.checked=True
            time.sleep(self.interval)

pv_wr = SolarLog()
akku_wr = Victron(interval = 1)
while True:
   if pv_wr.checked == True:
      print("Solarlog sagt: {}  {:.0f}W ({:.0f}%)".format(pv_wr.datum, pv_wr.pac, pv_wr.relpower))
      pv_wr.checked = False
   if akku_wr.checked == True:
      print("Akku-Wechselrichter sagt: SOC={}% Ladeleistung={}W, L1={}W, L2={}W, L3={}W".format(akku_wr.soc, akku_wr.pac, akku_wr.pgrid1, akku_wr.pgrid2, akku_wr.pgrid3))
      print("Der Momentanverbrauch im Haus beträgt {}W".format(akku_wr.pgrid1 + akku_wr.pgrid2 + akku_wr.pgrid3 - akku_wr.pac + pv_wr.pac))
      akku_wr.checked = False
   time.sleep(1)
