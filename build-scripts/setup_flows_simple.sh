#!/usr/bin/env bash
# build-scripts/build_flows_simple.sh
# Simplified flows: Core API + live polling + forms, using BUILT-IN nodes only
# No dashboard dependency — displays live values in the editor sidebar!

set -euo pipefail

NODE_RED_DIR="./node-red"
FLOWS_FILE="$NODE_RED_DIR/flows_simple.json"
SETTINGS_FILE="$NODE_RED_DIR/settings_simple.js"

echo "Regenerating simplified Node-RED flows (core nodes only) at $NODE_RED_DIR"

# Quick settings tweak: Enable sidebar for live "gauges"
cat > "$SETTINGS_FILE" << 'EOF'
module.exports = {
    uiPort: 1880,
    httpAdminRoot: "/",
    httpNodeRoot: "/",
    userDir: ".",
    flowFile: "flows_simple.json",
    credentialSecret: false,
    editorTheme: {
        page: { titleBar: { title: "GasTrack – T.E. Maxson WWTP (Simple Mode)" } },
        projects: { enabled: false }
    },
    logging: { console: { level: "info" } }
};
EOF

# 100% valid JSON: Polling + API + debug "gauges" + manual entry (no ui_*)
cat > "$FLOWS_FILE" << 'EOF'
[
    {
        "id": "gastrack-main",
        "type": "tab",
        "label": "GasTrack – T.E. Maxson WWTP (Simple)",
        "disabled": false,
        "info": "Core flows: Poll API every 30s, enter flows/readings, watch live values in DEBUG sidebar.\nStart your GasTrack API on port 8000 first!"
    },
    {
        "id": "api-base",
        "type": "http request",
        "z": "gastrack-main",
        "name": "GasTrack API Call",
        "method": "use",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "http://127.0.0.1:8000/api{{path}}",
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": false,
        "headers": [],
        "x": 160,
        "y": 100,
        "wires": [["parse-response"]]
    },
    {
        "id": "parse-response",
        "type": "function",
        "z": "gastrack-main",
        "name": "Parse API Response",
        "func": "// Log raw response to debug\nnode.warn(\"API Response: \" + JSON.stringify(msg.payload));\n\n// Extract key values for 'live gauges' (display in sidebar)\nif (msg.payload && typeof msg.payload === 'object') {\n    const data = msg.payload;\n    if (data.sample_point === 'Inlet') {\n        msg.topic = 'Inlet CH4 %';\n        msg.payload = data.ch4_pct || 0;\n        return [msg, null, null];\n    } else if (data.sample_point === 'Outlet') {\n        msg.topic = 'Outlet CH4 %';\n        msg.payload = data.ch4_pct || 0;\n        return [null, msg, null];\n    }\n    // For H2S or other, duplicate logic as needed\n}\nreturn null;",
        "outputs": 3,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 380,
        "y": 100,
        "wires": [["debug-inlet-ch4"], ["debug-outlet-ch4"], ["debug-other"]]
    },
    {
        "id": "debug-inlet-ch4",
        "type": "debug",
        "z": "gastrack-main",
        "name": "Live: Inlet CH4 %",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 610,
        "y": 80,
        "wires": []
    },
    {
        "id": "debug-outlet-ch4",
        "type": "debug",
        "z": "gastrack-main",
        "name": "Live: Outlet CH4 %",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 610,
        "y": 100,
        "wires": []
    },
    {
        "id": "debug-other",
        "type": "debug",
        "z": "gastrack-main",
        "name": "Other Readings (H2S, etc.)",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "true",
        "targetType": "full",
        "statusVal": "",
        "statusType": "auto",
        "x": 610,
        "y": 120,
        "wires": []
    },
    {
        "id": "poll-inject",
        "type": "inject",
        "z": "gastrack-main",
        "name": "Poll Latest (30s)",
        "props": [{"p":"payload","v":"","vt":"date"}],
        "repeat": "30",
        "crontab": "",
        "once": true,
        "onceDelay": 0.1,
        "topic": "",
        "x": 120,
        "y": 200,
        "wires": [["build-paths"]]
    },
    {
        "id": "build-paths",
        "type": "function",
        "z": "gastrack-main",
        "name": "Build API Paths",
        "func": "// Send two parallel requests: Inlet & Outlet\nmsg.path = '/analyzer/latest?point=Inlet';\nnode.send(msg);\nmsg.path = '/analyzer/latest?point=Outlet';\nnode.send(msg);\nreturn null;",
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 300,
        "y": 200,
        "wires": [["api-base"]]
    },
    {
        "id": "manual-entry",
        "type": "inject",
        "z": "gastrack-main",
        "name": "Manual Test Reading",
        "props": [{"p":"payload","v":"{\"sample_point\":\"Inlet\",\"ch4_pct\":55,\"h2s_ppm\":1500,\"o2_pct\":2.5,\"t_sensor_f\":72,\"is_manual_override\":true,\"override_note\":\"Test from Node-RED\"}","vt":"json"}],
        "repeat": "",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "topic": "",
        "x": 120,
        "y": 280,
        "wires": [["submit-manual"]]
    },
    {
        "id": "submit-manual",
        "type": "change",
        "z": "gastrack-main",
        "name": "POST Manual Reading",
        "rules": [{"t":"set","p":"method","pt":"msg","to":"POST","tot":"str"},{"t":"set","p":"url","pt":"msg","to":"http://127.0.0.1:8000/api/analyzer","tot":"str"}],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 340,
        "y": 280,
        "wires": [["api-base"]]
    },
    {
        "id": "daily-flow-test",
        "type": "inject",
        "z": "gastrack-main",
        "name": "Test Daily Flow",
        "props": [{"p":"payload","v":"{\"date\":\"2025-11-26\",\"blower_1_scf_day\":10000,\"blower_2a_scf_day\":8000,\"biogas_flared_scf_day\":2000}","vt":"json"}],
        "repeat": "",
        "crontab": "",
        "once": false,
        "onceDelay": 0.1,
        "topic": "",
        "x": 120,
        "y": 360,
        "wires": [["submit-daily"]]
    },
    {
        "id": "submit-daily",
        "type": "change",
        "z": "gastrack-main",
        "name": "POST Daily Flow",
        "rules": [{"t":"set","p":"method","pt":"msg","to":"POST","tot":"str"},{"t":"set","p":"url","pt":"msg","to":"http://127.0.0.1:8000/api/daily-flow","tot":"str"}],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 340,
        "y": 360,
        "wires": [["api-base"]]
    }
]
EOF

echo ""
echo "Simplified flows ready! No missing types, no dashboard drama."
echo ""
echo "Start it:"
echo "  cd node-red && killall node 2>/dev/null || true && npx node-red -u ."
echo ""
echo "Open: http://127.0.0.1:1880"
echo ""
echo "What you'll get:"
echo "  - Auto-polls your API every 30s (click the inject to start)"
echo "  - Live 'gauges' in the DEBUG sidebar (CH4 % updates in real-time!)"
echo "  - Test buttons for manual readings + daily flows (inject nodes)"
echo "  - All responses logged to console/debug for easy troubleshooting"
echo ""
echo "Pro tip: Deploy the flow (red button), then watch the sidebar for live biogas data."
echo ""

chmod +x "$0"