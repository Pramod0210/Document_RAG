import yaml


def load_config(file_path="config/config.yaml"):
    """
    Load configuration from a YAML file.

    :param file_path: Path to the YAML configuration file.
    :return: Parsed configuration as a dictionary.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        print(f"Configuration loaded from {file_path}: {config}")
    return config

if __name__ == "__main__":
    config = load_config()
    print(config)
