# %% [markdown]
# ## This reads the csv file and creates taxononies
# 
# This is for generating a rdf taxonomy from a csv file

# %% [markdown]
# Update the following values to setup a new taxonomy

# %%
import datetime

ontname = "cybersecurity" #change this to the name of the taxonomy
taxtype = "csdomain" #change this to the name of the schema
taxtypename  = "Cyber Security Domain" #change this to the display name of the schema
artclass = "article" #change this the specific class that inherits from skos:Concept (or just use a keyword)
artclassname = "Article" #change this the specific class that inherits from skos:Concept (or just use a keyword)
arttop = "articles" #change this the specific name of the top level concept for the articles
conclass = "keyword" #change this the specific class that inherits from skos:Concept (or just use a keyword)
conclassname  = "Cyber Security Keyword" #change this to the display name of the concepts
contop = "keywords" #change this the specific name of the top level concept for the keywords
dtoday = datetime.date.today()
CSVF = "./CSTax.csv" #change this to the name of the csv file to consume
TAXA = "./out_tax"+ str(dtoday) +".ttl" #change this to the output file to write the taxonomy to

# %% [markdown]
# Libraries

# %%
#!pip install rdflib

# %% [markdown]
# Imports

# %%
# import libraries
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, SKOS, OWL, PROV, XSD, SDO, DCTERMS
from utils import *

import csv

# %% [markdown]
# basic replacing info

# %%
#replacing function
REPLACEALL = str.maketrans({" ": "_", "(": "_", ")": "_", "&": "_and_", "|": "", "-": ""}) #this also replaces spaces with underscores

# %% [markdown]
# Namespaces & Prefixes

# %%
# READ these files

#Namespaces
ONT = Namespace("https://data.uc.edu.au/def/" + ontname + "/")
TAX = URIRef("https://data.uc.edu.au/def/" + taxtype)
ART = URIRef("https://data.uc.edu.au/def/" + ontname + "/" + artclass + "#")
ELE = URIRef("https://data.uc.edu.au/def/" + ontname + "/" + conclass + "#")

ARTC = URIRef(ART + arttop)
ELEC = URIRef(ELE + contop)

#BASEURI & IMPORTURI to add after serialization (this is specific for topbraid but doesn't stop other tools working as well)
BASEURI = "# baseuri: https://data.uc.edu.au/def/" + taxtype
IMPORTURI = "# imports: https://data.uc.edu.au/def/" + ontname



# %% [markdown]
# create the graph to build

# %%
# create a new graph
atax = Graph()
# bind the prefixes
bind_prefixes(atax)
atax.bind("ONT", ONT)

#create the conceptschmeme and top level 
atax.add((TAX, RDF.type, SKOS.ConceptScheme))
atax.add((TAX, SKOS.prefLabel, Literal(taxtypename)))

#articles top level
atax.add((ARTC, RDF.type, SKOS.Concept))
atax.add((TAX, SKOS.hasTopConcept, ARTC))
atax.add((ARTC, SKOS.prefLabel, Literal(artclassname)))

#keywords top level
atax.add((ELEC, RDF.type, SKOS.Concept))
atax.add((TAX, SKOS.hasTopConcept, ELEC))
atax.add((ELEC, SKOS.prefLabel, Literal(conclassname)))


# %%
# layout
# article title, article year, article author, term, synonym, definition, reference
# 

# %% [markdown]
# read the models CSV and create the triples needed

# %%
# Open and read the recipe taxonomy

with open(CSVF) as csvfile:
   #read the csv fields
   csv_reader = csv.reader(csvfile, delimiter=',')
   # keep track of the line count
   line_count = 0
   for line in csv_reader:
      #if the first line, this is the headings
      line_count += 1
      if line_count == 1: 
         pass
      else:
         #read and build the article detail
         # 1/2/3
         artval = line[1].strip().translate(REPLACEALL) + "_" + line[2].strip().translate(REPLACEALL)
         atax.add((URIRef(ART + artval), RDF.type, SKOS.Concept))
         atax.add((URIRef(ART + artval), SKOS.prefLabel, Literal(line[0])))
         atax.add((URIRef(ART + artval), DCTERMS.date, Literal(line[1])))
         atax.add((URIRef(ART + artval), DCTERMS.creator, Literal(line[2])))
         atax.add((URIRef(ART + artval), SKOS.broader, ARTC))
         
         #read and build the term detail
         eval = ""
         tval = line[3].strip().split("|")
         tcnt = len(tval) #get the number of terms
         lval = ""
         #get the main link
         for i in range(0,tcnt):
            eval = eval + tval[i].strip().translate(REPLACEALL)
         #get the parent - is the nested val one less than this one
         for i in range(0,tcnt-1):
            lval = lval + tval[i].strip().translate(REPLACEALL)
         
         atax.add((URIRef(ELE + eval), RDF.type, SKOS.Concept))
         atax.add((URIRef(ELE + eval), SKOS.prefLabel, Literal(tval[tcnt-1].strip().capitalize())))
         atax.add((URIRef(ELE + eval), SKOS.altLabel, Literal(line[3].strip())))
         atax.add((URIRef(ELE + eval), SKOS.definition, Literal(line[5].strip())))
         atax.add((URIRef(ELE + eval), SKOS.note, Literal(line[6].strip())))
         if lval == "":
            atax.add((URIRef(ELE + eval), SKOS.broader, ELEC)) #connect to the top level OR
            atax.add((URIRef(ELE + eval), SKOS.broader, URIRef(ART + artval))) #connect to the article
         else:
            atax.add((URIRef(ELE + eval), SKOS.broader, URIRef(ELE + lval))) #connect to the nested level
            
         #see if there is any synonym - only supports one
         sval = ""
         if line[4].strip() != "":
            sval = line[4].strip().translate(REPLACEALL)

         if sval != "":
             atax.add((URIRef(ELE + eval), SKOS.exactMatch, URIRef(ELE + sval))) #connect to the synonym
             atax.add((URIRef(ELE + sval), SKOS.exactMatch, URIRef(ELE + eval))) #connect backwards




# %% [markdown]
# Inital Graph Data

# %%

   
   # store it in a turtle file
   atax.serialize(TAXA, format="turtle")
   
   # open and add the base URI to the start of the file (from utils.py)
   add_pragmas_to_file(TAXA, BASEURI ) # + "\n" + IMPORTURI)

