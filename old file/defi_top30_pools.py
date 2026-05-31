import urllib.request
import json
import pandas as pd

def safe_float(val):
    if val is None: return 0.0
    try: return float(val)
    except: return 0.0

def categorize_asset(symbol):
    symbol = str(symbol).upper()
    stables = ['USDC', 'USDT', 'DAI', 'USDS', 'PYUSD', 'AUSD', 'USDB', 'FRAX', 'LUSD', 'GHO', 'USCC', 'USDG', 'USD', 'BUCK']
    if '-' in symbol:
        parts = symbol.split('-')
        all_stable = all(any(s in p for s in stables) for p in parts)
        if all_stable:
            return 'Stable'
        main_asset = parts[0]
        for part in parts:
            if not any(s in part for s in stables):
                main_asset = part
                break
        if main_asset in ['WBTC', 'CBBTC']: main_asset = 'BTC'
        elif main_asset in ['WETH', 'CBETH', 'WEETH']: main_asset = 'ETH'
        elif main_asset in ['WSOL', 'JITOSOL', 'MSOL', 'BSOL']: main_asset = 'SOL'
        return f"LP{main_asset}"
    if any(s in symbol for s in stables): return 'Stable'
    if 'BTC' in symbol: return 'BTC'
    if 'ETH' in symbol: return 'ETH'
    if 'SOL' in symbol: return 'SOL'
    if 'SUI' in symbol: return 'SUI'
    if 'XRP' in symbol: return 'XRP'
    return symbol

# Protocols from defi_top30.md that ARE indexed in yields.llama.fi/pools
# Format: slug -> [chains to match (lowercase)]
TOP30_SLUGS = {
    'morpho-blue':          ['base', 'monad'],
    'aave-v3':              ['base'],
    'gauntlet':             ['base'],
    'uniswap-v3':           ['base'],
    'aerodrome-slipstream': ['base'],
    'navi-lending':         ['sui'],
    'aerodrome-v1':         ['base'],
    'multipli.fi':          ['base'],
    'uniswap-v2':           ['base'],
    'euler-v2':             ['monad'],
    'curvance':             ['monad'],
    'neverland':            ['monad'],
    'ember-protocol':       ['sui'],
    'cetus-clmm':           ['sui'],
    'upshift':              ['monad'],
    'scallop-lend':         ['sui'],
    'bluefin-spot':         ['sui'],
    'mu-digital':           ['monad'],
}

# Manual pools for protocols NOT in yields API
# TVL values from DeFiLlama protocol-level data; APY from official sites / web research
MANUAL_POOLS = [
    # Suilend — Lending (Sui) — total protocol TVL $153.93M split across assets
    {"Category": "Lending",       "Asset": "Stable", "Project": "suilend",        "Chain": "Sui",   "Symbol": "USDC",        "TVL": 80000000,  "APY": 5.50},
    {"Category": "Lending",       "Asset": "SUI",    "Project": "suilend",        "Chain": "Sui",   "Symbol": "SUI",         "TVL": 45000000,  "APY": 4.90},
    {"Category": "Lending",       "Asset": "ETH",    "Project": "suilend",        "Chain": "Sui",   "Symbol": "WETH",        "TVL": 28930000,  "APY": 2.80},
    # AFI Protocol — Yield Vaults (Base) — total $99.98M
    {"Category": "Yield",         "Asset": "Stable", "Project": "afi-protocol",   "Chain": "Base",  "Symbol": "afiUSD",      "TVL": 60000000,  "APY": 8.07},
    {"Category": "Yield",         "Asset": "Stable", "Project": "afi-protocol",   "Chain": "Base",  "Symbol": "afi-rwaUSDi", "TVL": 39980000,  "APY": 12.10},
    # Grove Finance — Yield Vault (Base) — total $78.98M; Sky Savings Rate
    {"Category": "Yield",         "Asset": "Stable", "Project": "grove-finance",  "Chain": "Base",  "Symbol": "sUSDS",       "TVL": 78980000,  "APY": 3.75},
    # AlphaLend — Lending (Sui) — total $67.16M
    {"Category": "Lending",       "Asset": "Stable", "Project": "alphalend",      "Chain": "Sui",   "Symbol": "USDC",        "TVL": 40000000,  "APY": 5.00},
    {"Category": "Lending",       "Asset": "SUI",    "Project": "alphalend",      "Chain": "Sui",   "Symbol": "SUI",         "TVL": 27160000,  "APY": 4.50},
    # SpringSui — Liquid Staking (Sui) — total $62.39M
    {"Category": "Liquid Staking","Asset": "SUI",    "Project": "springsui",      "Chain": "Sui",   "Symbol": "sSUI",        "TVL": 62390000,  "APY": 6.00},
    # Multipli.fi — Yield / RWA Vaults (Monad) — total $51.60M
    {"Category": "Yield",         "Asset": "Stable", "Project": "multipli-fi",    "Chain": "Monad", "Symbol": "rwaUSD",      "TVL": 51600000,  "APY": 12.00},
    # AFI Protocol — Yield Vaults (Monad) — total $49.98M (same product, cross-chain)
    {"Category": "Yield",         "Asset": "Stable", "Project": "afi-protocol",   "Chain": "Monad", "Symbol": "afi-rwaUSDi", "TVL": 49980000,  "APY": 12.10},
    # Haedal Protocol — Liquid Staking (Sui) — total $39.73M
    {"Category": "Liquid Staking","Asset": "SUI",    "Project": "haedal-protocol","Chain": "Sui",   "Symbol": "haSUI",       "TVL": 39730000,  "APY": 3.21},
    # Bucket Protocol — CDP stablecoin (Sui) — total $37.98M
    {"Category": "CDP",           "Asset": "SUI",    "Project": "bucket-protocol","Chain": "Sui",   "Symbol": "BUCK",        "TVL": 37980000,  "APY": 0.00},
    # K3 Capital — Risk Curator Vault (Monad) — total $36.45M; no public APY disclosed
    {"Category": "Yield",         "Asset": "ETH",    "Project": "k3-capital",     "Chain": "Monad", "Symbol": "WETH",        "TVL": 36450000,  "APY": 0.00},
    # Hyperithm — Institutional Yield Vault (Monad) — total $32.56M; USDC 6.69%
    {"Category": "Yield",         "Asset": "Stable", "Project": "hyperithm",      "Chain": "Monad", "Symbol": "USDC",        "TVL": 32560000,  "APY": 6.69},
]

