import urllib.request
import json
import pandas as pd
import re

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
        if all_stable: return 'Stable'
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

MANUAL_POOLS = [
    {"Category": "Lending",       "Asset": "Stable", "Project": "suilend",        "Chain": "Sui",   "Symbol": "USDC",        "TVL": 80000000,  "APY": 5.50},
    {"Category": "Lending",       "Asset": "SUI",    "Project": "suilend",        "Chain": "Sui",   "Symbol": "SUI",         "TVL": 45000000,  "APY": 4.90},
    {"Category": "Lending",       "Asset": "ETH",    "Project": "suilend",        "Chain": "Sui",   "Symbol": "WETH",        "TVL": 28930000,  "APY": 2.80},
    {"Category": "Yield",         "Asset": "Stable", "Project": "afi-protocol",   "Chain": "Base",  "Symbol": "afiUSD",      "TVL": 60000000,  "APY": 8.07},
    {"Category": "Yield",         "Asset": "Stable", "Project": "afi-protocol",   "Chain": "Base",  "Symbol": "afi-rwaUSDi", "TVL": 39980000,  "APY": 12.10},
    {"Category": "Yield",         "Asset": "Stable", "Project": "grove-finance",  "Chain": "Base",  "Symbol": "sUSDS",       "TVL": 78980000,  "APY": 3.75},
    {"Category": "Lending",       "Asset": "Stable", "Project": "alphalend",      "Chain": "Sui",   "Symbol": "USDC",        "TVL": 40000000,  "APY": 5.00},
    {"Category": "Lending",       "Asset": "SUI",    "Project": "alphalend",      "Chain": "Sui",   "Symbol": "SUI",         "TVL": 27160000,  "APY": 4.50},
    {"Category": "Liquid Staking","Asset": "SUI",    "Project": "springsui",      "Chain": "Sui",   "Symbol": "sSUI",        "TVL": 62390000,  "APY": 6.00},
    {"Category": "Yield",         "Asset": "Stable", "Project": "multipli-fi",    "Chain": "Monad", "Symbol": "rwaUSD",      "TVL": 51600000,  "APY": 12.00},
    {"Category": "Yield",         "Asset": "Stable", "Project": "afi-protocol",   "Chain": "Monad", "Symbol": "afi-rwaUSDi", "TVL": 49980000,  "APY": 12.10},
    {"Category": "Liquid Staking","Asset": "SUI",    "Project": "haedal-protocol","Chain": "Sui",   "Symbol": "haSUI",       "TVL": 39730000,  "APY": 3.21},
    {"Category": "CDP",           "Asset": "SUI",    "Project": "bucket-protocol","Chain": "Sui",   "Symbol": "BUCK",        "TVL": 37980000,  "APY": 0.00},
    {"Category": "Yield",         "Asset": "ETH",    "Project": "k3-capital",     "Chain": "Monad", "Symbol": "WETH",        "TVL": 36450000,  "APY": 0.00},
    {"Category": "Yield",         "Asset": "Stable", "Project": "hyperithm",      "Chain": "Monad", "Symbol": "USDC",        "TVL": 32560000,  "APY": 6.69},
]

def fetch_live():
    category_map = {}
    try:
        req = urllib.request.Request("https://api.llama.fi/protocols")
        with urllib.request.urlopen(req) as res:
            for p in json.loads(res.read()):
                cat = p.get('category', 'Unknown')
                if cat == 'Yield Aggregator': cat = 'Lending'
                category_map[p.get('slug')] = cat
    except: pass

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
            if tvl < 1000000 or project not in TOP30_SLUGS: continue
            if chain not in TOP30_SLUGS[project]: continue
            symbol = str(pool.get('symbol', 'N/A'))
            key = (project, chain, symbol)
            if key in seen: continue
            seen.add(key)
            api_pools.append({
                "Category": category_map.get(project, 'Unknown'),
                "Asset":    categorize_asset(symbol),
                "Project":  project,
                "Chain":    pool.get('chain', 'N/A'),
                "Symbol":   symbol,
                "TVL":      tvl,
                "APY":      safe_float(pool.get('apy')),
            })
    except Exception as e:
        print("Warning:", e)

    all_rows = api_pools + MANUAL_POOLS
    return pd.DataFrame(all_rows)

def parse_md(path):
    rows = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('|') or line.startswith('| Rank') or line.startswith('|---') or line.startswith('| Category'):
                continue
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) < 7: continue
            try:
                rows.append({
                    "Category": parts[1],
                    "Asset":    parts[2],
                    "Project":  parts[3],
                    "Chain":    parts[4],
                    "Symbol":   parts[5],
                    "TVL":      float(parts[6].replace(',', '')),
                    "APY":      float(parts[7].replace(',', '')),
                })
            except: continue
    return pd.DataFrame(rows)

