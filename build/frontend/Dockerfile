FROM node:22-alpine3.23

WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm ci

CMD ["npm", "start"]
