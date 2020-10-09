# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.controllers.stock_controller import StockController
from frappe import _
from frappe.utils import cstr, cint, flt, comma_or, getdate, nowdate, formatdate, format_time

class MaterialReceipt(StockController):
	def validate(self):
		self.validate_items()


	def validate_items(self):
		stock_items = self.get_stock_items()
		serialized_items = self.get_serialized_items()
		frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(self.get("items"))))
		if not len(self.get("items")):
			frappe.throw(_("At least one item is required in the items table"))

		for item in self.get("items"):
			if item.item_code not in stock_items:
				frappe.throw(_("{0} is not a stock Item").format(item.item_code))

			item_details = self.get_item_details(frappe._dict(
				{"item_code": item.item_code, "company": self.company,
				"project": self.project, "uom": item.uom, 's_warehouse': item.s_warehouse}),
				for_update=True)

			for f in ("uom", "stock_uom", "description", "item_name", "expense_account", "cost_center", "conversion_factor"):
					if f in ["stock_uom", "conversion_factor"] or not item.get(f):
						item.set(f, item_details.get(f))

			if not item.transfer_qty and item.qty:
				item.transfer_qty = ( flt(item.qty, item.precision("qty")) * flt(item.conversion_factor, item.precision("conversion_factor")) )

			if (self.purpose in ("Material Transfer") and not item.serial_no and item.item_code in serialized_items):
				frappe.throw(_("Row #{0}: Please specify Serial No for Item {1}").format(item.idx, item.item_code),
					frappe.MandatoryError)

	def validate_warehouse(self):
		"""perform various (sometimes conditional) validations on warehouse"""

		validate_for_manufacture_repack = any([d.bom_no for d in self.get("items")])
		for d in self.get('items'):
			if not (d.s_warehouse and d.t_warehouse):
				frappe.throw(_("Source warehouse and target warehouse is mandatory for row {0}").format(d.idx))

			if d.s_warehouse == d.t_warehouse:
				frappe.throw(_("Source warehouse and target warehouse cannot be the same for row {0}").format(d.idx))

			if cstr(d.s_warehouse) == cstr(d.t_warehouse) and not self.purpose == "Material Transfer for Manufacture":
				frappe.throw(_("Source and target warehouse cannot be same for row {0}").format(d.idx))