import json
import argparse
import sys


class Config:
    def __init__(self):
        self.package_name = ""
        self.repository_url = ""
        self.test_mode = False
        self.output_file = "graph.png"
        self.ascii_tree = False
        self.max_depth = 10

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {filename}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {filename}")

        self.package_name = data.get('package_name', '')
        self.repository_url = data.get('repository_url', '')
        self.test_mode = data.get('test_mode', False)
        self.output_file = data.get('output_file', 'graph.png')
        self.ascii_tree = data.get('ascii_tree', False)
        self.max_depth = data.get('max_depth', 10)

        self._validate()

    def _validate(self):
        if not self.package_name:
            raise ValueError("Package name is required")
        if not self.repository_url:
            raise ValueError("Repository URL is required")
        if not isinstance(self.max_depth, int) or self.max_depth < 1:
            raise ValueError("Max depth must be a positive integer")


def print_config(config):
    print("Configuration parameters:")
    print(f"  package_name: {config.package_name}")
    print(f"  repository_url: {config.repository_url}")
    print(f"  test_mode: {config.test_mode}")
    print(f"  output_file: {config.output_file}")
    print(f"  ascii_tree: {config.ascii_tree}")
    print(f"  max_depth: {config.max_depth}")


def main():
    parser = argparse.ArgumentParser(description='Dependency graph visualizer')
    parser.add_argument('--config', required=True, help='Path to config file')

    try:
        args = parser.parse_args()
        config = Config()
        config.load_from_file(args.config)
        print_config(config)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()