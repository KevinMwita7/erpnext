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
		pass
		#frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(source)))
		#frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(target)))

	doc = get_mapped_doc("Purchase Order", source_name, {
		"Purchase Order": {
			"doctype": "Issue and Receipt Voucher",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Order Item": {
			"doctype": "Issue and Receipt Voucher Items",
			"field_map": {
				# Source      Target
				"item_code": "item_description",
				"uom": "unit_of_issue",
				"qty": "qty_required"
			},
			# "postprocess": update_item,
		}
	}, target_doc, set_missing_values)

	return doc
	
@frappe.whitelist()
def get_items_from_material_request(source_name, target_doc=None):
	doc = get_mapped_doc("Material Request", source_name, {
	"Material Request": {
		"doctype": "Issue and Receipt Voucher",
		"validation": {
			"docstatus": ["=", 1]
		}
	},
	"Material Request Item": {
		"doctype": "Issue and Receipt Voucher Items",
		"field_map": {
			# Source      Target
			"item_code": "item_description",
			"uom": "unit_of_issue",
			"qty": "qty_required"
		}
	}
}, target_doc)

	return doc
