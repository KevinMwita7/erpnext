# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# ERPNext - web based ERP (http://erpnext.com)
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext

from frappe.utils import cstr, flt, getdate, new_line_sep, nowdate, add_days
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.get_item_details import get_bin_details
from erpnext.stock.stock_balance import update_bin_qty, get_indented_qty
from erpnext.controllers.buying_controller import BuyingController
from erpnext.controllers.stock_controller import update_gl_entries_after
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.buying.utils import check_for_closed_status, validate_for_items
from erpnext.accounts.utils import get_fiscal_year
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.accounts.general_ledger import make_gl_entries, delete_gl_entries, process_gl_map
from erpnext.stock.doctype.serial_no.serial_no import update_serial_nos_after_submit, get_serial_nos
from erpnext.stock import get_warehouse_account_map
from frappe.utils import cint, flt, cstr

from six import string_types

form_grid_templates = {
	"items": "templates/form_grid/material_request_grid.html"
}

class MaterialRequest(BuyingController):
	def get_feed(self):
		return _("{0}: {1}").format(self.status, self.material_request_type)

	def check_if_already_pulled(self):
		pass

	def validate_qty_against_so(self):
		so_items = {} # Format --> {'SO/00001': {'Item/001': 120, 'Item/002': 24}}
		for d in self.get('items'):
			if d.sales_order:
				if not d.sales_order in so_items:
					so_items[d.sales_order] = {d.item_code: flt(d.qty)}
				else:
					if not d.item_code in so_items[d.sales_order]:
						so_items[d.sales_order][d.item_code] = flt(d.qty)
					else:
						so_items[d.sales_order][d.item_code] += flt(d.qty)

		for so_no in so_items.keys():
			for item in so_items[so_no].keys():
				already_indented = frappe.db.sql("""select sum(qty)
					from `tabMaterial Request Item`
					where item_code = %s and sales_order = %s and
					docstatus = 1 and parent != %s""", (item, so_no, self.name))
				already_indented = already_indented and flt(already_indented[0][0]) or 0

				actual_so_qty = frappe.db.sql("""select sum(stock_qty) from `tabSales Order Item`
					where parent = %s and item_code = %s and docstatus = 1""", (so_no, item))
				actual_so_qty = actual_so_qty and flt(actual_so_qty[0][0]) or 0

				if actual_so_qty and (flt(so_items[so_no][item]) + already_indented > actual_so_qty):
					frappe.throw(_("Material Request of maximum {0} can be made for Item {1} against Sales Order {2}").format(actual_so_qty - already_indented, item, so_no))

	# Validate
	# ---------------------
	def validate(self):
		super(MaterialRequest, self).validate()

		self.validate_schedule_date()
		self.validate_uom_is_integer("uom", "qty")

		if not self.status:
			self.status = "Draft"

		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status,
			["Draft", "Submitted", "Stopped", "Cancelled", "Pending",
			"Partially Ordered", "Ordered", "Issued", "Transferred"])

		validate_for_items(self)

		self.set_title()
		# self.validate_qty_against_so()
		# NOTE: Since Item BOM and FG quantities are combined, using current data, it cannot be validated
		# Though the creation of Material Request from a Production Plan can be rethought to fix this

	def set_title(self):
		'''Set title as comma separated list of items'''
		if not self.title:
			items = ', '.join([d.item_name for d in self.items][:3])
			self.title = _('{0} Request for {1}').format(self.material_request_type, items)[:100]

	def on_submit(self):
		# frappe.db.set(self, 'status', 'Submitted')
		self.update_requested_qty()
		self.update_requested_qty_in_production_plan()
		if self.material_request_type == 'Purchase':
			self.validate_budget()

	def before_save(self):
		self.set_status(update=True)
		#if(self.workflow_state == "Acknowledged Supply" and self.doctype == "Material Request" and self.material_request_type == "Material Transfer"):
		if(self.workflow_state == "Approved by Supplying"):
			self.supplying_approver = frappe.session.user

	def before_submit(self):
		self.set_status(update=True)
		if(self.workflow_state == "Approved by Receiving"):
			self.receiving_approver = frappe.session.user

	def before_cancel(self):
		# if MRQ is already closed, no point saving the document
		check_for_closed_status(self.doctype, self.name)
		self.set_status(update=True, status='Cancelled')

	def check_modified_date(self):
		mod_db = frappe.db.sql("""select modified from `tabMaterial Request` where name = %s""",
			self.name)
		date_diff = frappe.db.sql("""select TIMEDIFF('%s', '%s')"""
			% (mod_db[0][0], cstr(self.modified)))

		if date_diff and date_diff[0][0]:
			frappe.throw(_("{0} {1} has been modified. Please refresh.").format(_(self.doctype), self.name))

	def update_status(self, status):
		self.check_modified_date()
		self.status_can_change(status)
		self.set_status(update=True, status=status)
		self.update_requested_qty()

	def status_can_change(self, status):
		"""
		validates that `status` is acceptable for the present controller status
		and throws an Exception if otherwise.
		"""
		if self.status and self.status == 'Cancelled':
			# cancelled documents cannot change
			if status != self.status:
				frappe.throw(
					_("{0} {1} is cancelled so the action cannot be completed").
						format(_(self.doctype), self.name),
					frappe.InvalidStatusError
				)

		elif self.status and self.status == 'Draft':
			# draft document to pending only
			if status != 'Pending':
				frappe.throw(
					_("{0} {1} has not been submitted so the action cannot be completed").
						format(_(self.doctype), self.name),
					frappe.InvalidStatusError
				)

	def on_cancel(self):
		self.update_requested_qty()
		self.update_requested_qty_in_production_plan()

	def update_completed_qty(self, mr_items=None, update_modified=True):
		if self.material_request_type == "Purchase":
			return

		if not mr_items:
			mr_items = [d.name for d in self.get("items")]

		for d in self.get("items"):
			if d.name in mr_items:
				if self.material_request_type in ("Material Issue", "Material Transfer"):
					d.ordered_qty =  flt(frappe.db.sql("""select sum(transfer_qty)
						from `tabStock Entry Detail` where material_request = %s
						and material_request_item = %s and docstatus = 1""",
						(self.name, d.name))[0][0])

					if d.ordered_qty and d.ordered_qty > d.stock_qty:
						frappe.throw(_("The total Issue / Transfer quantity {0} in Material Request {1}  \
							cannot be greater than requested quantity {2} for Item {3}").format(d.ordered_qty, d.parent, d.qty, d.item_code))

				elif self.material_request_type == "Manufacture":
					d.ordered_qty = flt(frappe.db.sql("""select sum(qty)
						from `tabWork Order` where material_request = %s
						and material_request_item = %s and docstatus = 1""",
						(self.name, d.name))[0][0])

				frappe.db.set_value(d.doctype, d.name, "ordered_qty", d.ordered_qty)

		target_ref_field = 'qty' if self.material_request_type == "Manufacture" else 'stock_qty'
		self._update_percent_field({
			"target_dt": "Material Request Item",
			"target_parent_dt": self.doctype,
			"target_parent_field": "per_ordered",
			"target_ref_field": target_ref_field,
			"target_field": "ordered_qty",
			"name": self.name,
		}, update_modified)

	def update_requested_qty(self, mr_item_rows=None):
		"""update requested qty (before ordered_qty is updated)"""
		item_wh_list = []
		for d in self.get("items"):
			if (not mr_item_rows or d.name in mr_item_rows) and [d.item_code, d.warehouse] not in item_wh_list \
					and frappe.db.get_value("Item", d.item_code, "is_stock_item") == 1 and d.warehouse:
				item_wh_list.append([d.item_code, d.warehouse])

		for item_code, warehouse in item_wh_list:
			update_bin_qty(item_code, warehouse, {
				"indented_qty": get_indented_qty(item_code, warehouse)
			})

	def update_requested_qty_in_production_plan(self):
		production_plans = []
		for d in self.get('items'):
			if d.production_plan and d.material_request_plan_item:
				qty = d.qty if self.docstatus == 1 else 0
				frappe.db.set_value('Material Request Plan Item',
					d.material_request_plan_item, 'requested_qty', qty)

				if d.production_plan not in production_plans:
					production_plans.append(d.production_plan)

		for production_plan in production_plans:
			doc = frappe.get_doc('Production Plan', production_plan)
			doc.set_status()
			doc.db_set('status', doc.status)

	def make_gl_entries(self, stock_entry, gl_entries=None, repost_future_gle=True, from_repost=False):
		if stock_entry.docstatus == 2:
			delete_gl_entries(voucher_type=stock_entry.doctype, voucher_no=stock_entry.name)

		if cint(erpnext.is_perpetual_inventory_enabled(stock_entry.company)):
			warehouse_account = get_warehouse_account_map(stock_entry.company)

			if stock_entry.docstatus==1:
				if not gl_entries:
					gl_entries = stock_entry.get_gl_entries(warehouse_account)
				make_gl_entries(gl_entries, from_repost=from_repost)

			if repost_future_gle:
				items, warehouses = get_items_and_warehouses(stock_entry)
				update_gl_entries_after(stock_entry.posting_date, stock_entry.posting_time, [], [],
					warehouse_account, company=stock_entry.company)

	def validate_reserved_serial_no_consumption(self, stock_entry):
		for item in stock_entry.items:
			if item.s_warehouse and not item.t_warehouse and item.serial_no:
				for sr in get_serial_nos(item.serial_no):
					sales_order = frappe.db.get_value("Serial No", sr, "sales_order")
					if sales_order:
						frappe.throw(_("Item {0} (Serial No: {1}) cannot be consumed as is reserverd\
						 to fullfill Sales Order {2}.").format(item.item_code, sr, sales_order))

