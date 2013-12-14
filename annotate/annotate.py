from lxml import etree
from lxml.builder import E
import urllib2
import re

def main():
    url = "http://www.gpo.gov/fdsys/pkg/BILLS-113hr1120rh/xml/BILLS-113hr1120rh.xml"
    source_tree = get_tree_from_url(url)
    
    akn_tree = generate_akn(source_tree)
    print etree.tostring(akn_tree, pretty_print=True)




def get_tree_from_url(url):
    xml = urllib2.urlopen(url)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml, parser)
    return tree

def generate_akn(tree):
    root = E('akomaNtosos', xmlns='http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD05')
    root.append(generate_meta(tree))

    return root

def generate_meta(tree):
    meta = E("meta")
    
    meta.append(generate_identification(tree))
    '''
    generate_lifecycle(tree)
    generate_analysis(tree)
    '''
    meta.append(generate_references(tree))
    return meta
    

def generate_identification(tree):
    identification = E("identification")
    '''
    identification.append(generate_frbr_work)
    identification.append(generate_frbr_expression)
    identification.append(generate_frbr_manifestation)
    '''
    return identification

'''
def generate_frbr_work(tree):
    #ontology path = /country/state/item(bill)/date/bill#
    # frbr_work = 
def generate_frbr_expression(tree):

def generate_frbr_manifestation(tree):
'''
def generate_references(tree):
    references = E('references', source='#somebody')
    references.append(get_sponsor(tree))
    for sponsor in get_cosponsors(tree):
        references.append(sponsor)
    return references
'''
def generate_publication():

def generate_lifecycle():
'''

def get_sponsor(tree):
    """returns an etree element containing TLCPerson tag with sponsor information"""
    sponsor_text = tree.find('.//sponsor').text
    sponsor_name = re.search('(Mr.|Mrs.|Ms.)? (?P<sponsor>[a-zA-Z]*)', sponsor_text).group('sponsor')
    ontology_path = '/ontology/person/akn/' + sponsor_name
    attributes = {
        'id': sponsor_name,
        'href': ontology_path,
        'showas': sponsor_name
    }
    #sponsor_element = make_tlc_element('TLCPerson', sponsor_name, ontology_path, sponsor_name)
    sponsor_element = E('TLCPerson', id=sponsor_name, href=ontology_path, showas=sponsor_name)
    return sponsor_element

def get_cosponsors(tree):
    """returns a list of etree elements with containing TLCPerson tag with co sponsor information"""
    cosponsors = []
    cosponsor_matches = tree.findall('.//cosponsor')
    for cosponsor_text in cosponsor_matches:
        print cosponsor_text
    for cosponsor_match in cosponsor_matches:
        cosponsor_name = re.search('(Mr.|Mrs.|Ms.)? (?P<cosponsor>[a-zA-Z]*)', cosponsor_match.text).group('cosponsor')
        ontology_path = '/ontology/person/akn/' + cosponsor_name
        cosponsor_element = E('TLCPerson', id=cosponsor_name, href=ontology_path, showas=cosponsor_name)
        cosponsors.append(cosponsor_element)
    return cosponsors

if __name__ == "__main__":
    main()

