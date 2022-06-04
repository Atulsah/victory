# Copyright (c) 2022, Atul Sah and contributors
# For license information, please see license.txt

from pydoc import doc
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
#import os.path
from google.oauth2.service_account import Credentials
#from google.oauth2 import service_account
import gspread

class StockOpeningReconciliation(Document):

    def validate(self):
        items = self.get_data_from_sheet()
        msg = self.create_reconciliation_entry(items)
        frappe.msgprint(msg)

    def get_data_from_sheet(self):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = {
            "type": "service_account",
            "project_id": "amplified-vine-352304",
            "private_key_id": "bf45918c601308bc5fe59f7823a15a15cdd1ef60",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0Wf1ZhzR2/IkM\ngaaLmtjN5mPDO/aUZjmI+yzBghotQXonLYzzjLm0EvG5lQ+OXifI8KU5bEcpuANy\nz6bWp+MgMRmTizZdq/umJZi7UJplg92FkHOm0KKAvHL8Lz7esdzu2Et6bU8G2e/G\nmkIiaXKXOTHDSwrM6rRMtenSSTC07/QK0FjWA9LHFmXbUZjmPAs487oHM6De1+C8\nOgaR/eVGv9STYDnnIkKEyIBsz+E4n5p1Zua+iGK3SldmHiB2TqXFIsnvaJ1+TWlN\nsygJr+wIb9vbxQjxBEMDjPLaWqu/iOdFTkgvKzsF4Rva25rPH6jphXWVeDq+tAxa\nJYLORDD5AgMBAAECggEAECrGeydzgKyV8QLwzfAzOe7ql8Jo8efhhbnlatHZvJ+T\nXo525ZDCh2XQ2TbnanbeiGTpHMcL8I2UMo8yiKjLY5P/M9KdjKNZh0z0vmrk8k9y\nNNJMicJHZPSvtpNaJo6pbFhDmN2SYV35QHOM1OagvPVltHjmRpUOFVfT1nPU6801\ngtAOD7WUBl8NCgrVa/4Cd3gz3RgIPrK5AkIB6s1WR0Z9PIawft2ZI3uee17j2IoA\nR5X9/IGFckFQPLEQlRKX+dzHX78ZbneMAexPEAsywuq9xqklSrNdZqEhQdmBrHjE\nLgQ/FaBwQQ16vBFaiWPDHrtTqQSNTxokezKoomn8kQKBgQDywId2MD3inn+TAuEh\nMZaIT4I1IsPIXFB+we4U/BPiGzSX3Q4vVe6uZ8iC0VH/AvwqI8xONM0+i1I7rypn\nvNvHGI4H0M7yfPtPizx7yAHTWVqnLleKCH7x3OntGoWqaJccMH6vuDuCUQFEqvCy\nm9fZ5fpLiT06J00wt90KUd2yiQKBgQC+MarMnpwfbd2DIvVzS7hPfQaizKNsm27/\nrCeElw1lxVetEhfuuyOCjIJSHIYosiENfzL7Nu6W7o3/P7HfZwjWfqnOSAqoHCXS\n3R+VJtTqDDsGuHdzB6B0YF4O9gMTBXNClHZ6vwqzKtsAiGCT7QCNMuxbwfrKZhDP\nKtvObgau8QKBgBjbnEN/BydIobm1JsaWZFrLAYNdbvz6bwe75hxh/8s8i/MtIMG6\nI/naCM9Ujff2H0pVZhtwDsBj1eTkuAvta/gETK8CM97i630mvefTAFTbJoxOE4q/\n+ffcblvoRl2/3hF16dMmo3lhwCZ+9qzjhoP6p9nKUOm+kon1mf3viis5AoGAaJIk\nR4a5bipYzV4uN+sc9k9Wk7IR9IftWpOL0sG+cwMytoypLfAkkQWyLXVTahKuS55x\nKGBGhCO7XOjnYl5jJJPVxv4jJdT8EtjTIY2NKPX6ijJoMo2x8ep+LJmkjRPFEIlS\nLyDUwDfC26Mf/pUjZX7nJ3ga7Kd7fHwjCHfEIvECgYByihIqoLrYpYrHTSFwVTx0\ntTOtJgbvPLxvmmt3ollJJchjYuZxZQov78wI6ATE3svoQbzIP0SB6rTH6S1Vqnm1\nujplNKkxCPwBkM8pXIMbi7Ddv6lFz6sfP6QkINmkGFtjcRWJEigwNRPA9N6p4yoR\nlhFVTH7muAwHPvDXjQ2axQ==\n-----END PRIVATE KEY-----\n",
            "client_email": "erp-viwl@amplified-vine-352304.iam.gserviceaccount.com",
            "client_id": "100832027379896973953",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/erp-viwl%40amplified-vine-352304.iam.gserviceaccount.com"
            }

        gc = gspread.service_account_from_dict(credentials)
        sh = gc.open(self.spreadsheet_name)
        wks = sh.worksheet(self.worksheet_name)
        items = wks.get_all_records()
        return items
        

     
    def create_reconciliation_entry(self, items):
        #mydate = getdate(self.date).strftime("%d")
        #entry_date = self.entry_type + "_" + mydate
        #serise = "MAT/"+self.buyer+"-"+self.date+"/"
        #print(serise)
        #print(items)
        sre = frappe.new_doc("Stock Reconciliation")
        sre.update({
            "stock_entry_type": "Material Receipt",
            "company":self.company,
            "purpose": "Stock Reconciliation",
            "set_posting_time" : 1,
            "posting_date" : self.date,
            "posting_time" : "01:00:00",
            "to_warehouse": self.warehouse,
        })
        for sre_item in items:
            if self.buyer == sre_item['Buyer']:
                if sre_item[entry_date] > 0:
                    sre.append("items", { 
                        "t_warehouse":self.warehouse,
                        "item_code":sre_item['Item_code'],
                        "qty": sre_item[entry_date],
                        "transfer_qty" : sre_item[entry_date],
                        "uom":sre_item['UOM'],
                        "stock_uom":sre_item['UOM'],
                        "conversion_factor": 1,
                        "valuation_rate":1
                    })
        
        
        print(se)
        se.insert()
        se.save()
        print(se)   
             
        msg = "Stock Entry has been created for " + self.buyer + " items for the date : " + self.date +" and Saved in Draft from. Please Submit the Stock entry. ( " + se.name + " ) "
        return msg

#frappe.get_last_doc('Stock Entry', filters={"name": se.name})