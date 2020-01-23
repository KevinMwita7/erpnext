
from __future__ import unicode_literals
import frappe, base64, hashlib, hmac, json
from frappe import _

def verify_request():
	woocommerce_settings = frappe.get_doc("Woocommerce Settings")
	sig = base64.b64encode(
		hmac.new(
			woocommerce_settings.secret.encode('utf8'),
			frappe.request.data,
			hashlib.sha256
		).digest()
	)

	if frappe.request.data and \
		frappe.get_request_header("X-Wc-Webhook-Signature") and \
		not sig == bytes(frappe.get_request_header("X-Wc-Webhook-Signature").encode()):
			frappe.throw(_("Unverified Webhook Data"))
	frappe.set_user(woocommerce_settings.creation_user)

@frappe.whitelist(allow_guest=True)
def order(*args, **kwargs):
	try:
		_order(*args, **kwargs)
	except Exception:
		error_message = frappe.get_traceback()+"\n\n Request Data: \n"+json.loads(frappe.request.data).__str__()
		frappe.log_error(error_message, "WooCommerce Error")
		raise
<<<<<<< HEAD

def _order(*args, **kwargs):
	woocommerce_settings = frappe.get_doc("Woocommerce Settings")
	if frappe.flags.woocomm_test_order_data:
		order = frappe.flags.woocomm_test_order_data
		event = "created"

	elif frappe.request and frappe.request.data:
		verify_request()
		try:
			order = json.loads(frappe.request.data)
		except ValueError:
			#woocommerce returns 'webhook_id=value' for the first request which is not JSON
			order = frappe.request.data
		event = frappe.get_request_header("X-Wc-Webhook-Event")

	else:
		return "success"

	if event == "created":
		raw_billing_data = order.get("billing")
		customer_name = raw_billing_data.get("first_name") + " " + raw_billing_data.get("last_name")
		link_customer_and_address(raw_billing_data, customer_name)
		link_items(order.get("line_items"), woocommerce_settings)
		create_sales_order(order, woocommerce_settings, customer_name)

def link_customer_and_address(raw_billing_data, customer_name):
	customer_woo_com_email = raw_billing_data.get("email")
	customer_exists = frappe.get_value("Customer", {"woocommerce_email": customer_woo_com_email})
	if not customer_exists:
		# Create Customer
=======


