// Copyright (c) 2018, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Journal', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__("Reload Data"), function() {
				frappe.call({
				   method: "productionjournal.production_journal.doctype.production_journal.production_journal.clear_data",
				   args: {
						"name": frm.doc.name
				   },
				   callback: function(response) {
						frappe.show_alert('Data reloaded', 5);
						cur_frm.reload_doc();
				   }
				});
			});
		}
	}
});