frappe.query_reports["Cumulative Collection Report"] = {
    "filters": [
        {
			"fieldname":"creation",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
        {
			"fieldname":"creation",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},        
    ]
};