def update_completed_and_requested_qty(stock_entry, method=None):
	# Make deductions from stock if it is a stock entry or the workflow_state is Acknowledged Supply(if the supplier agrees to supplier then automatically deduct from the stock)
	if stock_entry.doctype == "Stock Entry":
		material_request_map = {}

		for d in stock_entry.get("items"):
			if d.material_request:
				material_request_map.setdefault(d.material_request, []).append(d.material_request_item)

		for mr, mr_item_rows in material_request_map.items():
			if mr and mr_item_rows:
				mr_obj = frappe.get_doc("Material Request", mr)

				if mr_obj.status in ["Stopped", "Cancelled"]:
					frappe.throw(_("{0} {1} is cancelled or stopped").format(_("Material Request"), mr),
						frappe.InvalidStatusError)

				mr_obj.update_completed_qty(mr_item_rows)
				mr_obj.update_requested_qty(mr_item_rows)

def set_missing_values(source, target_doc):
	if target_doc.doctype == "Purchase Order" and getdate(target_doc.schedule_date) <  getdate(nowdate()):
		target_doc.schedule_date = None
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")

def update_item(obj, target, source_parent):
	target.conversion_factor = obj.conversion_factor
	target.qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor
	target.stock_qty = (target.qty * target.conversion_factor)
	if getdate(target.schedule_date) < getdate(nowdate()):
		target.schedule_date = None

