from flask import Blueprint, jsonify, request
from database import ThreatIntelDB

api = Blueprint('api', __name__)
db = ThreatIntelDB()

@api.route('/pipeline-overview', methods=['GET'])
def pipeline_overview():
    """Get pipeline statistics"""
    try:
        data = db.get_pipeline_overview()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/risk-distribution', methods=['GET'])
def risk_distribution():
    """Get risk level distribution"""
    try:
        data = db.get_risk_distribution()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/category-distribution', methods=['GET'])
def category_distribution():
    """Get category distribution"""
    try:
        data = db.get_category_distribution()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/threat-timeline', methods=['GET'])
def threat_timeline():
    """Get threat timeline data"""
    try:
        days = int(request.args.get('days', 7))
        data = db.get_threat_timeline(days)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/recent-threats', methods=['GET'])
def recent_threats():
    """Get recent threats"""
    try:
        limit = int(request.args.get('limit', 10))
        risk_filter = request.args.get('risk', None)
        data = db.get_recent_threats(limit, risk_filter)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/ioc-stats', methods=['GET'])
def ioc_stats():
    """Get IOC statistics"""
    try:
        data = db.get_ioc_stats()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/rss-feed-stats', methods=['GET'])
def rss_feed_stats():
    """Get RSS feed statistics"""
    try:
        data = db.get_rss_feed_stats()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/threat-families', methods=['GET'])
def threat_families():
    """Get threat family word cloud data"""
    try:
        data = db.get_threat_families()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/article/<int:article_id>', methods=['GET'])
def article_details(article_id):
    """Get detailed article information"""
    try:
        data = db.get_article_details(article_id)
        if data:
            return jsonify(data), 200
        else:
            return jsonify({"error": "Article not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
