import urllib.request
import json

def safe_float(val):
    if val is None: return 0.0
    try: return float(val)
    except: return 0.0

def categorize_asset(symbol):
    symbol = str(symbol).upper()
    
    stables = ['USDC', 'USDT', 'DAI', 'USDS', 'PYUSD', 'AUSD', 'USDB', 'FRAX', 'LUSD', 'GHO', 'USCC', 'USDG', 'USD', 'BUCK']
    
    # 1. Handle LP Tokens (Contains '-')
    if '-' in symbol:
        parts = symbol.split('-')
        
        # Check stablecoin presence
        all_stable = True
        has_stable = False
        for part in parts:
            is_stable = any(stable in part for stable in stables)
            if not is_stable:
                all_stable = False
            if is_stable:
                has_stable = True
                
        if all_stable:
            return 'Stable'
            
        # If it's an LP but has no stablecoin, mark it for removal
        if not has_stable:
            return 'NonStableLP'
            
        # Prioritize the non-stable asset for the LP name
        main_asset = parts[0]
        for part in parts:
            if not any(stable in part for stable in stables):
                main_asset = part
                break
        
        # Clean up common wrapped/staked prefixes for cleaner LP names
        if main_asset in ['WBTC', 'CBBTC']: main_asset = 'BTC'
        elif main_asset in ['WETH', 'CBETH', 'WEETH']: main_asset = 'ETH'
        elif main_asset in ['WSOL', 'JITOSOL', 'MSOL', 'BSOL']: main_asset = 'SOL'
        elif main_asset in ['WMON']: main_asset = 'MON'
        
        return f"LP{main_asset}"
        
    # 2. Handle Stablecoins
    if any(stable in symbol for stable in stables):
        return 'Stable'
        
    # 3. Handle Major Single Assets
    if 'BTC' in symbol: return 'BTC'
    if 'ETH' in symbol: return 'ETH'
    if 'SOL' in symbol: return 'SOL'
    if 'SUI' in symbol: return 'SUI'
    if 'MON' in symbol: return 'MON'
    
    # Fallback to the original symbol
    return symbol

