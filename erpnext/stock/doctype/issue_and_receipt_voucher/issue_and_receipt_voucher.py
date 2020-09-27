# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IssueandReceiptVoucher(Document):
	@frappe.whitelist()
	def get_items_from_purchase_order(source_name, target_doc=None):
		frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(source_name)))
		def update_item(obj, target, source_parent):
			pass
		
		def set_missing_values(source, target):
			frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(source)))
			frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(target)))
			target.issued_date = frappe.utils.nowdate()

		doc = get_mapped_doc("Purchase Order", source_name, {
			"Purchase Invoice": {
				"doctype": "Issue and Receipt Voucher",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Purchase Invoice Item": {
				"doctype": "Issue and Receipt Voucher Item",
				"field_map": {
					# Source      Target
					"item_code": "item_description",
					"uom": "batch_no",
					"qty": "qty_required"
				},
				# "postprocess": update_item,
			}
		}, target_doc, set_missing_values)

		return doc
