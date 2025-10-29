import json
import argparse
import sys
import urllib.request
import gzip
import xml.etree.ElementTree as ET


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


def get_package_dependencies(package_name, repository_url):
    try:
        if repository_url.endswith('/'):
            repository_url = repository_url[:-1]

        search_url = f"{repository_url}/FindPackagesById()?id='{package_name}'"

        request = urllib.request.Request(search_url)
        request.add_header('Accept-Encoding', 'gzip')

        with urllib.request.urlopen(request) as response:
            if response.info().get('Content-Encoding') == 'gzip':
                content = gzip.decompress(response.read()).decode('utf-8')
            else:
                content = response.read().decode('utf-8')

        dependencies = []
        namespace = {
            'atom': 'http://www.w3.org/2005/Atom',
            'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
            'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices'
        }

        root = ET.fromstring(content)
        entries = root.findall('.//atom:entry', namespace)

        for entry in entries:
            properties = entry.find('.//m:properties', namespace)
            if properties is not None:
                deps_elem = properties.find('d:Dependencies', namespace)
                if deps_elem is not None and deps_elem.text:
                    deps_str = deps_elem.text
                    for dep in deps_str.split('|'):
                        if ':' in dep:
                            dep_package = dep.split(':')[0]
                            if dep_package and dep_package != package_name:
                                dependencies.append(dep_package)

        return list(set(dependencies))

    except Exception as e:
        raise ValueError(f"Error fetching dependencies for {package_name}: {e}")


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

        print(f"\nDirect dependencies for package '{config.package_name}':")
        dependencies = get_package_dependencies(config.package_name, config.repository_url)

        if dependencies:
            for i, dep in enumerate(dependencies, 1):
                print(f"  {i}. {dep}")
        else:
            print("  No dependencies found")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()