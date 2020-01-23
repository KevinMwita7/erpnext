// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Department Sales"] = {
    "filters": [
        {
			"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Date",
		"width": "80",
		"default": frappe.datetime.month_start()
	},
	{
		"fieldname":"to_date",
		"label": __("To Date"),
		"fieldtype": "Date",
		"width": "80",
		"default": frappe.datetime.month_end()
		},
    ]
};