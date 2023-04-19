import pandas as pd

def split_option_chain(chain: pd.DataFrame) -> list[pd.DataFrame]:
    index = chain.index
    chain_split_locs = [0]
    current_exp = str(index[0][1])[:10]

    for idx, tup in enumerate(index):
        if str(tup[1])[:10] != current_exp:
            chain_split_locs.append(idx)
            current_exp = str(tup[1])[:10]
    chain_split_locs.append(len(chain.index))

    return [
        chain.iloc[val:chain_split_locs[idx + 1]] for idx, val in enumerate(chain_split_locs[:-1])
    ]

def split_calls_puts(chain: pd.DataFrame) -> tuple[pd.DataFrame]:
    return (chain.filter(like='calls', axis=0), chain.filter(like='puts', axis=0))
