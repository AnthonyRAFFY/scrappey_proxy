<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6295/6295417.png" width="100" />
</p>
<p align="center">
    <h1 align="center">SCRAPPEY_PROXY</h1>
</p>
<p align="center">
    <em>Flaresolverr alternative, using Scrappey.com</em>
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

## Quick Links

> - [ Overview](#overview)
> - [ Repository Structure](#repository-structure)
> - [ Installation](#installation)
> - [ License](#license)

---

## Overview

Replaces Flaresolverr by listening to the same port and parsing the requests the same way Flaresolverr would. 
Instead of doing all the bypassing work itself, the script simply delegate the task to scrappey.com and returns the necessary cookies and content.

As Cloudflare ``cf_clearance`` cookie is tied to a specific User-Agent and IP address, you need a public working forward proxy (Squid for example) where Scrappey.com requests will be redirected to.

The script has only been tested with Prowlarr, with an average of one request every 2 hours (which is the cf_clearance cookie lifespan). 

Feel free to test it with Jackett or any other tool and give your feedback.

---

## Repository Structure

```sh
└── scrappey_proxy/
    ├── Dockerfile
    ├── poetry.lock
    ├── pyproject.toml
    └── scrappey_proxy
        ├── flaresolverr.py
        ├── main.py
        ├── scrappey.py
        └── utils.py
```

---

## Installation

An amd64 docker image is available for Docker & Kubernetes installation.

You will need to provide the following environment variables :
  - ``PROXY_USERNAME``: Username of your forward proxy
  - ``PROXY_PASSWORD``: Password of your forward proxy
  - ``PROXY_INTERNAL_IP`` : Internal IP address of your forward proxy
  - ``PROXY_EXTERNAL_IP`` : External IP address of your forward proxy
  - ``PROXY_INTERNAL_PORT`` : Internal port of your forward proxy
  - ``PROXY_EXTERNAL_PORT`` : External port of your forward proxy
  - ``SCRAPPEY_API_KEY`` : API Key of your scrappey.com account

### Prowlarr configuration

Add two indexers proxies in "Settings" -> "Indexers" :
  - A flaresolverr proxy with the IP address of the machine the script is running on. You do not need to change the default port (8191).
  - An HTTP proxy, using ``PROXY_INTERNAL_IP`` as host, ``PROXY_INTERNAL_PORT`` as port, and ``PROXY_USERNAME``& ``PROXY_PASSWORD`` as credentials.

For each indexer proxies, set a tag and add it to the list of tags in your indexer configuration.

---

## License

This project is protected under the [GPL3-0](LICENSE) License. For more details, refer to the [LICENSE](LICENSE) file.

---
