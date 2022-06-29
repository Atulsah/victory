# Copyright (c) 2022, Atul Sah 
# For license information, please see license.txt


from pydoc import doc
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
#import os.path
from google.oauth2.service_account import Credentials
#from google.oauth2 import service_account
import gspread

class ProductionEntry(Document):

    def validate(self):
        items = self.get_data_from_sheet()
        msg = self.create_stock_entry(items)
        frappe.msgprint(msg)

    def get_data_from_sheet(self):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = {
            "type": "service_account",
            
            }

        gc = gspread.service_account_from_dict(credentials)
        sh = gc.open(self.spreadsheet_name)
        wks = sh.worksheet(self.worksheet_name)
        items = wks.get_all_records()
        return items
        

     
    def create_stock_entry(self, items):
        mydate = getdate(self.date).strftime("%d")
        entry_date = self.entry_type + "_" + mydate
        serise = "MAT/"+self.buyer+"-"+self.date+"/"
        print(serise)
        print(items)
        se = frappe.new_doc("Stock Entry")
        se.update({ 
            "serise": serise,
            "stock_entry_type": "Material Receipt",
            "company":self.company,
            "purpose": "Manufacture", 
            "type": "Manufacture",
            "set_posting_time" : 1,
            "posting_date" : self.date,
            "posting_time" : "09:00:00",
            "to_warehouse": self.warehouse,
            #"buyer": self.buyer
        })
        for se_item in items:
            if self.buyer == se_item['Buyer']:
                if se_item[entry_date] > 0:
                    se.append("items", { 
                        "t_warehouse":self.warehouse,
                        "item_code":se_item['Item_code'],
                        "qty": se_item[entry_date],
                        "transfer_qty" : se_item[entry_date],
                        "uom":se_item['UOM'],
                        "stock_uom":se_item['UOM'],
                        "conversion_factor": 1,
                        "valuation_rate":1
                    })
        
        
        se.insert()
        se.save()
        #se.submit()  
             
        msg = "Stock Entry has been created for " + self.buyer + " items for the date : " + self.date +" and Saved in Draft from. Please Submit the Stock entry. ( " + se.name + " ) "
        return msg

#frappe.get_last_doc('Stock Entry', filters={"name": se.name})
