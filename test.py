
import datetime
import difflib
import re
import pandas as pd
from requests.exceptions import HTTPError
from typing import Iterable
import xmlschema
import os
from xmlschema import XMLSchema, etree_tostring
from mindee import Client, PredictResponse, product
import os.path
from mindee import Client, PredictResponse, product





file_path = 'obchodni_partneri.txt'

column_names = ['Kód obchodního partnera', 'Obchodní partner', 'IČO', 'DIČ', 'Obec']

# Read only the first 5 columns of each line into a DataFrame
df = pd.read_csv(file_path, sep=';', encoding='latin-1', header=None, names =column_names, usecols=range(5))



def find_company_index(company):
  n = 4
  cutoff = 0.6

  close_matches = difflib.get_close_matches(company,
                df['Obchodní partner'], n, cutoff)
  try: find_item = str(df[df['Obchodní partner']==close_matches[0]].index.values[0])


  except:
    find_item='0'

  return(find_item)


def find_company_ico(company):
  n = 4
  cutoff = 0.6

  close_matches = difflib.get_close_matches(company,
                df['Obchodní partner'], n, cutoff)
  try: find_item = str(df[df['Obchodní partner']==close_matches[0]].index.values[0])


  except:
    find_item='1'

  return(str(df.iloc[int(find_item)]['IČO']))

def find_ico(company):
  #company=company.lower()
  print('company (FIND ICO)', company)

  file_path = 'obchodni_partneri.txt'

  column_names = ['Kód obchodního partnera', 'Obchodní partner', 'IČO', 'DIČ', 'Obec']
  ico_list=[]

# Read only the first 5 columns of each line into a DataFrame
  df = pd.read_csv(file_path, sep=';', encoding='latin-1', header=None, names =column_names, usecols=range(5))
  list_companies=df['Obchodní partner'].to_list()

  print(difflib.get_close_matches(company, list_companies, cutoff=0.35))

  index_company=list_companies.index(company)
  return(df.iloc[index_company]['IČO'])


  #for index, row in df.iterrows():
  #  if (difflib.SequenceMatcher(None, company, row['Obchodní partner']).ratio()) > 0.7:
  #    ico_list.append(row['IČO'])
  #if len(ico_list) == 0:
  #  for index, row in df.iterrows():
  #    seek_text=row['Obchodní partner']
  #
  #    if company.find(seek_text) != -1:
  #      print(ico_list)
  #      print('seek text', seek_text)
  #      ico_list.append(row['IČO'])
  #if len(ico_list) == 0:
  #  return('99999999')
  #else:
  #  return(ico_list[0])


def find_company_dic(company):
  n = 4
  cutoff = 0.6

  close_matches = difflib.get_close_matches(company,
                df['Obchodní partner'], n, cutoff)
  try: find_item = str(df[df['Obchodní partner']==close_matches[0]].index.values[0])


  except:
    find_item='1'

  return(str(df.iloc[int(find_item)]['DIČ']))