@frappe.whitelist()
def update_status(name, status):
	material_request = frappe.get_doc('Material Request', name)
	material_request.check_permission('write')
	material_request.update_status(status)

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):

	def postprocess(source, target_doc):
		if frappe.flags.args and frappe.flags.args.default_supplier:
			# items only for given default supplier
			supplier_items = []
			for d in target_doc.items:
				default_supplier = get_item_defaults(d.item_code, target_doc.company).get('default_supplier')
				if frappe.flags.args.default_supplier == default_supplier:
					supplier_items.append(d)
			target_doc.items = supplier_items

		set_missing_values(source, target_doc)

	def select_item(d):
		return d.ordered_qty < d.stock_qty

	doclist = get_mapped_doc("Material Request", source_name, 	{
		"Material Request": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Material Request Item": {
			"doctype": "Purchase Order Item",
			"field_map": [
				["name", "material_request_item"],
				["parent", "material_request"],
				["uom", "stock_uom"],
				["uom", "uom"],
				["sales_order", "sales_order"],
				["sales_order_item", "sales_order_item"]
			],
			"postprocess": update_item,
			"condition": select_item
		}
	}, target_doc, postprocess)

	return doclist

@frappe.whitelist()
def make_request_for_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc("Material Request", source_name, 	{
		"Material Request": {
			"doctype": "Request for Quotation",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Material Request Item": {
			"doctype": "Request for Quotation Item",
			"field_map": [
				["name", "material_request_item"],
				["parent", "material_request"],
				["uom", "uom"]
			]
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_purchase_order_based_on_supplier(source_name, target_doc=None):
	if target_doc:
		if isinstance(target_doc, string_types):
			import json
			target_doc = frappe.get_doc(json.loads(target_doc))
		target_doc.set("items", [])

	material_requests, supplier_items = get_material_requests_based_on_supplier(source_name)

	def postprocess(source, target_doc):
		target_doc.supplier = source_name
		if getdate(target_doc.schedule_date) < getdate(nowdate()):
			target_doc.schedule_date = None
		target_doc.set("items", [d for d in target_doc.get("items")
			if d.get("item_code") in supplier_items and d.get("qty") > 0])

		set_missing_values(source, target_doc)

	for mr in material_requests:
		target_doc = get_mapped_doc("Material Request", mr, 	{
			"Material Request": {
				"doctype": "Purchase Order",
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "stock_uom"],
					["uom", "uom"]
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.ordered_qty < doc.qty
			}
		}, target_doc, postprocess)

	return target_doc

def get_material_requests_based_on_supplier(supplier):
	supplier_items = [d.parent for d in frappe.db.get_all("Item Default",
		{"default_supplier": supplier}, 'parent')]
	if supplier_items:
		material_requests = frappe.db.sql_list("""select distinct mr.name
			from `tabMaterial Request` mr, `tabMaterial Request Item` mr_item
			where mr.name = mr_item.parent
				and mr_item.item_code in (%s)
				and mr.material_request_type = 'Purchase'
				and mr.per_ordered < 99.99
				and mr.docstatus = 1
				and mr.status != 'Stopped'
			order by mr_item.item_code ASC""" % ', '.join(['%s']*len(supplier_items)),
			tuple(supplier_items))
	else:
		material_requests = []
	return material_requests, supplier_items

def get_default_supplier_query(doctype, txt, searchfield, start, page_len, filters):
	doc = frappe.get_doc("Material Request", filters.get("doc"))
	item_list = []
	for d in doc.items:
		item_list.append(d.item_code)

	return frappe.db.sql("""select default_supplier
		from `tabItem Default`
		where parent in ({0}) and
		default_supplier IS NOT NULL
		""".format(', '.join(['%s']*len(item_list))),tuple(item_list))

@frappe.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)

	doclist = get_mapped_doc("Material Request", source_name, {
		"Material Request": {
			"doctype": "Supplier Quotation",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Material Request Item": {
			"doctype": "Supplier Quotation Item",
			"field_map": {
				"name": "material_request_item",
				"parent": "material_request",
				"sales_order": "sales_order"
			}
		}
	}, target_doc, postprocess)

	return doclist

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor \
			if flt(obj.stock_qty) > flt(obj.ordered_qty) else 0
		target.qty = qty
		target.transfer_qty = qty * obj.conversion_factor
		target.conversion_factor = obj.conversion_factor
		target.actual_qty = get_bin_details(obj.item_code, obj.warehouse).actual_qty

		if source_parent.material_request_type == "Material Transfer":
			#frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(obj)))
			target.t_warehouse = obj.warehouse
			# Set the quantity requested and quantity issued
			target.qty_requested = target.qty
			target.qty = 0
			if source_parent.source_warehouse:
				target.s_warehouse = source_parent.source_warehouse
		else:
			target.s_warehouse = obj.warehouse

	def set_missing_values(source, target):
		target.purpose = source.material_request_type
		if source.job_card:
			target.purpose = 'Material Transfer for Manufacture'

		target.run_method("calculate_rate_and_amount")
		target.set_job_card_data()
	
	doclist = get_mapped_doc("Material Request", source_name, {
		"Material Request": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["in", ["Material Transfer", "Material Issue", "Material Receipt"]]
			}
		},
		"Material Request Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"name": "material_request_item",
				"parent": "material_request",
				"uom": "stock_uom",
			},
			"postprocess": update_item,
			"condition": lambda doc: doc.ordered_qty < doc.stock_qty
		}
	}, target_doc, set_missing_values)
	return doclist

