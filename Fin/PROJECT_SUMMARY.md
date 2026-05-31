# AEGIS INTENT ORACLE — Project Summary

**Tagline:** The risk oracle DeFi bots pay to trust — and retail users can't afford to ignore.

---

## What It Is

An AI-powered DeFi risk oracle that scores 200+ liquidity pools across **Base, Solana, Monad, and Sui** in real-time. It guides users to the best yield strategies through a conversational chatbot — not a wall of numbers.

## The Problem

Retail DeFi users make deposit decisions using Google and gut feeling. They see "18% APY" but miss the funding rate collapse, the anonymous admin multisig, or the 2-year-old audit on changed code. **$2B+ lost to exploits in 2023 alone.** No tool warns them *before* they deposit.

## How It Works

### Data Engine
- Pulls live pool data from **DeFiLlama API** (yields + protocols)
- Filters: 4 target chains, TVL > $1M, deduped by project/chain/symbol
- Categorizes assets: **Stable** (USDC, USDT, DAI, etc.) vs **Volatile** (BTC, ETH, SOL, MON, SUI) vs **LP pairs**
- Computes a **Risk Point (max 2.0)** per pool combining protocol dominance ranking + TVL quartile positioning

### AI Chatbot Flow
1. **"What asset do you want to hold?"** → Stable or Volatile
2. **Stable** → Shows ranked table of stable strategies (by APY, TVL, Risk Point)
3. **Volatile** → Asks which asset (BTC/ETH/SOL/MON/SUI) → Asks full or partial position
   - **Full position** → Recommends lending/staking strategies for that asset
   - **Partial position** → Recommends LP pools (e.g., BTC-USDC) for yield + stability

### 5-Pillar Risk Score (0–80)
| Pillar | Measures |
|--------|----------|
| 🔒 Smart Contract | Audit tier, mainnet age, bug bounty, exploit history |
| 💧 Liquidity | TVL depth, utilization, exit liquidity |
| 🏛️ Governance | DAO + timelock > multisig > EOA admin |
| 📈 Yield Quality | Real fees vs. token emissions vs. suspicious APY |
| 🪙 Asset Risk | Peg risk, correlation, impermanent loss |

**≥72 = PASS** · **48–71 = WARNING** · **<48 = REJECT (blocked)**

## Revenue Model

| Stream | Who Pays | Price |
|--------|----------|-------|
| B2C Retail | Users requesting Deep Analysis | 0.001 USDC/call |
| B2B M2M | Trading bots via **x402 protocol** | 0.001 USDC/API call |

No subscriptions. No API keys. Bots pay per-call in USDC via HTTP 402 → payment → 200 OK. Self-enforcing.

## Tech Stack

- **Backend:** Python FastAPI + DeFiLlama API + LLM (risk scoring + chat)
- **Frontend:** Next.js + React + TypeScript
- **Blockchain:** Base Sepolia (USDC payment rail)
- **Intelligence:** Tavily AI (live news search) + LLM synthesis
- **Execution:** Enso Finance (cross-protocol deposit routing)

## Key Differentiators

1. **Not a chatbot** — it's an oracle that scores like an institutional risk desk
2. **Not mock data** — every APY/TVL is live from DeFiLlama at query time
3. **Not B2C only** — x402 enables machine-to-machine payments with zero friction
4. **Kill Switch** — if news detects "hack/exploit/depeg", the transaction is blocked regardless of passing score

---

