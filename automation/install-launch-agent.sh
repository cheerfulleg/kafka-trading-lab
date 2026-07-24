#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNNER="$PROJECT_DIR/automation/run-daily-agent.sh"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/com.kafka-trading-lab.daily-agent.plist"
UID_VALUE="$(id -u)"

mkdir -p "$PLIST_DIR" "$PROJECT_DIR/.agent-logs"
chmod +x "$RUNNER"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.kafka-trading-lab.daily-agent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUNNER</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$PROJECT_DIR</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>6</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>StandardOutPath</key>
  <string>$PROJECT_DIR/.agent-logs/launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>$PROJECT_DIR/.agent-logs/launchd.stderr.log</string>
</dict>
</plist>
EOF

plutil -lint "$PLIST_PATH"
launchctl bootout "gui/$UID_VALUE/com.kafka-trading-lab.daily-agent" 2>/dev/null || true
launchctl bootstrap "gui/$UID_VALUE" "$PLIST_PATH"

echo "Installed. The local agent will run at 20:00 Monday-Friday."
echo "Test now with: launchctl kickstart -k gui/$UID_VALUE/com.kafka-trading-lab.daily-agent"
