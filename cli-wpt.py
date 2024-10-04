import pprint
import argparse
import json
from collections import Counter
from WPTParser.Fetch import Fetch
from WPTParser.JSONParser import JSONParser
import requests
import yaml

# Definição das keys padrão
DEFAULT_KEYS = [
    'loadTime',
    'detected_technologies',
    'origin_dns.soa',
    'origin_dns.ns',
    'jsLibsVulns',
    'securityHeaders'
]

def print_pretty_dict(data, title=None):
    """Pretty print dictionaries with a title if provided."""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    pprint.pprint(data, width=120)

def output_json(data):
    """Return JSON formatted data."""
    return json.dumps(data, indent=4)

def output_yaml(data):
    """Return YAML formatted data."""
    return yaml.dump(data, default_flow_style=False)

def fetch_json_from_source(source, file=None, test_id=None, WPT_URI=None):
    """Fetch JSON data from either a file or API."""
    fetch = Fetch()
    if source == 'file':
        try:
            with open(file, 'r') as json_file:
                return fetch.json_from_file(json_file)
        except FileNotFoundError:
            print(f"Error: File {file} not found.")
        except json.JSONDecodeError:
            print(f"Error: Failed to parse JSON from file {file}.")
    elif source == 'api':
        try:
            return fetch.json(test_id=test_id, WPT_URI=WPT_URI)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from the API: {e}")
    return None

def process_json_data(json_data, data_prefix, keys):
    """Process JSON data and extract specified keys and CDN information."""
    result = JSONParser(json_data).pick(keys=keys).exec()

    sub_requests = JSONParser(json_data).pick(keys=[f'{data_prefix}.requests']).exec().values()

    cdn_providers = [
        request.get('cdn_provider') 
        for request_list in sub_requests if request_list
        for request in request_list if request.get('cdn_provider')
    ]

    output_data = {}
    
    if cdn_providers:
        cdn_provider_counts = Counter(cdn_providers)
        output_data['cdn_provider_counts'] = dict(cdn_provider_counts)
    else:
        output_data['cdn_provider_counts'] = "No CDN providers found in the requests."

    domains_detected = JSONParser(json_data).pick(keys=[f'{data_prefix}.domains']).exec().values()

    hostname_cdn_provider = {
        domain: details.get('cdn_provider')
        for domain_details in domains_detected if domain_details
        for domain, details in domain_details.items()
    }

    if hostname_cdn_provider:
        output_data['hostname_cdn_provider_mapping'] = hostname_cdn_provider
    else:
        output_data['hostname_cdn_provider_mapping'] = "No domains detected."

    output_data['extracted_data'] = result if result else "No data extracted from the specified keys."

    return output_data

def get_keys(custom_keys=None):
    """Return the custom keys or default if none provided."""
    if custom_keys:
        return custom_keys
    return DEFAULT_KEYS

def main():
    """Main function to parse arguments and execute data fetching and processing."""
    parser = argparse.ArgumentParser(
        description="Fetch JSON from file or API, extract specific keys, and analyze CDN and domain data.",
        epilog="Example usage: python cli-wpt.py --source api --test_id <TEST_ID> --keys loadTime --data_prefix data.runs.1.firstView"
    )

    parser.add_argument('--source', choices=['file', 'api'], required=True, help="Source of JSON: 'file' to load from a file, 'api' to fetch using a test_id.")
    parser.add_argument('--file', type=str, help="Path to the JSON file (required if source is 'file').")
    parser.add_argument('--test_id', type=str, help="Test ID to fetch JSON from the API (required if source is 'api').")
    parser.add_argument('--WPT_URI', type=str, default=None, help="Optional WebPageTest URI.")
    parser.add_argument('--data_prefix', type=str, default='data.runs.1.firstView', help="Prefix for the JSON data keys.")
    parser.add_argument('--keys', type=str, nargs='+', default=get_keys(), help="Keys to extract from the JSON.")
    parser.add_argument('--output_format', choices=['json', 'yaml'], default='json', help="Format of the output (default: 'json').")

    args = parser.parse_args()

    if not args.keys or len(args.keys) == 0:
        print("Error: --keys argument is required and should contain at least one key.")
        return

    json_data = fetch_json_from_source(args.source, file=args.file, test_id=args.test_id, WPT_URI=args.WPT_URI)

    if not json_data:
        print("No JSON data to process.")
        return

    data_prefix = args.data_prefix
    keys = [f'{data_prefix}.{key}' for key in get_keys(args.keys)]

    output_data = process_json_data(json_data, data_prefix, keys)

    if args.output_format == 'json':
        print(output_json(output_data))
    elif args.output_format == 'yaml':
        print(output_yaml(output_data))

if __name__ == "__main__":
    main()
