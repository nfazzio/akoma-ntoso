from lxml import etree
from lxml.builder import E
import urllib2
import re
from os import path
import argparse
import sys
import string
import requests
import time

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
    root = E('akomaNtosos', xmlns='http://akomantoso.googlecode.com/svn/release/trunk/schema/akomantoso30.xsd')
    root.append(generate_meta(tree))

    return root

def generate_meta(tree):
    """Generates the meta portion of the xml"""
    meta = E("meta")
    
    meta.append(generate_identification(tree))
    
    meta.append(generate_lifecycle(tree))
    '''
    generate_analysis(tree)
    '''
    meta.append(generate_references(tree))
    return meta
    

def generate_identification(tree):
    """Generates the identification portion of the meta"""
    identification = E("identification")
    identification.append(generate_frbr_work(tree))
    #for element in generate_frbr_work(tree):
    #   identification.append(element)
    
    identification.append(generate_frbr_expression(tree))
    identification.append(generate_frbr_manifestation(tree))
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
    #The "introduced on" date represents the original work's date, and is appropriate for using FRBR standards.
    date_introduced = get_sunlight('introduced_on', bill_id)['results'][0]['introduced_on']
    frbr_work = E("FRBRWork")
    frbr_work.append(E("FRBRthis", value=string.join([country, state, item, date_introduced, bill_id, 'main'],"/")))
    frbr_work.append(E("FRBRuri", value=string.join([country, state, item, date_introduced, bill_id],"/")))
    frbr_work.append(E("FRBRdate", date=date_introduced, name='introduced'))
    frbr_work.append(E("FRBRauthor", author=get_sponsor(tree).get("id")))
    frbr_work.append(E("FRBRcountry", value=country))
    return frbr_work

'''
def get_bill_number(tree):
    """returns the bill's number"""
    #TODO legis-num
    bill_num = tree.find('.//legis-num').text
    bill_num = re.match('\d*',bill_num).group()
    print "bill_num: " + bill_num

    return bill_num
'''

def generate_frbr_expression(tree):
    """Generates the FRBRExpression portion of the identification"""
    '''
    EXAMPLE:
    <FRBRthis value="/us/california/bill/2010-12-06/4/eng@/main"/>
    <FRBRuri value="/us/california/bill/2010-12-06/4/eng@"/>
    <FRBRdate date="2010-12-06" name="Expression"/>
    <FRBRauthor href="#somebody" as="#editor"/>
    <FRBRlanguage language="eng"/>
    '''
    country = 'us'
    state = 'house'
    item = 'bill'
    #The "introduced on" date represents the original work's date, and is appropriate for using FRBR standards.
    last_action = get_sunlight('last_action', bill_id)['results'][0]['last_action']['acted_at']
    frbr_expression = E("FRBRExpression")
    frbr_expression.append(E("FRBRthis", value=string.join([country, state, item, last_action, bill_id, 'eng@', 'main'],"/")))
    frbr_expression.append(E("FRBRuri", value=string.join([country, state, item, last_action, bill_id, 'eng@'],"/")))
    frbr_expression.append(E("FRBRdate", date=last_action, name='last_action'))
    frbr_expression.append(E("FRBRauthor", author='#authors'))
    frbr_expression.append(E("FRBRlanguage", language='eng'))
    return frbr_expression


def generate_frbr_manifestation(tree):

    '''
    <FRBRthis value="/us/california/bill/2010-12-06/4/eng@/main.xml"/>
    <FRBRuri value="/us/california/bill/2010-12-06/4/eng@/main.akn"/>
    <FRBRdate date="2010-12-06" name="XML-markup"/>
    <FRBRauthor href="#somebody" as="#editor"/>
    '''
    country = 'us'
    state = 'house'
    item = 'bill'
    #The "introduced on" date represents the original work's date, and is appropriate for using FRBR standards.
    date_accessed = time.strftime("%Y-%m-%d")
    frbr_manifestation = E("FRBRmanifestation")
    frbr_manifestation.append(E("FRBRthis", value=string.join([country, state, item, date_accessed, bill_id, 'eng@', 'main.xml'],"/")))
    frbr_manifestation.append(E("FRBRuri", value=string.join([country, state, item, date_accessed, bill_id, 'eng@', 'main.akn'],"/")))
    frbr_manifestation.append(E("FRBRdate", date=date_accessed, name='accessed'))
    frbr_manifestation.append(E("FRBRauthor", author='#authors'))
    return frbr_manifestation

def generate_references(tree):
    """Returns the references portion of the meta"""
    references = E('references', source='#somebody')
    references.append(get_sponsor(tree))
    for sponsor in get_cosponsors(tree):
        references.append(sponsor)
    for committee in get_committees(tree):
        references.append(committee)
    return references

'''
def generate_publication(tree):
'''

def generate_lifecycle(tree):
    source = "nick_fazzio"
    lifecycle_element = E("lifecycle", source=source)
    lifecycle_element.append(generate_eventRef(tree))
    return lifecycle_element
        

def generate_eventRef(tree):
    action_date = time.strftime("%Y-%m-%d")
    source = "nick_fazzio"
    refers = generate_frbr_manifestation(tree).getchildren()[1].get('value')
    print refers
    eventref_element = E('eventRef', date=action_date, source=source, refers=refers)
    return eventref_element

def get_sponsor(tree):
    """Returns an etree element containing TLCPerson tag with sponsor information"""
    sponsor_text = tree.find('.//sponsor').text
    sponsor_name = re.search('(Mr.|Mrs.|Ms.)? (?P<sponsor>[a-zA-Z]*)', sponsor_text).group('sponsor')
    ontology_path = '/ontology/person/akn/' + sponsor_name
    sponsor_element = E('TLCPerson', id=sponsor_name, href=ontology_path, showas=sponsor_name)
    return sponsor_element

def get_cosponsors(tree):
    """Returns a list of etree elements with containing TLCPerson tag with co sponsor information"""
    cosponsors = []
    cosponsor_matches = tree.findall('.//cosponsor')
    for cosponsor_match in cosponsor_matches:
        cosponsor_name = re.search('(Mr.|Mrs.|Ms.)? (?P<cosponsor>[a-zA-Z]*)', cosponsor_match.text).group('cosponsor')
        ontology_path = '/ontology/person/akn/' + cosponsor_name
        cosponsor_id = cosponsor_match.get('name-id')
        cosponsor_element = E('TLCPerson', id=cosponsor_id, href=ontology_path, showas=cosponsor_name)
        cosponsors.append(cosponsor_element)
    return cosponsors

def get_committees(tree):
    committees = []
    committee_matches = tree.findall('.//committee-name')
    for committee in committee_matches:
        committee_name = committee.text
        committee_id = committee.get('committee-id')
        ontology_path = '/ontology/organization/akn/' + committee_name.replace(' ', '_')
        committee_element = E('TLCOrganization', id=committee_id, href=ontology_path, showas=committee_name)
        committees.append(committee_element)
    return committees


def getFromDict(dataDict, mapList):
    """Retrieves nested values from a dictionary"""
    return reduce(lambda d, k: d[k], mapList, dataDict)

def set_up_parser():
    parser = argparse.ArgumentParser(description='generate akn xml for a bill')
    bill = parser.parse_args()
    return bill

if __name__ == "__main__":
    main(sys.argv[0])

