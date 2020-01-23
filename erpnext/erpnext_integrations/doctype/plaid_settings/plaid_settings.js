// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.provide("erpnext.integrations");

frappe.ui.form.on('Plaid Settings', {
<<<<<<< HEAD
	enabled: function(frm) {
		frm.toggle_reqd('plaid_client_id', frm.doc.enabled);
		frm.toggle_reqd('plaid_secret', frm.doc.enabled);
		frm.toggle_reqd('plaid_public_key', frm.doc.enabled);
		frm.toggle_reqd('plaid_env', frm.doc.enabled);
	},
	refresh: function(frm) {
		if(frm.doc.enabled) {
			frm.add_custom_button('Link a new bank account', () => {
				new erpnext.integrations.plaidLink(frm);
			});
		}
=======
	link_new_account: function(frm) {
		new erpnext.integrations.plaidLink(frm);
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
	}
});

erpnext.integrations.plaidLink = class plaidLink {
	constructor(parent) {
		this.frm = parent;
		this.product = ["transactions", "auth"];
		this.plaidUrl = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
		this.init_config();
	}

	init_config() {
		const me = this;
<<<<<<< HEAD
		me.plaid_env = me.frm.doc.plaid_env;
		me.plaid_public_key = me.frm.doc.plaid_public_key;
		me.client_name = frappe.boot.sitename;
		me.init_plaid();
=======
		frappe.xcall('erpnext.erpnext_integrations.doctype.plaid_settings.plaid_settings.plaid_configuration')
			.then(result => {
				if (result !== "disabled") {
					if (result.plaid_env == undefined || result.plaid_public_key == undefined) {
						frappe.throw(__("Please add valid Plaid api keys in site_config.json first"));
					}
					me.plaid_env = result.plaid_env;
					me.plaid_public_key = result.plaid_public_key;
					me.client_name = result.client_name;
					me.init_plaid();
				} else {
					frappe.throw(__("Please save your document before adding a new account"));
				}
			});
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
	}

	init_plaid() {
		const me = this;
		me.loadScript(me.plaidUrl)
			.then(() => {
				me.onScriptLoaded(me);
			})
			.then(() => {
				if (me.linkHandler) {
					me.linkHandler.open();
				}
			})
			.catch((error) => {
				me.onScriptError(error);
			});
	}

	loadScript(src) {
		return new Promise(function (resolve, reject) {
			if (document.querySelector('script[src="' + src + '"]')) {
				resolve();
				return;
			}
			const el = document.createElement('script');
			el.type = 'text/javascript';
			el.async = true;
			el.src = src;
			el.addEventListener('load', resolve);
			el.addEventListener('error', reject);
			el.addEventListener('abort', reject);
			document.head.appendChild(el);
		});
	}

	onScriptLoaded(me) {
		me.linkHandler = window.Plaid.create({
			clientName: me.client_name,
			env: me.plaid_env,
			key: me.plaid_public_key,
			onSuccess: me.plaid_success,
			product: me.product
		});
	}

	onScriptError(error) {
		frappe.msgprint('There was an issue loading the link-initialize.js script');
		frappe.msgprint(error);
	}

	plaid_success(token, response) {
		const me = this;

		frappe.prompt({
			fieldtype:"Link",
			options: "Company",
			label:__("Company"),
			fieldname:"company",
			reqd:1
		}, (data) => {
			me.company = data.company;
			frappe.xcall('erpnext.erpnext_integrations.doctype.plaid_settings.plaid_settings.add_institution', {token: token, response: response})
				.then((result) => {
					frappe.xcall('erpnext.erpnext_integrations.doctype.plaid_settings.plaid_settings.add_bank_accounts', {response: response,
						bank: result, company: me.company});
				})
				.then(() => {
					frappe.show_alert({message:__("Bank accounts added"), indicator:'green'});
				});
		}, __("Select a company"), __("Continue"));
	}
<<<<<<< HEAD
};
=======
};
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
