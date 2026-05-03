import yaml
import sys

MODULE_CONTRACT = {
    "required_fields": ["name", "version", "description", "capabilities", "api_endpoint"],
    "optional_fields": ["dependencies", "is_active"]
}

def validate_module(module_yaml_path: str) -> bool:
    try:
        with open(module_yaml_path, "r") as f:
            module = yaml.safe_load(f)
        for field in MODULE_CONTRACT["required_fields"]:
            if field not in module:
                print(f"❌ Fehlendes Feld: {field}")
                return False
        print(f"✅ Modul {module['name']} ist gültig.")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Validieren: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Verwendung: python validate_module.py <pfad/zur/module.yaml>")
        sys.exit(1)
    validate_module(sys.argv[1])
