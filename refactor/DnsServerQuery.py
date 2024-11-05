import fofa
import logging


class FofaRetriever:
    def __init__(self, api_key, region=None):
        try:
            self.client = fofa.Client(api_key)
        except:
            logging.error("Invalid API key")
            raise ValueError("Invalid API key")

        self.query_str = 'protocol="dns" && port="53" && banner="dnsmasq"'
        if region is not None:
            self.query_str += f' && region="{region}"'

        self.result = None


    def get_data(self, size):
        fpoint = self.get_fpoint()
        if size > fpoint:
            logging.error(f"Insufficient fpoint: {fpoint} < {size}")
            raise ValueError(f"Insufficient fpoint: {fpoint} < {size}")

        batch = [100] * (size // 100) + ([size % 100] if size % 100 != 0 else [])
        result = []
        for i in range(len(batch)):
            data = self.client.search(self.query_str, size=batch[i], page=i+1, fields= "ip")
            result += data["results"]

        self.result = result
        return result

    def get_fpoint(self):
        return self.client.get_userinfo()["fofa_point"]

    def get_previous_result(self):
        if self.result is None:
            logging.warning("No previous result")
        else:
            return self.result



if __name__ == '__main__':
    key = "0d964795105b2e6820ae22838be52452"
    print(FofaRetriever(key).get_data(50))




