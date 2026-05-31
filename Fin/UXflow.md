# Aegis-Intent AI Chatbot UX Flow

This document outlines the core User Experience (UX) flow for the Aegis-Intent AI Chatbot. The chatbot leverages data from the `defillama_API_data.py` pipeline to help users find the optimal financial tools and yield strategies across multiple chains based on their personal risk and asset preferences.

## 1. Landing & Chatbot Initiation
- **Action:** User lands on the Aegis-Intent WebApp.
- **Visuals:** Minimalist interface featuring the AI chatbot prominently.
- **Interaction:** The AI chatbot proactively engages the user by pre-typing or recommending the first question to kickstart the user journey.

## 2. Step 1: Asset Preference (The 1st Question)
- **Chatbot Prompt:** "What asset do you want to hold?"
- **User Options:** 
  1. **Stable Asset** (Assets pegged to $1, e.g., USDC, USDT, DAI, USDS, PYUSD, etc.)
  2. **Volatile Asset** (Non-pegged assets with price fluctuations)

## 3. Step 2: Strategy Branching

### Branch A: User Selects "Stable Asset"
- **Action:** The chatbot processes the request for stable yield.
- **Result:** The chatbot generates a concise dashboard/table summarizing the best available stablecoin strategies by filtering the data table from the `defillama_API_data.py` script specifically for rows where the "Asset" column contains a stable type of asset.
- **Ranking Criteria:** Strategies are ranked based on a combination of **APY**, **TVL (Total Value Locked)**, and **Risk Point**.
- **Next Step:** User reviews the table and selects a stable strategy to execute.

### Branch B: User Selects "Volatile Asset"
- **Chatbot Prompt:** "Which specific asset are you choosing?"
- **User Options:** BTC, ETH, SOL, MON, or SUI.
- **Action:** Once the user selects an asset (e.g., BTC), the chatbot asks a follow-up question regarding their position sizing.
- **Chatbot Prompt:** "Are you going to buy it all now, or not? (i.e., take a partial position, buying some while keeping some in stablecoins)"
- **User Options:**
  1. **Full Position** (Buy it all now)
  2. **Not Full Position / Partial** (Buy some, keep some stable)

#### Branch B1: User Selects "Not Full Position" (Partial)
- **Action:** The chatbot recognizes the user wants to limit risk or average in.
- **Recommendation:** The chatbot recommends an **LP (Liquidity Provider)** type of financial tool by filtering the data table from the `defillama_API_data.py` script specifically for rows where the "Asset" column contains the name of the volatile asset that the user answered (e.g., a BTC-USDC liquidity pool). This allows the user to earn yield while maintaining partial stablecoin exposure to reduce volatility.

#### Branch B2: User Selects "Full Position"
- **Action:** The chatbot recognizes the user wants maximum exposure to the selected asset.
- **Recommendation:** The chatbot recommends single-sided yield strategies, lending, or staking financial tools by filtering the data table from the `defillama_API_data.py` script specifically for rows where the "Asset" column contains the name of the volatile asset that the user answered (e.g., Lending BTC) to maximize returns on the held asset.

## 4. Execution & Portfolio Monitoring
- **Execution:** Once the user selects a recommended strategy (Stable, LP, or Single-Sided Volatile), the Aegis engine seamlessly routes the transaction for execution.
- **Monitoring:** The user is redirected to a personalized dashboard to track their real-time APY, invested TVL, and live Risk Score for the active positions.
