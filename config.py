import json

config_ref = None

def load_config():
    new_config = {}

    try:
        with open('config/config.json', 'r') as f:
            data = json.load(f)
        
            new_config["quantization_level"] = data["quantization_level"]
    except Exception as e:
        print(f"Config loading had an error! {e}")

        new_config["quantization_level"] = 8
    
    return new_config


def get_config():
    if config_ref is None:
        return load_config()

    return config_ref