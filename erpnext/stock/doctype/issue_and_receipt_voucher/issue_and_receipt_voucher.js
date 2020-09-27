// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Issue and Receipt Voucher', {
	refresh: function(frm) {
		frm.add_custom_button(__('Purchase Order'), function() {
			erpnext.utils.map_current_doc({
				method: "erpnext.stock.doctype.issue_and_receipt_voucher.issue_and_receipt_voucher.get_items_from_purchase_order",
				source_doctype: "Purchase Order",
				target: frm,
				setters: {
					// supplier: frm.doc.supplier || undefined,
				},
				/*get_query_filters: {
					docstatus: 1,
					status: ["!=", "Closed"],
					per_billed: ["<", 99.99],
					company: frm.doc.company
				}*/
			})
		}, __("Get items from"));

		frm.add_custom_button(__('Material Request'), function() {
			erpnext.utils.map_current_doc({
				method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice",
				source_doctype: "Purchase Order",
				target: frm,
				setters: {
					// supplier: frm.doc.supplier || undefined,
				},
				/*get_query_filters: {
					docstatus: 1,
					status: ["!=", "Closed"],
					per_billed: ["<", 99.99],
					company: frm.doc.company
				}*/
			})
		}, __("Get items from"));		
	},
});
