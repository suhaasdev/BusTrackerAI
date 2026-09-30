from flask import jsonify


def success(data=None, message="Operation successful", status=200):
    return jsonify({"success": True, "message": message, "data": data or {}}), status


def error(message="Something went wrong", code="ERROR", status=400):
    return jsonify({"success": False, "message": message, "error": code}), status
