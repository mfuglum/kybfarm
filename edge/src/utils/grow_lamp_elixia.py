import requests

# This is a Class for interfacing with the grow lamp Heliospectra Elixia
# Datasheet: https://led.heliospectra.com/hubfs/Heliospectra%20ELIXIA%2c%20DYNA%20User%20Manual%20V.8.2.pdf
# API documentation: https://support.heliospectra.com/knowledge/api-documentation-all-series-models
class grow_lamp_elixia:
    """
    Expected payload for configuring channel intensities:
    payload = {
                cmd: type of command,
                intesity: n:n:n:n,
                res_topic: response topic,
            }
    """
    def __init__ (self, ip_address):
        self.ip_address = ip_address
        self.base_url = f"http://{self.ip_address}/"

    def update_ip_address(self, new_ip_address):
        self.ip_address = new_ip_address
        self.base_url = f"http://{self.ip_address}/"
    
    def set_channel_intensities(self, intensities):
        # Intensities should be format n:n:n:n
        url = self.base_url + "intensity.cgi?int=" + str(intensities)
        try:
            print("Try get url")
            response = requests.get(url, timeout=5)
            return response
        except Exception as e:
            return e
    
    def get_diagnostic_data(self):
        url = self.base_url + "diag.xml"
        try:
            response = requests.get(url, timeout=5)
            return response
        except Exception as e:
            return e
        
    def get_status(self):
        url = self.base_url + "status.xml"
        try:
            response = requests.get(url, timeout=5)
            return response
        except Exception as e:
            return e