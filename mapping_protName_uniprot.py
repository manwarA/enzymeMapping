import os
import pandas as pd
import requests

'''
The file (brenda_results_Enzymes_in_human2.csv) has been downloaded from BRENDA database regarding enzymes. However, it contains only the protein name (niether gene name
or any other IDs), thus making it very difficult to map.

'''

#read the file in Pandas df. It has only one column 
ezymes_brenda = pd.read_csv("../brenda_results_Enzymes_in_human2.csv",
                            sep = "\t", header = None, names = ["protein"], nrows = 5)

# lower/upper case cause problems
ezymes_brenda['protein'] = ezymes_brenda['protein'].str.lower()

# an empty list to holds all the df
enzymeData = []

'''
For the request query, the space in protein name should be replaced with "%20".
The link at "https://stackoverflow.com/questions/1634271/url-encoding-the-space-character-or-20"
says that you should encode space with %20 before the "?" and with "+" after the "?".
Here, it has been encoded with %20

The actual query should look like this:
https://rest.uniprot.org/uniprotkb/search?query=reviewed:true+organism_id:9606+AND+inositol%20oxygenase&format=tsv
'''

def nameBuilder(enzyme_name):
    # function to add %20 in the name instead of spaces for Uniprot query
    enzyme_name = enzyme_name.strip()
    if " " in enzyme_name:
        enzyme_name = enzyme_name.replace(" ", "%20")
    else:
        pass
    return enzyme_name

'''
Each request query returns text that has been converted to data frame for easy manipulation.
The function "query2df" takes two values as input:
    urltext : the output of requests.get().txt
    enzymeName : to distinguished the enzyme name in merged dataframe
'''

def query2df(urltext, enzyme_name):
    if urltext:
        urltext = urltext.split("\n")
        urltext = [urlt.split("\t") for urlt in urltext]
        urltext = [x for x in urltext if len(x) > 1 ] # There is an empty list at the end with len(x) ==1
        df = pd.DataFrame(urltext[1:], columns = urltext[0])
        df["enzymeName"] =enzyme_name
    else:
        print("Query did not generate any output")
    return df

# A counter for the completed list
completed_enzyme = 0

for i in range(0, ezymes_brenda.shape[0]):
    #This will loop through the df and get the enzyme names
    try:
        eN = ezymes_brenda.iloc[i, 0]
        #if space, it is replaced by "%20"
        eName = nameBuilder(eN)
        myquery = "https://rest.uniprot.org/uniprotkb/search?query=reviewed:true+organism_id:9606+AND+" +eName +"&format=tsv"
        geneInfo = requests.get(myquery).text
        # converting to df and appending the output to list
        enzymeData.append(query2df(geneInfo, eN))
        completed_enzyme = completed_enzyme + 1
        print("Remaining Enzymes :\t", ezymes_brenda.shape[0] - completed_enzyme)
    except:
        pass # pass is a bad practice, please avoid


#concat all the df into 1; pd.concat works on the list of dfs    
enzymeData2 = pd.concat(enzymeData, ignore_index = True)
'''
enzymeData2 may be messy, and it contains many empty lines, that could be removed by

enzymeData2 = enzymeData2[~enzymeData2["Entry Name"].isin(["Entry Name"])] 

enzymeData2 contains a column with "Entry Name"
Every requests query yileded multiple entries, at this momnet, all have been saved

'''
#save it to current directory
enzymeData2.to_csv("testfinalData.txt", sep = "\t", index = False)




