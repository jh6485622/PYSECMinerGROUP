from flask import Flask, request, jsonify

app = Flask(__name__)
BLOCKS_FILE = "blocks.txt"

def block_exists(block_look):
    try:
        with open(BLOCKS_FILE, "r") as f:
            for line in f:
                if block_look in line:
                    return True
    except FileNotFoundError:
        return False

def write_block(block_look):
    with open(BLOCKS_FILE, "a") as f:
        f.write(block_look + "\n")

@app.route("/")
def index():
    return "<h1>Welcome to the NukeHash Server</h1><p>Use the /block_mining endpoint to submit blocks.</p>"

@app.route("/block_mining", methods=["POST"])
def submit_block():
    data = request.get_json()
    block_look = data.get("block_look")
    if not block_look:
        return jsonify({"error": "Missing block_look"}), 400
    if block_exists(block_look):
        return jsonify({"status": "duplicate", "message": "Block already exists"}), 200
    write_block(block_look)
    return jsonify({"status": "success", "message": "Block written"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=17884, debug=True)