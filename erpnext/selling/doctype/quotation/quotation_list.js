frappe.listview_settings['Quotation'] = {
	add_fields: ["customer_name", "base_grand_total", "status",
		"company", "currency", 'valid_till'],

	onload: function(listview) {
		listview.page.fields_dict.quotation_to.get_query = function() {
			return {
				"filters": {
					"name": ["in", ["Customer", "Lead"]],
				}
			};
		};
	},

	get_indicator: function(doc) {
		if(doc.status==="Open") {
<<<<<<< HEAD
			return [__("Open"), "orange", "status,=,Open"];
=======
			if (doc.valid_till && doc.valid_till < frappe.datetime.nowdate()) {
				return [__("Expired"), "darkgrey", "valid_till,<," + frappe.datetime.nowdate()];
			} else {
				return [__("Open"), "orange", "status,=,Open"];
			}
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
		} else if(doc.status==="Ordered") {
			return [__("Ordered"), "green", "status,=,Ordered"];
		} else if(doc.status==="Lost") {
			return [__("Lost"), "darkgrey", "status,=,Lost"];
		} else if(doc.status==="Expired") {
			return [__("Expired"), "darkgrey", "status,=,Expired"];
		}
	}
};