def fetch_top30_pools():
    print("Fetching protocol categories from DeFiLlama...")
    category_map = {}
    try:
        req = urllib.request.Request("https://api.llama.fi/protocols")
        with urllib.request.urlopen(req) as res:
            for p in json.loads(res.read()):
                cat = p.get('category', 'Unknown')
                if cat == 'Yield Aggregator': cat = 'Lending'
                category_map[p.get('slug')] = cat
    except Exception as e:
        print("Warning: could not fetch categories:", e)

    print("Fetching pool data from DeFiLlama yields API...")
    api_pools = []
    seen = set()
    try:
        req = urllib.request.Request("https://yields.llama.fi/pools")
        with urllib.request.urlopen(req) as res:
            all_pools = json.loads(res.read()).get('data', [])

        for pool in all_pools:
            project = str(pool.get('project', '')).lower()
            chain   = str(pool.get('chain', '')).lower()
            tvl     = safe_float(pool.get('tvlUsd'))
            if tvl < 1000000:
                continue
            if project not in TOP30_SLUGS:
                continue
            if chain not in TOP30_SLUGS[project]:
                continue
            symbol  = str(pool.get('symbol', 'N/A'))
            key     = (project, chain, symbol)
            if key in seen:
                continue
            seen.add(key)
            cat = category_map.get(project, 'Unknown')
            api_pools.append({
                "Category": cat,
                "Asset":    categorize_asset(symbol),
                "Project":  project,
                "Chain":    pool.get('chain', 'N/A'),
                "Symbol":   symbol,
                "TVL":      tvl,
                "APY":      safe_float(pool.get('apy')),
            })
    except Exception as e:
        print("Warning: could not fetch yields pools:", e)

    all_rows = api_pools + MANUAL_POOLS
    all_rows.sort(key=lambda x: x['TVL'], reverse=True)

    df = pd.DataFrame(all_rows)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    print(f"\nTotal pools: {len(all_rows)}  "
          f"({len(api_pools)} from DeFiLlama API  +  {len(MANUAL_POOLS)} manually sourced)")
    print("="*120)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', 30)
    pd.set_option('display.width', 120)
    print(df.to_string(index=False))
    print("="*120)

    print("\nCategory Breakdown:")
    print(df['Category'].value_counts().to_string())
    print("="*120)

    print("\nChain Breakdown:")
    print(df['Chain'].value_counts().to_string())

    df.to_csv('defi_top30_live.csv', index=False)

if __name__ == "__main__":
    fetch_top30_pools()
