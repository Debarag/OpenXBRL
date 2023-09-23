"""
Convert JSON files from Edgar into CSV.
Using the companyfacts.zip (all XBRL accounting data in SEC filings),
parse to find the accounting terms we want.
"""
import os
import json
import datetime 


class AccountingParser() :

    _MAPPED_SUFFIX = "_map_from"

    def __init__(self, workingdir : str ) :
        self._workingdir = workingdir

        # import field mappings, assume in JSON file in same dir as code
        jsonfile = os.path.join( os.path.dirname(__file__), 'concept_handling.json') 
        with open(jsonfile, "r") as f:
            self._concept_handling = json.load(f)

        # find concepts where we calculate/impute quarter's value
        self._concepts_to_calc_quarter = [key for key, value in self._concept_handling.items() if "calc_quarter" in value and value["calc_quarter"] is True]
        
        self._output_params = list()
        for m in self._concept_handling.keys():
            self._output_params.append( m )
            self._output_params.append( f"{m}{AccountingParser._MAPPED_SUFFIX}")

        self._filing_id_params =  [     'FY_year'
                                   ,    'FY_quarter'
                                   ,    'form'      
                                   ,    'FY_date'   
                                   ,    'CY_date'   
                                   ,    'CY_filing_date' 
                                   ,    'accession_num'
                                  ]


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

        for accounting_parameter in entries:
            
            entry = entries.get(accounting_parameter)

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

                # Assume all entries have same filing date
                filing_date = item['filed']

                # Calendar Year framing may not exist, if so impute 
                cy_frame = item.get('frame')
                if( (cy_frame == None) or (cy_frame == '') ) :
                    # impute from 'end' (end of period)
                    # back up date a bit (just in case reporting date goes a little past end-of-quarter)
                    d        = datetime.datetime.strptime(item['end'], '%Y-%m-%d') - datetime.timedelta(days=8)
                    cy_frame = f"{d.year}Q{(d.month - 1) // 3 + 1}"
                else :  # format is CYyyyyQqI
                    cy_frame = cy_frame[2:8]
                    if( (len(cy_frame)==5) or (len(cy_frame)==4) ) :
                        # frame is missing Q; try to fix
                        cy_year = int(cy_frame[0:5])
                        d = datetime.datetime.strptime(item['end'], '%Y-%m-%d') - datetime.timedelta(days=8)
                        if( cy_year == d.year ):
                            cy_frame = f"{d.year}Q{(d.month - 1) // 3 + 1}"
                        else :
                            if( item.get('start') != None ) :
                                d = datetime.datetime.strptime(item['start'], '%Y-%m-%d') 
                                if( cy_year == d.year ) :
                                    cy_frame = f"{d.year}Q4"
                            if( len(cy_frame) < 6 ) :
                                print (f"[Warning] CIK:{cik} Form:{form} Year:{fy_year} Quarter:{fy_quarter} Tag:{accounting_parameter} has CY_frame mismatch to end-of-period.")

                index = (fy_year,fy_quarter,form)
                value = item['val']
                
                filing = filings.get(index)
                if( filing == None ) :
                    # Create new filing record
                    new_q = fy_quarter
                    if( new_q == 0 ) :
                        new_q = 4       # Put yearly results in Q4
                    filings[index] = {  
                                        'FY_year'            : fy_year
                                     ,  'FY_quarter'         : fy_quarter 
                                     ,  'form'               : form 
                                     ,  'FY_date'            : f"{fy_year}Q{new_q}"
                                     ,  'CY_date'            : cy_frame
                                     ,  'CY_filing_date'     : filing_date
                                     ,  'accession_num'      : item['accn']
                                     }
                    filing = filings[index]

                # Add the parameter to the filing record
                filing[accounting_parameter] = value
        # end for 

        # STEP 2: 
        # Go through form by form and calculate the accounting concepts we want
        
        VALUE_NaN           = "NaN"
        VALUE_NotAvailable  = "NA"

        # Mapping between accounting concepts and fields
        #   Code will try to go down the list for each concept until it finds one
        concept_handling = self._concept_handling

        for ndx in filings.keys() :
            row = filings[ndx]

            for entry_name in concept_handling.keys() :
                row[entry_name] = None
                for field_name in concept_handling[entry_name]['map'] :
                    if( row.get(field_name) != None ) :
                        row[entry_name] = row[field_name]
                        row[f"{entry_name}{AccountingParser._MAPPED_SUFFIX}"] = field_name
                        break
                if( row[entry_name] == None ) :
                    row[entry_name] = concept_handling[entry_name]['on_missing']
                    row[f"{entry_name}{AccountingParser._MAPPED_SUFFIX}"] = "Not_Found"
                    if( row[entry_name] == VALUE_NaN ) :
                        print (f"[Warning] CIK:{cik} Form:{row['form']} Year:{row['FY_year']} Quarter:{row['FY_quarter']} is missing {entry_name}")

            # Public float
            entry_name = '_EntityPublicFloat'
            if( row.get('EntityPublicFloat') != None ) :
                row[entry_name] = row['EntityPublicFloat']
            elif( row['form'].startswith("10-Q") ) :
                # 10-Q's don't have this value
                row[entry_name] = VALUE_NotAvailable
            else :
                row[entry_name] = VALUE_NaN
                print (f"[Warning] CIK:{cik} Form:{row['form']} Year:{row['FY_year']} is missing EntityPublicFloat")
       
        # end loop on accounting concepts

        # STEP 3: Impute certain quarterly data
        for ndx in filings.keys() :
            row = filings[ndx]

            # We modify the 10-K rows (these are the FY 4Q)
            if( not row['form'].startswith('10-K') ) :
                continue 
        
            fy_year = row[ 'FY_year' ]
            for series_name in self._concepts_to_calc_quarter:
                year_value = row[ series_name ]
                if( year_value == VALUE_NaN ) :
                    continue
                
                # Keep old values as _annual
                row[ series_name + '_annual' ] = row[series_name]

                # impute quarterly value on this FY 10-K
                #  by subtracting the FY 10-Q values from the year's
                for q in range(1,4) :
                    # look for amended first
                    q_row = filings.get((fy_year, q, '10-Q/A'))
                    if( q_row == None ) :
                        q_row = filings.get((fy_year, q, '10-Q'))
                    if( (q_row == None) or ( q_row[series_name] == VALUE_NaN ) ) :
                        print( f"[Warning] Missing 10-Q form for CIK:{cik} FY_year:{fy_year} for quarter: {q}. Skipping year's {series_name}")
                        year_value = VALUE_NaN
                        break
                    else :
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


    def _csv_header(self) -> str :
        """
        CSV header fields
        """
        column_names = self._filing_id_params + self._output_params
        s = '"CIK","entityName"'
        for param in column_names:
            s += f',"{param}"'
        return s
    
    def _csv_filing(self, cik : int, entityName : str, filing_fields : dict ) -> str :
        """
        Takes output of parse_file() and returns CSV row
        """
        cols = self._filing_id_params + self._output_params
        s    = f'{cik},"{entityName}"'
        for c in cols :
            param = filing_fields[c]
            if( type(param) == str ) :
                s += f',"{param}"'
            else :
                s += f',{param}'
        return s


    def parse_files_to_csv( self, ciks : list, outputfile : str ) -> None :
        """
        Read files of CIKs in list, call .parse_file() on each one, and produce CSV
        Parameters: 
            ciks : list of CIKS to read. Filename in format 'CIK{cik:010}.json'
            outputfile : path (folder and filename) to write CSV to
        """
        progress_update_at = max(1, int(len(ciks)/50))
        cik_progress       = 0

        column_names = self._filing_id_params + self._output_params
        with open(outputfile, "w") as f:
            print(self._csv_header(), file=f)  #header

            num_rows = 0
            for cik in ciks :
                x = self.parse_file( f"CIK{cik:010}.json" )
                for ndx in x['filings'].keys() :
                    filing_fields = x['filings'][ndx]
                    s = self._csv_filing( cik, x['entityName'], filing_fields)                
                    print(s, file=f)
                    num_rows += 1
                cik_progress += 1
                # Show progress
                if( cik_progress % progress_update_at == 0 ) :
                    print( f"Parsed {cik_progress} out of {len(ciks)}")

        print( f"Finished parsing. Total filings: {num_rows} ")



    def get_CIK_list( self, min_size : int = 0 ) -> list :
        """
        Read <working_dir>, find all CIK files, extract CIKs for big-enough files
        Parameters: 
            min_size       : minimum size (in KB) of files
        """
        min_size   = min_size * 1024

        # Get list of all files only in the given directory
        func       = lambda x : os.path.isfile(os.path.join(self._workingdir, x))
        files_list = filter(func, os.listdir(self._workingdir))

        cik_list = list()
        for f in files_list :
            sz = os.stat(os.path.join(self._workingdir, f)).st_size
            if( sz > min_size ) :
                cik = int(f[3:13])
                cik_list.append(cik)
        
        return cik_list
    

# end AccountingParser


