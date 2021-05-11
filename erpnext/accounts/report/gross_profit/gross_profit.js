// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Gross Profit"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			// "default": frappe.defaults.get_user_default("year_start_date")
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			// // "default": frappe.defaults.get_user_default("year_end_date")
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"sales_invoice",
			"label": __("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice"
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			//"options": "Invoice\nItem Code\nItem Group\nBrand\nWarehouse\nCustomer\nCustomer Group\nTerritory\nSales Person\nProject",
			"options": "Invoice\nItem Code\nItem Group\nBrand\nCustomer",
			"default": "Invoice"
		},
	]
}
