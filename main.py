"""
LinkedIn Scraper API
A REST API for scraping LinkedIn profiles, companies, and schools using multiple account rotation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import re
from account_manager import LinkedInAccountManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize account manager
account_manager = LinkedInAccountManager()

def extract_linkedin_id(url):
    """Extract LinkedIn ID from URL"""
    patterns = {
        'profile': r'/in/([^/?]+)',
        'company': r'/company/([^/?]+)', 
        'school': r'/school/([^/?]+)'
    }
    
    for type_name, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return type_name, match.group(1)
    
    return None, None

def convert_urn_to_url(urn):
    """Convert LinkedIn URN to URL"""
    if not urn:
        return None
    
    # Remove urn:li: prefix if present
    if urn.startswith('urn:li:'):
        urn = urn[7:]
    
    # Extract entity type and ID
    if ':' in urn:
        entity_type, entity_id = urn.split(':', 1)
        
        # Map entity types to URL patterns
        url_patterns = {
            'person': f'https://www.linkedin.com/in/{entity_id}/',
            'company': f'https://www.linkedin.com/company/{entity_id}/',
            'school': f'https://www.linkedin.com/school/{entity_id}/',
            'fs_profile': f'https://www.linkedin.com/in/{entity_id}/',
            'fs_company': f'https://www.linkedin.com/company/{entity_id}/',
            'fs_school': f'https://www.linkedin.com/school/{entity_id}/'
        }
        
        return url_patterns.get(entity_type)
    
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "LinkedIn Scraper API is running"
    })

@app.route('/accounts/status', methods=['GET'])
def accounts_status():
    """Get status of all accounts"""
    try:
        available_accounts = account_manager.get_available_accounts()
        return jsonify({
            "total_accounts": len(account_manager.accounts_data["accounts"]),
            "available_accounts": len(available_accounts),
            "accounts": [
                {
                    "id": acc["id"],
                    "status": acc["status"],
                    "challenge_count": acc["challenge_count"],
                    "requests_count": acc["requests_count"]
                }
                for acc in account_manager.accounts_data["accounts"]
            ]
        })
    except Exception as e:
        logger.error(f"Error getting accounts status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/scrape/profile', methods=['POST'])
def scrape_profile():
    """Scrape LinkedIn profile from URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        url_type, linkedin_id = extract_linkedin_id(url)
        
        if url_type != 'profile':
            return jsonify({"error": "Invalid LinkedIn profile URL"}), 400
        
        # Get LinkedIn API instance
        api = account_manager.get_api()
        if not api:
            return jsonify({"error": "No available LinkedIn accounts"}), 503
        
        # Scrape profile
        profile_data = api.get_profile(linkedin_id)
        
        # Update account usage
        if account_manager.current_account:
            account_manager.mark_request(account_manager.current_account["id"])
        
        return jsonify({
            "success": True,
            "data": profile_data,
            "account_used": account_manager.current_account["id"] if account_manager.current_account else None
        })
        
    except Exception as e:
        logger.error(f"Error scraping profile: {e}")
        # Mark account as potentially challenged
        if account_manager.current_account:
            account_manager.mark_challenge(account_manager.current_account["id"])
        
        return jsonify({"error": str(e)}), 500

@app.route('/scrape/company', methods=['POST'])
def scrape_company():
    """Scrape LinkedIn company from URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        url_type, linkedin_id = extract_linkedin_id(url)
        
        if url_type != 'company':
            return jsonify({"error": "Invalid LinkedIn company URL"}), 400
        
        # Get LinkedIn API instance
        api = account_manager.get_api()
        if not api:
            return jsonify({"error": "No available LinkedIn accounts"}), 503
        
        # Scrape company
        company_data = api.get_company(linkedin_id)
        
        # Update account usage
        if account_manager.current_account:
            account_manager.mark_request(account_manager.current_account["id"])
        
        return jsonify({
            "success": True,
            "data": company_data,
            "account_used": account_manager.current_account["id"] if account_manager.current_account else None
        })
        
    except Exception as e:
        logger.error(f"Error scraping company: {e}")
        # Mark account as potentially challenged
        if account_manager.current_account:
            account_manager.mark_challenge(account_manager.current_account["id"])
        
        return jsonify({"error": str(e)}), 500

@app.route('/scrape/school', methods=['POST'])
def scrape_school():
    """Scrape LinkedIn school from URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        url_type, linkedin_id = extract_linkedin_id(url)
        
        if url_type != 'school':
            return jsonify({"error": "Invalid LinkedIn school URL"}), 400
        
        # Get LinkedIn API instance
        api = account_manager.get_api()
        if not api:
            return jsonify({"error": "No available LinkedIn accounts"}), 503
        
        # Scrape school
        school_data = api.get_school(linkedin_id)
        
        # Update account usage
        if account_manager.current_account:
            account_manager.mark_request(account_manager.current_account["id"])
        
        return jsonify({
            "success": True,
            "data": school_data,
            "account_used": account_manager.current_account["id"] if account_manager.current_account else None
        })
        
    except Exception as e:
        logger.error(f"Error scraping school: {e}")
        # Mark account as potentially challenged
        if account_manager.current_account:
            account_manager.mark_challenge(account_manager.current_account["id"])
        
        return jsonify({"error": str(e)}), 500

@app.route('/convert/urn-to-url', methods=['POST'])
def urn_to_url():
    """Convert LinkedIn URN to URL"""
    try:
        data = request.get_json()
        if not data or 'urn' not in data:
            return jsonify({"error": "URN is required"}), 400
        
        urn = data['urn']
        url = convert_urn_to_url(urn)
        
        if not url:
            return jsonify({"error": "Invalid URN format"}), 400
        
        return jsonify({
            "success": True,
            "urn": urn,
            "url": url
        })
        
    except Exception as e:
        logger.error(f"Error converting URN to URL: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/convert/url-to-urn', methods=['POST'])
def url_to_urn():
    """Convert LinkedIn URL to URN"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        url_type, linkedin_id = extract_linkedin_id(url)
        
        if not url_type or not linkedin_id:
            return jsonify({"error": "Invalid LinkedIn URL"}), 400
        
        # Map URL types to URN formats
        urn_patterns = {
            'profile': f'urn:li:person:{linkedin_id}',
            'company': f'urn:li:company:{linkedin_id}',
            'school': f'urn:li:school:{linkedin_id}'
        }
        
        urn = urn_patterns.get(url_type)
        
        return jsonify({
            "success": True,
            "url": url,
            "urn": urn,
            "type": url_type
        })
        
    except Exception as e:
        logger.error(f"Error converting URL to URN: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
