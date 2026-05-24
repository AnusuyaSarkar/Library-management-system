from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from ..ai import LibraryAIAgent

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")
agent = LibraryAIAgent()


@ai_bp.route("/recommendations", methods=["GET"])
@login_required
def recommendations():
    keyword = request.args.get("keyword", "").strip()
    limit = int(request.args.get("limit", "5"))
    data = agent.recommend(user_id=current_user.id, keyword=keyword, limit=limit)
    return jsonify({"ok": True, "recommendations": data})


@ai_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    payload = request.get_json(silent=True) or {}
    query = (payload.get("query") or "").strip()
    if not query:
        return jsonify({"ok": False, "error": "Query is required."}), 400
    response = agent.chat(user_id=current_user.id, query=query)
    return jsonify({"ok": True, "response": response})


@ai_bp.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"ok": False, "error": "query is required"}), 400
    limit = int(request.args.get("limit", "10"))
    results = agent.nl_search(query=query, limit=limit)
    return jsonify({"ok": True, "results": results})


@ai_bp.route("/reminders", methods=["GET"])
@login_required
def reminders():
    data = agent.reminders(user_id=current_user.id)
    return jsonify({"ok": True, "reminders": data})


@ai_bp.route("/reminders/persist", methods=["POST"])
@login_required
def persist_reminders():
    created = agent.persist_reminders(user_id=current_user.id)
    return jsonify({"ok": True, "created_notifications": created})


@ai_bp.route("/summary/<int:book_id>", methods=["GET"])
@login_required
def summary(book_id):
    data = agent.summarize_book(book_id)
    if not data:
        return jsonify({"ok": False, "error": "Book not found"}), 404
    return jsonify({"ok": True, "summary": data})


@ai_bp.route("/analytics", methods=["GET"])
@login_required
def analytics():
    if current_user.role != "admin":
        return jsonify({"ok": False, "error": "Admin access required"}), 403
    return jsonify({"ok": True, "insights": agent.analytics()})
