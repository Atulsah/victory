# Copyright (c) 2022, Atul Sah 
# For license information, please see license.txt


from pydoc import doc
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
#import os.path
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import gspread

class ProductionEntry(Document):

    def validate(self):
        self.get_data_from_sheet()

    def get_data_from_sheet(self):
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
        sh = gc.open(self.spreadsheet_name)
        wks = sh.worksheet(self.worksheet_name)
        items = wks.get_all_records()
        self.create_stock_entry(items)

        mydate = getdate(self.date).strftime("%d")
        entry_date = self.entry_type + "_" + mydate

        for i in items:
            if self.buyer == i['buyer']:
                if i[entry_date] > 0:
                    print(i['buyer'], i['item_code'], i[entry_date])

        #stock_entry_items = []



    
            
    def create_stock_entry(doc, handler=""):
        se = frappe.new_doc("Stock Entry")
        se.update({ 
            "purpose": "Material Transfer" , 
            "stock_entry_type": "Material Transfer" , 
            "from_warehouse": "Reservation Warehouse - G" , 
            "to_warehouse": "Finished Goods - G"
        })
        for se_item in doc.items:
            se.append("items", { 
                "item_code":se_item.item_code, 
                "item_group": se_item.item_group, 
                "item_name":se_item.item_name, 
                "amount":se_item.amount, 
                "qty": se_item.qty , 
                "uom":se_item.uom, 
                "conversion_factor": se_item.conversion_factor }) 
        frappe.msgprint('Stock Entry is created please submit the stock entry')
        se.insert()
        se.save()         
