from __future__ import unicode_literals
from frappe import _


def get_data():
	return[
		{
			"label": _("Google Data"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Production Entry",
					"onboard": 1,
					"dependencies": [],
					"description": _("Production Entry"),
				},	
			]
		},
        {	"label": _("Key Report"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Sales Order Status Report",
					"doctype": "Sales Order",
				},	
				{
					"type": "report",
					"is_query_report": True,
					"name": "Set Unset Report",
					"doctype": "Sales Order",
				},

			]
		}
    ]