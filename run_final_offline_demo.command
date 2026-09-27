#!/bin/zsh
set -u

PROJECT_DIR="${0:A:h}"
LOG_FILE="$PROJECT_DIR/evidence/final-offline-terminal.txt"
cd "$PROJECT_DIR" || exit 1

wifi_device=$(/usr/sbin/networksetup -listallhardwareports | awk '/Hardware Port: (Wi-Fi|AirPort)/ {getline; print $2; exit}')
wifi_state="unavailable"
if [[ -n "$wifi_device" ]]; then
  wifi_state=$(/usr/sbin/networksetup -getairportpower "$wifi_device")
  if [[ "$wifi_state" != *": Off" ]]; then
    print -u2 "Wi-Fi is still on ($wifi_state). Turn Wi-Fi off, then run this script again."
    exit 2
  fi
else
  if /usr/bin/curl -Is --max-time 5 https://huggingface.co >/dev/null 2>&1; then
    print -u2 "Internet access is still available. Turn Wi-Fi off, then run this script again."
    exit 2
  fi
  wifi_state="Wi-Fi hardware unavailable to script; network probe failed as expected"
fi

mkdir -p "$PROJECT_DIR/evidence" "$PROJECT_DIR/.wiki-data" "$PROJECT_DIR/work"
exec > >(tee "$LOG_FILE") 2>&1

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1

print "FINAL OFFLINE DEMONSTRATION"
print "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
print "Network: $wifi_state"
print "Model path: $(sed -n 's/^model = //p' wiki_config.toml)"
print "Runtime: $(./launch.command --help >/dev/null 2>&1; print 'local MLX via launch.command')"
print "\n== Memory before =="
/usr/bin/memory_pressure | tail -n 1

if [[ -f .wiki-data/index.sqlite3 ]]; then
  backup="work/index-before-final-offline.sqlite3"
  if [[ -e "$backup" ]]; then
    backup="work/index-before-final-offline-$(date +%Y%m%dT%H%M%S).sqlite3"
  fi
  mv .wiki-data/index.sqlite3 "$backup"
  print "Archived prior generated index: $backup"
fi

print "\n== Help after fresh CLI start =="
./launch.command --help

print "\n== Fresh local ingestion =="
/usr/bin/time -l ./launch.command ingest

print "\n== Duplicate-safety re-ingestion =="
./launch.command ingest

print "\n== Raw source search; no Gemma call =="
./launch.command search "retrieval ranking recommender systems" --limit 3 --save

print "\n== Ask 1: K-means =="
/usr/bin/time -l ./launch.command ask "How does K-means update its centroids, and why should initialization be repeated?" --save

print "\n== Ask 2: recommender retrieval and ranking =="
/usr/bin/time -l ./launch.command ask "What roles do retrieval and ranking play in a recommender system?" --save

print "\n== Ask 3: product leadership archetypes =="
/usr/bin/time -l ./launch.command ask "What distinguishes an Operator from a Craftsperson in product leadership?" --save

print "\n== Ask 4: unsupported question =="
/usr/bin/time -l ./launch.command ask "When was the Eiffel Tower completed?" --save

print "\n== Chat and conversational follow-up =="
/usr/bin/time -l ./launch.command chat --script tests/offline-chat.txt --save

print "\n== Memory after =="
/usr/bin/memory_pressure | tail -n 1
print "Completed: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
print "Transcript: $LOG_FILE"