def _order(*args, **kwargs):
	woocommerce_settings = frappe.get_doc("Woocommerce Settings")
	if frappe.flags.woocomm_test_order_data:
		fd = frappe.flags.woocomm_test_order_data
		event = "created"

	elif frappe.request and frappe.request.data:
		verify_request()
		fd = json.loads(frappe.request.data)
		event = frappe.get_request_header("X-Wc-Webhook-Event")

	else:
		return "success"

	if event == "created":
		raw_billing_data = fd.get("billing")
		customer_woo_com_email = raw_billing_data.get("email")

		if frappe.get_value("Customer",{"woocommerce_email": customer_woo_com_email}):
			# Edit
			link_customer_and_address(raw_billing_data,1)
		else:
			# Create
			link_customer_and_address(raw_billing_data,0)


		items_list = fd.get("line_items")
		for item in items_list:

			item_woo_com_id = item.get("product_id")

			if frappe.get_value("Item",{"woocommerce_id": item_woo_com_id}) or\
				frappe.get_value("Item",{"item_name": item.get('name')}):
				#Edit
				link_item(item,1)
			else:
				link_item(item,0)


		customer_name = raw_billing_data.get("first_name") + " " + raw_billing_data.get("last_name")

		new_sales_order = frappe.new_doc("Sales Order")
		new_sales_order.customer = customer_name

		created_date = fd.get("date_created").split("T")
		new_sales_order.transaction_date = created_date[0]

		new_sales_order.po_no = fd.get("id")
		new_sales_order.woocommerce_id = fd.get("id")
		new_sales_order.naming_series = woocommerce_settings.sales_order_series or "SO-WOO-"

		placed_order_date = created_date[0]
		raw_date = datetime.datetime.strptime(placed_order_date, "%Y-%m-%d")
		raw_delivery_date = frappe.utils.add_to_date(raw_date,days = 7)
		order_delivery_date_str = raw_delivery_date.strftime('%Y-%m-%d')
		order_delivery_date = str(order_delivery_date_str)

		new_sales_order.delivery_date = order_delivery_date
		default_set_company = frappe.get_doc("Global Defaults")
		company = raw_billing_data.get("company") or default_set_company.default_company
		found_company = frappe.get_doc("Company",{"name":company})
		company_abbr = found_company.abbr

		new_sales_order.company = company

		for item in items_list:
			woocomm_item_id = item.get("product_id")
			found_item = frappe.get_doc("Item",{"woocommerce_id": woocomm_item_id})

			ordered_items_tax = item.get("total_tax")

			new_sales_order.append("items",{
				"item_code": found_item.item_code,
				"item_name": found_item.item_name,
				"description": found_item.item_name,
				"delivery_date":order_delivery_date,
				"uom": woocommerce_settings.uom or _("Nos"),
				"qty": item.get("quantity"),
				"rate": item.get("price"),
				"warehouse": woocommerce_settings.warehouse or "Stores" + " - " + company_abbr
				})

			add_tax_details(new_sales_order,ordered_items_tax,"Ordered Item tax",0)

		# shipping_details = fd.get("shipping_lines") # used for detailed order
		shipping_total = fd.get("shipping_total")
		shipping_tax = fd.get("shipping_tax")

		add_tax_details(new_sales_order,shipping_tax,"Shipping Tax",1)
		add_tax_details(new_sales_order,shipping_total,"Shipping Total",1)

		new_sales_order.submit()

		frappe.db.commit()

def link_customer_and_address(raw_billing_data,customer_status):

	if customer_status == 0:
		# create
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
		customer = frappe.new_doc("Customer")
	else:
		# Edit Customer
		customer = frappe.get_doc("Customer", {"woocommerce_email": customer_woo_com_email})
		old_name = customer.customer_name

	customer.customer_name = customer_name
	customer.woocommerce_email = customer_woo_com_email
	customer.flags.ignore_mandatory = True
	customer.save() 

	if customer_exists:
		frappe.rename_doc("Customer", old_name, customer_name)
		address = frappe.get_doc("Address", {"woocommerce_email": customer_woo_com_email})
	else:
		address = frappe.new_doc("Address")

	address.address_line1 = raw_billing_data.get("address_1", "Not Provided")
	address.address_line2 = raw_billing_data.get("address_2", "Not Provided")
	address.city = raw_billing_data.get("city", "Not Provided")
	address.woocommerce_email = customer_woo_com_email
	address.address_type = "Billing"
	address.country = frappe.get_value("Country", {"code": raw_billing_data.get("country", "IN").lower()})
	address.state = raw_billing_data.get("state")
	address.pincode = raw_billing_data.get("postcode")
	address.phone = raw_billing_data.get("phone")
	address.email_id = customer_woo_com_email
	address.append("links", {
		"link_doctype": "Customer",
		"link_name": customer.customer_name
	})
	address.flags.ignore_mandatory = True
	address = address.save()

	if customer_exists:
		old_address_title = address.name
		new_address_title = customer.customer_name + "-billing"
		address.address_title = customer.customer_name
		address.save()

		frappe.rename_doc("Address", old_address_title, new_address_title)

<<<<<<< HEAD
def link_items(items_list, woocommerce_settings):
	for item_data in items_list:
		item_woo_com_id = item_data.get("product_id")
