class TlpMessage:
    def __init__(self, t: int, product: int, baseg: int):
        self.t = t
        self.product = product
        self.baseg = baseg

    @staticmethod
    def from_json(json_data: dict):
        return TlpMessage(
            t=int(json_data['t']),
            product=int(json_data['product']),
            baseg=int(json_data['baseg']),
        )

    def to_json(self) -> dict:
        return {
            't': str(self.t),
            'product': str(self.product),
            'baseg': str(self.baseg),
        }
