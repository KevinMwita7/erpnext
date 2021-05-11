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
        /*{
			"fieldname":"collection_type",
			"label": __("Collection Type"),
			"fieldtype": "Data",
			"default": ""
		},*/
		{
			"fieldname":"collection_type",
			"label": __("Collection Type"),
			"fieldtype": "Select",
			"options": "''\nCash\nNHIF\nChild Under Five\nOld Age\nException - Child Under 5\nLinda Mama\nPrisoner\nUnable to Meet Cost\nException - Person Aged 65 or Above\nOthers",
			"default": ""
		},		
    ]
};