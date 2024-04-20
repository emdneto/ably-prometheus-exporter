import requests
import yaml

ABLY_SCHEMA_URL = "https://schemas.ably.com/json/app-stats-0.0.3.json"

MAP_METRIC_TYPE_ABLY = {
    "number": "gauge"
}

def _get_stats_schema(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        schema = response.json()["properties"]["entries"]["properties"]
        return schema
    except requests.exceptions.RequestException as err:
        print(f"Fetching Ably stats schema ({url}) failed:", err)
        return None

def _format_name(name):
    return name.replace(".", "_")

def _build_schema(schema):
    def _build(entry_key, entry):
        try:
            metric_name = _format_name(entry_key)
            metric_description = entry.get("description", "")
            metric_type = entry.get("type")
            mapped_metric_type = MAP_METRIC_TYPE_ABLY.get(metric_type, "number")
            mapped_labels = ["applicationId"]
            return {
                "name": metric_name,
                "description": metric_description,
                "type": mapped_metric_type,
                "labels": mapped_labels
            }
        except Exception as err:
            print(f"Failed to generate metric entry {metric_name}: {err}")

    return [_build(entry_key, entry) for entry_key, entry in schema.items() if entry_key and entry]

def generate_and_save_schema_yaml():
    schema = _get_stats_schema(ABLY_SCHEMA_URL)
    if not schema:
        print("Failed to retrieve Ably stats schema. Exiting.")
        return
    
    metrics = _build_schema(schema)

    yaml_data = {"metrics": metrics}

    with open("schema.yaml", "w") as yaml_file:
        yaml.dump(yaml_data, yaml_file, default_flow_style=False)

    print("Schema YAML file generated successfully.")

if __name__ == "__main__":
    generate_and_save_schema_yaml()