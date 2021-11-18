################################################
# utils.py is to support the manifest generator
# @Author - Simon Thompson (most code copied/updated from other SURROUND projects)
# @Date - 6/09/2021
################################################

from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, SKOS, OWL, PROV, XSD, SDO, DCTERMS

# Author 
SEMAIL = URIRef("mailto:simon@thompson-hq.net")
SNAME = Literal("Simon Thompson")

SOPBL = Namespace("https://data.surroundaustralia.com/def/standards-baseline#")
PROF = Namespace("http://www.w3.org/ns/dx/prof/")
ROLE = Namespace("http://www.w3.org/ns/dx/prof/role/")
TPSWA = Namespace("http://topbraid.org/swa#")
TPTEAM = Namespace("http://topbraid.org/teamwork#")

# URIs
DEV = URIRef("http://topbraid.org/metadata#UnderDevelopmentStatus")

#prefixes

prefixes = {
    # bind some standard prefixes
    "skos": SKOS,
    "owl": OWL,
    "prov": PROV,
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "sdo": SDO,
    "dct": DCTERMS,
    
    # bind the specific prefixes
    "swa": TPSWA,
    "teamwork": TPTEAM,
    "prof": PROF,
    "role": ROLE,
    "sopbl": SOPBL
}

# return the iri for the unit from the unit graph, but works for other graphs matching on the SKOS.altLabel
def get_vocab_uri(g: Graph, function_text: str) -> URIRef:
   #print("seeking {}".format(function_text))
   for s in g.subjects(predicate=SKOS.altLabel, object=Literal(function_text, datatype=XSD.string)):
      #print(s)
      return s

   return None
       
# bind the standard prefixes for all the graphs
def bind_prefixes(g: Graph):
   global prefixes
   for k, v in prefixes.items():
    g.bind(k, v)


# add in the pragmas - the baseURI and import statements at the top of the file
def add_pragmas_to_file(filename: str, pragmas: str):
   with open(filename,'r') as contents:
         savettl = contents.read()
   with open(filename,'w') as contents:
         contents.write(pragmas + '\n\n')
   with open(filename,'a') as contents:
         contents.write(savettl)


