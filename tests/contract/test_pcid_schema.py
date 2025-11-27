import json
from pathlib import Path

import jsonschema

SCHEMA_DIR = Path("schemas/pcid")


def test_template_schema_is_valid_json_schema():
    schema_path = SCHEMA_DIR / "template_pcid_schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft7Validator.check_schema(schema)

