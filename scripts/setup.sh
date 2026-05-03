#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Ur-PiGenus v0.1 Setup für Raspberry Pi 5 ===${NC}"

echo -e "${YELLOW}1. Prüfe Systemvoraussetzungen...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker ist nicht installiert. Installiere Docker zuerst!${NC}"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 ist nicht installiert. Installiere Python 3 zuerst!${NC}"
    exit 1
fi
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    echo -e "${RED}❌ System ist kein ARM64 (aarch64/arm64). Ur-PiGenus benötigt ARM64!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Systemvoraussetzungen erfüllt.${NC}"

echo -e "${YELLOW}2. Installiere System-Abhängigkeiten...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io git python3-pip python3-venv

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}   Installiere docker-compose...${NC}"
    sudo apt install -y docker-compose-plugin
fi

sudo systemctl enable docker

echo -e "${YELLOW}3. Installiere Python-Abhängigkeiten...${NC}"
pip install -r requirements.txt

mkdir -p data/redis data/qdrant

echo -e "${YELLOW}4. Starte Docker-Container (Core + Echo-Modul)...${NC}"
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo -e "${YELLOW}5. Initialisiere Datenbanken...${NC}"
if ! python3 -c "from core.memory_manager import init_db; init_db()"; then
    echo -e "${RED}❌ Datenbank-Initialisierung fehlgeschlagen!${NC}"
    exit 1
fi

echo -e "${YELLOW}6. Erstelle Test-Task...${NC}"
if ! python3 -c "
from core.task_manager import save_task
task = {
    'title': 'Echo-Modul testen',
    'description': 'Teste das Echo-Modul mit: curl -X POST http://localhost:8001/echo -H \"Content-Type: application/json\" -d \"{\\\"input\\\": \\\"Test\\\"}\"',
    'priority': 'high',
    'status': 'open',
    'acceptance_criteria': ['Echo-Modul antwortet mit {\"output\": \"Test\"}'],
    'dependencies': []
}
save_task(task)
"; then
    echo -e "${RED}❌ Test-Task konnte nicht erstellt werden!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Setup erfolgreich abgeschlossen!${NC}"
echo -e "Ur-PiGenus läuft unter: ${YELLOW}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo -e "Echo-Modul läuft unter: ${YELLOW}http://$(hostname -I | awk '{print $1}'):8001/echo${NC}"
echo -e "Docker-Container anzeigen:"
if command -v docker-compose &> /dev/null; then
    echo -e "  ${YELLOW}docker-compose ps${NC}"
else
    echo -e "  ${YELLOW}docker compose ps${NC}"
fi
echo -e "${GREEN}Hinweis: Redis/Qdrant können mit:${NC}"
echo -e "  ${YELLOW}docker-compose --profile redis --profile qdrant up -d${NC}"
echo -e "  ${YELLOW}oder${NC}"
echo -e "  ${YELLOW}docker compose --profile redis --profile qdrant up -d${NC}"
echo -e "${GREEN}gestartet werden.${NC}"
