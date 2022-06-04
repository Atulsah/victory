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

"""
    scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

    credentials = {
        "type": "service_account",
        "project_id": "erpnext-victory",
        "private_key_id": "d1b3ab6e809d37da229b6d7add80313d0cd38b56",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCqOozwWapnXW8u\n7lTQaL9zEmyEs8He4uNyjgqOFAxalZLwnGZJeNIDDmpFIROBjcHUVWr5ZVhCs7JG\nppAB2XSitV3cnGtac3rGvg0X7U8lkguX3HvB1xo2pm614/IuMslGF4lSqUkCYCji\ntydcVARy7za72WXI4lnwPuSOZM2QBfHVcTQR6s5TkqA8N553z+RrM8N/cPVs4Ecc\nCYTslV3izvna7dhYSvO27hLuxN+gPIKMw6niv4CEkMMYuHzX0MTC5hsljps+gNVC\nssVyF9p/RMKx3crhTBN/ibxx2HetVQYPuhn19lDxVpizpln1tGtOF4QLJpQbh/kg\nQPIxZMQNAgMBAAECggEALjG6WmTyvZ8Y02MAqBes0HTQ9wfy1eG7ODR8f8bH/XL2\nj43ZohmD4ClyxDSwHumRjmXppCkQ1PT/rXV4wc+5e4f9IyddaIvK5xDe673NyxPB\nSqIeAWG2btsmUvy7FTdZ8Eflz4U510eyAKgUKdVw6aGpuDtMCEIIhw4CJvQK5oiN\nJTfnWqFkQdWfympS279N1SqeDIi9Q6oMjbRjAPHsZ03A/nnFhsBiC8SWcchINSuh\n4cxLkBZzeja4Qtwj+NoKKOr17JMbd7rcKhxQToAaPCQgv7TdRjhwT/yhmUc6kwY2\nokDxpXxXBGA9vqZjMgDAHUk92cam0d1K+LdobTyQLwKBgQDR3pqDxiMQwLmLWwUl\ndXx/YbZ0HTppb3cJSM0KZDk5RTc6jky57Hbr2BR9HHzYhUwIT0ngWIXz04A9+XdO\nBPBffRTAzi8t1twB3WROw6NSHcP9ayjq600xOK8FHTqiGqNDZbrtq8CKbakkonG4\npYP0uXL5GegpC9HqggIBx9EAfwKBgQDPpVmvbo3PrcDLz/VBgoV3CbLtPUeZn3e7\n0wG9GHNT4HmM5pNJH1C2TTQyJ8ZKLWcWgFJOFFrSWDQ/ZqGmg7wvmJWyafSntlzr\nVZSsmyzNIDJmqcSsU5B7/1Bw13kFtkQxp1yHxK+0Wj8NduEv5m0TtgpJ6FG0ngkl\nFKoXEvj1cwKBgGP8UNMM97HIj91TnO0OvySU8e756dVHlIeo1n7n5tdhIYHVP7qo\nbLPJ+2DrzJL/Vozy8Xhf1Fmo3wUnr+5MrhRgLB37XUDSh3if+GUKEepSYgh/IDxj\npCAaKFAgb8nBNR0r/1WyKQYKXrYkaleVC3vxSlRhQlkj13uJOtmMUAeTAoGAB9Q9\nMG8jq6vqdATQQ3sPWzCjbWx9EZ7AnfVTwHR2jLgO/TAIZ55lpan9iNKVGGDj3SZT\ndBwyXHH07lsJR0T6SHUhV8vE7LnkgP8GDwf+xXEsVVCbWMAB15sFxmtpZby8j362\n72uMEGnCrNhJn0u52x9m/ehjhELdJ2fDDgGqH18CgYBLUWsr7iMBpEi6BBmYhh4L\n1HAVpLjT5Zv8xHmj+XM9Zm2ayDSrrwx6JrEJKc54p0uRYA6ov9llxGMhd24d7hg/\nifzPRwLvwSc587Qm6W8uHu2VaQjX1+AJvm0XCxVPRv/qmKlDqUmcW5rp8DbeKaVe\nlvVXdlF669pyaaOsF2F+Vg==\n-----END PRIVATE KEY-----\n",
        "client_email": "erpnext@erpnext-victory.iam.gserviceaccount.com",
        "client_id": "103608811821822475700",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/erpnext%40erpnext-victory.iam.gserviceaccount.com"
    }


    gc = gspread.service_account_from_dict(credentials)
    sh = gc.open("D I SHEET")

    wks = sh.worksheet("APR_22") # for Worksheet Name
    items = wks.get_all_records() # will import all data from worksheet
    for i in items:
       print(i['Item_code'], i['Item_Name'], i['IN_01'])
"""

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
        
        
        print(se)
        se.insert()
        se.save()
        print(se)   
             
        msg = "Stock Entry has been created for " + self.buyer + " items for the date : " + self.date +" and Saved in Draft from. Please Submit the Stock entry. ( " + se.name + " ) "
        return msg

#frappe.get_last_doc('Stock Entry', filters={"name": se.name})