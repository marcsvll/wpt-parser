import requests
import json
from WPTParser import WPTParser

class Fetch():

    def __init__(self, headers: dict = {}):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        self.headers.update(headers)

    def json(self, test_id: str='241004_AiDcW0_A9N', WPT_URI: str = None) -> dict:
        """Fetches the JSON format result for a WPT test

        Keyword Arguments:
            test_id {str} -- unique WPT test ID (default: {'200518_Y2_c736f1cb25d54ac8cd93ebdfdcf6375b'})

        Returns:
            dict -- json response of the WPT test
        """
        # api rejects the request with unauthorized if user-agent header not set
        url = '{0}/jsonResult.php?test={1}'.format(WPTParser().WPT_URI(WPT_URI), test_id)
        json_data = requests.get(url, headers = self.headers)
        json_data = json_data.json()
        return json_data

    def json_from_file(self, file_path: str) -> dict:
        """Reads JSON format result for a WPT test from a file

        Keyword Arguments:
            file_path {str} -- path to the JSON file

        Returns:
            dict -- json response of the WPT test
        """
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
            return json_data
        except Exception as ex:
            print(f"An error occurred while reading the file: {ex}")
            return {}
