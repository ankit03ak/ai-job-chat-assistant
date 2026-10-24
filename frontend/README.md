# AI Job Assistant frontend

## Local development

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` to the FastAPI origin. Gemini credentials remain
server-side and are never exposed to this app.

Validation commands:

```powershell
npm run typecheck
npm run lint
npm run build
```
