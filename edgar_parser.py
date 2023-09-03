"""
Convert JSON files from Edgar into CSV.
Using the companyfacts.zip (all XBRL accounting data in SEC filings),
parse to find the accounting terms we want.
"""
import os
import json


class AccountingParser() :

    # Things we want for calculating our params
    _selected_parameters = [    'EntityPublicFloat'
                            ,   'Assets'
                            ,   'CurrentAssets'
                            ,   'CostsAndExpenses'
                            ,   'DebtCurrent'
                            ,   'DeferredIncomeTaxExpenseBenefit'
                            ,   'DeferredTaxAssetsLiabilitiesNet'
                            ,   'DividendsCommonStock'
                            ,   'EarningsPerShareBasic'
                            ,   'EarningsPerShareDiluted'
                            ,   'NetIncomeLoss'
                            ,   'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'
                            ,   'Liabilities'
                            ,   'LiabilitiesAndStockholdersEquity'
                            ,   'ProfitLoss'
                            ,   'GrossProfit'
                            ,   'OperatingIncomeLoss'
                            ,   'Revenues'
                            ,   'RevenueFromContractWithCustomerExcludingAssessedTax'
                            ,   'SellingGeneralAndAdministrativeExpense'
                            ,   'TreasuryStockCommonValue'
                            ]        

    # Columns to print to CSV
    _output_params  = [     '_Liabilities'
                       ,    '_Assets'
                       ,    '_Profits'
                       ,    '_Dividends'
                       ,    '_Revenues'
                       ,    '_Costs'
                       ,    '_EntityPublicFloat'
                       ]

    def __init__(self, workingdir : str ) :
        self._workingdir = workingdir


    def parse_file( self, filename : str ) -> dict :
        """
        Parse Edgar JSON file w/ accounting data
        Parameters:
            filename : the JSON file to read
        Returns :
            dict with CIK and other corp parameters
            and SEC filings in ['filings']
        """
        filename = os.path.join( self._workingdir, filename )
        with open(filename, "r") as f:
            data = json.load(f)

        entries = data['facts'].get('us-gaap')
        if( entries == None ) :
            entries = data['facts'].get('ifrs-full')
            if( entries == None ) :
                print( '[ERROR] CIK: {cik} does not have US-GAAP or IFRS-FULL data.')
                return None

        # STEP 1: Transform JSON to dict w/ filings
        filings = dict()

        cik         = data['cik']
        entityName  = data['entityName']

        # Add from facts.dei 
        entry = data['facts'].get('dei')
        if( entry != None ) :
            entry = data['facts']['dei'].get('EntityPublicFloat')
            if( entry != None ) :
                entries['EntityPublicFloat'] = entry

        # Restrict entries to things we want
        selected_parameters = AccountingParser._selected_parameters      
        for accounting_parameter in selected_parameters:
            
            entry = entries.get(accounting_parameter)
            if( entry == None ) :
                continue

            # TBD: Check for non-USD currency
            #  Also, some units are 'shares'; we ignore those
            if( entry['units'].get('USD') == None ) :
                continue
            units = entry['units']['USD']
            for item in units :
                form = item['form']
                # restrict to 10-X forms --> 10-Q, 10-K, 10-K/A
                if( form[0:2] != '10' ) :
                    continue

                fy_year = item['fy']
                # Remove bad data (there are some year=0 and other nonsense)
                if( (fy_year == None) or (fy_year == '') ) :
                    continue
                else :
                    fy_year = int(fy_year)
                if( (fy_year < 2009) or (fy_year > 2025) ) :
                    continue 
                
                fy_quarter = item['fp']
                if(   (fy_quarter == 'FY') or (fy_quarter == 'CY') 
                   or (fy_quarter == None) or (fy_quarter == ''  ) ) :
                    fy_quarter = 0
                else :
                    fy_quarter = int(fy_quarter[1:2])
                
                index = (fy_year,fy_quarter,form)
                value = item['val']
                
                row = filings.get(index)
                if( row == None ) :
                    new_q = fy_quarter
                    if( new_q == 0 ) :
                        new_q = 4       # Put yearly results in Q4
                    filings[index] = {  
                                        'FY_year'            : fy_year
                                     ,  'FY_quarter'         : fy_quarter 
                                     ,  'form'               : form 
                                     ,  'FY_date'            : f"{fy_year}Q{new_q}"
                                     ,  accounting_parameter : value
                                     }
                else : 
                    row[accounting_parameter] = value
        # end for

        # STEP 2: 
        # Go through form by form and calculate the accounting concepts we want
        
        MSG_NaN = "NaN"
        MSG_NA  = "NA"

        # Mapping between accounting concepts and fields
        #   Code will try to go down the list for each concept until it finds one
        HANDLING_FIELDS     = 0
        HANDLING_MISSING    = 1
        field_handling = { 
                            '_Liabilities'  : [['Liabilities', 'LiabilitiesAndStockholdersEquity'], MSG_NaN]
                        ,   '_Assets'       : [['Assets'], MSG_NaN]
                        ,   '_Profits'      : [['GrossProfit', 'ProfitLoss', 'OperatingIncomeLoss', 'NetIncomeLoss'], MSG_NaN]
                        ,   '_Revenues'     : [['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'], MSG_NaN]
                        ,   '_Costs'        : [['CostsAndExpenses'], MSG_NaN]

                        ,   '_Dividends'    : [['DividendsCommonStock', 'DividendsCommonStockCash'], 0]
                         }

        for ndx in filings.keys() :
            row = filings[ndx]

            for entry_name in field_handling.keys() :
                row[entry_name] = None
                for field_name in field_handling[entry_name][HANDLING_FIELDS] :
                    if( row.get(field_name) != None ) :
                        row[entry_name] = row[field_name]
                        break
                if( row[entry_name] == None ) :
                    row[entry_name] = field_handling[entry_name][HANDLING_MISSING]
                    if( row[entry_name] == MSG_NaN ) :
                        print (f"[Warning] CIK:{cik} Form:{row['form']} Year:{row['FY_year']} Quarter:{row['FY_quarter']} is missing {entry_name}")

            # Public float
            entry_name = '_EntityPublicFloat'
            if( row.get('EntityPublicFloat') != None ) :
                row[entry_name] = row['EntityPublicFloat']
            elif( row['form'].startswith("10-Q") ) :
                # 10-Q's don't have this value
                row[entry_name] = MSG_NA
            else :
                row[entry_name] = MSG_NaN
                print (f"[Warning] CIK:{cik} Form:{row['form']} Year:{row['FY_year']} is missing EntityPublicFloat")
       
        # end loop on accounting concepts

        # STEP 3: Impute certain quarterly data
        for ndx in filings.keys() :
            row = filings[ndx]

            # We modify the 10-K rows (these are the FY 4Q)
            if( not row['form'].startswith('10-K') ) :
                continue 
        
            fy_year = row[ 'FY_year' ]
            for series_name in [ '_Profits' ] :
                year_value  = row[ series_name ]
                
                # Keep old values as _actual
                row[ series_name + '_actual' ] = row[series_name]

                # impute quarterly value on this FY 10-K
                #  by subtracting the FY 10-Q values from the year's
                for q in range(1,4) :
                    q_row = filings.get((fy_year, q, '10-Q'))
                    if( q_row == None ) :
                        # try another form
                        q_row = filings.get((fy_year, q, '10-Q/A'))
                        if( q_row == None ) :
                            print( f"[Warning] Missing 10-Q form for CIK:{cik} FY_year:{fy_year} for quarter: {q}. Skipping year's {series_name}")
                            year_value = "NaN"
                            break
                    year_value -= q_row[series_name]

                # Overwrite w/ imputed value
                row[series_name] = year_value
        # end loop on imputation
                
        all = dict()
        all['CIK']          = cik
        all['entityName']   = entityName
        all['filings']      = filings
        return all
    # end parse_file


    def parse_files_to_csv( self, ciks : list, outputfile : str ) -> None :
        """
        Read files of CIKs in list, call .parse_file() on each one, and produce CSV
        Parameters: 
            ciks : list of CIKS to read. Filename in format 'CIK{cik:010}.json'
            outputfile : path (folder and filename) to write CSV to
        """
        progress_update_at = max(1, int(len(ciks)/50))
        cik_progress       = 0

        column_names = ['FY_year', 'FY_quarter', 'form', 'FY_date'] + AccountingParser._output_params
        with open(outputfile, "w") as f:
            s = '"CIK","entityName"'
            for param in column_names:
                s = s + f',"{param}"'
            print(s, file=f)  #header

            num_rows = 0
            for cik in ciks :
                filename = f"CIK{cik:010}.json"
                x        = self.parse_file( filename )
                base_s   = str(x['CIK']) + ',"' + x['entityName'] + '"'
                filings  = x['filings']
                for ndx in filings.keys() :
                    row = filings[ndx]
                    s   = base_s 
                    for c in column_names :
                        param = row[c]
                        if( type(param) == str ) :
                            s = s + f',"{param}"'
                        else :
                            s = s + f',{param}'

                    print(s, file=f)
                    num_rows += 1

                cik_progress += 1
                # Show progress
                if( cik_progress % progress_update_at == 0 ) :
                    print( f"Parsed {cik_progress} out of {len(ciks)}")

        print( f"Finished parsing. Total filings: {num_rows} ")


    def get_CIK_list( self ) -> list :
        """
        Read <working_dir>, find all CIK files, extract CIKs for big-enough files
        """
        MIN_SIZE = 1000 * 1024

        # Get list of all files only in the given directory
        func       = lambda x : os.path.isfile(os.path.join(self._workingdir, x))
        files_list = filter(func, os.listdir(self._workingdir))

        cik_list = list()
        for f in files_list :
            sz = os.stat(os.path.join(self._workingdir, f)).st_size
            if( sz > MIN_SIZE ) :
                cik = int(f[3:13])
                cik_list.append(cik)
        
        return cik_list
    

# end AccountingParser


