// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Cash Flow"] = $.extend({},
		erpnext.financial_statements);

	// The last item in the array is the definition for Presentation Currency
	// filter. It won't be used in cash flow for now so we pop it. Please take
	// of this if you are working here.

<<<<<<< HEAD
	frappe.query_reports["Cash Flow"]["filters"].splice(5, 1);

	frappe.query_reports["Cash Flow"]["filters"].push(
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check"
		}
	);
=======
	frappe.query_reports["Cash Flow"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check"
	});

	frappe.query_reports["Cash Flow"]["filters"].push({
		"fieldname": "include_default_book_entries",
		"label": __("Include Default Book Entries"),
		"fieldtype": "Check"
	});
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
});