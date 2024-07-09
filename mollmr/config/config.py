import yaml


def load_config(file_path):
    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f'Error loading YAML file: {e}')
            return None


config = load_config('config.yaml')
