🛡️ Aegis-Intent: Master Blueprint (SEABW 2026 Hackathon)

The Autonomous Omni-Asset Retail Allocator & M2M Risk Oracle

1. Executive Summary (บทสรุปผู้บริหาร)

Vision: เปลี่ยนการใช้งาน Web3 จาก "Click-and-Trade" เป็น "Chat-to-Execute"

The Product: ระบบ AI ผู้จัดการกองทุนส่วนตัวสำหรับรายย่อย ที่จะประเมินความเสี่ยงเชิงลึก (ทั้ง On-chain และ Off-chain) ก่อนอนุญาตให้ลูกค้าย้ายเงินเข้าโปรโตคอล

Business Model (ทำเงินตั้งแต่วินาทีแรก):

B2C (Retail): เก็บค่าบริการ 0.5 USDC ต่อการจัดพอร์ต 1 ครั้ง ผ่านระบบ Smart Account (ERC-4337)

B2B (M2M): ขาย Data "Risk Score" ให้บอทตัวอื่นดึงไปใช้ ผ่านระบบ API Paywall (x402)

Sponsor Hook (AWS): สถาปัตยกรรมรันบน AWS 100% (Amplify, EC2, Secrets Manager) โชว์ความเป็น Enterprise-ready

2. System Architecture (สถาปัตยกรรมระบบ 2 เลเยอร์)

ระบบถูกออกแบบให้ครอบคลุมทั้ง UX สำหรับคนทั่วไป และ API สำหรับบอท:

               [ 🧑 Retail Users ]                 [ 🤖 AI/Trading Bots ]
                       |                                     |
           (Chat Interface / 1-Click)             (REST API Requests)
                       |                                     |
      +---------------------------------+   +---------------------------------+
      |       Layer 1: ERC-4337         |   |         Layer 2: x402           |
      |   Smart Account (Zero-Gas UX)   |   |   Pre-funded Credit Ledger L2   |
      +---------------------------------+   +---------------------------------+
                       |                                     |
                       +------------------+------------------+
                                          |
                                [ 🛡️ AEGIS BACKEND ]
                                [ Python FastAPI / EC2 ]
                                          |
        +-------------------------------------------------------------------+
        |                       🧠 Intelligence Layer                       |
        | - Supervisor Agent (OpenClaw / LangGraph)                         |
        | - Gemini 1.5 Pro (Semantic Reasoning & 5-Pillar Matrix)           |
        | - Data Normalizer (Standardize APIs to single JSON format)        |
        +-------------------------------------------------------------------+
             |                            |                            |
    [ 📊 Quantitative Data ]     [ 📰 Qualitative Data ]    [ ⚡ Execution Layer ]
    - 7-Platform APIs            - CryptoPanic API          - Enso Finance API
    - DeFiLlama API (Hub)        - (Mock Breaking News)     - Smart Contract Payload


3. Tech Stack & APIs (รายละเอียดการเชื่อมต่อข้อมูล)

A. Frontend & UX Layer

Framework: React / Next.js (ใช้ AI อย่าง Lovable.dev สร้างหน้า Dashboard + Chat UI)

Web3 Integration: ZeroDev หรือ Biconomy SDK สำหรับทำ ERC-4337 Smart Account (ให้ลูกค้า Deposit เงินก้อนเดียวตอนเริ่ม แล้วกด Sign อนุมัติ Session Key)

B. Backend & Agentic Layer

Framework: Python FastAPI

Agent Orchestrator: OpenClaw หรือ LangGraph

LLM: Gemini 1.5 Pro (เก่งเรื่อง Context ยาวและการทำ JSON Output)

