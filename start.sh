#!/bin/bash
HOME="/Users/sachaariel"
STREAMLIT="$HOME/Library/Python/3.9/bin/streamlit"
APP_DIR="$HOME/Desktop/Projets Immobiliers/miami-analyzer"
LOG="$APP_DIR/.streamlit_log.txt"
PORT=8501
export PATH="$HOME/Library/Python/3.9/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

already_running() {
    curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" 2>/dev/null | grep -q "200"
}

if already_running; then
    if [ -d "/Applications/Google Chrome.app" ]; then
        open -na "Google Chrome" --args --app="http://localhost:$PORT" --window-size=1440,900
    else
        open "http://localhost:$PORT"
    fi
    exit 0
fi

lsof -ti :$PORT 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1

cd "$APP_DIR"
nohup "$STREAMLIT" run app.py \
  --server.headless true \
  --server.port $PORT \
  --browser.gatherUsageStats false \
  --server.fileWatcherType none > "$LOG" 2>&1 &

for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    if already_running; then
        break
    fi
    sleep 1
done

if already_running; then
    if [ -d "/Applications/Google Chrome.app" ]; then
        open -na "Google Chrome" --args --app="http://localhost:$PORT" --window-size=1440,900
    elif [ -d "/Applications/Brave Browser.app" ]; then
        open -na "Brave Browser" --args --app="http://localhost:$PORT" --window-size=1440,900
    else
        open "http://localhost:$PORT"
    fi
else
    osascript -e 'display dialog "PATONRIEL failed to start. Check the log at:\n'"$LOG" buttons {"OK"} default button "OK" with title "PATONRIEL"'
fi
