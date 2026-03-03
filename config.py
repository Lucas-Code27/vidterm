import json

config_ref = None

def load_config():
    new_config = {}

    try:
        with open('config/config.json', 'r') as f:
            data = json.load(f)
        
            new_config["quantization_level"] = data["quantization_level"]
            new_config["black_point"] = data["black_point"]
    except Exception as e:
        print(f"Config loading had an error! {e}")

        new_config["quantization_level"] = 12
        new_config["black_point"] = 0
    
    return new_config


def get_config():
    if config_ref is None:
        return load_config()

    return config_ref