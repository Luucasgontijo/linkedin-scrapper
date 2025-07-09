from flask import Flask, jsonify, request
from flask_cors import CORS
from linkedin_api import Linkedin
import logging
import os
from dotenv import load_dotenv
from account_manager import LinkedInAccountManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global LinkedIn Account Manager
account_manager = LinkedInAccountManager()

def urn_to_url(urn):
    """Convert LinkedIn URN to URL"""
    try:
        # Remove the 'urn:li:' prefix if present
        if urn.startswith('urn:li:'):
            urn = urn[7:]
        
        # Handle different types of URNs
        if urn.startswith('person:'):
            # Person URN: urn:li:person:ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU
            profile_id = urn.replace('person:', '')
            return f"https://www.linkedin.com/in/{profile_id}/"
        
        elif urn.startswith('company:'):
            # Company URN: urn:li:company:123456
            company_id = urn.replace('company:', '')
            return f"https://www.linkedin.com/company/{company_id}/"
        
        elif urn.startswith('organization:'):
            # Organization URN: urn:li:organization:123456
            org_id = urn.replace('organization:', '')
            return f"https://www.linkedin.com/company/{org_id}/"
        
        elif urn.startswith('school:'):
            # School URN: urn:li:school:123456
            school_id = urn.replace('school:', '')
            return f"https://www.linkedin.com/school/{school_id}/"
        
        elif urn.startswith('industry:'):
            # Industry URN: urn:li:industry:123456
            industry_id = urn.replace('industry:', '')
            return f"https://www.linkedin.com/company/industry/{industry_id}/"
        
        elif urn.startswith('skill:'):
            # Skill URN: urn:li:skill:123456
            skill_id = urn.replace('skill:', '')
            return f"https://www.linkedin.com/skills/skill/{skill_id}/"
        
        elif urn.startswith('post:'):
            # Post URN: urn:li:post:123456
            post_id = urn.replace('post:', '')
            return f"https://www.linkedin.com/posts/{post_id}/"
        
        elif urn.startswith('activity:'):
            # Activity URN: urn:li:activity:123456
            activity_id = urn.replace('activity:', '')
            return f"https://www.linkedin.com/posts/{activity_id}/"
        
        else:
            # Try to detect if it's a profile ID directly
            if len(urn) > 20 and not ':' in urn:
                return f"https://www.linkedin.com/in/{urn}/"
            else:
                return None
    
    except Exception as e:
        logger.error(f"Erro ao converter URN para URL: {e}")
        return None

def initialize_linkedin_api():
    """Initialize LinkedIn API connection with account rotation"""
    try:
        logger.info("Inicializando sistema de contas LinkedIn...")
        success = account_manager.initialize_api()
        if success:
            logger.info("Sistema de contas inicializado com sucesso!")
        else:
            logger.error("Falha na inicialização do sistema de contas")
        return success
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        return False

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "message": "LinkedIn Scraper API",
        "endpoints": {
            "profile": "/api/profile/<profile_id>",
            "profile_contact": "/api/profile/<profile_id>/contact",
            "profile_connections": "/api/profile/<profile_id>/connections",
            "company": "/api/company/<company_id>",
            "company_employees": "/api/company/<company_id>/employees",
            "search_people": "/api/search/people?keywords=<keywords>",
            "search_companies": "/api/search/companies?keywords=<keywords>",
            "urn_to_url": "/api/urn-to-url?urn=<urn>",
            "account_status": "/api/accounts/status"
        }
    })

