# Copyright (c) 2022, Atul Sah and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe import utils
from frappe.utils import flt
from datetime import datetime,timedelta,date
from frappe.utils import getdate, date_diff,add_days, add_years, cstr,formatdate, strip


def execute(filters):
	columns = get_columns() 
	
	if filters.report_type == "Complete Report":
		data = []
		data = complete_report(filters)

	elif filters.report_type == "Dispatched Item Report":
		data = []
		data = dispatched_item_report(filters)
	
	elif filters.report_type == "Order Item Report":
		data = []
		data = ordered_item_report(filters)
	else:
		data = [] 
		data = ordered_item_report(filters)

		
	return columns, data

def get_item_conditions(filters):
	conditions = []
	if filters.get("item_group"):
		conditions.append("so_item.item_group=%(item_group)s")	

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_ordered_items(filters):
	return frappe.db.sql("""
		select 
			so.name,so.po_no,so.po_date,so.delivery_date,
			so.foreign_buyer_name,so.final_destination,
			so_item.item_code,so_item.item_name,
			so_item.qty,so_item.uom,so_item.delivered_qty,
			so_item.weight_per_unit,so_item.weight_uom,
			so_item.pch_pallet_size
		from 
			`tabSales Order Item` so_item,`tabSales Order` so
		where 
			so.transaction_date BETWEEN %(from_date)s and %(to_date)s and 
			so.company=%(company)s and 
			so.foreign_buyer_name=%(foreign_buyer_name)s and
			so_item.parent=so.name and 
			so.docstatus=1 
			{itm_conditions} 
		order by 
			so.delivery_date Asc """.format(itm_conditions=get_item_conditions(filters)),
			{'from_date':filters.from_date,'to_date':filters.to_date,
			'company':filters.company,'foreign_buyer_name':filters.foreign_buyer_name,'item_group': filters.item_group},as_dict=1) 

def get_dispatcheded_items(name, item_code):
	return frappe.db.sql("""
		select 
			pk_item.parent_item, pk_item.item_code, pk_item.item_name, pk_item.qty, pk_item.uom
		from 
			`tabPacked Item` pk_item
		where 
			pk_item.parent= %s and pk_item.parent_item=%s""",(name, item_code),as_dict=1)

def get_current_stock_from_bin(item_code, warehouse):
	item_stock_qty = frappe.db.sql("""
		select 
			ifnull(actual_qty,0) as actual_qty 
		from 
			`tabBin` 
		where 
			warehouse = %s and item_code = %s 
		order by 
			creation Desc limit 1""",(warehouse, item_code),as_dict=1)
	if item_stock_qty and item_stock_qty[0].actual_qty > 0:
		return item_stock_qty[0].actual_qty
	else:
		return 0

def get_planned_qty(item_code, so_name):
	planned_qty = frappe.db.sql("""
		select 
			ifnull(sum(dn_item.qty),0) as planned_qty
		from 
			`tabDelivery Note Item` dn_item, `tabDelivery Note` dn
		where 
			dn_item.against_sales_order=(%s) and dn_item.item_code=(%s)
			and dn.name=dn_item.parent and dn.docstatus=0 limit 1""",(so_name, item_code),as_dict=1) 
	return planned_qty[0].planned_qty

