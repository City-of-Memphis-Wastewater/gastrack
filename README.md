### Install from source
```bash
git clone https://github.com/city-of-memphis-wastewater/gastrack.git
cd gastrack
uv sync
source .venv/bin/activate
```

### First time on a new machine / phone
```bash
cd frontend && npm install && npm run build && cd ..
python -m src.main start
```


### Run the app and then start the node-red interface.
#### Terminal 1 – start the Python API
```bash
cd ~/dev/gastrack && source .venv/bin/activate && python -m src.cli start
```

#### Terminal 2 – start Node-RED dev console
```bash
cd ~/dev/gastrack/node-red/simple && npx node-red -u .
```