def filling_mindee_xml(image_file, file_path_):
  import xml.etree.ElementTree as ET


  myfile=open('protokol_conversion.txt','a')

  mytree = ET.parse('priklad.isdoc')
  myroot = mytree.getroot()

  mindee_client = Client(api_key="50a18642a4f354d983511b86d7b3214b")
  input_doc = mindee_client.source_from_path(image_file)
  result : PredictResponse= mindee_client.parse(product.InvoiceV4, input_doc)

  # iterating through the all values.
  for item in myroot[4].iter():
    item.text=str(result.document.inference.prediction.date.value)
    print('Invoice date:', item.text)
    myfile.writelines('Invoice date:'+ item.text)
    myfile.writelines('\n')

  for item in myroot[3].iter():
    item.text=str(result.document.inference.prediction.date.value)

  for item in myroot[1].iter():
    item.text= str(result.document.inference.prediction.invoice_number.value)
    print('Invoice number', str(result.document.inference.prediction.invoice_number.value))
    #data_processing_text+=('Invoice number' + str(result.document.inference.prediction.invoice_number.value))
    myfile.writelines('Invoice number'+ str(result.document.inference.prediction.invoice_number.value))
    myfile.writelines('\n')

  for item in myroot[6].iter():
    item.text=' '

  for item in myroot[7].iter():
    item.text=' '

  for item in myroot[9].iter('{http://isdoc.cz/namespace/2013}ForeignCurrencyCode'):
    item.text='   '



  for count, item in enumerate(myroot[12].iter('{http://anydomain.cz/branch/developer/head}UserfieldName')):
    item.text=' -- '

  for item in myroot[12].iter('{http://anydomain.cz/branch/developer/head}AdditionalHeadDiscount'):
    item.text='0'

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}UserID' ):
    item.text='0001'

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}CatalogFirmIdentification' ):
    item.text=find_company_index(str(result.document.inference.prediction.supplier_name.value))


  ico=[]
  for supplier_company_registrations_elem in result.document.inference.prediction.supplier_company_registrations:
    ico.append(supplier_company_registrations_elem.value)
    #print('Supplier company ICO):', supplier_company_registrations_elem.value)

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}ID'):
    #item.text=find_company_ico(str(result.document.inference.prediction.supplier_name.value))
    #item.text=ico[1] if len(ico) > 1 else find_ico(str(result.document.inference.prediction.supplier_name.value))
    item.text=supplier_company_registrations_elem.value


    #if len(ico) > 1:
    #  if ico[1] != find_ico(str(result.document.inference.prediction.supplier_name.value)):
    #    ico[1]=find_ico(str(result.document.inference.prediction.supplier_name.value))
    #    ico[0]='CZ' + ico[1]
    #    item.text=ico[1]
    item.text=supplier_company_registrations_elem.value
    print('Supplier company ICO :', item.text)
    myfile.writelines('Supplier company ICO :'+ item.text)
    myfile.writelines('\n')

    print('Original currency', result.document.inference.prediction.locale.value)
    myfile.writelines('Original currency'+ str(result.document.inference.prediction.locale.value))
    myfile.writelines('\n')

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}Name'):
    #item.text= str(result.document.inference.prediction.supplier_name.value)
    item.text=result.document.inference.prediction.supplier_name.value

  #my_dict['AccountingCustomerParty']['Party']['PartyIdentification']['ID']=item_['buyer_ic']
  #my_dict['AccountingSupplierParty']['Party']['PartyIdentification']['CatalogFirmIdentification']=find_company_index(item_['seller_name'])

  #my_dict['IssueDate']=item['issue_date']


  #my_dict['AccountingSupplierParty']['Party']['PartyName']['Name']=item_['seller_name']
  #my_dict['AccountingSupplierParty']['Party']['PostalAddress']['StreetName']=''

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}CompanyID' ):
    #item.text= find_company_dic(str(result.document.inference.prediction.supplier_name.value))
    #item.text=ico[0] if len(ico) > 1 else 'CZ' + find_ico(str(result.document.inference.prediction.supplier_name.value))
    item.text='CZ'+ supplier_company_registrations_elem.value
    print('Supplier company DIC: ', item.text)
    myfile.writelines('Supplier company DIC: ' + item.text)
    myfile.writelines('\n')

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}StreetName' ):
    item.text='  '

  for item in myroot[13].iter( '{http://isdoc.cz/namespace/2013}BuildingNumber'):
    item.text='  '

  for item in myroot[13].iter( '{http://isdoc.cz/namespace/2013}PostalZone'):
    item.text=' '

  for item in myroot[13].iter( '{http://isdoc.cz/namespace/2013}CityName'):
    item.text=df['Obec'].iloc[int(find_company_index(str(result.document.inference.prediction.supplier_name.value)))]

  #my_dict['AccountingSupplierParty']['Party']['PostalAddress']['BuildingNumber']=''
  #my_dict['AccountingSupplierParty']['Party']['PostalAddress']['CityName']=df['Obec'].iloc[int(find_company_index(item['seller_name']))]
  #my_dict['AccountingSupplierParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['AccountingSupplierParty']['Party']['PostalAddress']['PostalZone']=''

  #my_dict['AccountingSupplierParty']['Party']['PartyTaxScheme'][0]['CompanyID']=item_['buyer_dic']
  #my_dict['TaxPointDate']=item_['taxable_fulfillment_date']

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}RegisterKeptAt'):
    item.text='-- '

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}RegisterFileRef'):
    item.text='-- '

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}RegisterDate'):
    item.text='2016-01-01 '

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}Telephone' ):
    item.text='-- '

  for item in myroot[13].iter('{http://isdoc.cz/namespace/2013}ElectronicMail'):
    item.text=' -- '





  #my_dict['AccountingSupplierParty']['Party']['Contact']['Name']=''
  #my_dict['AccountingSupplierParty']['Party']['Contact']['Telephone']=''
  #my_dict['AccountingSupplierParty']['Party']['Contact']['ElectronicMail']=''
  #my_dict['AccountingSupplierParty']['Party']['RegisterIdentification']['RegisterKeptAt']=''
  #my_dict['AccountingSupplierParty']['Party']['RegisterIdentification']['RegisterFileRef']=''
  #my_dict['AccountingSupplierParty']['Party']['RegisterIdentification']['RegisterDate']=''

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}UserID' ):
    item.text='0001'

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}CatalogFirmIdentification' ):
    #item.text=find_company_index(str(result.document.inference.prediction.supplier_name.value))
    item.text='001'


  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}ID'):
    #item.text=find_company_ico(str(result.document.inference.prediction.supplier_name.value))
    #item.text=ico[1] if len(ico) > 1 else find_ico(str(result.document.inference.prediction.supplier_name.value))
    item.text= supplier_company_registrations_elem.value

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}Name' ):
    item.text=str(result.document.inference.prediction.supplier_name.value)
    print('Supplier name:', item.text)
    myfile.writelines('Supplier name:'+ item.text)
    myfile.writelines('\n')

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}StreetName'):
    item.text=' '

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}BuildingNumber'):
    item.text=' '

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}CityName'):
    item.text= df['Obec'].iloc[int(find_company_index(str(result.document.inference.prediction.supplier_name.value)))]

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}CompanyID'):
    #item.text=find_company_dic(str(result.document.inference.prediction.supplier_name.value))
    #item.text=ico[0] if len(ico) > 1 else 'CZ' + find_ico(str(result.document.inference.prediction.supplier_name.value))
    item.text='CZ' + supplier_company_registrations_elem.value
    print('Supplier company DIC ;', item.text)
    myfile.writelines('Supplier company DIC ;'+ item.text)
    myfile.writelines('\n')

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}RegisterKeptAt'):
    item.text=' -- '

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}RegisterFileRef'):
    item.text=' -- '

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}RegisterDate'):
      item.text='2016-01-01'

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}Telephone'):
    item.text='--'

  for item in myroot[14].iter('{http://isdoc.cz/namespace/2013}ElectronicMail'):
    item.text=' '

  for item in myroot[15].iter( '{http://isdoc.cz/namespace/2013}PostalZone'):
    item.text=' '

  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}ElectronicMail'):
    item.text=' '



  #my_dict['SellerSupplierParty']['Party']['PartyIdentification']['User']='0001'
  #my_dict['SellerSupplierParty']['Party']['PartyIdentification']['CatalogFirmIdentification']=find_company_index(item_['seller_name'])
  #my_dict['SellerSupplierParty']['Party']['PartyIdentification']['ID']=item_['seller_ic']
  #my_dict['SellerSupplierParty']['Party']['PartyName']['Name']=item_['seller_name']
  #my_dict['SellerSupplierParty']['Party']['PostalAddress']['StreetName']=''
  #my_dict['SellerSupplierParty']['Party']['PostalAddress']['BuildingNumber']=''
  #my_dict['SellerSupplierParty']['Party']['PostalAddress']['CityName']=df['Obec'].iloc[int(find_company_index(item['seller_name']))]
  #my_dict['SellerSupplierParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['SellerSupplierParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['SellerSupplierParty']['Party']['PartyTaxScheme'][0]['CompanyID']=item_['seller_dic']
  #my_dict['SellerSupplierParty']['Party']['Contact']['Name']=''
  #my_dict['SellerSupplierParty']['Party']['Contact']['Telephone']=''
  #my_dict['SellerSupplierParty']['Party']['Contact']['ElectronicMail']=''

  ico=[]
  for customer_company_registrations_elem in result.document.inference.prediction.customer_company_registrations:
    ico.append(customer_company_registrations_elem.value)

  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}ID'):
    #item.text=str(find_company_ico(str(result.document.inference.prediction.supplier_name.value)))
    item.text=ico[1] if len(ico) > 1 else '   '


  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}Name'):
    if result.document.inference.prediction.customer_name.value == None:
        item.text='SV Metal spol. s r.o'

    else:
      if result.document.inference.prediction.customer_name.value .find(result.document.inference.prediction.supplier_name.value ) != -1 or result.document.inference.prediction.supplier_name.value .find(result.document.inference.prediction.customer_name.value ) != -1:
        item.text='SV Metal spol. s r.o.'
        print('item.text 16', item.text )
      else:
        item.text=result.document.inference.prediction.customer_name.value
    print('Customer name', item.text )
    myfile.write('Customer name :'+ item.text)
    myfile.writelines('\n')

  for item in myroot[16].iter( '{http://isdoc.cz/namespace/2013}ID'):
    item.text=ico[1] if len(ico) > 1 else  '25257366'
    print('Customer ICO :', item.text)
    myfile.writelines('Customer ICO :'+ item.text)
    myfile.writelines('\n')

  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}StreetName' ):
    item.text=' '

  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}BuildingNumber' ):
    item.text=' '

  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}CityName' ):
    item.text=' '

  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}PostalZone' ):
    item.text=' '


  for item in myroot[16].iter( '{http://isdoc.cz/namespace/2013}CompanyID'  ):
    #item.text= find_company_dic(str(result.document.inference.prediction.supplier_name.value))
    item.text=ico[0] if len(ico) > 1 else 'CZ25257366'
    print('Customer DIC :', item.text)
    myfile.writelines('Customer DIC :'+ item.text)
    myfile.writelines('\n')


  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}Telephone'  ):
    item.text=' '

  for item in myroot[16].iter('{http://isdoc.cz/namespace/2013}ElectronicMail' ):
    item.text=' '



  #my_dict['Extensions']['extenzeH:UserfieldName'][0]['@xmlns:extenzeH']=''
  #my_dict['Extensions']['extenzeH:UserfieldName']['#text']=''
  #my_dict['Extensions']['extenzeH:UserfieldName'][0]['@xmlns:extenzeH']=''

  #my_dict['Extensions']['extenzeH:AdditionalHeadDiscount'][0]['@xmlns:extenzeH']=''
  #my_dict['Extensions']['extenzeH:AdditionalHeadDiscount']['#text']=''


  #my_dict['AccountingSupplierParty']['Party']['RegisterIdentification']['RegisterDate']='2016-01-01'
  #my_dict['SellerSupplierParty']['Party']['RegisterIdentification']['RegisterDate']='2016-01-01'
  ico=[]
  for customer_company_registrations_elem in result.document.inference.prediction.customer_company_registrations:
    ico.append(customer_company_registrations_elem.value)


  for item in myroot[15].iter( '{http://isdoc.cz/namespace/2013}ID'):
    #item.text=str(find_company_ico(str(result.document.inference.prediction.supplier_name.value)))
    item.text=ico[1] if len(ico) > 1 else '25257366'

  #if str(result.document.inference.prediction.supplier_name.value).upper() == str(result.document.inference.prediction.customer_name.value).upper():
  #  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}Name' ):
  #    item.text= 'SV Metal s.r.o.'
  #else:
  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}Name' ):
          #item.text= str(result.document.inference.prediction.customer_name.value)
    if result.document.inference.prediction.customer_name.value == None:
      item.text='SV Metal spol. s r.o.'
    else:
      if result.document.inference.prediction.customer_name.value .find(result.document.inference.prediction.supplier_name.value ) != -1 or result.document.inference.prediction.supplier_name.value .find(result.document.inference.prediction.customer_name.value ) != -1:
        item.text='SV Metal spol. r.o.'
      else:
          item.text=result.document.inference.prediction.customer_name.value

