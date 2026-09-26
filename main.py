import asyncio

from flask import Flask, jsonify, request

from ai_script import generate_ai_response

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/v1/ai", methods=["POST"])
def ai():
    data = request.get_json(silent=True) or {}
    required_fields = ["prompt", "context", "history", "system_command"]
    missing = [field for field in required_fields if field not in data]

    if missing:
        return jsonify({
            "error": "Bad Request",
            "message": f"Missing required fields: {missing}"
        }), 400

    prompt = str(data["prompt"]).strip()
    context = str(data["context"]).strip()
    history = str(data["history"]).strip()
    system_command = str(data["system_command"]).strip()

    try:
        result = asyncio.run(
            generate_ai_response(
                prompt=prompt,
                context=context,
                history=history,
                system_command=system_command,
            )
        )
        return jsonify({
            "success": True,
            "provider": result["provider"],
            "response": result["response"],
        }), 200
    except Exception as exc:  # pragma: no cover - defensive API fallback
        return jsonify({
            "success": False,
            "error": "AI request failed",
            "message": str(exc),
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)