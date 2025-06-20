## Bitcoin Mining Revenue Calculator

I used nextjs-fastapi-template as starting point, see source [here](https://github.com/vintasoftware/nextjs-fastapi-template/)

This is a Revenue calculator that calculates how many ASICs you need to consume 1MWh for a modern list of ASICs. For each ASIC it then calculates how much revenue it would've generated for each block.

It has a small simple frontend that lets you visualize this.


## Tech Stack
Backend:
 - FastAPI
 - Postgres
 - Celery
 - Redis
Frontend:
 - Next.js

## Get Started

### Requirements
 - `docker`
 - `docker compose`
 - `make`

 ### Setup

In order to run this project you need to have a Bitcoin node with the RPC server enabled. The RPC server must accept connections from within the Docker container (Only accepts localhost by default). In order to enable this you must update your bitcoin.conf file so it includes the following lines:

```
rpcbind=0.0.0.0  # Bind the RPC server so it listens to requests from all ip addresses.
rpcallowip=172.0.0.0/8  # Whitelist the Docker network, I'm leaving this very wide to make sure it works out of the box for you, but you can narrow it down if you want to.

```

After making these changes you must restart your node.

Now navigate to fastapi_backend and move `.env.example` to `.env` in the backend. Then you must update `BTC_NODE_USER` and `BTC_NODE_PASS`, if you're not running your node locally then you'll also have to update `BTC_NODE_RPC_URL`.

Optionally you can choose to change `START_BLOCK_HEIGHT` if you wish to backfill data older than this block, I advise against doing this since this project uses CoinGecko's Public API which is throttled which makes the backfill very slow since I fetch the price of BTC at every block.

You must also navigate to nextjs-frontend and move `.env.example` to `.env`. No need to update anything here.

Now that you've done this you should be ready to get this going. To start up the project simply run:

`make`

You can now navigate to `http://localhost` to view the dashboard. Keep in mind celery will take 10 minutes before it starts backfilling data, and once finished it will check if there's a new block to add every 10 minutes.

## Design Overview.

This system is structured as a set of loosely-coupled, containerized services that collaborate over a private Docker bridge network (my_network). Each component has a single responsibility, enabling independent development, scaling, and deployment:

### 1. Frontend (Next.js)

 - **User interface & client-side routing** built in React/Next.js.

 - Reads the OpenAPI spec generated by the backend (via a shared volume) to drive client code generation and live API docs.

 - Communicates with the backend at http://backend:8000 (through nginx proxy) for data retrieval.

### 2. API Backend (FastAPI + PostgreSQL)

 - **FastAPI** serves JSON REST endpoints, defined via Pydantic schemas and dependency-injected, async SQLAlchemy sessions.

 - **PostgreSQL (v17)** holds 4 core tables:

   - `block_data` records each mined block’s timestamp, subsidy, fees, and network hash rate.

   - `exchange_rate` stores the closest available USD price at the block time.

   - `asics` stores a list of 3 modern ASICs and their attributes.

   - `mwh_revenue` stores how much revenue each group of ASICs would've made for each block.

 - Uses **SQLAlchemy’s async engine** over `asyncpg` for non-blocking DB access.

### 3. Asynchronous Processing (Celery + Redis)

 - **Celery-beat** schedules a single, recurring job every 10 minutes to match how frequently BTC tries to add a block.

 - **Celery-worker** executes the pipeline:

   1. Traverse the Bitcoin blockchain by following nextblockhash from the last stored block.

   2. Compute block subsidy and total fees via the coinbase transaction.

   3. Enrich each record with the closest‐in‐time BTC/USD price from CoinGecko, dynamically adjusting the query window based on public‐API granularity.

   4. Persist results into block_data and exchange_rate.

   5. Calculates the revenue each group of ASICs would've made for that block and saves this to mwh_revenue.

 - *Redis* acts as the broker and results backend, decoupling scheduling from execution and allowing horizontal scaling of workers.

### 4. Configuration & Secrets

 - All service endpoints (Postgres URL, Redis URL, Bitcoin RPC URL/credentials, Celery broker/backend) are injected via environment variables (or an `.env` file), making it easy to swap out dependencies or run different environments.

 - Pydantic’s `Settings` loads and validates them at startup, failing fast if anything is missing.

### 5. Local Development & Deployment

 - **Docker Compose** ties everything together:

   - Shared volumes for code (enabling hot-reload in dev) and for the OpenAPI JSON.

   - A single network for inter-service discovery by container name.

   - Individual services for frontend, backend, DB, broker, scheduler, and worker.

   - Nginx to tie frontend and backend into a single port.

Most of the work was centered around the Celery task that ingests the data. Considering my lack of work experience working on Bitcoin I considered it appropriate to fetch block data from a Bitcoin node instead of some API to demonstrate that I am able to interact with nodes and am eager to learn more about Bitcoin.

The celery task was setup so it would handle situations were a block might not have been found yet or more than one block might've been found since the last time the task ran.

## Trade-offs

Because I'm using CoinGecko's public api, there are a lot of constraints that I had to work around. This makes backfilling data quite slow since I need to make sure I do not exceed their rate limits.

Also the resolution of the price data available to me is not ideal, the further back in time I go the less resolution I get, which of course will impact the accuracy of the profitability calculation.

I recently learned that some blocks are actually completely empty, due to miners briefly using an empty block template to avoid including transactions from the previous block. I have not yet taken this particular edge case into consideration in my code.

## What would I add with more time?

If I had more time, I would spend more time decoupling the different parts of the data ingestion so I could speed up the backfill. For example, I could very quickly ingest all block data and in a seperate task I could query a a range of time in CoinGecko and tie that in to the block data in a seperate task.

Part of the reason I favored keeping everything together is that it provided me an opportunity to demonstrate composability and HOF in Python. Also with a paid subscription to CoinGecko this would be much faster as is.

I would've also liked to make the dashboard nicer, allowing you to compare multiple ASICs would've been a nice feature I could've added with more time.