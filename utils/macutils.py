import csv
import copy
from urllib.request import Request, urlopen

class MacUtils:
    def __init__(self, addr: str) -> None:
        self.mac = addr
        self.mac_user_input = copy.copy(self.mac)
        self.headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Accept-Language': 'en-US,en;q=0.5'
                        }
        self.oui_fp = "config/ieee/oui.csv"
        self.ieee_link = 'http://standards-oui.ieee.org/oui/oui.csv'
        self.headers = ["Registry","Assignment",
                               "Organization Name","Organization Address"]
        self.separators = [":", "-", "."]
        self.oui_vendors: dict = []
        self.mac_full = None
        self.mac_oui = None
    
    def get_update_bases(self):
        req = Request(self.ieee_link, self.headers)
        with urlopen(req, timeout=180) as response:
            if response.status == 200:
                new_data = response.read()
                with open(self.oui_fp, 'w') as update:
                    update.write(new_data.decode('utf-8'))
             
    def format_addr(self) -> None:
        for sep in self.separators:
            if self.mac.find(sep) == 2:
                self.mac_full = self.mac.replace(sep, '') 
    
    def load_oui_base(self) -> dict:
        with open(self.oui_fp, 'r', newline='', encoding='utf-8') as vendors_database:
                for row in csv.DictReader(vendors_database):
                    if row[self.headers[1]] == self.mac_full[:6]:
                        return row
    
    def runner(self) -> bool:
        try:
            self.format_addr()
            self.mac_oui = self.load_oui_base()
            if self.mac_oui:
                return True
            else: return False
        except:
            return False

    

