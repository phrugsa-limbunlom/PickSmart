# Use an official Node.js image
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Copy package files first to leverage caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 3000

ENV VITE_BACKEND_URL=http://localhost:8000

# Start the application
CMD ["npm", "start"]