#  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}Name' ):
#    item.text=str(result.document.inference.prediction.customer_name.value)

  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}StreetName'):
    item.text=' '

  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}BuildingNumber' ):
    item.text=' '

  for item in myroot[15].iter( '{http://isdoc.cz/namespace/2013}CityName' ):
    item.text=' '

  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}CompanyID' ):
    #item.text = str(find_company_ico(str(result.document.inference.prediction.supplier_name.value)))
    item.text=ico[0] if len(ico) > 1 else 'CZ25257366'

  for item in myroot[15].iter('{http://isdoc.cz/namespace/2013}Telephone'):
    item.text=' '



  #my_dict['AccountingCustomerParty']['Party']['PartyIdentification']['UserID']=''
  #my_dict['AccountingCustomerParty']['Party']['PartyIdentification']['CatalogFirmIdentification']=''
  #my_dict['AccountingCustomerParty']['Party']['PartyIdentification']['ID']=''
  #my_dict['AccountingCustomerParty']['Party']['PartyName']['Name']=item_['buyer_name']
  #my_dict['AccountingCustomerParty']['Party']['PostalAddress']['StreetName']=''
  #my_dict['AccountingCustomerParty']['Party']['PostalAddress']['BuildingNumber']=''
  #my_dict['AccountingCustomerParty']['Party']['PostalAddress']['CityName']=df['Obec'].iloc[int(find_company_index(item['buyer_name']))]

  #my_dict['AccountingCustomerParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['AccountingCustomerParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['AccountingCustomerParty']['Party']['PartyTaxScheme'][0]['CompanyID']=item_['buyer_dic']
  #my_dict['AccountingCustomerParty']['Party']['Contact']['Name']=''
  #my_dict['AccountingCustomerParty']['Party']['Contact']['Telephone']=''
  #my_dict['AccountingCustomerParty']['Party']['Contact']['ElectronicMail']=''

  #my_dict['BuyerCustomerParty']['Party']['PartyIdentification']['UserID']=''
  #my_dict['BuyerCustomerParty']['Party']['PartyIdentification']['CatalogFirmIdentification']=''
  #my_dict['BuyerCustomerParty']['Party']['PartyIdentification']['ID']=''
  #my_dict['BuyerCustomerParty']['Party']['PartyName']['Name']=item_['buyer_name']
  #my_dict['BuyerCustomerParty']['Party']['PostalAddress']['StreetName']=''
  #my_dict['BuyerCustomerParty']['Party']['PostalAddress']['BuildingNumber']=''
  #my_dict['BuyerCustomerParty']['Party']['PostalAddress']['CityName']=df['Obec'].iloc[int(find_company_index(item['buyer_name']))]

  #my_dict['BuyerCustomerParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['BuyerCustomerParty']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['BuyerCustomerParty']['Party']['PartyTaxScheme'][0]['CompanyID']=item_['buyer_dic']
  #my_dict['BuyerCustomerParty']['Party']['Contact']['Name']=''
  #my_dict['BuyerCustomerParty']['Party']['Contact']['Telephone']=''
  #my_dict['BuyerCustomerParty']['Party']['Contact']['ElectronicMail']=''

  #my_dict['OrderReferences']['OrderReference'][0]['id']='0000'
  #my_dict['OrderReferences']['OrderReference'][0].pop('id')
  #my_dict['OrderReferences']['OrderReference'][0]['SalesOrderID']='0000'
  #my_dict['OrderReferences']['OrderReference'][0]['ExternalOrderID']=''
  #my_dict['OrderReferences']['OrderReference'][0]['IssueDate']=''

  #my_dict['OrderReferences']['OrderReference'][1]['id']=''
  #my_dict['OrderReferences']['OrderReference'][1]['SalesOrderID']=''
  #my_dict['OrderReferences']['OrderReference'][1]['ExternalOrderID']=''
  #my_dict['OrderReferences']['OrderReference'][1]['IssueDate']=''

    for item in myroot[17].iter('{http://isdoc.cz/namespace/2013}ExternalOrderID'):
      item.text=' '

    for item in myroot[17].iter('{http://isdoc.cz/namespace/2013}IssueDate'):
      item.text='2016-01-01'

    for item in myroot[17].iter('{http://isdoc.cz/namespace/2013}SalesOrderID'):
      item.text=' '

    for item in myroot[17].iter('{http://isdoc.cz/namespace/2013}ExternalOrderID'):
      item.text=' '

    for item in myroot[17].iter('{http://isdoc.cz/namespace/2013}IssueDate'):
      item.text='2016-01-01'

  #my_dict['DeliveryNoteReferences']['DeliveryNoteReference'][0]['@id']=''
  #my_dict['DeliveryNoteReferences']['DeliveryNoteReference'][0]['ID']=''
  #my_dict['DeliveryNoteReferences']['DeliveryNoteReference'][0]['IssueDate']=''

  for item in myroot[18].iter('{http://isdoc.cz/namespace/2013}ID'):
    item.text=' '

  for item in myroot[18].iter('{http://isdoc.cz/namespace/2013}IssueDate'):
    item.text='2016-01-01'

  #my_dict['OriginalDocumentReferences']['OriginalDocumentReference'][0]['@id']=''
  #my_dict['OriginalDocumentReferences']['OriginalDocumentReference'][0]['ID']=item_['invoice_number']
  #my_dict['OriginalDocumentReferences']['OriginalDocumentReference'][0]['IssueDate']=''

  for item in myroot[19].iter('{http://isdoc.cz/namespace/2013}ID'):
    item.text=' '

  for item in myroot[19].iter('{http://isdoc.cz/namespace/2013}IssueDate' ):
    item.text='2016-01-01'


  #my_dict['Delivery']['Party']['PartyIdentification']['UserID']=''
  #my_dict['Delivery']['Party']['PartyIdentification']['CatalogFirmIdentification']=''
  #my_dict['Delivery']['Party']['PartyIdentification']['ID']=item_['seller_ic']
  #my_dict['Delivery']['Party']['PartyName']['Name']=item_['buyer_name']
  #my_dict['Delivery']['Party']['PostalAddress']['StreetName']=''
  #my_dict['Delivery']['Party']['PostalAddress']['BuildingNumber']=''
  #my_dict['Delivery']['Party']['PostalAddress']['CityName']=''
  #my_dict['Delivery']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['Delivery']['Party']['PostalAddress']['PostalZone']=''
  #my_dict['Delivery']['Party']['PartyTaxScheme'][0]['CompanyID']=item_['buyer_dic']
  #my_dict['Delivery']['Party']['Contact']['Name']=''
  #my_dict['Delivery']['Party']['Contact']['Telephone']=''
  #my_dict['Delivery']['Party']['Contact']['ElectronicMail']=''


  ico=[]
  for customer_company_registrations_elem in result.document.inference.prediction.customer_company_registrations:
    ico.append(customer_company_registrations_elem.value)

  for item in myroot[20].iter( '{http://isdoc.cz/namespace/2013}ID'):
    #item.text=str(find_company_ico(str(result.document.inference.prediction.supplier_name.value)))
    item.text=ico[1] if len(ico)> 1 else '25257366'

  for item in myroot[20].iter( '{http://isdoc.cz/namespace/2013}Name'):
    item.text=result.document.inference.prediction.customer_name.value
    if result.document.inference.prediction.customer_name.value == None:
           item.text='SV Metal spol. s r.o.'
    else:
      if result.document.inference.prediction.customer_name.value .find(result.document.inference.prediction.supplier_name.value ) != -1 or result.document.inference.prediction.supplier_name.value .find(result.document.inference.prediction.customer_name.value ) != -1:
        item.text='SV Metal spol. s r.o.'

  for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}StreetName' ):
    item.text=' '

  for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}BuildingNumber' ):
    item.text=' '

  for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}CityName' ):
    item.text=' '

  for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}PostalZone' ):
    item.text=' '

  if len(ico) > 0:
    for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}CompanyID' ):
      item.text=str(ico[0])
  else:
    for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}CompanyID' ):
      item.text=ico[0] if len(ico) > 1 else 'CZ25257366'


  for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}Telephone' ):
    item.text=' '

  for item in myroot[20].iter('{http://isdoc.cz/namespace/2013}ElectronicMail'):
    item.text=' '

  #my_dict['InvoiceLines']['InvoiceLine'][0]['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['OrderReference']['@ref']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['OrderReference']['LineID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['DeliveryNoteReference']['@ref']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['DeliveryNoteReference']['LineID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['OriginalDocumentReference']['@ref']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['OriginalDocumentReference']['LineID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['InvoicedQuantity']['@unitCode']='ks'
  #my_dict['InvoiceLines']['InvoiceLine'][0]['InvoicedQuantity']['#test']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['LineExtensionAmountCurr']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['LineExtensionAmount']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['LineExtensionAmountTaxInclusiveCurr']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['LineExtensionAmountTaxInclusive']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['LineExtensionTaxAmount']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['UnitPrice']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['UnitPriceTaxInclusive']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['ClassifiedTaxCategory']['Percent']='21'
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Note']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['Description']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['CatalogueItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['SecondarySellersItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['TertiarySellersItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['BuyersItemIdentification']['ID']=''


  for item in myroot[21].iter( '{http://isdoc.cz/namespace/2013}LineID'):
    item.text=' '

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}OrderReference'):
    item.text=' '

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}InvoicedQuantity'):
    item.text='1'

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}LineExtensionAmountCurr'):
    item.text='0,00'



  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}LineExtensionAmountCurr'):
    item.text='0.00'

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}LineExtensionAmount'):
    item.text='0.00'



  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}LineExtensionAmountTaxInclusiveCurr'):
    item.text='0.00'

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}UnitPrice' ):
    item.text='0.00'

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}UnitPriceTaxInclusive' ):
    item.text='0.00'


  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}Percent'):
    item.text='0'

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}Note'):
    item.text=' '

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}Description'):
    item.text=' '

  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}ExpirationDate' ):
    item.text='2016-01-01'


  for item in myroot[21].iter('{http://isdoc.cz/namespace/2013}ID' ):
    if len(item.text) > 1:
      item.text='0'

  for count, item in enumerate(myroot[21].iter('{http://isdoc.cz/namespace/2013}LineExtensionAmountTaxInclusive' )):
    item.text='0.00'

