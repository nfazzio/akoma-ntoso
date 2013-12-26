from lxml import etree
from lxml.builder import E
import urllib2
import re
from os import path
import argparse
import sys
import string
import requests

api_url='http://congress.api.sunlightfoundation.com/bills?'
api_key= open('api_key.txt').read().rstrip()
bill_id = ("hr4310-112")

def main(argv):
    bill_id = argv
    print bill_id
    url = "http://www.gpo.gov/fdsys/pkg/BILLS-113hr1120rh/xml/BILLS-113hr1120rh.xml"
    
    source_tree = get_tree_from_url(url)
    
    akn_tree = generate_akn(source_tree)
    print etree.tostring(akn_tree, pretty_print=True)

def get_sunlight(parameters,bill_id):
    """Takes in a bill_id and a list of desired fields to return from the Sunlight Foundation API, and returns them"""
    url = 'http://congress.api.sunlightfoundation.com/bills'
    header = {'X-APIKEY':api_key}
    fields = {'fields':parameters, 'bill_id':bill_id}
    print header
    print fields
    json_response = requests.request('get', url, headers=header, data=fields).json()

    return json_response

def get_tree_from_url(url):
    """Returns an lxml tree from a url"""
    xml = urllib2.urlopen(url)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml, parser)
    return tree

def generate_akn(tree):
    """Take in an lxml tree and returns xml fitting akomaNtoso standards"""
    root = E('akomaNtosos', xmlns='http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD05')
    root.append(generate_meta(tree))

    return root

def generate_meta(tree):
    """Generates the meta portion of the xml"""
    meta = E("meta")
    
    meta.append(generate_identification(tree))
    '''
    generate_lifecycle(tree)
    generate_analysis(tree)
    '''
    meta.append(generate_references(tree))
    return meta
    

def generate_identification(tree):
    """Generates the identification portion of the meta"""
    identification = E("identification")

    for element in generate_frbr_work(tree):
        identification.append(element)
    '''
    identification.append(generate_frbr_expression)
    identification.append(generate_frbr_manifestation)
    '''
    return identification


def generate_frbr_work(tree):
    """Generates the FRBRWork portion of the identification"""
    #ontology path = /country/state/item(bill)/date/bill#
    '''
    EXAMPLE:
    <FRBRthis value="/us/california/bill/2010-12-06/4/main"/>
    <FRBRuri value="/us/california/bill/2010-12-06/4"/>
    <FRBRdate date="2010-12-06" name="Enactment"/>
    <FRBRauthor href="#assembly" as="#author"/>
    <FRBRcountry value="us"/>
   '''
    country = 'us'
    state = 'house'
    item = 'bill'
    #The "introduced on" date represents the original work's date
    date = get_sunlight('introduced_on', bill_id)['results'][0]['introduced_on']
    print date
    bill_number = get_bill_number(tree)

    frbr_work = E("FRBRWork")
    this = E("FRBRthis", value=string.join([country, state, item, date, bill_id, 'main'],"/"))
    frbr_work.append(this)
    frbr_work.append(E("FRBRuri"))
    frbr_work.append(E("FRBRdate"))
    frbr_work.append(E("FRBRauthor"))
    frbr_work.append(E("FRBRcountry"))
    return frbr_work


def get_bill_number(tree):
    """returns the bill's number"""
    #TODO legis-num
    bill_num = tree.find('.//legis-num').text
    bill_num = re.match('\d*',bill_num).group()
    print "bill_num: " + bill_num

    return bill_num
'''
def generate_frbr_expression(tree):

def generate_frbr_manifestation(tree):
'''
def generate_references(tree):
    """Returns the references portion of the meta"""
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
    """Returns an etree element containing TLCPerson tag with sponsor information"""
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
    """Returns a list of etree elements with containing TLCPerson tag with co sponsor information"""
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

def getFromDict(dataDict, mapList):
    """Retrieves nested values from a dictionary"""
    return reduce(lambda d, k: d[k], mapList, dataDict)

def set_up_parser():
    parser = argparse.ArgumentParser(description='generate akn xml for a bill')
    bill = parser.parse_args()
    return bill

if __name__ == "__main__":
    main(sys.argv[0])

