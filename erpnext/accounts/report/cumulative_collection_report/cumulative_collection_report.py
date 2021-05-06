# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data

def get_data(filters):
	frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(filters)))
	cumulative_data = frappe.db.sql("""
	SELECT sum(base_total), if(remarks='No Remarks',"Others",remarks) 
	FROM 4fc07e5444f76a8c.`tabSales Invoice` group by remarks;
	""")

	data = [
		[
			row['base_total'],
			row['remarks']
		] for row in cumulative_data]

	return data	

def get_columns():
	return [{
		"fieldname": "total_amount",
		"label": _("Total Amount"),
		"fieldtype": "Data",
		"width": 550
	},
	{
		"fieldname": "collection_type",
		"label": _("Collection Type"),
		"fieldtype": "Data",
		"width": 550
	}]