# replacing values from table of invoice items
  data = {
  "description": [' '],
  "quantity": [' '],
  "unit_price":[' '],
  "total_amount":[' ']
}


#load data into a DataFrame object:
  df_ = pd.DataFrame(data)


  # je nutne osetrit kdyz se df_ vrati prazdne
  # overit na fakture c. 43
  # if df_.empty
  for index,line_items_elem in enumerate(result.document.inference.prediction.line_items):
      df_.at[index,'description']=line_items_elem.description
      df_.at[index,'quantity']=(line_items_elem.quantity) if line_items_elem.quantity != None else '1'
      df_.at[index,'unit_price']=(line_items_elem.unit_price)
      df_.at[index,'total_amount']=line_items_elem.total_amount

      print('Description: ',line_items_elem.description )
      print('Quantity: ', df_.at[index,'quantity'])
      print('Unit price: ', df_.at[index,'unit_price'])
      print('Total amount: ', df_.at[index,'total_amount'] )
      #if df_.loc[index,'unit_price']==None or  df_.loc[index,'quantity'] == None or df_.loc[index,'Total_amount'] == None:
      #  df_.drop()
      #  entering_missing_data(index)


  df_.dropna(subset=['quantity'], inplace=True)
  df_.dropna(subset=['unit_price'], inplace=True)
  df_.dropna(subset=['total_amount'], inplace=True)
  myfile.writelines('Descriptio og goods ')
  myfile.writelines('\n')
  myfile.writelines(str(df_))
  myfile.writelines('\n')

  for  count, item in enumerate(myroot[21].iter('{http://isdoc.cz/namespace/2013}InvoicedQuantity')):
      if count < len(df_.index):
        item.text= str(df_.iloc[count-1]['quantity']) if len(str(df_.iloc[count-1]['quantity'])) >0 else'1'


      else:
        item.text='0'



  for  count, item in enumerate(myroot[21].iter('{http://isdoc.cz/namespace/2013}UnitPrice')):
      if count < len(df_.index):
        item.text= str(df_.iloc[count-1]['unit_price']) if df_.iloc[count-1]['unit_price'] > 0 else '1'
      else:
        item.text='0'



  for count, item in enumerate(myroot[21].iter('{http://isdoc.cz/namespace/2013}Description')):
      if count < len(df_.index):
        item.text= str(df_.iloc[count-1]['description'])
      else:
        item.text='0'


  for count, item in enumerate(myroot[21].iter('{http://isdoc.cz/namespace/2013}LineExtensionAmount')):
      if count < len(df_.index):
        item.text= str(df_.iloc[count-1]['total_amount']) if df_.iloc[count-1]['total_amount'] !=None else 0.00
      else:
        item.text='0'


















  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['Name']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['Note']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['ExpirationDate']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['Specification']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['Quantity']['@unitCode']='ks'
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['Quantity']['#text']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][0]['BatchOrSerialNumber']=''

  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['Name']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['Note']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['ExpirationDate']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['Specification']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['Quantity']['@unitCode']='ks'
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['Quantity']['#text']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Item']['StoreBatches']['StoreBatch'][1]['BatchOrSerialNumber']=''
  #my_dict['InvoiceLines']['InvoiceLine'][0]['Extensions']['extenzeL:UserfieldName'][0]['@xmlns:extenzeL']=''

  #my_dict['InvoiceLines']['InvoiceLine'][1]['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['OrderReference']['@ref']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['OrderReference']['LineID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['DeliveryNoteReference']['@ref']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['DeliveryNoteReference']['LineID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['InvoicedQuantity']['@unitCode']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['InvoicedQuantity']['#text']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['LineExtensionAmountCurr']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['LineExtensionAmount']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['LineExtensionAmountTaxInclusiveCurr']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1][ 'LineExtensionAmountTaxInclusive']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['LineExtensionTaxAmount']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['UnitPrice']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['UnitPriceTaxInclusive']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['ClassifiedTaxCategory']['Percent']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['ClassifiedTaxCategory']['VATCalculationMethod']
  #my_dict['InvoiceLines']['InvoiceLine'][1]['Note']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['Item']['Description']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['Item']['CatalogueItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['Item']['SellersItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['Item']['TertiarySellersItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][1]['Item']['BuyersItemIdentification']['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['ID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['DeliveryNoteReference']['@ref']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['DeliveryNoteReference']['LineID']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['InvoicedQuantity']['@unitCode']='ks'
  #my_dict['InvoiceLines']['InvoiceLine'][2]['InvoicedQuantity']['#text']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['LineExtensionAmountCurr']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['LineExtensionAmount']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['LineExtensionAmountTaxInclusiveCurr']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['LineExtensionAmountTaxInclusive']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['LineExtensionTaxAmount']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['UnitPrice']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['ClassifiedTaxCategory']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['ClassifiedTaxCategory']['Percent']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['ClassifiedTaxCategory']['VATCalculationMethod']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['Note']=''
  #my_dict['InvoiceLines']['InvoiceLine'][2]['Item']['Description']=''

  #my_dict['NonTaxedDeposits']['NonTaxedDeposit'][0]['ID']=''
  #my_dict['NonTaxedDeposits']['NonTaxedDeposit'][0]['VariableSymbol']=''
  #my_dict['NonTaxedDeposits']['NonTaxedDeposit'][0]['DepositAmountCurr']=''
  #my_dict['NonTaxedDeposits']['NonTaxedDeposit'][0]['DepositAmount']=''

  for item in myroot[22].iter('{http://isdoc.cz/namespace/2013}ID'):
    item.text='--'

  for item in myroot[22].iter('{http://isdoc.cz/namespace/2013}DepositAmountCurr'):
    item.text='0.00'

  for item in myroot[22].iter('{http://isdoc.cz/namespace/2013}VariableSymbol'):
    item.text='--'



  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['ID']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['VariableSymbol']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['TaxableDepositAmountCurr']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['TaxableDepositAmount']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['TaxInclusiveDepositAmountCurr']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['TaxInclusiveDepositAmount']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['ClassifiedTaxCategory']['Percent']
  #my_dict['TaxedDeposits']['TaxedDeposit'][0]['ClassifiedTaxCategory']['VATCalculationMethod']=''

  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['ID']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['VariableSymbol']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['TaxableDepositAmountCurr']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['TaxableDepositAmount']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['TaxInclusiveDepositAmountCurr']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['TaxInclusiveDepositAmount']=''
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['ClassifiedTaxCategory']['Percent']
  #my_dict['TaxedDeposits']['TaxedDeposit'][1]['ClassifiedTaxCategory']['VATCalculationMethod']=''

  for item in myroot[23].iter('{http://isdoc.cz/namespace/2013}ID' ):
    item.text=' '

  for item in myroot[23].iter('{http://isdoc.cz/namespace/2013}VariableSymbol' ):
    item.text=' '

  for item in myroot[23].iter( '{http://isdoc.cz/namespace/2013}TaxableDepositAmountCurr'):
    item.text='0.00'

  for item in myroot[23].iter('{http://isdoc.cz/namespace/2013}TaxableDepositAmount' ):
    item.text='0.00'

  for item in myroot[23].iter('{http://isdoc.cz/namespace/2013}TaxInclusiveDepositAmount'):
    item.text='0.00'

  for item in myroot[23].iter('{http://isdoc.cz/namespace/2013}TaxInclusiveDepositAmountCurr' ):
    item.text='0.00'






  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxableAmount']=item['total_without_vat']
  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxAmount']=item['total_incl_vat']
  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['AlreadyClaimedTaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['AlreadyClaimedTaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['AlreadyClaimedTaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['AlreadyClaimedTaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['AlreadyClaimedTaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['AlreadyClaimedTaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['DifferenceTaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['DifferenceTaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['DifferenceTaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['DifferenceTaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['DifferenceTaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['DifferenceTaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][0]['TaxCategory']['Percent']=''


  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['AlreadyClaimedTaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['AlreadyClaimedTaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['AlreadyClaimedTaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['AlreadyClaimedTaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['AlreadyClaimedTaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['AlreadyClaimedTaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['DifferenceTaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['DifferenceTaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['DifferenceTaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['DifferenceTaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['DifferenceTaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['DifferenceTaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][1]['TaxCategory']['Percent']=''

  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['AlreadyClaimedTaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['AlreadyClaimedTaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['AlreadyClaimedTaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['AlreadyClaimedTaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['AlreadyClaimedTaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['AlreadyClaimedTaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['DifferenceTaxableAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['DifferenceTaxableAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['DifferenceTaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['DifferenceTaxAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['DifferenceTaxInclusiveAmountCurr']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['DifferenceTaxInclusiveAmount']=''
  #my_dict['TaxTotal']['TaxSubTotal'][2]['TaxCategory']['Percent']=''

  #my_dict['TaxTotal']['TaxAmountCurr']=''
  #my_dict['TaxTotal']['TaxAmount']=''


  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}TaxableAmountCurr'):
    item.text='0.00'

  for count, item in enumerate(myroot[24].iter('{http://isdoc.cz/namespace/2013}TaxableAmount')):

    if count == 0:
      item.text=str(result.document.inference.prediction.total_net.value)
      print('Total net value: ', item.text)
      myfile.writelines('Total net value: '+ item.text)
      myfile.writelines('\n')
    else:
      item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}TaxAmountCurr'):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}TaxAmount'):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}TaxInclusiveAmountCurr'):
    item.text='0.00'

  for count, item in enumerate(myroot[24].iter('{http://isdoc.cz/namespace/2013}TaxInclusiveAmount')):
    if count == 0:
      item.text=str(result.document.inference.prediction.total_amount.value)
      print('Total value : ', item.text)
      myfile.writelines('Total value : '+ item.text)
      myfile.writelines('\n')
    else:
      item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}DifferenceTaxableAmountCurr'):
    item.text='0'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}DifferenceTaxableAmount'):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}DifferenceTaxAmountCurr' ):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}DifferenceTaxAmount' ):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxableAmountCurr'):
    item.text='0.00'

  for count, item in enumerate(myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxableAmount')):
      item.text='0'


  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxAmountCurr' ):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxAmount'):
    item.text='0.00'

  for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmountCurr'):
    item.text='0.00'

  for count, item in enumerate(myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmount' )):
        item.text = '0.00'



  for item in myroot[24].iter( '{http://isdoc.cz/namespace/2013}DifferenceTaxInclusiveAmountCurr' ):
    item.text='0.00'

  for item in myroot[24].iter( '{http://isdoc.cz/namespace/2013}DifferenceTaxInclusiveAmount' ):
    item.text='0.00'

  for item in myroot[24].iter( '{http://isdoc.cz/namespace/2013}Percent' ):
    item.text='21'

  for  count, item in enumerate(myroot[24].iter()):

    if count == 9:
      for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxableAmount' ):
        item.text='0.00'



    if count == 13:
      for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmount' ):
        item.text='0.00'



    if count == 30:
      for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxableAmount' ):
        item.text='0.00'


    if count==34:
      for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmount' ):
        item.text='0.00'


    if count==51:
      for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxableAmount'):
        item.text='0.00'

    if count==55:
      for item in myroot[24].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmount'):
        item.text='0.00'







  #my_dict['LegalMonetaryTotal']['TaxExclusiveAmount']=''
  #my_dict['LegalMonetaryTotal']['TaxExclusiveAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['TaxInclusiveAmount']=''
  #my_dict['LegalMonetaryTotal']['TaxInclusiveAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['AlreadyClaimedTaxExclusiveAmount']=''
  #my_dict['LegalMonetaryTotal']['AlreadyClaimedTaxExclusiveAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['AlreadyClaimedTaxInclusiveAmount']=''
  #my_dict['LegalMonetaryTotal']['AlreadyClaimedTaxInclusiveAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['DifferenceTaxExclusiveAmount']=''
  #my_dict['LegalMonetaryTotal']['DifferenceTaxExclusiveAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['DifferenceTaxInclusiveAmount']=''
  #my_dict['LegalMonetaryTotal']['DifferenceTaxInclusiveAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['PayableRoundingAmount']=''
  #my_dict['LegalMonetaryTotal']['PayableRoundingAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['PaidDepositsAmount']=''
  #my_dict['LegalMonetaryTotal']['PaidDepositsAmountCurr']=''
  #my_dict['LegalMonetaryTotal']['PayableAmount']=''
  #my_dict['LegalMonetaryTotal']['PayableAmountCurr']=''

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}TaxExclusiveAmount'):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}TaxExclusiveAmountCurr'):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}TaxInclusiveAmount' ):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}TaxInclusiveAmountCurr' ):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxExclusiveAmount'):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxExclusiveAmountCurr'):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmount'):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}AlreadyClaimedTaxInclusiveAmountCurr'):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}DifferenceTaxExclusiveAmount' ):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}DifferenceTaxExclusiveAmountCurr' ):
    item.text='0.00'

  for item in myroot[25].iter( '{http://isdoc.cz/namespace/2013}DifferenceTaxInclusiveAmount'):
    item.text='0.00'

  for item in myroot[25].iter( '{http://isdoc.cz/namespace/2013}DifferenceTaxInclusiveAmountCurr' ):
    item.text='0.00'

  for item in myroot[25].iter( '{http://isdoc.cz/namespace/2013}PayableRoundingAmount' ):
    item.text='0.00'

  for item in myroot[25].iter( '{http://isdoc.cz/namespace/2013}PayableRoundingAmountCurr'  ):
    item.text='0.00'

  for item in myroot[25].iter( '{http://isdoc.cz/namespace/2013}PaidDepositsAmount' ):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}PaidDepositsAmountCurr' ):
    item.text='0.00'

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}PayableAmount' ):
    item.text=str(result.document.inference.prediction.total_amount.value)

  for item in myroot[25].iter('{http://isdoc.cz/namespace/2013}PayableAmountCurr'):
    item.text='0.00'




  #my_dict['PaymentMeans']['Payment'][0]['PaidAmount']=''
  #my_dict['PaymentMeans']['Payment'][0]['PaymentMeansCode']=''
  #my_dict['PaymentMeans']['Payment'][0]['Details']['DocumentID']=''
  #my_dict['PaymentMeans']['Payment'][0]['Details']['IssueDate']=''

  #my_dict['PaymentMeans']['Payment'][1]['PaidAmount']=''
  #my_dict['PaymentMeans']['Payment'][1]['PaymentMeansCode']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['PaymentDueDate']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['ID']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['BankCode']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['Name']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['IBAN']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['BIC']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['VariableSymbol']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['ConstantSymbol']=''
  #my_dict['PaymentMeans']['Payment'][1]['Details']['SpecificSymbol']=''

  #my_dict['PaymentMeans']['Payment'][2]['PaidAmount']=''
  #my_dict['PaymentMeans']['Payment'][2]['PaymentMeansCode']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['PaymentDueDate']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['ID']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['BankCode']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['Name']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['IBAN']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['BIC']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['VariableSymbol']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['ConstantSymbol']=''
  #my_dict['PaymentMeans']['Payment'][2]['Details']['SpecificSymbol']=''


  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][0]['ID']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][0]['BankCode']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][0]['Name']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][0]['IBAN']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][0]['BIC']=''

  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][1]['ID']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][1]['BankCode']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][1]['Name']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][1]['IBAN']=''
  #my_dict['PaymentMeans']['AlternateBankAccounts']['AlternateBankAccount'][1]['BIC']=''

  #my_dict.pop('Extensions' )

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}DocumentID'):
    item.text=' '

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}IssueDate'):
    item.text='2016-01-01'

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}PaymentMeansCode'):
    item.text='10'



  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}ID'):
    item.text='0001'

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}BankCode'):
    item.text='0000'


  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}IBAN'):
    item.text=' '

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}BIC' ):
    item.text=' '

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}VariableSymbol'):
    item.text=' '

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}ConstantSymbol' ):
    item.text=' '

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}SpecificSymbol' ):
    item.text=' '

  for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}PaymentDueDate'):
      for item in myroot[26].iter('{http://isdoc.cz/namespace/2013}PaymentDueDate'):
        #item_['issue_date']=datetime.datetime.strptime(item_['issue_date'], "%d.%m.%Y").strftime("%Y-%m-%d")

        if result.document.inference.prediction.due_date.value != None:
          item.text=result.document.inference.prediction.due_date.value
        else:
          item.text=result.document.inference.prediction.date.value







  print(df_)
  print()
  myfile.writelines('-----------------------------------------------------------------------------------------------')
  myfile.writelines('\n')
  print('print from procedure  ', file_path_)
  mytree.write(file_path_)
  return

