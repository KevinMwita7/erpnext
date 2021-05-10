# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext import get_default_currency
from frappe.model.meta import get_field_precision

def execute(filters=None):
	columns = get_column()
	args = get_args()
	data = get_ordered_to_be_billed_data(args)
	return columns, data

def get_column():
	return [
		_("Sales Order") + ":Link/Sales Order:120", 
		_("Date") + ":Date:100",
		# _("Supplier") + ":Link/Customer:120", 
		_("Customer Name") + "::120",
		# _("Project") + ":Link/Project:120", 
		_("Item Code") + ":Link/Item:120", 
		_("Amount") + ":Currency:100", 
		_("Billed Amount") + ":Currency:100", 
		_("Pending Amount") + ":Currency:100",
		_("Item Name") + "::120", 
		_("Description") + "::120", 
		_("Company") + ":Link/Company:120",
	]

def get_args():
	return {'doctype': 'Sales Order', 'party': 'customer', 
		'date': 'transaction_date', 'order': 'transaction_date', 'order_by': 'asc'}

def get_ordered_to_be_billed_data(args):
	doctype, party = args.get('doctype'), args.get('party')
	child_tab = doctype + " Item"
	precision = get_field_precision(frappe.get_meta(child_tab).get_field("billed_amt"),
		currency=get_default_currency()) or 2

	project_field = get_project_field(doctype, party)

	# old
	#return frappe.db.sql("""
	#	Select
	#		`{parent_tab}`.name, `{parent_tab}`.{date_field}, `{parent_tab}`.{party}, `{parent_tab}`.{party}_name,
	#		{project_field}, `{child_tab}`.item_code, `{child_tab}`.base_amount,
	#		(`{child_tab}`.billed_amt * ifnull(`{parent_tab}`.conversion_rate, 1)),
	#		(`{child_tab}`.base_amount - (`{child_tab}`.billed_amt * ifnull(`{parent_tab}`.conversion_rate, 1))),
	#		`{child_tab}`.item_name, `{child_tab}`.description, `{parent_tab}`.company
	#	from
	#		`{parent_tab}`, `{child_tab}`
	#	where
	#		`{parent_tab}`.name = `{child_tab}`.parent and `{parent_tab}`.docstatus = 1
	#		and `{parent_tab}`.status not in ('Closed', 'Completed')
	#		and `{child_tab}`.amount > 0 and round(`{child_tab}`.billed_amt *
	#		ifnull(`{parent_tab}`.conversion_rate, 1), {precision}) < `{child_tab}`.base_amount
	#	order by
	#		`{parent_tab}`.{order} {order_by}
	#	""".format(parent_tab = 'tab' + doctype, child_tab = 'tab' + child_tab, precision= precision, party = party,
	#		date_field = args.get('date'), project_field = project_field, order= args.get('order'), order_by = args.get('order_by')))
	
	# new
	return frappe.db.sql("""
		Select
			`{parent_tab}`.name, `{parent_tab}`.{date_field}, `{parent_tab}`.{party}_name,
			`{child_tab}`.item_code, `{child_tab}`.base_amount,
			(`{child_tab}`.billed_amt * ifnull(`{parent_tab}`.conversion_rate, 1)),
			(`{child_tab}`.base_amount - (`{child_tab}`.billed_amt * ifnull(`{parent_tab}`.conversion_rate, 1))),
			`{child_tab}`.item_name, `{child_tab}`.description, `{parent_tab}`.company
		from
			`{parent_tab}`, `{child_tab}`
		where
			`{parent_tab}`.name = `{child_tab}`.parent and `{parent_tab}`.docstatus = 1
			and `{parent_tab}`.status not in ('Closed', 'Completed')
			and `{child_tab}`.amount > 0 and round(`{child_tab}`.billed_amt *
			ifnull(`{parent_tab}`.conversion_rate, 1), {precision}) < `{child_tab}`.base_amount
		order by
			`{parent_tab}`.{order} {order_by}
		""".format(parent_tab = 'tab' + doctype, child_tab = 'tab' + child_tab, precision= precision, party = party,
			date_field = args.get('date'), project_field = project_field, order= args.get('order'), order_by = args.get('order_by')))	

def get_project_field(doctype, party):
	if party == "supplier": doctype = doctype + ' Item'
	return "`tab%s`.project"%(doctype)		