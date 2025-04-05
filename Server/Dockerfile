FROM Node:22

WORKDIR /app
COPY package*.json ./
COPY . . 
RUN npm install
EXPOSE 5000
CMD ["node", "index.js"]