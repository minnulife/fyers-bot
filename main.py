from auth import get_fyers
from engine import Engine

if __name__ == "__main__":
    fyers = get_fyers()
    Engine(fyers).run()
