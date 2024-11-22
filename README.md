# Recorging Application for biosignalsplux

## Overview
This application is a Python application that retrieves data in real-time from the Plux device and visualizes it graphically using Streamlit.

## Features
- Real-time data acquisition and visualization
- Dynamic channel name setting
- Interactive graph display using Altair

## Requirements
- uv (Package manager for Python)
- Python 3.11.0 or higher
- Dependency libraries:
  - Streamlit (>=1.39.0)
  - Altair (>=5.4.1)

## Installation Instructions
1. Clone this repository
2. Copy the PLUX-API-Python3 directory from [official API files](https://github.com/pluxbiosignals/python-samples.git)
3. Change the permission of `plux.so`
    ```bash
    cd PLUX-API-Python3/{OS}_{python_version}
    chmod 777 plux.so
    ```
4. Change the permission of `bth_macprocess` (If you are using Mac (M chip)).  
    ```bash
    cd PLUX-API-Python3/M1_{python_version}
    chmod 777 bth_macprocess
    ```
5. Create a virtual environment and install dependencies
    ```bash
    uv sync
    ```

## How to use
```bash
uv run streamlit run src/app.py --server.headless=true 
```
## TODO
- [ ] Refactor app.py
- [ ] Confirm compatibility with platforms other than macOS (M chip)

## License
This repository is licensed under the MIT License.