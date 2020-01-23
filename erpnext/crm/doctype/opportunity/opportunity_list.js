frappe.listview_settings['Opportunity'] = {
	add_fields: ["customer_name", "opportunity_type", "opportunity_from", "status"],
	get_indicator: function(doc) {
		var indicator = [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		if(doc.status=="Quotation") {
			indicator[1] = "green";
		}
		return indicator;
	},
	onload: function(listview) {
		var method = "erpnext.crm.doctype.opportunity.opportunity.set_multiple_status";

		listview.page.add_menu_item(__("Set as Open"), function() {
			listview.call_for_selected_items(method, {"status": "Open"});
		});

		listview.page.add_menu_item(__("Set as Closed"), function() {
			listview.call_for_selected_items(method, {"status": "Closed"});
		});

<<<<<<< HEAD
		if(listview.page.fields_dict.opportunity_from) {
			listview.page.fields_dict.opportunity_from.get_query = function() {
				return {
					"filters": {
						"name": ["in", ["Customer", "Lead"]],
					}
				};
			};
		}
=======
		listview.page.fields_dict.opportunity_from.get_query = function() {
			return {
				"filters": {
					"name": ["in", ["Customer", "Lead"]],
				}
			};
		};
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
	}
};