=======
def link_item(item_data,item_status):
	woocommerce_settings = frappe.get_doc("Woocommerce Settings")

	if item_status == 0:
		#Create Item
		item = frappe.new_doc("Item")

	if item_status == 1:
		#Edit Item
		item_woo_com_id = item_data.get("product_id")
		item = frappe.get_doc("Item",{"woocommerce_id": item_woo_com_id})

	item.item_name = str(item_data.get("name"))
	item.item_code = "woocommerce - " + str(item_data.get("product_id"))
	item.woocommerce_id = str(item_data.get("product_id"))
	item.item_group = _("WooCommerce Products")
	item.stock_uom = woocommerce_settings.uom or _("Nos")
	item.save()
	frappe.db.commit()

def add_tax_details(sales_order,price,desc,status):

	woocommerce_settings = frappe.get_doc("Woocommerce Settings")
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2

		if frappe.get_value("Item", {"woocommerce_id": item_woo_com_id}):
			#Edit Item
			item = frappe.get_doc("Item", {"woocommerce_id": item_woo_com_id})
		else:
			#Create Item
			item = frappe.new_doc("Item")
	
		item.item_name = item_data.get("name")
		item.item_code = _("woocommerce - {0}").format(item_data.get("product_id"))
		item.woocommerce_id = item_data.get("product_id")
		item.item_group = _("WooCommerce Products")
		item.stock_uom = woocommerce_settings.uom or _("Nos")
		item.flags.ignore_mandatory = True
		item.save()

def create_sales_order(order, woocommerce_settings, customer_name):	
	new_sales_order = frappe.new_doc("Sales Order")
	new_sales_order.customer = customer_name

	new_sales_order.po_no = new_sales_order.woocommerce_id = order.get("id")
	new_sales_order.naming_series = woocommerce_settings.sales_order_series or "SO-WOO-"

	created_date = order.get("date_created").split("T")
	new_sales_order.transaction_date = created_date[0]
	delivery_after = woocommerce_settings.delivery_after_days or 7
	new_sales_order.delivery_date = frappe.utils.add_days(created_date[0], delivery_after)

	new_sales_order.company = woocommerce_settings.company

	set_items_in_sales_order(new_sales_order, woocommerce_settings, order)
	new_sales_order.flags.ignore_mandatory = True
	new_sales_order.insert()
	new_sales_order.submit()

	frappe.db.commit()

<<<<<<< HEAD
def set_items_in_sales_order(new_sales_order, woocommerce_settings, order):
	company_abbr = frappe.db.get_value('Company', woocommerce_settings.company, 'abbr')

	for item in order.get("line_items"):
		woocomm_item_id = item.get("product_id")
		found_item = frappe.get_doc("Item", {"woocommerce_id": woocomm_item_id})

		ordered_items_tax = item.get("total_tax")

		new_sales_order.append("items",{
			"item_code": found_item.item_code,
			"item_name": found_item.item_name,
			"description": found_item.item_name,
			"delivery_date": new_sales_order.delivery_date,
			"uom": woocommerce_settings.uom or _("Nos"),
			"qty": item.get("quantity"),
			"rate": item.get("price"),
			"warehouse": woocommerce_settings.warehouse or _("Stores - {0}").format(company_abbr)
			})

		add_tax_details(new_sales_order, ordered_items_tax, "Ordered Item tax", woocommerce_settings.tax_account)

	# shipping_details = order.get("shipping_lines") # used for detailed order

	add_tax_details(new_sales_order, order.get("shipping_tax"), "Shipping Tax", woocommerce_settings.f_n_f_account)
	add_tax_details(new_sales_order, order.get("shipping_total"), "Shipping Total", woocommerce_settings.f_n_f_account)
			
def add_tax_details(sales_order, price, desc, tax_account_head):
	sales_order.append("taxes", {
		"charge_type":"Actual",
		"account_head": tax_account_head,
		"tax_amount": price,
		"description": desc
	})
=======
	sales_order.append("taxes",{
							"charge_type":"Actual",
							"account_head": account_head_type,
							"tax_amount": price,
							"description": desc
							})
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
