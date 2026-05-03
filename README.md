# Ur-PiGenus v0.1 – Stabilitätsoptimiert für Raspberry Pi 5

## 🎯 Zweck
Ur-PiGenus ist der **embryonale Kern von GENUS**, der:
- **Aufgaben verwaltet** (Tasks für Agenten).
- **Gedächtnis speichert** (SQLite).
- **Module koordiniert** (Docker-Container).
- **Agenten steuert** (Mistral Vibe, Devstral 2).

**Design-Prinzipien:**
> *"Wenn Annahmen unklar sind, entscheide **immer** zugunsten von **Stabilität, Wartbarkeit und Raspberry-Pi-Kompatibilität**."*

---

## 🚀 Schnellstart (Raspberry Pi 5)

### 1. Systemvoraussetzungen
- **Betriebssystem:** Raspberry Pi OS (64-bit) oder Ubuntu Server 22.04 (ARM64).
- **Hardware:** Raspberry Pi 5 (4 GB RAM empfohlen).
- **Abhängigkeiten:** Docker, Docker Compose, Python 3.11+.

### 2. Repository klonen
```bash
git clone https://github.com/WoltLab51/UrPi.git
cd UrPi
```

### 3. Setup-Skript ausführen
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```
→ Startet nur die aktiven Komponenten (FastAPI, Echo-Modul, SQLite).
Redis/Qdrant müssen explizit mit `--profile` gestartet werden.

### 4. API testen
```bash
# Core-Health-Check
curl http://localhost:8000/health
# → {"status": "healthy", "version": "0.1.0", "workers": 1}

# Task erstellen (ID wird automatisch generiert!)
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Echo-Modul testen", "description": "Teste das Echo-Modul.", "priority": "high"}'

# Echo-Modul testen
curl -X POST http://localhost:8001/echo \
  -H "Content-Type: application/json" \
  -d '{"input": "Hallo Ur-PiGenus!"}'
# → {"output": "Hallo Ur-PiGenus!"}
```

### 5. Pi5-Deploy-Verifikation
Nach dem Deployment können Sie die vollständige Funktionalität mit dieser Sequenz testen:
```bash
# 1. Docker-Container starten
docker compose up -d

# 2. Health-Check
curl http://localhost:8000/health

# 3. Task erstellen
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Echo testen","description":"Teste Echo"}'

# 4. Memory-Eintrag erstellen
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"content":"Deploy-Test","type":"system","metadata":{"source":"pi5_check"}}'

# 5. Echo-Modul testen
curl -X POST http://localhost:8001/echo \
  -H "Content-Type: application/json" \
  -d '{"input":"Hallo Pi5"}'

# 6. Tests ausführen
pytest
```

### 6. Redis/Qdrant starten (optional)
```bash
docker compose --profile redis --profile qdrant up -d
```

---
## ⚠️ Bekannte Einschränkungen & Stabilitätshinweise
| Problem | Lösung | Status |
|---------|--------|--------|
| SQLite + Workers > 1 | `--workers 1` in docker-compose.yml | ✅ Behoben |
| Task-IDs manuell | Auto-ID-Generierung in agent_api.py | ✅ Behoben |
| Redis nicht genutzt | SQLite als primäre Queue | ✅ Dokumentiert |
| Qdrant nicht genutzt | SQLite als primärer Speicher | ✅ Dokumentiert |

---
## 📜 Dokumentation
- [GENUS_MANIFEST.md](docs/GENUS_MANIFEST.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [MODULE_CONTRACT.md](docs/MODULE_CONTRACT.md)
- [ROADMAP.md](docs/ROADMAP.md)

---
## 🔌 Endpunkte
| Endpunkt | Methode | Beschreibung | Status-Code |
|----------|---------|--------------|-------------|
| `/tasks` | GET | Liste aller Tasks | 200 |
| `/tasks` | POST | Task erstellen | 201 |
| `/tasks/{id}` | PUT | Task aktualisieren | 200/404 |
| `/tasks/next` | GET | Nächster offener Task (null wenn keiner) | 200 |
| `/memory` | GET/POST | Gedächtnis | 200/201 |
| `/modules` | GET | Liste aller Module | 200 |
| `/health` | GET | Health-Check | 200 |

---
## 🧪 Tests
```bash
pytest
pytest tests/test_core.py -v
```

---
## 📦 Docker-Befehle
```bash
docker compose up -d
docker compose --profile redis --profile qdrant up -d
docker compose down
```

---
## 📞 Support
- **Issues:** [GitHub Issues](https://github.com/WoltLab51/UrPi/issues)
- **Kontakt:** Ronny Wolter