from dataclasses import dataclass

@dataclass
class AliceTLPData:
    baseg: int
    product: int
    t: int

    @staticmethod
    def from_dict(data: dict) -> 'AliceTLPData':
        """
        Create an AliceTLPMessage instance from a dictionary.
        
        Args:
            data (dict): The dictionary containing baseg, product, and t.
        
        Returns:
            AliceTLPData: The parsed instance.
        """
        # Validate the required fields
        required_fields = ["baseg", "product", "t"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(data[field], int):
                raise ValueError(f"Field '{field}' must be an integer.")

        return AliceTLPData(
            baseg=data["baseg"],
            product=data["product"],
            t=data["t"]
        )

    def to_dict(self) -> dict:
        """
        Convert the AliceTLPData instance back to a dictionary.
        
        Returns:
            dict: The dictionary representation of the message.
        """
        return {
            "baseg": self.baseg,
            "product": self.product,
            "t": self.t
        }
