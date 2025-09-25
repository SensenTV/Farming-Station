# Indoor Farming Station – Projektarbeit


## Quick Stat Guide
1. Run pip install -r /Stickpfad/requirements.txt
2. Run python3 /MainPfad/app.py

## Koordination
- Prof. Dr.-Ing. Pascal Stoffels  
- Matthias Wilbert  
- Thorsten Murach  

## Projektpartner
| Name              | Matrikelnummer | E-Mail                     |
|-------------------|----------------|----------------------------|
| Steven Haupenthal | 5013788        | stha00005@htwsaar.de       |
| Alexander Masseli | 5014288        | alma00016@htwsaar.de       |
| Daniel Shapiro    | 5015020        | dash00004@htwsaar.de       |

---

## Inhaltsverzeichnis
1. [Vorhaben](#1-vorhaben)  
   1.1 [Anforderungen](#11-anforderungen)  
   1.2 [Projektplan](#12-projektplan)  
2. [Umsetzung](#2-umsetzung)  
   2.1 [Reflexion](#21-reflexion)  
   2.2 [Architektur und Technologie-Stack](#22-architektur-und-technologie-stack)  
   2.3 [Features](#23-features)  
   2.4 [Warnungen und Limits](#24-warnungen-und-limits)  
   2.5 [Dokumentation](#25-dokumentation)

---

## 1. Vorhaben

### 1.1 Anforderungen
Das Ziel unseres Projektes besteht darin, ein bestehendes Indoor-Farming-System durch eine auf einem Raspberry Pi basierende digitale Lösung möglichst effizient zu überwachen und die dabei gewonnenen Daten für die Zukunft nutzbar zu machen. Hierfür wurden verschiedene Sensoren am Pi angeschlossen (Temperatur, Luftfeuchtigkeit usw.).

Alle von den Sensoren gesammelten Daten werden zentral auf dem Pi erfasst, gespeichert und in einer von uns entworfenen Weboberfläche dargestellt. Diese Visualisierung erfolgt durch Diagramme sowie Tabellen und andere Möglichkeiten. Zusätzlich haben wir uns das Ziel gesetzt, unser gesamtes Projekt möglichst modular zu gestalten, um eine Erweiterbarkeit gewährleisten zu können.

### 1.2 Projektplan

#### Arbeitspakete
- **AP1: Einrichtung des Raspberry Pi**  
  Zeitraum: 11. Mai  
  Inhalt: Grundkonfiguration, Repository erstellt, Entwicklungsumgebung eingerichtet  
  Ergebnis: Raspberry Pi betriebsbereit.

- **AP2: Anschließen und Testen der Sensoren**  
  Zeitraum: 11. Mai – 6. Sep  
  Inhalt: Integration der Sensoren, Anpassung und Tests.  
  Ergebnis: Alle Sensoren liefern zuverlässig Werte.

- **AP3: Aufsetzen der Website (Dash)**  
  Zeitraum: 21. – 26. Mai  
  Inhalt: Umsetzung einer funktionierenden „Baseline“ mit Login-/Register-Seite und Dashboard.  
  Ergebnis: Erste Website mit Admin/User-Verwaltung.

- **AP4: Erstellung und Erweiterung der Datenbank**  
  Zeitraum: 11. Mai – 7. Sep  
  Inhalt: Entwicklung einer SQLite-Datenbank, Exportfunktionen, Speicherung der Sensordaten.  
  Ergebnis: Stabile Datenbank mit Export und Logging.

- **AP5: Anzeige und Visualisierung der Sensordaten auf der Website**  
  Zeitraum: 22. Mai – heute  
  Inhalt: Visualisierung in Tabellen und Graphen, Optimierungen am Dashboard, Logs.  
  Ergebnis: Echtzeit-Visualisierung inkl. Logs und Exportmöglichkeiten.

- **AP6: Erweiterung der Steuerung (Pumpen, Lüfter, Licht, User-Dashboard)**  
  Zeitraum: 1. Sep – heute  
  Inhalt: Steuerungsmöglichkeiten für Pumpen, Lüfter und Licht, Pumpenzeitschalter, User-Dashboard.  
  Ergebnis: Steuerungsfunktionen verfügbar.

#### Meilensteine
- **MS1 (11. Mai):** Raspberry Pi eingerichtet  
- **MS2 (21. Mai):** Website-Grundgerüst steht  
- **MS3 (26. Mai):** Funktionierende Baseline der Weboberfläche  
- **MS4 (21. Juni):** Sensoren vollständig integriert  
- **MS5 (7. Juli):** Datenbank implementiert und angebunden  
- **MS6 (7. Sep):** Alle Sensorwerte werden gespeichert und angezeigt  
- **MS7 (8. Sep):** Steuerung & User-Dashboard fertiggestellt  

---

## 2. Umsetzung

### 2.1 Reflexion
Wir konnten wesentliche Meilensteine erreichen: Einrichtung des Pi, Anbindung der Sensoren, Website mit Dash. Ein MVP wurde erstellt und kontinuierlich verbessert. Die ursprünglichen Ziele wurden erfüllt und teilweise übertroffen. 

Die Aufgabenverteilung im Team war ausgewogen. Probleme traten u. a. durch defekte Sensoren oder Git-Account-Probleme auf, die Zeit kosteten. Dennoch konnten wir eine stabile Lösung umsetzen.

### 2.2 Architektur und Technologie-Stack
- **Hardware:** Raspberry Pi mit Sensoren (Temperatur, Luftfeuchtigkeit, Wasserstand, pH, TDS)  
- **Datenerfassung:** Python-Skripte, Speicherung in SQLite  
- **Backend:** Flask/Dash, APIs und Live-Daten  
- **Frontend:** Dash-Weboberfläche mit Login/Registrierung, Admin-/User-Dashboard, Visualisierungen, Steuerung  
- **Datenbank:** SQLite (lokal auf dem Pi)  
- **Steuerung:** GPIO-Bibliotheken für Pumpen, Lüfter, Licht  

### 2.3 Features (MVP)
- **Benutzerverwaltung**: Registrierung, Login, Rollen (Admin/User)  
- **Sensorintegration**: Temperatur, Luftfeuchtigkeit, Wasserstand, pH, TDS  
- **Datenbank**: Speicherung in SQLite, CSV-Export  
- **Visualisierung**: Echtzeit-Anzeige, Graphen, Logs  
- **Steuerung**: Pumpen, Lüfter, Licht (Buttons, Statusanzeige, Zeitschaltung)  

### 2.4 Warnungen und Limits
Um einen sicheren Betrieb zu gewährleisten, sind Sicherheitsmechanismen integriert, die bei Abweichungen von Grenzwerten Warnungen ausgeben. Diese erscheinen im Dashboard im Log-Bereich. 

Die Grenzwerte können im Code (Datei `admin_dashboardpage.py`) angepasst werden. Suche nach `"Warngrenzen"`, dort ist die Konstante `SENSOR_LIMITS` definiert:

| Sensorname   | Mindestwert | Maximalwert |
|--------------|-------------|-------------|
| EC_Sensor    | 0.6         | 1.8         |

### 2.5 Dokumentation

#### Starten des Projekts
1. Raspberry Pi vorbereiten  
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   sudo apt-get install python3 python3-pip
   ```
2. Repository klonen  
   ```bash
   git clone https://github.com/SensenTV/Farming-Station
   cd <projektordner>
   ```
3. Wichtige Libraries installieren: Flask, Dash, SQLite3, Plotly, RPi.GPIO  
4. Datenbank initialisieren  
   ```bash
   python init_db.py
   ```
5. Projekt starten  
   ```bash
   python app.py
   ```
   Die Website ist dann erreichbar unter: `http://<raspberrypi-ip>:8050`
