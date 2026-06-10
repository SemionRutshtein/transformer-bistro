# ── build stage ───────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


# ── serve stage ───────────────────────────────────────────────────────────────
FROM nginx:alpine AS runtime

COPY --from=builder /app/dist /usr/share/nginx/html
# Store as template; envsubst substitutes PORT and API_URL at container start
COPY frontend/nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

# nginx image automatically runs envsubst on *.template files
CMD ["nginx", "-g", "daemon off;"]
