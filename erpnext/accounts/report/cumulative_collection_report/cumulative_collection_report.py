# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from datetime import datetime
from frappe import msgprint, _, as_json, db

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	# msgprint("<pre>{}</pre>".format(as_json(filters)))
	from_date = filters["from_date"] if "from_date" in filters else "26-10-2020"
	to_date = filters["to_date"] if "to_date" in  filters else datetime.now().strftime('%Y-%m-%d')
	collection_type = filters["collection_type"] if "collection_type" in filters else ''
	msgprint("""
	SELECT sum(base_total) as total_sum, IF(remarks='No Remarks',"Others",remarks) as remarks
	FROM `tabSales Invoice` 
	WHERE creation >= {from_date} AND creation <= {to_date} AND remarks LIKE '%%{collection_type}%%'
	GROUP BY remarks;
	""".format(from_date = from_date, to_date = to_date, collection_type = collection_type))

	cumulative_data = db.sql("""
	SELECT sum(base_total) as total_sum, IF(remarks='No Remarks',"Others",remarks) as remarks
	FROM `tabSales Invoice` 
	WHERE creation >= {from_date} AND creation <= {to_date} AND remarks LIKE '%%{collection_type}%%'
	GROUP BY remarks;
	""".format(from_date = from_date, to_date = to_date, collection_type = collection_type), as_dict=1)
	
	# msgprint(filters["from_date"])
	data = []
	grand_total = 0
	for row in cumulative_data:
		data.append([row['total_sum'], row['remarks']])
		grand_total += float(row["total_sum"])

	data.append([grand_total, "Grand Total"])

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