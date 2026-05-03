# Modul-Vertrag

## 📜 Allgemeine Regeln
- Jedes Modul muss eine `module.yaml` enthalten.
- Jedes Modul muss als Docker-Container lauffähig sein.

## 📁 Struktur
```
modules/<modulname>/
├── module.yaml
├── main.py
├── Dockerfile
├── requirements.txt
└── tests/
    └── test_<modulname>.py
```

## 📝 `module.yaml` (Pflichtfelder)
```yaml
name: "modulname"
version: "0.1.0"
description: "Beschreibung"
capabilities: ["fähigkeit1"]
api_endpoint: "/endpoint"
```

## 🧪 Tests
- Jedes Modul muss Tests in `tests/test_<modulname>.py` enthalten.
