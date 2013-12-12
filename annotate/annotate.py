from lxml import etree
import urllib2

def main():
    url = "http://www.gpo.gov/fdsys/pkg/BILLS-112hconres83eh/xml/BILLS-112hconres83eh.xml"
    tree = get_tree(url)
    print etree.tostring(tree, pretty_print=True)

def get_tree(url):

    html = urllib2.urlopen(url)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(html, parser)
    return tree

if __name__ == "__main__":
    main()

