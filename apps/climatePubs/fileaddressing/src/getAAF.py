__author__ = 'weituo'


import xmltodict, json
from xml.dom import minidom
from collections import OrderedDict
import urllib2


AAFInstru = list()
with open("../text_info/AAF_instrument.txt", "r") as reader:
    for ins in reader.readlines():
        AAFInstru.append(ins.strip())

def construct_helper(doc, current, category):
    """
    input: doc is the xml file by solr search,
           current is the dict for current instrument
           category is the instrument name
    output: json file indicates the knowledge information eg: <ARM> <hasSite> <SGP>
    """
   for arr in doc['arr']:
       if arr['@name'] == 'instrument_class':#'instrument_class_name':
           current['instrument_class'] = current.get('instrument_class', [])
           na = arr['str']
           if na not in current['instrument_class']:
               current['instrument_class'].append(na)

       elif arr['@name'] == 'instrument_class_name':
           current['instrument_class_name'] = current.get('instrument_class_name', [])
           na = arr['str']
           if na not in current['instrument_class_name']:
               current['instrument_class_name'].append(na)

       elif arr['@name'] == 'ConCat_site':
           current['site_info'] = current.get('site_info', [])
           site_info = arr['str']
           if site_info not in current['site_info']:
               current['site_info'].append(site_info)

       elif arr['@name'] == 'ConCat_facility':
           current['sites'] = current.get('sites', [])
           site = arr['str']
           if site not in current['sites']:
               current['sites'].append(site)

       elif arr['@name'] == 'ConCat_category': #or 'ConCat_measSubCat':
           category.append(arr['str'])

       elif arr['@name'] == 'ConCat_measSubCat':
           category.append(arr['str'])

   for s in doc['str']:
       if s['@name'] == 'primary_meas_name':
           category.insert(0, s['#text'])
       if s['@name'] == 'datastream':
           current['outputs'] = current.get('outputs', [])
           outname = s['#text']
           if outname not in current['outputs']:
               current['outputs'].append(outname)
   # date ?

   current['primary_meas'] = current.get('primary_meas', [])
   cat = tuple(category)
   if cat not in current['primary_meas']:
       current['primary_meas'].append(cat)


def construct(doclist, data, ins):
    """
    input: doclist is the xml list by solr search
           data is the dict to store information
           ins is the instrument name
    """
    current = OrderedDict()
    if type(doclist) == OrderedDict:
        category = list()
        construct_helper(doclist, current, category)
    else:
        for doc in doclist:
            category = list()
            construct_helper(doc, current, category)

    data[ins] = current

def main():
    url_str = "http://ui1b.ornl.gov/solr6/browser_0/select?q=" # solr search
    data = OrderedDict()
    for ins in AAFInstru:
        xml_str = urllib2.urlopen(url_str + ins).read()
        o = xmltodict.parse(xml_str)

        doclist = o['response']['result'].get('doc', [])
        print "###################" + ins + "#####################"
        construct(doclist, data, ins)

    with open('aafdata.json', 'wt') as out:
        json.dump(data, out, indent=4, separators=(',',':'))

main()


