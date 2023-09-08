# Specs

1. Python package w/ all the standard things (e.g. make installable via pip)

2. Fool-proof operation: Basic access should be easy. Package should handle any 
needed contingencies--for example, dowload and unzip companyfacts.

3. API to extract all accounting concepts from filings. Filter by CIK and date. 
We only deal with 10-Qs and 10-Ks, so filter by form does not seem useful. Accounting
should clearly distinguish quarterly and annual (if appropriate) amounts. 
    (a) Accounting concepts mapped to basic financials (our value add)
    (b) API to also provide the actual filing concepts (why not)

4. API to extract the plaintext of a filing.

5. API to query filings (just a mapping to SEC API)

6. API to find CIK (SEC API has this, we think)


# Things to do
* Determine accounting concepts we want and find mappings for them. Put into JSON file.
    -- Income (or PnL) statement
        Revenue
            CostOfRevenue
            Gross Profit (this is revenue minus cost-of-revenue)
        Expenses
        NetIncome ( Profit )
        Earnings per Share (Basic & Diluted)
    -- Cashflow statement (TBD)
    -- Balance sheet (TBD)

* Identify handling of quarterly vs annual. Rem: 10-Ks have annual data so need to impute 4Q quarterly data.
Some data are stocks and don't need adjustment (e.g. Assets, Debt)

* For Spec (4) [Plaintext extraction], look at code in OpenEdgar repo. May be useful.

* Implement Spec (5) [Querying]

* Implement Spec (6) [Find CIK]