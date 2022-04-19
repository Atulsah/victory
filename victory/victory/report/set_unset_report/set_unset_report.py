# Copyright (c) 2022, Atul Sah and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from dataclasses import dataclass
from warnings import filters
import frappe
from frappe import _
from frappe.model.document import Document
from frappe import utils
from frappe.utils import flt
from datetime import datetime,timedelta,date
from frappe.utils import getdate, date_diff,add_days, add_years, cstr,formatdate, strip


def execute(filters):

	columns = get_columns() 
	data = []
	data = set_unset_report(filters)

	return columns, data

def set_unset_report(filters):
	data = []

	return data

def set_unset_item(filters):
	items = frappe.db.sql("""
		select 
			item_code, item_name, foreign_buyer_name
		from 
			`tabItem` item
		where 
			item.company=%(company)s and item.foreign_buyer_name =%(buyer)s
			item.pch_made = "10" """,
			{'company':filters.company, 'buyer':filters.foreign_buyer_name},
		as_dict=1)

	return items

def product_bundle_items(item_code):
	return frappe.db.sql("""
		select 
			pb.new_item_code,
			pbi.item_code as item_code,pbi.item_name as item_name,
			pbi.qty as qty, pbi.uom as uom
	 	from 
			`tabProduct Bundle Item` pbi,`tabProduct Bundle` pb 
		where 
			pbi.parent=pb.name and pb.new_item_code = %s """,(item_code),as_dict=1)

def get_order_dispatch_qty(item_code):

	return data

def get_opening_balance_from_slee(item_code,posting_date,warehouse):
	balance_qty = frappe.db.sql("""select qty_after_transaction from `tabStock Ledger Entry`
		where item_code=%s and posting_date < %s and 
		warehouse = %s and is_cancelled='No'
		order by posting_date desc, posting_time desc, name desc
		limit 1""", (item_code, posting_date, warehouse))

	return flt(balance_qty[0][0]) if balance_qty else 0.0

def get_production_qty(filters, item_code):
	print("entring production qty methode.....")
	pro_qty = frappe.db.sql("""
		select
			ifnull(sum(qty),0) as qty 
		from 
			`tabStock Entry Detail` sted,`tabStock Entry` ste 
		where 
			ste.stock_entry_type = "Manufacture" and 
			ste.posting_date BETWEEN %(from_date)s and %(to_date)s and
			ste.company=%(company)s and sted.item_code = %(item)s and 
			sted.t_warehouse =%(warehouse)s and
			sted.parent=ste.name and ste.docstatus=1""",
			{'from_date':filters.from_date,'to_date':filters.to_date,
			 'company':filters.company,'item':item_code, 
			 'warehouse':filters.warehouse},as_dict=1)
	print(pro_qty)
	if pro_qty and pro_qty[0].qty > 0:
		return pro_qty[0].qty
	else:
		return 0

def get_closing_stock_from_bin(item_code, warehouse):
	item_stock_qty = frappe.db.sql("""
		select 
			ifnull(actual_qty,0) as actual_qty 
		from 
			`tabBin` 
		where 
			item_code = %s and warehouse = %s 
		order by 
			creation Desc limit 1""",
			(item_code, warehouse),as_dict=1)

	if item_stock_qty and item_stock_qty[0].actual_qty > 0:
		return item_stock_qty[0].actual_qty
	else:
		return 0



#Columns in report
def get_columns():
	columns = [{
		"fieldname": "flag",
		"label": _(" "),
		"fieldtype": "data",
		"width": 10
	}]
	columns.append({
		"fieldname": "item_code",
		"label": _("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"width": 100
	})
	columns.append({
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "data",
		"width": 200
	})
	columns.append({
		"fieldname": "opening_stock",
		"label": _("Opening Stock"),
		"fieldtype": "data",
		"width": 120
	})
	columns.append({
		"fieldname": "production_qty",
		"label": _("Production Qty"),
		"fieldtype": "data",
		"width": 120
	})
	columns.append({
		"fieldname": "order_received",
		"label": _("Order Received"),
		"fieldtype": "data",
		"width": 120
	})
	columns.append({
		"fieldname": "dispatched_qty",
		"label": _("Dispatched Qty"),
		"fieldtype": "data",
		"width": 150
	})
	columns.append({
		"fieldname": "pending_qty",
		"label": _("Pending Qty"),
		"fieldtype": "data",
		"width": 120
	})
	columns.append({
		"fieldname": "closing_stock",
		"label": _("Closing Stock"),
		"fieldtype": "data",
		"width": 120
	})
	columns.append({
		"fieldname": "product_remains",
		"label": _("Product Remains"),
		"fieldtype": "data",
		"width": 120
	})

	return columns	

