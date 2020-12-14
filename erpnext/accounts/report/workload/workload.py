# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe import _

def execute(filters=None):
	if not filters: 
		filters = frappe._dict({})

	columns = data = []
	
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select customer,grand_total,modified_by,total_qty,
	age,gender,patient_id,ordered_by,transaction_date FROM `tabSales Order` where %s""" % conditions , as_list=1)
							
	for cust in query:
		data.append(cust)
	
	columns = get_columns()
	
	return columns, data

	
	
def get_columns():
	return [
		_("Customer") + ":Link/Customer:120",
		_("Grand Total") + ":Currency:120",
		_("Modified By") + ":Data:120",
		_("Total Quantity") + ":Int:120",
		_("Age") + ":Int:120",
		_("Gender") + ":Data:120",
		_("Patient_Id") + ":Link/Customer:120",
		_("Ordered By") + ":Data:120",
		_("Transaction Date") + ":Date:80",
	]

def get_conditions(filters):
	conditions = ""
	
	if filters.get("modified_by"): 
		conditions += "modified_by = '%(modified_by)s'" % filters.get("modified_by")
	elif not filters.get("modified_by"): 
		conditions += "modified_by = '*'"
	if filters.get("from_date"):
		conditions += " and transaction_date >= '%(from_date)s'" % filters.get("from_date")
	if filters.get("to_date"):
		conditions += " and transaction_date <= '%(to_date)s'" % filters.get("to_date")
		
	return conditions