@app.route('/api/urn-to-url')
def convert_urn_to_url():
    """Convert LinkedIn URN to URL"""
    try:
        urn = request.args.get('urn')
        if not urn:
            return jsonify({
                "status": "error",
                "message": "URN parameter is required"
            }), 400
        
        logger.info(f"Convertendo URN para URL: {urn}")
        url = urn_to_url(urn)
        
        if url:
            return jsonify({
                "status": "success",
                "data": {
                    "urn": urn,
                    "url": url
                }
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Unable to convert URN to URL. Unsupported URN format."
            }), 400
    
    except Exception as e:
        logger.error(f"Erro na conversão URN para URL: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/profile/<profile_id>')
def get_profile(profile_id):
    """Get LinkedIn profile data"""
    try:
        logger.info(f"Buscando perfil: {profile_id}")
        
        def fetch_profile():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.get_profile(profile_id)
        
        profile = account_manager.execute_with_retry(fetch_profile)
        
        return jsonify({
            "status": "success",
            "data": profile
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar perfil {profile_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/profile/<profile_id>/contact')
def get_profile_contact(profile_id):
    """Get LinkedIn profile contact information"""
    try:
        logger.info(f"Buscando informações de contato: {profile_id}")
        
        def fetch_contact():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.get_profile_contact_info(profile_id)
        
        contact_info = account_manager.execute_with_retry(fetch_contact)
        
        return jsonify({
            "status": "success",
            "data": contact_info
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar contato {profile_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/profile/<profile_id>/connections')
def get_profile_connections(profile_id):
    """Get LinkedIn profile connections"""
    try:
        logger.info(f"Buscando conexões: {profile_id}")
        
        def fetch_connections():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.get_profile_connections(profile_id)
        
        connections = account_manager.execute_with_retry(fetch_connections)
        
        return jsonify({
            "status": "success",
            "data": connections
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar conexões {profile_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/company/<company_id>')
def get_company(company_id):
    """Get LinkedIn company data"""
    try:
        logger.info(f"Buscando empresa: {company_id}")
        
        def fetch_company():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.get_company(company_id)
        
        company = account_manager.execute_with_retry(fetch_company)
        
        return jsonify({
            "status": "success",
            "data": company
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar empresa {company_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/company/<company_id>/employees')
def get_company_employees(company_id):
    """Get LinkedIn company employees"""
    try:
        logger.info(f"Buscando funcionários da empresa: {company_id}")
        
        def fetch_employees():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.get_company_employees(company_id)
        
        employees = account_manager.execute_with_retry(fetch_employees)
        
        return jsonify({
            "status": "success",
            "data": employees
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar funcionários da empresa {company_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/search/people')
def search_people():
    """Search for people on LinkedIn"""
    try:
        keywords = request.args.get('keywords', '')
        if not keywords:
            return jsonify({
                "status": "error",
                "message": "Keywords parameter is required"
            }), 400
        
        logger.info(f"Buscando pessoas: {keywords}")
        
        def search_people_func():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.search_people(keywords=keywords)
        
        results = account_manager.execute_with_retry(search_people_func)
        
        return jsonify({
            "status": "success",
            "data": results
        })
    
    except Exception as e:
        logger.error(f"Erro na busca de pessoas: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/search/companies')
def search_companies():
    """Search for companies on LinkedIn"""
    try:
        keywords = request.args.get('keywords', '')
        if not keywords:
            return jsonify({
                "status": "error",
                "message": "Keywords parameter is required"
            }), 400
        
        logger.info(f"Buscando empresas: {keywords}")
        
        def search_companies_func():
            api = account_manager.get_api()
            if not api:
                raise Exception("Falha ao obter instância da API")
            return api.search_companies(keywords=keywords)
        
        results = account_manager.execute_with_retry(search_companies_func)
        
        return jsonify({
            "status": "success",
            "data": results
        })
    
    except Exception as e:
        logger.error(f"Erro na busca de empresas: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/accounts/status')
def get_accounts_status():
    """Get status of all LinkedIn accounts"""
    try:
        status = account_manager.get_account_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        logger.error(f"Erro ao obter status das contas: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Initialize LinkedIn Account Manager on startup
    if initialize_linkedin_api():
        logger.info("Iniciando servidor Flask...")
        port = int(os.getenv('PORT', 8080))
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        logger.error("Falha na inicialização. Encerrando aplicação.")