C. Data Fetching APIs (The Omni-Asset Adapters)
เทคนิคสำหรับ Hackathon: เราจะใช้ DeFiLlama API (https://yields.llama.fi/pools) เป็น "Data Hub หลัก" เพื่อกวาดหา Base APY และ TVL ของทั้ง 7 หมวดหมู่ใน Request เดียว จากนั้น Agent ค่อยยิง API เจาะลึกเฉพาะทาง (Deep Metadata) ตามรายชื่อด้านล่างนี้เมื่อต้องการประเมิน Pillar 2 และ 3:

หมวด Lending (Morpho):

API: GraphQL (https://graphql.morpho.org)

Data to Fetch: ดึงรายชื่อ MetaMorpho Vaults, Net APY, และเจาะลึกชื่อ Curator (เช่น Block Analitica) เพื่อนำชื่อไปค้นหาข่าวความน่าเชื่อถือ

หมวด Yield Aggregator (Yearn V3):

API: yDaemon REST API (https://ydaemon.yearn.fi/1/vaults/all)

Data to Fetch: ดึง strategies ที่ซ้อนอยู่ข้างใน, ประวัติผลตอบแทน, และรายชื่อคนเขียนกลยุทธ์ (Strategists)

หมวด Yield Trading (Pendle):

API: Pendle V2 REST API (https://api-v2.pendle.finance/core/v1/1/markets)

Data to Fetch: ดึงค่า Fixed APY, Implied APY และ Maturity Date (วันหมดอายุ) [AI จะใช้เตือนลูกค้าถ้าระยะล็อกเงินนานเกินไป]

หมวด Perp DEX (Hyperliquid):

API: Hyperliquid Info API (https://api.hyperliquid.xyz/info) ยิง POST Payload {"type": "vaults"}

Data to Fetch: ดึงข้อมูล HLP Vaults, APR, และ Max Drawdown [ถ้า Drawdown สูง AI จะปรับตกใน Pillar 2 ทันที]

หมวด Restaking (Ether.fi):

API: ดึงผ่าน DeFiLlama API (Filter project = ether.fi)

Data to Fetch: TVL และ Reward APY [และใช้ LLM สแกนข่าวหาคำว่า "Slashed" ควบคู่กัน]

หมวด Real World Assets / RWA (Ondo):

API: ดึงผ่าน DeFiLlama API (Filter project = ondo-finance)

Data to Fetch: TVL ของ USDY [และใช้ LLM สแกนข่าว FED Interest Rate ควบคู่กัน]

หมวด Delta-Neutral (Ethena):

API: ดึงผ่าน DeFiLlama API (Filter project = ethena)

Data to Fetch: ค่า APY ของ sUSDe [AI จะประเมินร่วมกับสถานการณ์ Funding Rate ของตลาด]

D. The Semantic & Execution Tools

CryptoPanic API: ดึงข่าว 7 วันย้อนหลังของโปรโตคอล/Curator ที่ดึงมาจากด้านบน

Enso Finance API (https://api.enso.finance/api/v1/shortcuts/route): เมื่อ AI ตัดสินใจเลือกโปรโตคอลเสร็จ ระบบจะส่ง tokenIn, tokenOut (เช่น PT-eETH ของ Pendle) ไปหา Enso เพื่อรับ Calldata (Hex code) กลับมาให้ลูกค้ายืนยันการฝากเงินข้ามเชนได้ในคลิกเดียว

4. The 5-Pillar Omni-Asset Risk Matrix (หัวใจของระบบ)

นี่คือ System Prompt Logic ที่จะใช้ครอบ Gemini ให้ตัดสินใจแบบ Hedge Fund (บังคับ Output เป็น JSON)

Pillar 1: Smart Contract & Architecture Risk (20%)

20 pts: Mainnet > 1 year, Audited (Tier 1), Bug Bounty active.

10 pts: Audited but new (< 1 year) or standard fork.

0 pts: Unaudited, anon team, past exploits.

Pillar 2: Liquidity & Volatility Risk (20%) - [DYNAMIC CATEGORY]

Lending/RWA: 20 pts if TVL > $10M & Utilization < 85%. 0 pts if TVL < $1M or Utilization > 95%.

Perp DEX/Delta-Neutral: 20 pts if Max Drawdown (30d) < 2% & Funding Rate positive. 0 pts if negative funding consistently or Capital Flight > 20%.

Pillar 3: Operator & Counterparty Risk (20%) - [DYNAMIC CATEGORY]

DeFi Vaults (Morpho/Yearn): 20 pts if DAO/Public Curator with Timelock. 0 pts if EOA Anon admin.

RWA/Restaking: 20 pts if On-chain Proof of Reserve & No slashing history. 0 pts if Custodian bankrupt news or Node slashed.

Pillar 4: Semantic & Macro Risk (20%) - [THE KILL SWITCH]

20 pts: Positive/Neutral sentiment.

10 pts: Macro-concerns (e.g., FED rate changes affecting RWA).

0 pts (AUTO-REJECT): News context contains "Hack", "Exploit", "Depeg", "SEC Lawsuit", "Bankrupt".

Pillar 5: Risk-Adjusted Yield Justification (20%)

20 pts: APY 5-15% derived from Real Yield (Fees).

10 pts: APY 15-30% heavily subsidized by token emissions.

0 pts: APY > 50% with unclear mechanics (Ponzi/Yield Trap).

Execution Routing:

>= 80 (PASS): Call Enso API -> Generate Confirm Deposit button.

60 - 79 (WARNING): Show risk warnings -> Require Accept Risk checkbox -> Call Enso API.

< 60 OR Pillar 4 = 0 (REJECT): Block transaction. Explain why AI saved the user's money.

5. Monetization Workflow (ระบบทำเงิน Hybrid ERC-4337 + x402)

B2C (รายย่อย - เน้น UX):

ลูกค้า Deposit 10 USDC เข้า Smart Account (บน Base Chain)

อนุมัติ Session Key ให้ Aegis-Intent หักเงินได้ครั้งละ 0.5 USDC โดยไม่ต้องกด Sign (Metamask) อีก

ทุกครั้งที่รัน AI -> Backend ตัด Balance ใน Smart Account อัตโนมัติ

B2B (M2M x402 - เน้น Data Economy):

Trading Bot ของบริษัทอื่น โอน 5 USDC มาที่ Wallet ของแพลตฟอร์ม (Pre-funded)

Backend ตรวจจับ Tx Hash -> เติม 10 API Credits ลง Database

บอทยิง API ดึง JSON 5-Pillar Risk Score -> Backend ตัด Credit ทีละ 1 (Zero-gas data fetch)

เครดิตหมด -> Backend ตอบ HTTP 402 Payment Required

6. The "Aha! Moment" Demo Playbook (บทพรีเซนต์บนเวที)

เพื่อป้องกัน API ล่ม (Live-Demo Insurance): ให้เขียนโค้ด Fallback Payload เตรียมไว้สำหรับ 1 Protocol ที่มีผลลัพธ์การยิง Enso API ไว้แล้ว

เปิดฉาก: โชว์หน้าแชท พิมพ์คำสั่ง "ฉันมี 10,000 USDC อยากกระจายความเสี่ยงไป Lending และ Pendle ห้ามมีข่าวแฮ็ก"

โชว์ UX การจ่ายเงิน: แจ้งกรรมการว่าลูกค้าทำ Account Abstraction ไว้แล้ว ระบบจึงตัดเงิน 0.5 USDC เป็นค่าบริการได้ทันทีแบบ Background process

โชว์ Data Normalization: เปิด Terminal ให้กรรมการดู AI กำลังดึง Data จาก DeFiLlama และยิง GraphQL เจาะลึก Morpho และ Pendle API

The Plot Twist (ฉีด Mock News): คุณจงใจกดปุ่มลับใน UI เพื่อฉีดข่าวจำลองเข้าระบบ: "BREAKING: Morpho Curator 'Steakhouse' suspected of breach."

The AI Magic: หน้าจอโชว์คะแนน Pillar 4 ของ Morpho ร่วงจาก 20 เหลือ 0 ทันที! ระบบขึ้นสีแดง "TRANSACTION REJECTED" AI เปลี่ยนไปแนะนำ Yearn V3 แทน (โชว์ความฉลาดระดับสถาบัน)

The Execution: ลูกค้ากด [Confirm Deposit] -> ระบบเรียก Enso API คาย Payload -> จบการทำงาน (หรือโชว์ Hex Code ว่าพร้อมรันจริง)!

Closing Statement: "เราไม่ได้สร้างแชทบอท แต่เราสร้าง AI Hedge Fund ระดับสถาบันที่วิเคราะห์ข้าม 7 สินทรัพย์ ป้องกันพอร์ตรายย่อย และเก็บค่าบริการระดับ Micro-payment แบบ M2M นี่คือรากฐานของ Autonomous Finance ครับ"