<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6295/6295417.png" width="100" />
</p>
<p align="center">
    <h1 align="center">SCRAPPEY_PROXY</h1>
</p>
<p align="center">
    <em>A Flaresolverr alternative using Scrappey.com</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/AnthonyRAFFY/scrappey_proxy?style=flat&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/AnthonyRAFFY/scrappey_proxy?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/AnthonyRAFFY/scrappey_proxy?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/AnthonyRAFFY/scrappey_proxy?style=flat&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
		<em>Developed with the software and tools below.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Poetry-60A5FA.svg?style=flat&logo=Poetry&logoColor=white" alt="Poetry">
	<img src="https://img.shields.io/badge/Gunicorn-499848.svg?style=flat&logo=Gunicorn&logoColor=white" alt="Gunicorn">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
	<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
	<img src="https://img.shields.io/badge/Flask-000000.svg?style=flat&logo=Flask&logoColor=white" alt="Flask">
</p>
<hr>

## 📋 Table of Contents

> - [Overview](#-overview)
> - [How it works](#-how-it-works)
> - [Architecture](#-architecture)
> - [Installation](#-installation)
> - [Configuration](#%EF%B8%8F-configuration)
> - [Usage examples](#-usage-examples)
> - [License](#-license)

---

## 🔍 Overview

**scrappey_proxy** is a drop-in replacement for FlareSolverr. It works with the exact same API as FlareSolverr, ensuring compatibility with your existing setup.

Instead of implementing Cloudflare bypass logic itself, it leverages Scrappey.com's bypassing capabilities while handling cookies and user-agent consistency.

The script uses approximately one cookie request every 2 hours (the typical cf_clearance cookie lifespan), which makes it a reliable and affordable solution.

The script has only been tested with Prowlarr, feel free to test it with Jackett or any other tool and give your feedback.

NOT all FlareSolverr functionalities have been implemented. It currently supports GET and POST requests, which should be enough for the majority of cases.

---

## 🧩 How it works

scrappey_proxy sits between your applications (like Prowlarr) and websites protected by Cloudflare, handling the challenge-solving process:

1. Your application sends a request to scrappey_proxy
2. scrappey_proxy checks if the site is protected by Cloudflare
3. If protected, scrappey_proxy forwards the request to Scrappey.com
4. Scrappey.com solves the challenge through its service
5. The request gets routed through your configured proxy to maintain IP consistency
6. scrappey_proxy receives the solution, saves cookies, and returns results
7. Future requests use saved cookies until they expire

This architecture ensures that both IP address and User-Agent remain consistent, which is crucial for Cloudflare bypass.

---

## 🏗 Architecture

The system consists of three main components working together:

### 1. scrappey_proxy Service
- Acts as a FlareSolverr-compatible API
- Detects Cloudflare protection
- Manages cookies and request routing
- Communicates with Scrappey.com

### 2. Scrappey.com Service
- Online Cloudflare bypass service
- Returns cookies and content

### 3. Your Forward Proxy (e.g., Squid)
- Provides a consistent external IP
- Routes Scrappey.com requests
- Maintains IP-based cookie validity

---

## 📦 Installation

### Docker

```bash
docker run -d \
  --name scrappey_proxy \
  -p 8191:8191 \
  -e PROXY_USERNAME="your_proxy_username" \
  -e PROXY_PASSWORD="your_proxy_password" \
  -e PROXY_INTERNAL_IP="proxy_internal_ip" \
  -e PROXY_EXTERNAL_IP="proxy_external_ip" \
  -e PROXY_INTERNAL_PORT="proxy_internal_port" \
  -e PROXY_EXTERNAL_PORT="proxy_external_port" \
  -e SCRAPPEY_API_KEY="your_scrappey_api_key" \
  anthonyraffy/scrappey_proxy:latest
```

### Kubernetes

Example manifests to come.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PROXY_USERNAME` | Username for your forward proxy |
| `PROXY_PASSWORD` | Password for your forward proxy |
| `PROXY_INTERNAL_IP` | Internal IP of your proxy (how scrappey_proxy connects to it) |
| `PROXY_EXTERNAL_IP` | External IP of your proxy (how Scrappey.com connects to it) |
| `PROXY_INTERNAL_PORT` | Internal port of your proxy |
| `PROXY_EXTERNAL_PORT` | External port of your proxy |
| `SCRAPPEY_API_KEY` | Your API key from Scrappey.com |

---

## ⚙️ Configuration

### Prerequisites

1. A working **forward proxy** (like Squid)
   - Must be accessible from both your server and the internet
   - Configured to allow authenticated access

2. A **Scrappey.com account** with an API key
   - Obtain your API key from your account dashboard

### Prowlarr Configuration

1. Go to **Settings** → **Indexers**
2. Add two proxies:
   - **FlareSolverr Proxy**:
     - Host: IP of your scrappey_proxy instance
     - Port: 8191 (default Flaresolverr port)
     - Tags: a tag like "scrappey"

   - **HTTP Proxy**:
     - Host: Your PROXY_INTERNAL_IP
     - Port: Your PROXY_INTERNAL_PORT
     - Username: Your PROXY_USERNAME
     - Password: Your PROXY_PASSWORD
     - Tags: a tag like "squid-proxy"

3. For each indexer that needs Cloudflare bypass:
   - Edit the indexer settings
   - Add both tags you created to the "Tags" field

### Jackett Configuration

Not tested with Jackett yet.

---

## 💡 Usage Examples

### Testing Your Setup

After installation, you can test if scrappey_proxy is working correctly:

```bash
curl -X POST http://localhost:8191/v1 \
  -H "Content-Type: application/json" \
  -d '{"cmd": "request.get", "url": "https://cloudflare-protected-site.com"}'
```

If successful, you should receive a JSON response with the page content and cookies.

### Common Request Pattern

The typical request structure follows FlareSolverr's format:

```json
{
  "cmd": "request.get",
  "url": "https://your-target-site.com",
  "maxTimeout": 60000
}

{
  "cmd": "request.post",
  "url": "https://your-target-site.com",
  "postData": "a=b&c=d",
  "maxTimeout": 60000
}
```

---

## 📄 License

This project is protected under the [GPL3.0](LICENSE) License. For more details, refer to the [LICENSE](LICENSE) file.

---
