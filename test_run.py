"""
Sample script to test and run downloaders and parsers.
"""

from openxbrl import Downloader, AccountingParser, OpenXBRL
import pandas

test_download   = False
test_parse      = True
test_getfacts   = False
test_tickers    = False
test_filing_PDF = False

openXBRL = OpenXBRL('./sec-data/')

if( test_filing_PDF ) :
  openXBRL.get_filing_as_pdf(1341439, 2023, 1, './sec-data/orcl_pdf.pdf')

if( test_tickers ) :
  downloader = Downloader(  )
  x = downloader.get_CIKs_from_tickers( ['MSFT', 'ORCL'])
  print( x )

if( test_download ) :
  downloader = Downloader(  )
  ciks      = [1750] # AAR Corp # [1341439, 34088]  # Oracle Corp, ExxonMobil
  forms     = ["10-K", "10-K/A", "10-Q", "10-Q/A"]
  from_date = '2022-01-01'
  to_date   = '2023-09-01'
  df = downloader.get_urls(ciks, forms, from_date, to_date)
  print(df)
  downloader.get_files(ciks, forms, from_date, to_date, workingdir='./sec-data/forms')

if( test_parse ) :
    outputfile = './sec-data/dataset.csv'
    # Assumes companyfacts.zip from SEC has been downloaded and unzipped
    # small test: 
    ciks = [1800]#[1750, 1341439, 34088, 28412] # AAR Corp, Oracle, ExxonMobil, Comerica
    Downloader().get_companyfacts(1800, './sec-data/companyfacts')
    ap   = AccountingParser('./sec-data/companyfacts/')
    # full set:
    # ciks = ap.get_CIK_list( 5000 )
    # larger set:
    ciks_set = set(ciks)
    tempciks = ap.get_CIK_list(1000)
    for i in range(0, len(tempciks), 36):
       ciks_set.add(tempciks[i])
    # ciks = list(ciks_set)
    ap.parse_files_to_csv( ciks=ciks, outputfile=outputfile)

    # Check by reading into dataframe
    df = pandas.read_csv(outputfile)
    print ( df )

if( test_getfacts ) :
  api        = OpenXBRL( './temp-data/')
  cik        = 1750 # 1341439 # Oracle Corp
  fy_year    = 2021
  fy_quarter = 0
  d = api.get_filing_accounting( cik, fy_year, fy_quarter )
  print (d)


