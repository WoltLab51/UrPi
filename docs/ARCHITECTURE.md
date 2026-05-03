# GENUS Architektur

## 🏗️ Übersicht
```
+-------------------+       +-------------------+       +-------------------+
|     Endgeräte     |<----->|      Worker       |<----->|     PiGenus        |
| (UI, TinyML)      |       | (LLMs, Training)  |       | (Orchestrierung)  |
+-------------------+       +-------------------+       +-------------------+
```

## 🔧 Komponenten
### 1. PiGenus (Raspberry Pi 5)
- **Rolle**: Zentraler Orchestrator.
- **Funktionen**: Aufgabenverteilung, Gedächtnisverwaltung, Modul-Registry.
- **Technologien**: FastAPI, SQLite, Docker.

### 2. Worker
- **Rolle**: Schwere KI-Aufgaben.
- **Funktionen**: LLM-Inferenz, Training, Caching.
- **Technologien**: Docker-Container.

### 3. Endgeräte
- **Rolle**: Benutzerinteraktion.
- **Funktionen**: UI, leichte KI, Offline-Speicher.
- **Technologien**: React, Python.

## 🔄 Kommunikation
- **Protokolle**: gRPC/QUIC, Libp2p.
- **Datenformat**: JSON/Protobuf.
