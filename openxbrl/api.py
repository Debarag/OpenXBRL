"""
Main access point for OpenXBRL api
"""
from openxbrl import AccountingParser, Downloader
import os

class OpenXBRL() :

    def __init__(self, base_dir : str ) :
        """
        Initialization requires pointing to a base directory.
        This folder will hold filings data.
        """
        self._base_dir = base_dir

    
    def get_filing_accounting( self, cik : int, fiscal_year : int, fiscal_quarter : int ) -> dict :
        """
        Return dict with accounting fields parsed from a corporate filing.
        Parameters: 
            cik             : CIK identifier of the company
            fiscal_year     : Fiscal year of the filing
            fiscal_quarter  : Fiscal quarter of the filing. 
                            NOTE: Use fiscal_quarter = 0 to get the annual (10-K) filing
        """
        workingdir = os.path.join(self._base_dir, 'companyfacts/')
        downloader = Downloader()
        parser     = AccountingParser( workingdir )
        filename   = downloader.get_companyfacts(cik=cik, workingdir=workingdir)
        
        result  = parser.parse_file( filename )
        filings = result['filings']

        # Look for filing. Rem index=(fy_year,fy_quarter,form)
        if( fiscal_quarter == 0 ) :
            form = '10-K'
        else :
            form = '10-Q'
        filing = filings.get((fiscal_year, fiscal_quarter, form))
        if( filing == None ) :
            form += '/A'    # look for amended
            filing = filings.get((fiscal_year, fiscal_quarter, form))
        
        if( filing != None ) :
            filing['CIK'] = cik
            filing['entityName'] = result['entityName']

        return filing
