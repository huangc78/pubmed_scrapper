from pymed import PubMed
import pandas as pd
from tqdm import tqdm
import json

lr_pair_df = pd.read_table('human_lr_pair.txt')

pubmed = PubMed(tool="PubMedSearcher", email="myemail@ccc.com")
total_df = pd.DataFrame(columns=['title','abstract', 'doi'])

print('Scrapping...')
for r in tqdm(lr_pair_df.iloc, total=len(lr_pair_df)):
    # print(r.ligand_gene_symbol,r.receptor_gene_symbol)
    
    ## PUT YOUR SEARCH TERM HERE ##
    # search_term = '("Cell-Cell" OR "Cell Cell" OR "Cell") AND ("Interaction" OR "Communciation") AND "Ligand" AND "Receptor" AND {} AND {} AND (NOT ("Animals"[Mesh] NOT ("Animals"[Mesh] AND "Humans"[Mesh])))'.format(r.ligand_gene_symbol,r.receptor_gene_symbol)
    search_term = '"Ligand" AND "Receptor" AND {} AND {} AND (NOT ("Animals"[Mesh] NOT ("Animals"[Mesh] AND "Humans"[Mesh])))'.format(r.ligand_gene_symbol,r.receptor_gene_symbol)
    
    try:
        results = pubmed.query(search_term, max_results=1000)
    

        articleList = []
        articleInfo = []

        for article in results:
        # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
        # We need to convert it to dictionary with available function
            articleDict = article.toDict()
            articleList.append(articleDict)

        # Generate list of dict records which will hold all article details that could be fetch from PUBMED API
        for article in articleList:
        #Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list - thats article pubmedId
            pubmedId = article['pubmed_id'].partition('\n')[0]
            # Append article info to dictionary 

            if article['title'] is not None and article['abstract'] is not None and article['doi'] not in set(total_df['doi']):
                articleInfo.append({# u'pubmed_id':pubmedId,
                                   u'ligand_gene_symbol':r.ligand_gene_symbol,
                                   u'receptor_gene_symbol':r.receptor_gene_symbol,
                                   u'title':article['title'],
                                   # u'keywords':article['keywords'],
                                   # u'journal':article['journal'],
                                   u'abstract':article['abstract'],
                                   # u'conclusions':article['conclusions'],
                                   # u'methods':article['methods'],
                                   # u'results': article['results'],
                                   # u'copyrights':article['copyrights'],
                                   u'doi':article['doi'],
                                   # u'publication_date':article['publication_date'], 
                                   # u'authors':article['authors'],
                                   })

        # Generate Pandas DataFrame from list of dictionaries
        articles_df = pd.DataFrame.from_dict(articleInfo)
        # export_csv = df.to_csv (r'C:\Users\YourUsernam\Desktop\export_dataframe.csv', index = None, header=True) 

        #Print first 10 rows of dataframe
        # print(articlesPD.head(10))

        total_df = pd.concat([total_df, articles_df], ignore_index=True) 
        
    except:
        print("An exception occurred")

print('Finishing...')
with open('nanoGPT-cci.txt', 'w') as f:
    for r in tqdm(total_df.iloc, total=len(total_df)):
        f.write("{}, {}, {}".format(r.ligand_gene_symbol, r.receptor_gene_symbol, r.title))
        f.write('\n')
        f.write(r.abstract)
        f.write('\n')
        f.write('\n')

with open('GPT4ALL-cci.jsonl', 'w') as outfile:
    for r in tqdm(total_df.iloc, total=len(total_df)):
        entry = {
            "prompt": "{}, {}, {}".format(r.ligand_gene_symbol, r.receptor_gene_symbol, r.title),
            "response": r.abstract,
            "source": "PubMed doi: {}".format(r.doi)
        }
        
        json.dump(entry, outfile)
        outfile.write('\n')


