from json import load

config_ref = None

def load_config():
    new_config: dict[str, int] = {}

    try:
        with open('config/config.json', 'r') as f:
            data = load(f)
        
            new_config["quantization_level"] = data["quantization_level"]
            new_config["buffer_size"] = data["buffer_size"]
            new_config["pre_load_buffer"] = data["pre_load_buffer"]
    except Exception as e:
        print(f"Config loading had an error! {e}")

        new_config["quantization_level"] = 12
        new_config["buffer_size"] = 100
        new_config["pre_load_buffer"] = 20
    
    return new_config


def get_config():
    if config_ref is None:
        return load_config()

    return config_ref