@frappe.whitelist()
def make_material_receipt(source_name, target_doc=None):
	# Set the material receipt parent
	def set_missing_values(source, target):
		items = []
		for item in source.items:
			temp = {}
			qty = flt(flt(item.stock_qty) - flt(item.ordered_qty))/ item.conversion_factor \
				if flt(item.stock_qty) > flt(item.ordered_qty) else 0
			temp["qty"] = qty
			temp["transfer_qty"] = qty * item.conversion_factor
			temp["conversion_factor"] = item.conversion_factor
			temp["actual_qty"] = get_bin_details(item.item_code, item.warehouse).actual_qty

			if source.material_request_type == "Material Transfer":
				#frappe.msgprint("<pre>{}</pre>".format(frappe.as_json(obj)))
				temp["t_warehouse"] = item.warehouse
				# Set the quantity requested and quantity issued
				temp["qty_requested"] = item.qty
				# Qty approved
				temp["qty"] = 0
				if source.source_warehouse:
					temp["s_warehouse"] = source.source_warehouse
			else:
				temp["s_warehouse"] = item.warehouse
			items.append(temp)

		target.items = items
		target.purpose = source.material_request_type
		target.run_method("calculate_rate_and_amount")
		target.posting_date = nowdate()
		target.material_request_name = source.name
		#target.set_job_card_data()

	doclist = get_mapped_doc("Material Request", source_name, {
		"Material Request": {
			"doctype": "Material Receipt",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Material Request Item": {
			"doctype": "Material Receipt Item",
			"field_map": {
				"name": "material_request_item",
				"parent": "material_request",
				"uom": "stock_uom",
			},
			#"postprocess": update_item,
			"condition": lambda doc: doc.ordered_qty < doc.stock_qty
		}
	}, target_doc, set_missing_values)
	
	return doclist

