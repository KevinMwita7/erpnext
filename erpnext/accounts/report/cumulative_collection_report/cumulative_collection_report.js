frappe.query_reports["Cumulative Collection Report"] = {
    "filters": [
        {
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": "2020-10-26"
		},
        {
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
        {
			"fieldname":"collection_type",
			"label": __("Collection Type"),
			"fieldtype": "Data",
			"default": "Cash"
		},
    ]
};