# karma-epic

Empty React and Vite app, served as static assets by a Cloudflare Worker at `leoreche.com/placeholder-path`.

## Commands

| Command           | What it does                                 |
| ----------------- | -------------------------------------------- |
| `npm install`     | Install dependencies                         |
| `npm run dev`     | Local development with hot reload            |
| `npm run preview` | Build and serve through the Workers runtime  |
| `npm run deploy`  | Build and publish to Cloudflare from here    |

Local URL: `http://localhost:8080/placeholder-path/`

## Deploying

Cloudflare builds and deploys every push to `main`, using `npm run build` and `npx wrangler deploy`.

## Changing the path

Replace `placeholder-path` in:

| File             | Setting                              |
| ---------------- | ------------------------------------ |
| `vite.config.js` | `base`                               |
| `wrangler.jsonc` | `assets.base_path` and `routes`      |
| `README.md`      | The URLs above                       |
