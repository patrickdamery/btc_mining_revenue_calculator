FROM node:20-bookworm
WORKDIR /app

# 1) Install pnpm as root
RUN npm install -g pnpm

# 2) Copy your lockfile and package.json first (for layer caching!)
COPY package.json pnpm-lock.yaml ./

# 3) Make /app owned by node, then switch
RUN chown -R node:node /app
USER node

# 4) As node, install dependencies
RUN pnpm install --frozen-lockfile

# 5) Copy the rest of your code (also owned by node)
COPY --chown=node:node . .

EXPOSE 3000
CMD ["./start.sh"]
