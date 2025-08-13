# Stage 1: Build Vue
FROM node:20 AS build
WORKDIR /app
COPY frontend/ /app
RUN npm install
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
