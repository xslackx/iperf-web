from urllib.request import urlopen
import json

URL = "https://export.iperf3serverlist.net/listed_iperf3_servers.json"

def download_content():
    with urlopen(URL) as server:
        if server.status == 200:
            response = server.read()
            data = json.loads(response.decode('utf-8'))
            if len(data) > 0:
                server.close()
                return data
            else: return []
        else: return []

def format_content(host):
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
      
def create_config(data):
    return list(map(format_content, data))


def standalone():
    data = download_content()
    content = create_config(data)
    for each in content:
        print(each)