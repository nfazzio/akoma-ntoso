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
    url = "http://www.gpo.gov/fdsys/pkg/BILLS-113hr1120rh/xml/BILLS-113hr1120rh.xml"
    
    source_tree = get_tree_from_url(url)
    
    akn_tree = generate_akn(source_tree)
    print etree.tostring(akn_tree, pretty_print=True)

def get_sunlight(parameters,bill_id):
    """Takes in a bill_id and a list of desired fields to return from the Sunlight Foundation API, and returns them"""
    url = 'http://congress.api.sunlightfoundation.com/bills'
    header = {'X-APIKEY':api_key}
    fields = {'fields':parameters, 'bill_id':bill_id}
    json_response = requests.request('get', url, headers=header, data=fields).json()

    return json_response

def get_tree_from_url(url):
    """Returns an lxml tree from a url"""
    xml = urllib2.urlopen(url)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml, parser)
    print etree.tostring(tree, pretty_print=True)
    return tree

def generate_akn(tree):
    """Take in an lxml tree and returns xml fitting akomaNtoso standards"""
    root = E('akomaNtoso', xmlns='http://akomantoso.googlecode.com/svn/release/trunk/schema/akomantoso30.xsd')
    bill = E('bill')
    root.append(bill)
    bill.append(generate_meta(tree))
    '''
    for tag in parse_section(tree, 'form', 'preface'):
        bill.append(tag)
    for tag in parse_section(tree, "*[substring(name(), string-length(name()) - 4) = '-body']", 'body'):
        bill.append(tag)
    '''
    for tag in parse_section(tree, 'form'):
        bill.append(tag)
    for tag in parse_section(tree, "*[substring(name(), string-length(name()) - 4) = '-body']"):
        bill.append(tag)

    bill.append(generate_preamble(tree))
    etree.tostring(root, pretty_print=True)
    return root

############################
# Methods to Generate Meta #
############################

def generate_meta(tree):
    """Generates the meta portion of the xml"""
    meta = E("meta")
    
    meta.append(generate_identification(tree))
    meta.append(generate_publication(tree))
    meta.append(generate_lifecycle(tree))
    meta.append(generate_analysis(tree))

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
    last_version = get_sunlight('last_version_on', bill_id)['results'][0]['last_version_on']
    frbr_expression = E("FRBRExpression")
    frbr_expression.append(E("FRBRthis", value=string.join([country, state, item, last_version, bill_id, 'eng@', 'main'],"/")))
    frbr_expression.append(E("FRBRuri", value=string.join([country, state, item, last_version, bill_id, 'eng@'],"/")))
    frbr_expression.append(E("FRBRdate", date=last_version, name='last_action'))
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


def generate_publication(tree):
    id = 'publication'
    date = get_sunlight('last_version_on', bill_id)['results'][0]['last_version_on']
    name = 'http://www.gpo.gov'
    publication_element = E('publication', date=date, name=name)
    return publication_element


def generate_lifecycle(tree):
    source = "nick_fazzio"
    lifecycle_element = E("lifecycle", source=source)
    lifecycle_element.append(generate_eventRef(tree))
    return lifecycle_element
        

def generate_eventRef(tree):
    action_date = time.strftime("%Y-%m-%d")
    source = "nick_fazzio"
    refers = generate_frbr_manifestation(tree).getchildren()[1].get('value')
    eventref_element = E('eventRef', date=action_date, source=source, refers=refers)
    return eventref_element

def generate_analysis(tree):
    source = "nick_fazzio"
    analysis_element = E("analysis", source=source)
    analysis_element.append(generate_active_modification(tree))
    return analysis_element

def generate_active_modification(tree):
    active_modification_element = E("activeModification")
    if tree.xpath("//*[@changed='deleted']"):
        active_modification_element.append(generate_textual_mod(tree, 'deletion'))
    if tree.xpath("//*[@changed='added']"):
        active_modification_element.append(generate_textual_mod(tree, 'insertion'))
    return active_modification_element

