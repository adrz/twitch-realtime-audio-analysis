# Installation

```bash
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

# Run

```bash
source env/bin/activate
python main --url https://www.twitch.tv/zombiunicorn
```

# Docker

```bash
docker build -t alpine-custom:latest .
docker run -it alpine-custom:latest python main --url https://www.twitch.tv/zombiunicorn
```
