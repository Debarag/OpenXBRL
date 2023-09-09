# OpenXBRL
Access any sets of SEC financial filings in XBRL into structured and unstructured data form

Democratizing financial information access is the first step to an efficient and just market where all participants can access and understand key financial data related to publicly traded stocks.  
The SEC has mandated that all financial filings by regulated publicly traded stocks are done using the XBRL format, and such filings are made available for free using the SEC APIs to accesss the same.
However the structure of the SEC APIs, as well as the format of XBRL itself has been difficult enough that it has not yet enabled a free ecosystem of data access based on which developers, and the lay investor, can build further financial knowledge bases, analytics, and products.  Many available solutions to access SEC data are via paid APIs provided by third parties. This pricing barrier imposes an efficiency cost and keeps more budget-constrained developers from having direct access to this public data.

This repo will be a Python SDK which will easily enable a developer to setup their access to SEC EDGAR filings that are in XBRL directly through the free SEC API, access and download them in the form they want, process basic transformations and harmonizations (e.g. combining all the revenue line items into the one most relevant etc.), and enable queries to be made across timespan and company tickers.
