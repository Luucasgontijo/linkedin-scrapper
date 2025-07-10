# LinkedIn Scraper API

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)
![REST API](https://img.shields.io/badge/REST-API-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![CORS](https://img.shields.io/badge/CORS-Enabled-4CAF50?style=for-the-badge&logo=web&logoColor=white)

</div>

A robust REST API for scraping LinkedIn profiles, companies, and schools with intelligent account rotation and challenge detection.

## 🚀 Features

- **🔄 Multi-Account Rotation**: Automatic rotation between multiple LinkedIn accounts
- **🛡️ Challenge Detection**: Smart detection and handling of LinkedIn challenges
- **👤 Profile Scraping**: Extract detailed profile information from LinkedIn URLs
- **🏢 Company Scraping**: Get comprehensive company data from LinkedIn company pages
- **🎓 School Scraping**: Retrieve educational institution information
- **📊 Account Management**: Real-time monitoring of account status and usage
- **🐳 Docker Ready**: Containerized deployment with Docker Compose
- **⚡ Rate Limiting**: Built-in request throttling and cooldown mechanisms

## 📋 Prerequisites

- Python 3.8+
- Valid LinkedIn account credentials
- Docker (optional, for containerized deployment)

## 🔧 Installation

### Option 1: Local Development

1. **Clone the repository**

```bash
git clone <repository-url>
cd linkedin-scrapper
```

2. **Create and activate virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure accounts**

```bash
# Edit accounts.json with your LinkedIn credentials
nano accounts.json
```

5. **Run the API**

```bash
python main.py
```

### Option 2: Docker Deployment

1. **Build and run with Docker Compose**

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8080`

## ⚙️ Configuration

### Accounts Configuration (`accounts.json`)

```json
{
  "accounts": [
    {
      "id": "account_1",
      "email": "your-email@gmail.com",
      "password": "your-password",
      "status": "active",
      "last_used": null,
      "challenge_count": 0,
      "blocked_until": null,
      "max_requests_per_hour": 100,
      "requests_count": 0,
      "requests_reset_time": null
    }
  ],
  "settings": {
    "rotation_strategy": "round_robin",
    "challenge_cooldown_minutes": 60,
    "max_challenge_retries": 3,
    "request_delay_seconds": 2,
    "retry_attempts": 3
  }
}
```

## 📡 API Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "message": "LinkedIn Scraper API is running"
}
```

### Account Status

```http
GET /accounts/status
```

**Response:**

```json
{
  "total_accounts": 1,
  "available_accounts": 1,
  "accounts": [
    {
      "id": "account_1",
      "status": "active",
      "challenge_count": 0,
      "requests_count": 10
    }
  ]
}
```

### Profile Scraping

```http
POST /scrape/profile
Content-Type: application/json

{
  "url": "https://www.linkedin.com/in/username/"
}
```

### Company Scraping

```http
POST /scrape/company
Content-Type: application/json

{
  "url": "https://www.linkedin.com/company/company-name/"
}
```

### School Scraping

```http
POST /scrape/school
Content-Type: application/json

{
  "url": "https://www.linkedin.com/school/university-name/"
}
```

## 🧪 Testing

### Using cURL

1. **Health Check**

```bash
curl http://localhost:8080/health
```

2. **Profile Scraping**

```bash
curl -X POST http://localhost:8080/scrape/profile \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/in/williamhgates/"}'
```

3. **Company Scraping**

```bash
curl -X POST http://localhost:8080/scrape/company \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.linkedin.com/company/microsoft/"}'
```

## 🔒 Security

- **Credentials Protection**: LinkedIn credentials are stored locally and never exposed
- **Rate Limiting**: Built-in protection against excessive requests
- **Challenge Handling**: Automatic detection and mitigation of LinkedIn challenges
- **Account Rotation**: Distributes load across multiple accounts

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build the image
docker build -t linkedin-scraper .

# Run with environment variables
docker run -d \
  --name linkedin-scraper \
  -p 8080:8080 \
  -v $(pwd)/accounts.json:/app/accounts.json \
  linkedin-scraper
```

## ⚠️ Important Notes

1. **LinkedIn Terms of Service**: Ensure compliance with LinkedIn's Terms of Service
2. **Rate Limits**: Respect LinkedIn's rate limits to avoid account restrictions
3. **Account Safety**: Use dedicated LinkedIn accounts for scraping
4. **Error Handling**: The API includes robust error handling and retry mechanisms

## 📝 License

This project is for educational purposes only. Please ensure compliance with LinkedIn's Terms of Service.

---

<div align="center">
Made with ❤️ for educational purposes
</div>
