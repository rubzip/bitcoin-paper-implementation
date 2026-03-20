import argparse
import uvicorn
from bitcoin.api.node_api import run_node
from bitcoin.api.registry import peer_handler

def main():
    parser = argparse.ArgumentParser(description="Bitcoin Paper Implementation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Registry command
    reg_parser = subparsers.add_parser("registry", help="Start the central peer registry")
    reg_parser.add_argument("--port", type=int, default=8000, help="Port to run the registry on")

    # Node command
    node_parser = subparsers.add_parser("node", help="Start a blockchain node")
    node_parser.add_argument("--id", type=str, required=True, help="Node ID (e.g. Alice)")
    node_parser.add_argument("--port", type=int, required=True, help="Port to run the node on")
    node_parser.add_argument("--registry", type=str, default="http://localhost:8000", help="Registry URL")

    args = parser.parse_args()

    if args.command == "registry":
        print(f"Starting Registry on port {args.port}...")
        uvicorn.run(peer_handler, host="0.0.0.0", port=args.port)
    elif args.command == "node":
        print(f"Starting Node {args.id} on port {args.port}...")
        run_node(node_id=args.id, port=args.port, registry_url=args.registry)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
