import os
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()

_driver: Driver | None = None

def get_driver() -> Driver:
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, username, password]):
            raise RuntimeError("Missing NEO4J_URI, NEO4J_USERNAME or NEO4J_PASSWORD in environment")

        if uri is not None and username is not None and password is not None:
            _driver = GraphDatabase.driver(uri, auth=(username, password))
            _driver.verify_connectivity()
        else:
            raise ValueError("Missing environment variables")

    return _driver

def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
