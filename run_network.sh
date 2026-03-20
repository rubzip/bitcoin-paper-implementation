#!/bin/bash

# Bitcoin Paper Network Automation Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default number of nodes
NUM_NODES=${1:-4}
REGISTRY_PORT=8000
BASE_NODE_PORT=8001

PIDS=()

cleanup() {
    echo -e "\n${RED}Stopping network...${NC}"
    for pid in "${PIDS[@]}"; do
        kill $pid 2>/dev/null
    done
    echo -e "${GREEN}All processes stopped.${NC}"
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

echo -e "${BLUE}Starting Central Registry on port $REGISTRY_PORT...${NC}"
uv run python main.py registry --port $REGISTRY_PORT > logs/registry.log 2>&1 &
PIDS+=($!)

echo -e "${BLUE}Waiting for registry to initialize...${NC}"
sleep 2

# Predefined names for the first few nodes, then generic names
NAMES=("Alice" "Bob" "Charlie" "Dave" "Eve" "Frank" "Grace" "Heidi")

for (( i=0; i<$NUM_NODES; i++ )); do
    PORT=$((BASE_NODE_PORT + i))
    if [ $i -lt ${#NAMES[@]} ]; then
        ID=${NAMES[$i]}
    else
        ID="Node-$((i+1))"
    fi
    
    echo -e "${BLUE}Starting Node $ID on port $PORT...${NC}"
    uv run python main.py node --id "$ID" --port "$PORT" --registry "http://localhost:$REGISTRY_PORT" > "logs/node_$ID.log" 2>&1 &
    PIDS+=($!)
done

echo -e "${GREEN}--------------------------------------------------${NC}"
echo -e "${GREEN}Network is UP with $NUM_NODES nodes!${NC}"
echo -e "${GREEN}Registry Dashboard: http://localhost:$REGISTRY_PORT/dashboard${NC}"
echo -e "Check the Registry Dashboard to see all connected nodes."
echo -e "${GREEN}--------------------------------------------------${NC}"
echo -e "Press Ctrl+C to stop the network."

# Keep script alive
wait
