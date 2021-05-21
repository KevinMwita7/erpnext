# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import flt
from frappe.model.meta import get_field_precision
from frappe.utils.xlsxutils import handle_html
from erpnext.accounts.report.sales_register.sales_register import get_mode_of_payments

def execute(filters=None):
	return _execute(filters)

def _execute(filters=None, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = {}
	filters.update({"from_date": filters.get("date_range") and filters.get("date_range")[0], "to_date": filters.get("date_range") and filters.get("date_range")[1]})
	columns = get_columns(additional_table_columns)

	item_list = get_items(filters, additional_query_columns)
	mode_of_payments = get_mode_of_payments(set([d.parent for d in item_list]))
	so_dn_map = get_delivery_notes_against_sales_order(item_list)

	data = []
	for d in item_list:
		delivery_note = None
		if d.delivery_note:
			delivery_note = d.delivery_note
		elif d.so_detail:
			delivery_note = ", ".join(so_dn_map.get(d.so_detail, []))

		if not delivery_note and d.update_stock:
			delivery_note = d.parent

		row = [
			d.item_code, 
			d.item_name, 
			d.item_group, 
			d.description, 
			d.parent, 
			d.posting_date, 
			]

		if additional_query_columns:
			for col in additional_query_columns:
				row.append(d.get(col))

		row += [
			", ".join(mode_of_payments.get(d.parent, [])),
		]

		if d.stock_uom != d.uom and d.stock_qty:
			row += [
			d.base_net_amount]
		else:
			row += [
			d.base_net_amount]


		row += [
			d.base_net_amount 
		]

		data.append(row)

	return columns, data

def get_columns(additional_table_columns):
	columns = [
		_("Item Code") + ":Link/Item:120", 
		_("Item Name") + "::120",
		_("Item Group") + ":Link/Item Group:100", 
		"Description::150", 
		_("Invoice") + ":Link/Sales Invoice:150",
		_("Posting Date") + ":Date:120", 
	]

	if additional_table_columns:
		columns += additional_table_columns

	columns += [
		_("Mode of Payment") + "::120", 
		_("Amount") + ":Currency/currency:120"
	]

	return columns

def get_conditions(filters):
	conditions = ""

	for opts in (("company", " and company=%(company)s"),
		("item_code", " and `tabSales Invoice Item`.item_code = %(item_code)s"),
		("from_date", " and `tabSales Invoice`.posting_date>=%(from_date)s"),
		("to_date", " and `tabSales Invoice`.posting_date<=%(to_date)s"),
		("company_gstin", " and `tabSales Invoice`.company_gstin = %(company_gstin)s"),
		("invoice_type", " and `tabSales Invoice`.invoice_type = %(invoice_type)s")):
			if filters.get(opts[0]):
				conditions += opts[1]

	if filters.get("mode_of_payment"):
		conditions += """ and exists(select name from `tabSales Invoice Payment`
			where parent=`tabSales Invoice`.name
				and ifnull(`tabSales Invoice Payment`.mode_of_payment, '') = %(mode_of_payment)s)"""

	if filters.get("warehouse"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=`tabSales Invoice`.name
			 	and ifnull(`tabSales Invoice Item`.warehouse, '') = %(warehouse)s)"""


	if filters.get("brand"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=`tabSales Invoice`.name
			 	and ifnull(`tabSales Invoice Item`.brand, '') = %(brand)s)"""

	if filters.get("item_group"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=`tabSales Invoice`.name
			 	and ifnull(`tabSales Invoice Item`.item_group, '') = %(item_group)s)"""


	return conditions

def get_items(filters, additional_query_columns):
	conditions = get_conditions(filters)
	match_conditions = frappe.build_match_conditions("Sales Invoice")

	if match_conditions:
		match_conditions = " and {0} ".format(match_conditions)

	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	return frappe.db.sql("""
		select
			`tabSales Invoice Item`.name, `tabSales Invoice Item`.parent,
			`tabSales Invoice`.posting_date, `tabSales Invoice`.debit_to,
			`tabSales Invoice Item`.item_code, `tabSales Invoice Item`.item_name,
			`tabSales Invoice Item`.item_group, `tabSales Invoice Item`.description, `tabSales Invoice Item`.sales_order,
			`tabSales Invoice Item`.delivery_note, `tabSales Invoice Item`.income_account,
			`tabSales Invoice Item`.stock_uom, `tabSales Invoice Item`.base_net_amount, `tabSales Invoice Item`.so_detail,
			{0}
		from `tabSales Invoice`, `tabSales Invoice Item`
		where `tabSales Invoice`.name = `tabSales Invoice Item`.parent
			and `tabSales Invoice`.docstatus = 1 %s %s
		group by `tabSales Invoice Item`.item_name
		order by `tabSales Invoice`.posting_date desc, `tabSales Invoice Item`.item_code desc
		""".format(additional_query_columns or '') % (conditions, match_conditions), filters, as_dict=1)

def get_delivery_notes_against_sales_order(item_list):
	so_dn_map = frappe._dict()
	so_item_rows = list(set([d.so_detail for d in item_list]))

	if so_item_rows:
		delivery_notes = frappe.db.sql("""
			select parent, so_detail
			from `tabDelivery Note Item`
			where docstatus=1 and so_detail in (%s)
			group by so_detail, parent
		""" % (', '.join(['%s']*len(so_item_rows))), tuple(so_item_rows), as_dict=1)

		for dn in delivery_notes:
			so_dn_map.setdefault(dn.so_detail, []).append(dn.parent)

	return so_dn_map

