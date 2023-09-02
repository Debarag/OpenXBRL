# OpenXBRL
Access any sets of SEC financial filings in XBLR into structured and unstructured data form

Democratizing financial information access is the first step to an efficient and just market where all participants can access and understand key financial data related to publicly traded stocks.  
The SEC has mandated that all financial filings by regulated publicly traded stocks are done using the XBLR format, and such filings are made available for free using the SEC APIs to accesss the same.
However the structure of the SEC APIs, as well as the format of XBLR itself has been difficult enough that it has not yet enabled a free ecosystem of data access based on which developers, and the lay investor, can build further financial knowledge bases, analytics, and products.  So far the only available solutions for them have been via paid APIs provided by third parties -which impose a pricing barrier / efficiency cost to enable them.
This repo will be a Python SDK which will easily enable a developer to setup their access to SEC EDGAR filings that are in XBLR directly through the free SEC API, access and download them in the form they want, process basic transformations and harmonizations (e.g. combining all the revenue line items into the one most relevant etc.), and enable queries to be made across timespan and company tickers.
