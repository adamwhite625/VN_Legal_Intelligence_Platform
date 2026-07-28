# --- Stage 1: Build React app ---
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first for better layer caching
COPY frontend/package*.json ./
RUN npm install

# Copy source and build production bundle
COPY frontend/ .
RUN npm run build

# --- Stage 2: Serve with Nginx ---
FROM nginx:stable-alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Configure Nginx to listen on port 80, support SPA routing, and health checks
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /health { \
        return 200 "ok"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