def fetch_defillama_specific_chains():
    print("Fetching protocol mappings from DeFiLlama...")
    protocols_url = "https://api.llama.fi/protocols"
    category_map = {}
    try:
        req_proto = urllib.request.Request(protocols_url)
        with urllib.request.urlopen(req_proto) as res_proto:
            protocols_data = json.loads(res_proto.read())
            for p in protocols_data:
                cat = p.get('category', 'Unknown')
                if cat == 'Yield Aggregator':
                    cat = 'Lending'
                category_map[p.get('slug')] = cat
    except Exception as e:
        print("Failed to fetch protocol categories:", e)

    print("Fetching pool data from DeFiLlama...")
    url = "https://yields.llama.fi/pools"
    req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read()).get('data', [])
            
            target_chains = ['solana', 'monad', 'base', 'sui']
            
            # Filter for the requested chains, TVL > 1M, and drop Liquidity Managers & RWA
            filtered_data = [
                pool for pool in data 
                if str(pool.get('chain', '')).lower() in target_chains
                and safe_float(pool.get('tvlUsd')) > 1000000
                and category_map.get(str(pool.get('project', '')), 'Unknown') not in ['Liquidity Manager', 'RWA']
            ]
            
            # Sort all of them by TVL descending
            filtered_data.sort(key=lambda x: safe_float(x.get('tvlUsd')), reverse=True)
            
            # Deduplicate by Project, Chain, and Symbol (keeps the one with highest TVL)
            seen = set()
            dedup_data = []
            for pool in filtered_data:
                key = (str(pool.get('project', '')), str(pool.get('chain', '')), str(pool.get('symbol', '')))
                if key not in seen:
                    seen.add(key)
                    dedup_data.append(pool)
            
            final_data = dedup_data
            
            allowed_assets = {'BTC', 'ETH', 'SOL', 'MON', 'SUI', 'Stable', 'LPBTC', 'LPETH', 'LPSOL', 'LPMON', 'LPSUI'}
            final_data = [pool for pool in final_data if categorize_asset(str(pool.get('symbol', 'N/A'))) in allowed_assets]
            
            import pandas as pd
            
            df_data = []
            for i, pool in enumerate(final_data, 1):
                project_slug = str(pool.get('project', 'N/A'))
                category = category_map.get(project_slug, 'Unknown')
                symbol = str(pool.get('symbol', 'N/A'))
                
                df_data.append({
                    "Rank": i,
                    "Category": category,
                    "Asset": categorize_asset(symbol),
                    "Project": project_slug,
                    "Chain": str(pool.get('chain', 'N/A')),
                    "Symbol": symbol,
                    "TVL": safe_float(pool.get('tvlUsd')),
                    "APY": safe_float(pool.get('apy'))
                })
                
            df = pd.DataFrame(df_data)
            
            # --- HELPER TO CALCULATE QUARTILE POINTS ---
            def calc_q_pts(rank, total):
                if total <= 0: return 0
                q = (rank - 1) / total
                if q < 0.25: return 100
                elif q < 0.50: return 75
                elif q < 0.75: return 50
                else: return 25
            
            # --- 1. CALCULATE PROTOCOL POINTS ---
            protocol_tvl = df.groupby(['Chain', 'Project'])['TVL'].sum().reset_index()
            protocol_tvl = protocol_tvl.sort_values(by=['Chain', 'TVL'], ascending=[True, False])
            protocol_tvl['Chain Rank'] = protocol_tvl.groupby('Chain')['TVL'].rank(method='min', ascending=False).astype(int)
            
            def calc_step_pts(rank, total):
                if total <= 0: return 0
                step = 100.0 / total
                return 100.0 - ((rank - 1) * step)
                
            proto_pts_map = {}
            for chain in protocol_tvl['Chain'].unique():
                chain_df = protocol_tvl[protocol_tvl['Chain'] == chain]
                num_prot = len(chain_df)
                for _, row in chain_df.iterrows():
                    proto_pts_map[(row['Chain'], row['Project'])] = calc_step_pts(row['Chain Rank'], num_prot)
                    
            df['Protocol Pts'] = df.apply(lambda r: proto_pts_map.get((r['Chain'], r['Project']), 0), axis=1)
            
            # --- 2. CALCULATE TVL QUARTER POINTS ---
            num_pools = len(df)
            df['TVL Quarter Pts'] = df['Rank'].apply(lambda r: calc_q_pts(r, num_pools))
            
            # --- 3. TOTAL RISK POINT ---
            df['Risk Point (max 2)'] = (df['Protocol Pts'] + df['TVL Quarter Pts']) / 100.0
            df = df.drop(columns=['Protocol Pts', 'TVL Quarter Pts'])
            
            print(f"\nFound {len(filtered_data)} total pools > $1M TVL across target chains.")
            print(f"Showing all {len(final_data)} deduplicated pools as DataFrame:")
            print("="*100)
            print(df.to_string(index=False))
            print("="*100)
            
            print(f"\nCategory Breakdown ({len(final_data)} pools):")
            print(df['Category'].value_counts().to_string())
            print("="*100)
            
            print("\nProtocol Rankings by Chain (based on curated pools TVL):")
            for chain in protocol_tvl['Chain'].unique():
                print(f"\n--- {chain.upper()} ---")
                chain_df = protocol_tvl[protocol_tvl['Chain'] == chain]
                num_protocols = len(chain_df)
                
                for _, row in chain_df.iterrows():
                    rank = row['Chain Rank']
                    points = calc_step_pts(rank, num_protocols)
                    tvl_formatted = f"${row['TVL']:,.0f}"
                    print(f"#{rank} {row['Project']} ({tvl_formatted}) - {points:.2f} Pts")
            print("="*100)
    except Exception as e:
        print("Failed to fetch from DeFiLlama:", e)

if __name__ == "__main__":
    fetch_defillama_specific_chains()
