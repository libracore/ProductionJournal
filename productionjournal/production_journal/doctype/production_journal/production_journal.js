// Copyright (c) 2018, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Journal', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		cur_frm.set_query("production_order", function() {
			return {
				"filters": {
					"status": "Completed"
				}
			};
		});
	}
});