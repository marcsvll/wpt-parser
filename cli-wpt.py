import argparse
from WPTParser.Fetch import Fetch
from WPTParser.JSONParser import JSONParser

def main():
    parser = argparse.ArgumentParser(description="Fetch JSON from file or API and extract specific keys.")
    
    parser.add_argument('--source', choices=['file', 'api'], required=True, help="Source of JSON: 'file' to load from a file, 'api' to fetch using a test_id.")
    
    parser.add_argument('--file', type=str, help="Path to the JSON file (required if source is 'file').")
    
    parser.add_argument('--test_id', type=str, help="Test ID to fetch JSON from the API (required if source is 'api').")
    
    parser.add_argument('--WPT_URI', type=str, default=None, help="Optional WebPageTest URI.")
    
    parser.add_argument('--keys', type=str, nargs='+', required=True, help="Keys to extract from the JSON (e.g., 'data.median.firstView.loadTime').")
    
    args = parser.parse_args()
    
    fetch = Fetch()
    
    if args.source == 'file':
        if not args.file:
            print("Error: --file argument is required when source is 'file'.")
            return
        json_data = fetch.json_from_file(args.file)
    elif args.source == 'api':
        if not args.test_id:
            print("Error: --test_id argument is required when source is 'api'.")
            return
        json_data = fetch.json(test_id=args.test_id, WPT_URI=args.WPT_URI)
    
    if json_data:
        keys = args.keys
        extracted_data = JSONParser(json_data).pick(keys=keys).exec()
        print(extracted_data)
    else:
        print("No JSON data to process.")

if __name__ == "__main__":
    main()
