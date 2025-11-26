### First time on a new machine / phone
```bash
cd frontend && npm install && npm run build && cd ..
python -m src.main start
```


### Running the app and then starting the node-red interface.
#### Terminal 1 – start the Python API
cd ~/dev/gastrack && source .venv/bin/activate && python -m src.cli start

#### Terminal 2 – start Node-RED dev console
cd ~/dev/gastrack/node-red/simple && npx node-red -u .