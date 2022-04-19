// Copyright (c) 2022, Atul Sah and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Status Report"] = {
	"filters": [
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd":1
         },

		 {
            "fieldname":"foreign_buyer_name",
            "label": __("Foreign Buyer Name"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd":1
         },

		 {
            "fieldname":"warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "reqd":1
         },

		 {
            "fieldname":"item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "reqd":0
         },
		 
		 {
		    "fieldname":"report_type",
		    "label": __("Report Type"),
			"fieldtype": "Select",
			"options": ["Dispatch Item Report","Set Item Report"],
			"default": "Dispatch Item Report",
		},
		{
		    "fieldname":"from_date",
		    "label": __("From Date"),
		    "fieldtype": "Date",
		    "default": frappe.defaults.get_user_default("year_start_date"),
		    "reqd":1
		},

		{
		    "fieldname":"to_date",
		    "label": __("To Date"),
		    "fieldtype": "Date",
		    "default": frappe.defaults.get_user_default("year_end_date"),
		    "reqd":1
		}

	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "flag" && data && data.flag == 0) {
			value = "<span style='color:red;background-color:red'>" + value + "</span>";
		}
		else if (data.flag == 0) {
			value = "<span style='font-weight: bold'>" + value + "</span>";
		}
		else if (column.fieldname == "flag" && data && data.flag == 1) {
			value = "<span style='color:green;background-color:green'>" + value + "</span>";
		}

		return value;
	}
};