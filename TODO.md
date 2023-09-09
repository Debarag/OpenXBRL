# Specs

1. Python package w/ all the standard things (e.g. make installable via pip)

2. Fool-proof operation: Basic access should be easy. Package should handle any 
needed contingencies--for example, dowload and unzip companyfacts. Also, maybe better
option is to have it access SEC API unless it finds companyfacts folder -- can suggest downloading 
for bulk access.

3. Python SDK with functions to extract all accounting concepts from filings. Filter by CIK and date. 
Accounting should clearly distinguish quarterly and annual (if appropriate) amounts. 
    (a) Accounting concepts mapped to basic financials (our value add)
    (b) Function to also provide the actual filing concepts (why not)

4. Python function to extract the plaintext of a filing.

5. Python function to query filings (just a mapping to SEC API)

6. Python function to find CIK (SEC API has this, we think)

7. The SEC.gov API access from these functions should take into consideration all kinds of restrictions and failure modes from that interface: e.g. there should be a rate-limiter consistent with SEC usage guidelines.  Also, should have checks, and retries, built in to ensure what was requested was actually what was downloaded


# Things to do
* Determine accounting concepts we want and find mappings for them. Put into JSON file.
    
    -- Income (or PnL) statement
        Revenue
            CostOfRevenue
            Gross Profit (this is revenue minus cost-of-revenue)
        Expenses
        NetIncome ( Profit )
        Earnings per Share (Basic & Diluted)
    
    -- Balance sheet
        Assets
            Cash and Cash equivalents
            Current Assets (includes cash)
            Longterm Assets (includes goodwill)
        Liabilities
            Short-term liabilities
            Long-term liabilities
            Stockholder equity
        (rem: Assets == Liabilities)
    
    -- Cashflow statement
        Net Income (matches from income statement)
        Cashflow from Operations
        Net cash from Financing activities
        Net cash from Investing
        Cash and cash equivalents (start of period; and end of period)

* Identify handling of quarterly vs annual. Rem: 10-Ks have annual data so need to impute 4Q quarterly data.
Some data are stocks and don't need adjustment (e.g. Assets, Debt)

* Map other XBRL tags as sub-items to concepts above. This is a tree which may have multiple levels.

* For Spec (4) [Plaintext extraction], look at code in OpenEdgar repo. May be useful.

* Implement Spec (5) [Querying]

* Implement Spec (6) [Find CIK]