def compare(live_df, saved_df):
    key_cols = ['Project', 'Chain', 'Symbol']
    check_cols = ['Category', 'Asset', 'TVL', 'APY']

    live_df  = live_df.copy()
    saved_df = saved_df.copy()
    live_df['_src']  = 'LIVE'
    saved_df['_src'] = 'SAVED'

    merged = pd.merge(
        live_df, saved_df,
        on=key_cols, suffixes=('_live', '_saved'), how='outer', indicator=True
    )

    result_rows = []

    for _, row in merged.iterrows():
        status = row['_merge']

        if status == 'both':
            diffs = []
            for col in check_cols:
                lv = row.get(f'{col}_live')
                sv = row.get(f'{col}_saved')
                if col in ('TVL', 'APY'):
                    try:
                        if abs(float(lv) - float(sv)) > 0.01:
                            diffs.append(col)
                    except: pass
                else:
                    if str(lv) != str(sv):
                        diffs.append(col)

            if diffs:
                live_row = {
                    'Status': f'CHANGED ({", ".join(diffs)})',
                    'Source': 'LIVE',
                    'Category': row['Category_live'],
                    'Asset':    row['Asset_live'],
                    'Project':  row['Project'],
                    'Chain':    row['Chain'],
                    'Symbol':   row['Symbol'],
                    'TVL':      row['TVL_live'],
                    'APY':      row['APY_live'],
                }
                saved_row = {
                    'Status': f'CHANGED ({", ".join(diffs)})',
                    'Source': 'SAVED',
                    'Category': row['Category_saved'],
                    'Asset':    row['Asset_saved'],
                    'Project':  row['Project'],
                    'Chain':    row['Chain'],
                    'Symbol':   row['Symbol'],
                    'TVL':      row['TVL_saved'],
                    'APY':      row['APY_saved'],
                }
                result_rows.append(live_row)
                result_rows.append(saved_row)
            else:
                result_rows.append({
                    'Status': 'SAME',
                    'Source': 'LIVE',
                    'Category': row['Category_live'],
                    'Asset':    row['Asset_live'],
                    'Project':  row['Project'],
                    'Chain':    row['Chain'],
                    'Symbol':   row['Symbol'],
                    'TVL':      row['TVL_live'],
                    'APY':      row['APY_live'],
                })

        elif status == 'left_only':
            result_rows.append({
                'Status': 'NEW (live only)',
                'Source': 'LIVE',
                'Category': row.get('Category_live', ''),
                'Asset':    row.get('Asset_live', ''),
                'Project':  row['Project'],
                'Chain':    row['Chain'],
                'Symbol':   row['Symbol'],
                'TVL':      row.get('TVL_live', 0),
                'APY':      row.get('APY_live', 0),
            })

        elif status == 'right_only':
            result_rows.append({
                'Status': 'REMOVED (saved only)',
                'Source': 'SAVED',
                'Category': row.get('Category_saved', ''),
                'Asset':    row.get('Asset_saved', ''),
                'Project':  row['Project'],
                'Chain':    row['Chain'],
                'Symbol':   row['Symbol'],
                'TVL':      row.get('TVL_saved', 0),
                'APY':      row.get('APY_saved', 0),
            })

    df = pd.DataFrame(result_rows)

    # Sort: CHANGED pairs first (grouped), then NEW, then REMOVED, then SAME
    order = {'CHANGED': 0, 'NEW': 1, 'REMOVED': 2, 'SAME': 3}
    df['_sort'] = df['Status'].apply(lambda s: order.get(s.split(' ')[0], 9))
    df = df.sort_values(['_sort', 'Project', 'Chain', 'Symbol', 'Source']).drop(columns='_sort')
    df = df.reset_index(drop=True)
    df.insert(0, 'Rank', range(1, len(df) + 1))

    return df

def main():
    print("Fetching live data...")
    live_df = fetch_live()
    print(f"Live rows: {len(live_df)}")

    print("Reading saved markdown...")
    saved_df = parse_md("defi_top30_pools.md")
    print(f"Saved rows: {len(saved_df)}")

    print("\nComparing...\n")
    result = compare(live_df, saved_df)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', 30)
    pd.set_option('display.width', 150)

    changed = result[result['Status'].str.startswith('CHANGED')]
    new_rows = result[result['Status'].str.startswith('NEW')]
    removed  = result[result['Status'].str.startswith('REMOVED')]
    same     = result[result['Status'] == 'SAME']

    print(f"Summary: {len(changed)//2} changed  |  {len(new_rows)} new  |  {len(removed)} removed  |  {len(same)} unchanged")
    print("="*150)

    if not changed.empty:
        print("\n--- CHANGED (LIVE vs SAVED side by side) ---")
        print(changed.to_string(index=False))

    if not new_rows.empty:
        print("\n--- NEW (live only, not in saved md) ---")
        print(new_rows.to_string(index=False))

    if not removed.empty:
        print("\n--- REMOVED (in saved md, not in live) ---")
        print(removed.to_string(index=False))

    if not same.empty:
        print("\n--- UNCHANGED ---")
        print(same.to_string(index=False))

    print("="*150)

if __name__ == "__main__":
    main()