## main ()
# remove protokol conversion
if os.path.isfile('protokol_conversion.txt'):
  os.remove('protokol_conversion.txt')


from pathlib import Path

def convert(file_path):
    working_dir=os.getcwd()
    i=0 # index of input file
    val_list=[]

    while(i< len(file_path)):
      #separate filename and change file type
      head, tail = os.path.split(file_path[i])
      base_name, _ = os.path.splitext(tail)
      #separate filename and change file type
      new_file_path = base_name + "." + "isdoc"
      try:
        mindee_client = Client(api_key="50a18642a4f354d983511b86d7b3214b")
      except  HTTPError as e:
              print(e.response.text)






      if not os.path.exists(working_dir +'/isdoc'):
        os.mkdir(working_dir + "/isdoc")


      filling_mindee_xml(file_path[i], working_dir +'/isdoc/' +new_file_path)




      my_schema = xmlschema.XMLSchema('isdoc-invoice-6.0.2.xsd')

      if my_schema.is_valid(working_dir +'/isdoc/' + new_file_path):
        val_list.append( new_file_path +  ' ISDOC Validation is O.K. ')
      else:
        val_list.append(new_file_path + ' ISDOC Validation is incorrect ')
      i+=1
    return val_list

import streamlit as st
import os
import tempfile
import time

