# Build as a desktop application
uv run streamlit-desktop-app build src/app.py --name "plux recorder" \
    --pyinstaller-options \
    --add-data "PLUX-API-Python3/:PLUX-API-Python3/" \
    --add-data "src/const.py:." \
    --add-data "src/logger.py:."