def generate_textual_mod(tree, type):
    textual_mod_element = E("textualMod",type=type)
    return textual_mod_element

def get_sponsor(tree):
    """Returns an etree element containing TLCPerson tag with sponsor information"""
    sponsor = tree.find('.//sponsor')
    sponsor_name = re.search('(Mr.|Mrs.|Ms.)? (?P<sponsor>[a-zA-Z]*)', sponsor.text).group('sponsor')
    ontology_path = '/ontology/person/akn/' + sponsor_name
    sponsor_id = sponsor.get('name-id')
    sponsor_element = E('TLCPerson', id=sponsor_id, href=ontology_path, showas=sponsor_name)
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

###############################
# Methods to Generate Preface #
###############################
''' 
    <distribution-code display="yes">IB</distribution-code>
    <calendar display="yes">Union Calendar No. 18</calendar>
    <congress display="yes">113th CONGRESS</congress>
    <session display="yes">1st Session</session>
    <legis-num>H. R. 1120</legis-num>
    <associated-doc role="report" display="yes">[Report No. 113&#x2013;30]</associated-doc>
    <current-chamber display="yes">IN THE HOUSE OF REPRESENTATIVES</current-chamber>
'''
def generate_preface(tree):
    
    form = tree.find('.//form')
    preface = E('preface')
    for child in form:
        p = E('p', '')
        if child.text and not child.get('display')=='no':
            #do first order checks
            p = translate_element(child, p)
        for rec_child in child.findall('.//*'):
            p = translate_element(rec_child, p)
        preface.append(p)

    return preface
    

def parse_section(tree, old_tag):
    translations = []
    segments_to_parse = tree.xpath('.//'+old_tag)
    for segment in segments_to_parse:
        segment = translate_element(segment)
        for element in segment.xpath('.//*'):
            translate_element(element)
        translations.append(segment)
    return translations


def translate_element(element):
    if element.tag == 'legis-num':
        element.tag = 'docNumber'
    elif element.tag == 'legis-body':
        element.tag = 'body'
        if element.get('changed'):
            element.attrib['status'] = element.attrib.pop('changed')
    elif element.tag in('sponsor', 'cosponsor'):
        element.attrib['id'] = element.attrib.pop('name-id')
        element.tag = 'person'
    elif element.tag =='text':
        element.tag = 'p'
    elif element.tag == 'associated-doc':
        element.tag = 'doc'
    elif element.tag == 'official-title':
        element.tag = 'title'
        for attrib in element.attrib:
            element.attrib.pop(attrib)
    elif element.tag == 'legis-type':
        element.tag = 'docType'
    elif element.tag == 'section':
        if element.get('section-type'):
            element.attrib.pop('section-type')
    elif element.tag == 'enum':
        element.tag = 'num'
    elif element.tag == 'external-xref':
        element.tag = 'ref'
        element.attrib['href']=element.attrib.pop('parsable-cite')
    elif element.tag == 'paragraph':
        element.tag = 'p'
    elif element.tag == 'short-title':
        element.tag = 'shortTitle'
    elif element.tag == 'section':
        element.attib.pop
    elif element.tag == 'session':
        element.attrib.pop('display')
    elif element.tag == 'current-chamber':
        element.attrib.pop('display')
    elif element.tag == 'header':
        pass

    else:
        element.tag = ('TODO'+element.tag)
    return element

################################
# Methods to Generate Preamble #
################################

def generate_preamble(tree):
    preamble_element = E('preamble')
    preamble_element.append(generate_container(tree))
    return preamble_element

def generate_container(tree):
    container_element = E('container', id='cnt1', name='motivation')
    return container_element

############################
# Methods to Generate Body #
############################

def generate_body(tree):
    body_element = E('body')


def set_up_parser():
    parser = argparse.ArgumentParser(description='generate akn xml for a bill')
    bill = parser.parse_args()
    return bill

if __name__ == "__main__":
    main(sys.argv[0])

