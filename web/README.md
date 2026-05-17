# SignalDesk Web

Next.js frontend test console for the industry intelligence backend.

## Run

```bash
npm install
npm run dev
```

Copy `.env.local.example` to `.env.local` if your backend is not on `http://127.0.0.1:8000`.

## Backend Proxy Routes

- `GET /api/health`
- `POST /api/query`
- `POST /api/report`
- `POST /api/crawl`