#Add columns in report
def get_columns():
	columns = [{
		"fieldname": "flag",
		"label": _(" "),
		"fieldtype": "data",
		"width": 10
	}]
	columns.append({
		"fieldname": "sales_order",
		"label": _("Sales Order"),
		"fieldtype": "Link",
		"options": "Sales Order",
		"width": 150
	})
	columns.append({
		"fieldname": "delivery_date",
		"label": _("Delivery Date"),
		"fieldtype": "Date",
		"width": 100,
	})
	columns.append({
		"fieldname": "foreign_buyer_name",
		"label": _("Buyer"),
		"fieldtype": "Data",
		"width": 100
	})
	columns.append({
		"fieldname": "final_destination",
		"label": _("Destination"),
		"fieldtype": "Data",
		"width": 75
	})
	columns.append({
		"fieldname": "po_no",
		"label": _("PO No"),
		"fieldtype": "Data",
		"width": 60
	})
	columns.append({
		"fieldname": "po_date",
		"label": _("Date"),
		"fieldtype": "Date",
		"width": 100
	})
	columns.append({
		"fieldname": "item_code",
		"label": _("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"width": 75
	})	
	columns.append({
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 100
	})
	columns.append({
		"fieldname": "weight_per_unit",
		"label": _("Unit Weight"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "weight_uom",
		"label": _("Weight UOM"),
		"fieldtype": "Data",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "order_qty",
		"label": _("P.O Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "uom",
		"label": _("UOM"),
		"fieldtype": "Data",
		"width": 75,
		"precision": 2
	})	
	columns.append({
		"fieldname": "delivered_qty",
		"label": _("Dlvrd Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "planned_qty",
		"label": _("Planned Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pending_qty",
		"label": _("Pending Qty"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pending_wt",
		"label": _("Pending Qty Wt"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "item_stock_qty",
		"label": _("Stock"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "stock_qty_wt",
		"label": _("Stock Qty Wt   "),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "required_qty",
		"label": _("Required"),
		"fieldtype": "Float",
		"width": 75,
		"precision": 2
	})
	columns.append({
		"fieldname": "pcs_per_crate",
		"label": _("Crate Size"),
		"fieldtype": "data",
		"width": 75,
		"precision": 2
	})
	return columns	

def ordered_item_report(filters):
	data = []
	items = get_ordered_items(filters)
	item_pending_stock_map = {}
	item_current_stock_map = {}
	for i in items:
		weight_per_unit = frappe.db.get_value("Item", {'name': i.item_code}, "weight_per_unit")
		item_weight_uom = frappe.db.get_value("Item", {'name': i.item_code}, "weight_uom")
		item_current_stock_map[i.item_code] = get_current_stock_from_bin(i.item_code, filters.warehouse) if i.item_code not in item_current_stock_map else item_current_stock_map[i.item_code]
		item_planned_qty = get_planned_qty(i.item_code, i.name)
		item_pending_stock_map[i.item_code] = 0 if i.item_code not in item_pending_stock_map else item_pending_stock_map[i.item_code]
		current_stock_qty = item_current_stock_map[i.item_code]
		stock_qty_wt = round(current_stock_qty * weight_per_unit, 2) if (current_stock_qty * weight_per_unit) > 0 else 0
		current_pending_qty = round(i.qty - (i.delivered_qty + item_planned_qty),2) if (i.delivered_qty + item_planned_qty) > 0 else i.qty
		pending_wt = round(current_pending_qty * weight_per_unit, 2)

		if current_stock_qty >= current_pending_qty:
			current_stock_qty = 0 if current_stock_qty <=current_pending_qty else current_stock_qty
			required_quantity = 0 if (current_pending_qty <= item_current_stock_map[i.item_code]) else item_pending_stock_map[i.item_code]+current_pending_qty
			item_current_stock_map[i.item_code]= item_current_stock_map[i.item_code] - current_pending_qty
			item_pending_stock_map[i.item_code]= item_pending_stock_map[i.item_code] + current_pending_qty
		else:
			current_stock_qty = 0 if current_stock_qty <=0 else current_stock_qty
			item_pending_stock_map[i.item_code]= item_pending_stock_map[i.item_code] + (current_pending_qty if current_stock_qty <= 0 else (current_pending_qty - current_stock_qty))
			required_quantity = 0 if (current_pending_qty < item_current_stock_map[i.item_code]) else item_pending_stock_map[i.item_code]
			item_current_stock_map[i.item_code]= item_current_stock_map[i.item_code] - current_pending_qty


		data.append([0,i.name,i.delivery_date,i.foreign_buyer_name,i.final_destination,i.po_no,i.po_date,i.item_code,i.item_name,i.weight_per_unit,item_weight_uom,i.qty,i.uom,i.delivered_qty,item_planned_qty,current_pending_qty,pending_wt,current_stock_qty,stock_qty_wt,required_quantity,i.pch_pallet_size])
	return data

def dispatched_item_report(filters):
	data = []
	items = get_ordered_items(filters)
	item_stock_map = {}
	item_pending_map = {}

	for i in items:
		o_item_planned_qty = get_planned_qty(i.item_code, i.name)
		o_pending = round((i.qty - (i.delivered_qty + o_item_planned_qty)),2)
		o_pending_wt = round((o_pending + i.weight_per_unit),2)	
		sub_items = get_dispatcheded_items(i.name, i.item_code)
		if sub_items:
			for j in sub_items:
				if i.item_code == j.parent_item:
					item_unit_wt = frappe.db.get_value("Item", {'name': j.item_code}, "weight_per_unit")
					item_uom = frappe.db.get_value("Item", {'name': j.item_code}, "weight_uom")
					dlvr = round(i.delivered_qty*(j.qty/i.qty),2)
					planed = round(o_item_planned_qty*(j.qty/i.qty),2)
					pending = round(j.qty - (dlvr+planed)) if(dlvr + planed) > 0 else j.qty
					pending_wt = round((pending * item_unit_wt),2)
					item_stock_map[j.item_code] = get_current_stock_from_bin(j.item_code, filters.warehouse) if j.item_code not in item_stock_map else item_stock_map[j.item_code]
					item_pending_map[j.item_code] = 0 if j.item_code not in item_pending_map else item_pending_map[j.item_code]
					sub_item_stock_qty = item_stock_map[j.item_code]
					sub_item_stock_qty_wt = 0 if sub_item_stock_qty<=0 else round(sub_item_stock_qty * item_unit_wt, 2)

					if sub_item_stock_qty >= pending:
						sub_item_stock_qty = 0 if sub_item_stock_qty <=pending else sub_item_stock_qty
						sub_item_required_qty = (pending - item_stock_map[j.item_code]) if (pending <= item_stock_map[j.item_code]) else item_pending_map[j.item_code]+pending
						item_stock_map[j.item_code]= item_stock_map[j.item_code] - pending
						item_pending_map[j.item_code]= item_pending_map[j.item_code] + pending
					else:
						sub_item_stock_qty = 0 if sub_item_stock_qty <=0 else sub_item_stock_qty
						item_pending_map[j.item_code]= item_pending_map[j.item_code] + (pending if sub_item_stock_qty <= 0 else (pending - sub_item_stock_qty))
						sub_item_required_qty = (pending - item_stock_map[j.item_code]) if (pending < item_stock_map[j.item_code]) else item_pending_map[j.item_code]
						item_stock_map[j.item_code]= item_stock_map[j.item_code] - pending
						

					pallet_size = round(i.pch_pallet_size * (j.qty/i.qty),2)
					data.append([1,i.name,i.delivery_date,i.foreign_buyer_name,
						i.final_destination,i.po_no,i.po_date,j.item_code,j.item_name,
						item_unit_wt,item_uom,j.qty,j.uom,dlvr,planed,pending,pending_wt,
						sub_item_stock_qty,sub_item_stock_qty_wt,sub_item_required_qty,
						pallet_size])
						
		else:
			item_stock_map[i.item_code] = get_current_stock_from_bin(i.item_code, filters.warehouse) if i.item_code not in item_stock_map else item_stock_map[i.item_code]
			item_pending_map[i.item_code] = 0 if i.item_code not in item_pending_map else item_pending_map[i.item_code]
			item_stock_qty = item_stock_map[i.item_code]
			print(item_stock_qty)
			if item_stock_qty >= o_pending:
				item_stock_qty = 0 if item_stock_qty <=o_pending else item_stock_qty
				item_required_qty = (o_pending - item_stock_map[i.item_code]) if (o_pending <= item_stock_map[i.item_code]) else item_pending_map[i.item_code]+o_pending
				item_stock_map[i.item_code]= item_stock_map[i.item_code] - o_pending
				item_pending_map[i.item_code]= item_pending_map[i.item_code] + o_pending
			else:
				item_stock_qty = 0 if item_stock_qty <=0 else item_stock_qty
				item_pending_map[i.item_code]= item_pending_map[i.item_code] + (o_pending if item_stock_qty <= 0 else (o_pending - item_stock_qty))
				item_required_qty = (o_pending - item_stock_map[i.item_code]) if (o_pending < item_stock_map[i.item_code]) else item_pending_map[i.item_code]
				item_stock_map[i.item_code]= item_stock_map[i.item_code] - o_pending
			
			o_stock_wt = item_stock_qty * i.weight_per_unit
			data.append([1,i.name,i.delivery_date,i.foreign_buyer_name,
				i.final_destination,i.po_no,i.po_date,i.item_code,i.item_name,
				i.weight_per_unit,i.weight_uom,i.qty,
				i.uom,i.delivered_qty,o_item_planned_qty,o_pending,o_pending_wt,			
				item_stock_qty,o_stock_wt,item_required_qty,
				i.pch_pallet_size])

	return data

def complete_report(filters):
	data = []
	items = get_ordered_items(filters)

	sub_item_stock_map = {}
	sub_item_pending_map = {}

	for i in items:
		o_item_planned_qty = get_planned_qty(i.item_code, i.name)
		o_pending = round((i.qty - (i.delivered_qty + o_item_planned_qty)),2)
		o_pending_wt = round((o_pending + i.weight_per_unit),2)
		sub_item_stock_map[i.item_code] = get_current_stock_from_bin(i.item_code, filters.warehouse) if i.item_code not in sub_item_stock_map else sub_item_stock_map[i.item_code]
		sub_item_pending_map[i.item_code] = 0 if i.item_code not in sub_item_pending_map else sub_item_pending_map[i.item_code]
		sub_item_stock_qty = sub_item_stock_map[i.item_code]

		if sub_item_stock_qty >= o_pending:
			sub_item_stock_qty = 0 if sub_item_stock_qty <=o_pending else sub_item_stock_qty
			sub_item_required_qty = (o_pending - sub_item_stock_map[i.item_code]) if (o_pending <= sub_item_stock_map[i.item_code]) else sub_item_pending_map[i.item_code]+o_pending
			sub_item_stock_map[i.item_code]= sub_item_stock_map[i.item_code] - o_pending
			sub_item_pending_map[i.item_code]= sub_item_pending_map[i.item_code] + o_pending
		else:
			sub_item_stock_qty = 0 if sub_item_stock_qty <=0 else sub_item_stock_qty
			sub_item_pending_map[i.item_code]= sub_item_pending_map[i.item_code] + (o_pending if sub_item_stock_qty <= 0 else (o_pending - sub_item_stock_qty))
			sub_item_required_qty = (o_pending - sub_item_stock_map[i.item_code]) if (o_pending < sub_item_stock_map[i.item_code]) else sub_item_pending_map[i.item_code]
			sub_item_stock_map[i.item_code]= sub_item_stock_map[i.item_code] - o_pending
			
		o_stock_wt = sub_item_stock_qty * i.weight_per_unit
		data.append([0,i.name,i.delivery_date,i.foreign_buyer_name,
			i.final_destination,i.po_no,i.po_date,i.item_code,i.item_name,
			i.weight_per_unit,i.weight_uom,i.qty,
			i.uom,i.delivered_qty,o_item_planned_qty,o_pending,o_pending_wt,			
			sub_item_stock_qty,o_stock_wt,sub_item_required_qty,
			i.pch_pallet_size])
		
		sub_items = get_dispatcheded_items(i.name, i.item_code)
		if sub_items:
			for j in sub_items:
				if i.item_code == j.parent_item:
					item_unit_wt = frappe.db.get_value("Item", {'name': j.item_code}, "weight_per_unit")
					item_uom = frappe.db.get_value("Item", {'name': j.item_code}, "weight_uom")
					dlvr = round(i.delivered_qty*(j.qty/i.qty),2)
					planed = round(o_item_planned_qty*(j.qty/i.qty),2)
					pending = round(j.qty - (dlvr+planed)) if(dlvr + planed) > 0 else j.qty
					pending_wt = round((pending * item_unit_wt),2)
					sub_item_stock_map[j.item_code] = get_current_stock_from_bin(j.item_code, filters.warehouse) if j.item_code not in sub_item_stock_map else sub_item_stock_map[j.item_code]
					sub_item_pending_map[j.item_code] = 0 if j.item_code not in sub_item_pending_map else sub_item_pending_map[j.item_code]
					sub_item_stock_qty = sub_item_stock_map[j.item_code]
					sub_item_stock_qty_wt = 0 if sub_item_stock_qty<=0 else round(sub_item_stock_qty * item_unit_wt, 2)

					if sub_item_stock_qty >= pending:
						sub_item_stock_qty = 0 if sub_item_stock_qty <=pending else sub_item_stock_qty
						sub_item_required_qty = (pending - sub_item_stock_map[j.item_code]) if (pending <= sub_item_stock_map[j.item_code]) else sub_item_pending_map[j.item_code]+pending
						sub_item_stock_map[j.item_code]= sub_item_stock_map[j.item_code] - pending
						sub_item_pending_map[j.item_code]= sub_item_pending_map[j.item_code] + pending
					else:
						sub_item_stock_qty = 0 if sub_item_stock_qty <=0 else sub_item_stock_qty
						sub_item_pending_map[j.item_code]= sub_item_pending_map[j.item_code] + (pending if sub_item_stock_qty <= 0 else (pending - sub_item_stock_qty))
						sub_item_required_qty = (pending - sub_item_stock_map[j.item_code]) if (pending < sub_item_stock_map[j.item_code]) else sub_item_pending_map[j.item_code]
						sub_item_stock_map[j.item_code]= sub_item_stock_map[j.item_code] - pending
						

					pallet_size = round(i.pch_pallet_size * (j.qty/i.qty),2)
					data.append([1,i.name,i.delivery_date,i.foreign_buyer_name,
						i.final_destination,i.po_no,i.po_date,j.item_code,j.item_name,
						item_unit_wt,item_uom,j.qty,j.uom,dlvr,planed,pending,pending_wt,
						sub_item_stock_qty,sub_item_stock_qty_wt,sub_item_required_qty,
						pallet_size])
						
	
	
	return data