@frappe.whitelist()
def raise_work_orders(material_request):
	mr= frappe.get_doc("Material Request", material_request)
	errors =[]
	work_orders = []
	default_wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", "default_wip_warehouse")

	for d in mr.items:
		if (d.qty - d.ordered_qty) >0:
			if frappe.db.exists("BOM", {"item": d.item_code, "is_default": 1}):
				wo_order = frappe.new_doc("Work Order")
				wo_order.update({
					"production_item": d.item_code,
					"qty": d.qty - d.ordered_qty,
					"fg_warehouse": d.warehouse,
					"wip_warehouse": default_wip_warehouse,
					"description": d.description,
					"stock_uom": d.stock_uom,
					"expected_delivery_date": d.schedule_date,
					"sales_order": d.sales_order,
					"bom_no": get_item_details(d.item_code).bom_no,
					"material_request": mr.name,
					"material_request_item": d.name,
					"planned_start_date": mr.transaction_date,
					"company": mr.company
				})

				wo_order.set_work_order_operations()
				wo_order.save()

				work_orders.append(wo_order.name)
			else:
				errors.append(_("Row {0}: Bill of Materials not found for the Item {1}").format(d.idx, d.item_code))

	if work_orders:
		message = ["""<a href="#Form/Work Order/%s" target="_blank">%s</a>""" % \
			(p, p) for p in work_orders]
		msgprint(_("The following Work Orders were created:") + '\n' + new_line_sep(message))

	if errors:
		frappe.throw(_("Productions Orders cannot be raised for:") + '\n' + new_line_sep(errors))

	return work_orders

