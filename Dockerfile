FROM node:20-alpine

WORKDIR /app

COPY . .
RUN npm ci --only=production

ENV NODE_ENV=production

EXPOSE 3000

CMD ["npm", "run", "start"]
