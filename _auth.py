from dotenv import dotenv_values
from pathlib import Path
import os

script_path = Path(os.path.dirname(os.path.abspath(__file__)))
config = dotenv_values(script_path / ".env")

# Webdav
USR_nextcloud = config["USR_nextcloud"]
PWD_nextcloud = config["PWD_nextcloud"]
URL_nextcloud = config["URL_nextcloud"]
ICS = config["ICS"]

# Trilium
URL_trilium = config["URL_trilium"]
TOKEN_trilium = config["TOKEN_trilium"]
