frappe.listview_settings['Material Receipt'] = {
	add_fields: ["purpose", "status"],
	get_indicator: function(doc) {
		if(doc.status=="Stopped") {
			return [__("Stopped"), "red", "status,=,Stopped"];
		} else if(doc.docstatus==0) {
			return [__("Pending"), "orange", "status,=,Pending"];
		}  else if(doc.docstatus==1) {
			return [__("Submitted"), "green", "status,=,Submitted"];
		}
	}
};
