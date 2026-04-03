from urllib.request import urlopen
import json

class ImportIperf3Servers:
    def __init__(self) -> None:
        self.URL = "https://export.iperf3serverlist.net/listed_iperf3_servers.json"
        self.CFG = 'config/config.json'

    def download_content(self) -> list:
        with urlopen(self.URL) as server:
            if server.status == 200:
                response = server.read()
                data = json.loads(response.decode('utf-8'))
                if len(data) > 0:
                    server.close()
                    return data
                else: return [{}]
            else: return [{}]

    def format_content(self, host) -> dict:
        name = host["PROVIDER"]+"-"+host['SITE']+"-"+host['COUNTRY']+"-"+host['IP/HOST']
        return {
                "name": name,
                "iperf_version": "3",
                "iperf_target": host['IP/HOST'],
                "iperf_port": host['PORT'],
                "iperf_conn_type": "TCP",
                "iperf_timeout": "10",
                "iperf_parameters": "--format m"
            }
        
    def create_config(self, data):
        return list(map(self.format_content, data))

            
    def update_config(self) -> bool:
        iperf_servers = self.download_content()
        if iperf_servers != [{}]:
            new_content = self.create_config(iperf_servers)
            with open(self.CFG, 'r+') as file:
                data = json.load(file)
                data['iperf'].extend(new_content)
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                return True
        else: return False    