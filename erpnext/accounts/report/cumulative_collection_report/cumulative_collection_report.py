# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import msgprint, _, as_json, db

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	msgprint("<pre>{}</pre>".format(as_json(filters)))
	cumulative_data = db.sql("""
	SELECT sum(base_total) as total_sum, IF(remarks='No Remarks',"Others",remarks) as remarks
	FROM `tabSales Invoice` GROUP BY remarks;
	""", as_dict=1)
	
	msgprint("<pre>{}</pre>".format(as_json(cumulative_data)))
	data = [
		[
			row['total_sum'],
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