@frappe.whitelist
def get_items_and_warehouses(stock_entry):
	items, warehouses = [], []

	if ("items" in stock_entry):
		item_doclist = stock_entry.get("items")

	if item_doclist:
		for d in item_doclist:
			if d.item_code and d.item_code not in items:
				items.append(d.item_code)

			if d.get("warehouse") and d.warehouse not in warehouses:
				warehouses.append(d.warehouse)

			if stock_entry.doctype == "Material Request" and stock_entry.material_request_type == "Material Receipt":
				if d.get("s_warehouse") and d.s_warehouse not in warehouses:
					warehouses.append(d.s_warehouse)
				if d.get("t_warehouse") and d.t_warehouse not in warehouses:
					warehouses.append(d.t_warehouse)

	return items, warehouses

@frappe.whitelist
def update_stock_ledger(stock_entry):
	sl_entries = []

	# make sl entries for source warehouse first, then do for target warehouse
	for d in stock_entry.get('items'):
		if cstr(d.s_warehouse):
			sl_entries.append(get_sl_entries(stock_entry, d, {
				"warehouse": cstr(d.s_warehouse),
				"actual_qty": -flt(d.transfer_qty),
				"incoming_rate": 0
			}))

	for d in stock_entry.get('items'):
		if cstr(d.t_warehouse):
			sl_entries.append(get_sl_entries(stock_entry, d, {
				"warehouse": cstr(d.t_warehouse),
				"actual_qty": flt(d.transfer_qty),
				"incoming_rate": flt(d.valuation_rate)
			}))

	# On cancellation, make stock ledger entry for
	# target warehouse first, to update serial no values properly

		# if cstr(d.s_warehouse) and self.docstatus == 2:
		# 	sl_entries.append(self.get_sl_entries(d, {
		# 		"warehouse": cstr(d.s_warehouse),
		# 		"actual_qty": -flt(d.transfer_qty),
		# 		"incoming_rate": 0
		# 	}))

	if stock_entry.docstatus == 2:
		sl_entries.reverse()

	make_stock_ledger_entries(sl_entries, stock_entry.amended_from and 'Yes' or 'No')

def get_sl_entries(parent, d, args):
	sl_dict = frappe._dict({
		"item_code": d.get("item_code", None),
		"warehouse": d.get("warehouse", None),
		"posting_date": parent.posting_date,
		"posting_time": parent.posting_time,
		'fiscal_year': get_fiscal_year(parent.posting_date, company=parent.company)[0],
		"voucher_type": parent.doctype,
		"voucher_no": parent.name,
		"voucher_detail_no": d.name,
		"actual_qty": (parent.docstatus==1 and 1 or -1)*flt(d.get("stock_qty")),
		"stock_uom": frappe.db.get_value("Item", args.get("item_code") or d.get("item_code"), "stock_uom"),
		"incoming_rate": 0,
		"company": parent.company,
		"batch_no": cstr(d.get("batch_no")).strip(),
		"serial_no": d.get("serial_no"),
		"project": d.get("project") or parent.get('project'),
		"is_cancelled": parent.docstatus==2 and "Yes" or "No"
	})

	sl_dict.update(args)
	return sl_dict

def make_stock_ledger_entries(sl_entries, is_amended=None, allow_negative_stock=False, via_landed_cost_voucher=False):
	from erpnext.stock.stock_ledger import make_sl_entries
	make_sl_entries(sl_entries, is_amended, allow_negative_stock, via_landed_cost_voucher)