st.image('page_13_img_1.jpg')
st.sidebar.title('conversion scan copy of invoices to isdoc format')


st.balloons()  # Celebration balloons



st.sidebar.write('Download selected files, and then click on convert')
uploaded_files=st.sidebar.file_uploader('Choose invoices to be converted to isdoc format:', accept_multiple_files=True)


if not os.path.exists(os.getcwd() +'/isdoc'):
        os.mkdir(os.getcwd() + "/isdoc")
else:
	files = os.listdir(os.getcwd() + "/isdoc")
	# removes all files in directoryt
	for file in files:
		os.remove(os.getcwd() + "/isdoc/"+file)




if not os.path.exists(os.getcwd() +'/invoices'):
        os.mkdir(os.getcwd() + "/invoices")
else:
	files = os.listdir(os.getcwd() + "/invoices")
# removes all files in directoryt
	for file in files:
		os.remove(os.getcwd() + "/invoices/"+file)

for uploaded_file in uploaded_files:
	bytes_data=uploaded_file.read()

	
	
      	#os.mkdir(path)
	
	with open(os.path.join(os.getcwd() + '/invoices/'+ uploaded_file.name),"wb") as f:
         f.write(uploaded_file.getbuffer())


    
	base = os.path.splitext(uploaded_file.name)[0]
	new_file_name=uploaded_file.name
	new_file_name=os.path.join(str(base) + ".isdoc")

files_path=os.listdir(os.getcwd() + '/invoices')

for i in files_path:
	base = os.path.splitext(i)
	new_file_name=os.path.join(str(base[0]) + ".isdoc")
	file_type=Path(i)
	st.write(base[0])
	st.write(os.path.join(os.getcwd() +'/isdoc/'+new_file_name))


	if file_type.suffix == '.jpg':

		filling_mindee_xml(os.path.join(os.getcwd() +'/invoices/'+i), os.path.join(os.getcwd() +'/isdoc/'+new_file_name))

exit_app = st.sidebar.button("Shut Down")
if exit_app:
  import keyboard
  st.write('Shut down')

  # Give a bit of delay for user experience
  time.sleep(5)
    # Close streamlit browser tab
   # Close streamlit browser tab
  keyboard.press_and_release('ctrl+w')
  pid = os.getpid()
  p = psutil.Process(pid)
  p.terminate()








