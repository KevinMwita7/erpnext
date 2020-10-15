// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Receipt', {
	onload: function(frm) {
		console.log(frm);
		console.log(cur_frm);
		if(!frm.doc.items.length) {
			cur_frm.add_child("items");
			cur_frm.refresh_field("items");
		}
	},
	onload_post_render: function(frm) {
		frm.get_field("items").grid.set_multiple_add("item_code", "qty");
	},
});
