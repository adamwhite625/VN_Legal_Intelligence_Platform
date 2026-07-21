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

# Configure Nginx to listen on port 8080 and support SPA routing
RUN echo 'server { \
    listen 8080; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
