FROM node:20-alpine

WORKDIR /workspace/worker

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 4000

CMD ["npm", "run", "dev"]
