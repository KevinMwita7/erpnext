# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from datetime import datetime
import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	# frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(filters)))
	from_date = filters["from_date"] if "from_date" in filters else "26-10-2020"
	to_date = filters["to_date"] if "to_date" in  filters else datetime.now().strftime('%Y-%m-%d')
	collection_type = "%" + filters["collection_type"] + "%" if "collection_type" in filters else '%%'
	cumulative_data = frappe.db.get_list('Sales Invoice',
	fields = ['sum(base_total) as total_sum', 'remarks'], 
	filters = {
		'creation': ['>=', from_date],
		'creation': ['<=', to_date],
		'remarks': ['like', collection_type if collection_type != "%Others%" else "%No Remarks%"]
	},
	group_by = 'remarks'
	)
	
	# frappe.msgprint(filters["from_date"])
	data = []
	grand_total = 0
	for row in cumulative_data:
		data.append([
			frappe.utils.fmt_money(row["total_sum"], currency="KES"),
			row['remarks'] if row['remarks'] != "No Remarks" else "Others"
		])
		grand_total += float(row["total_sum"])

	data.append([frappe.utils.fmt_money(grand_total, currency="KES"), "Grand Total"])

	return data	

def get_columns():
	return [{
		"fieldname": "total_amount",
		"label": frappe._("Total Amount"),
		"fieldtype": "Data",
		"width": 550
	},
	{
		"fieldname": "collection_type",
		"label": frappe._("Collection Type"),
		"fieldtype": "Data",
		"width": 550
	}]