# frontend_chat/Dockerfile

# Stage 1: Build the Next.js app
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Build the Next.js app
RUN npm run build

# (Optional) Export the app as a static site
# Uncomment the next line if you want to use static export
# RUN npm run export

# Stage 2: Serve the Next.js app
# If using server-side rendering
# FROM node:18-alpine AS production

# WORKDIR /app

# # Copy only necessary files from build stage
# COPY --from=build /app/package*.json ./
# COPY --from=build /app/.next ./.next
# COPY --from=build /app/public ./public

# # Install only production dependencies
# RUN npm install --production

# Expose the port Next.js runs on
EXPOSE 3000

# Start the Next.js server
CMD ["npm", "start"]
