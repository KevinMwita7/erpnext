# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class IssueandReceiptVoucher(Document):
	pass

@frappe.whitelist()
def get_items_from_purchase_order(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		pass
	
	def set_missing_values(source, target):
		frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(source)))
		frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(target)))
		#target.issued_date = frappe.utils.nowdate()

	doc = get_mapped_doc("Purchase Order", source_name, {
		"Purchase Order": {
			"doctype": "Issue and Receipt Voucher",
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc, set_missing_values)

	return doc