# coding: utf-8
"""
Provide a report and downloadable CSV according to the German DATEV format.

- Query report showing only the columns that contain data, formatted nicely for
  dispay to the user.
- CSV download functionality `download_datev_csv` that provides a CSV file with
  all required columns. Used to import the data into the DATEV Software.
"""
from __future__ import unicode_literals
<<<<<<< HEAD
import datetime
import json
import zlib
import zipfile
import six
from six import BytesIO
=======
import json
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
from six import string_types
import frappe
from frappe import _
import pandas as pd
<<<<<<< HEAD
from .datev_constants import DataCategory
from .datev_constants import Transactions
from .datev_constants import DebtorsCreditors
from .datev_constants import AccountNames
from .datev_constants import QUERY_REPORT_COLUMNS
=======
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2


def execute(filters=None):
	"""Entry point for frappe."""
<<<<<<< HEAD
	validate(filters)
	result = get_transactions(filters, as_dict=0)
	columns = QUERY_REPORT_COLUMNS
=======
	validate_filters(filters)
	result = get_gl_entries(filters, as_dict=0)
	columns = get_columns()
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2

	return columns, result


<<<<<<< HEAD
def validate(filters):
	"""Make sure all mandatory filters and settings are present."""
	if not filters.get('company'):
		frappe.throw(_('<b>Company</b> is a mandatory filter.'))

	if not filters.get('from_date'):
		frappe.throw(_('<b>From Date</b> is a mandatory filter.'))

	if not filters.get('to_date'):
		frappe.throw(_('<b>To Date</b> is a mandatory filter.'))

	try:
		frappe.get_doc('DATEV Settings', filters.get('company'))
	except frappe.DoesNotExistError:
		frappe.throw(_('Please create <b>DATEV Settings</b> for Company <b>{}</b>.').format(filters.get('company')))


def get_transactions(filters, as_dict=1):
=======
def validate_filters(filters):
	"""Make sure all mandatory filters are present."""
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if not filters.get('from_date'):
		frappe.throw(_('{0} is mandatory').format(_('From Date')))

	if not filters.get('to_date'):
		frappe.throw(_('{0} is mandatory').format(_('To Date')))


def get_columns():
	"""Return the list of columns that will be shown in query report."""
	columns = [
		{
			"label": "Umsatz (ohne Soll/Haben-Kz)",
			"fieldname": "Umsatz (ohne Soll/Haben-Kz)",
			"fieldtype": "Currency",
		},
		{
			"label": "Soll/Haben-Kennzeichen",
			"fieldname": "Soll/Haben-Kennzeichen",
			"fieldtype": "Data",
		},
		{
			"label": "Kontonummer",
			"fieldname": "Kontonummer",
			"fieldtype": "Data",
		},
		{
			"label": "Gegenkonto (ohne BU-Schlüssel)",
			"fieldname": "Gegenkonto (ohne BU-Schlüssel)",
			"fieldtype": "Data",
		},
		{
			"label": "Belegdatum",
			"fieldname": "Belegdatum",
			"fieldtype": "Date",
		},
		{
			"label": "Buchungstext",
			"fieldname": "Buchungstext",
			"fieldtype": "Text",
		},
		{
			"label": "Beleginfo - Art 1",
			"fieldname": "Beleginfo - Art 1",
			"fieldtype": "Data",
		},
		{
			"label": "Beleginfo - Inhalt 1",
			"fieldname": "Beleginfo - Inhalt 1",
			"fieldtype": "Data",
		},
		{
			"label": "Beleginfo - Art 2",
			"fieldname": "Beleginfo - Art 2",
			"fieldtype": "Data",
		},
		{
			"label": "Beleginfo - Inhalt 2",
			"fieldname": "Beleginfo - Inhalt 2",
			"fieldtype": "Data",
		}
	]

	return columns


def get_gl_entries(filters, as_dict):
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
	"""
	Get a list of accounting entries.

	Select GL Entries joined with Account and Party Account in order to get the
	account numbers. Returns a list of accounting entries.

	Arguments:
	filters -- dict of filters to be passed to the sql query
	as_dict -- return as list of dicts [0,1]
	"""
	gl_entries = frappe.db.sql("""
<<<<<<< HEAD
		SELECT
=======
		select
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2

			/* either debit or credit amount; always positive */
			case gl.debit when 0 then gl.credit else gl.debit end as 'Umsatz (ohne Soll/Haben-Kz)',

			/* 'H' when credit, 'S' when debit */
			case gl.debit when 0 then 'H' else 'S' end as 'Soll/Haben-Kennzeichen',

			/* account number or, if empty, party account number */
			coalesce(acc.account_number, acc_pa.account_number) as 'Kontonummer',

			/* against number or, if empty, party against number */
			coalesce(acc_against.account_number, acc_against_pa.account_number) as 'Gegenkonto (ohne BU-Schlüssel)',
			
			gl.posting_date as 'Belegdatum',
			gl.remarks as 'Buchungstext',
			gl.voucher_type as 'Beleginfo - Art 1',
			gl.voucher_no as 'Beleginfo - Inhalt 1',
			gl.against_voucher_type as 'Beleginfo - Art 2',
			gl.against_voucher as 'Beleginfo - Inhalt 2'

<<<<<<< HEAD
		FROM `tabGL Entry` gl
=======
		from `tabGL Entry` gl
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2

			/* Statistisches Konto (Debitoren/Kreditoren) */
			left join `tabParty Account` pa
			on gl.against = pa.parent
			and gl.company = pa.company

			/* Kontonummer */
			left join `tabAccount` acc 
			on gl.account = acc.name

			/* Gegenkonto-Nummer */
			left join `tabAccount` acc_against 
			on gl.against = acc_against.name

			/* Statistische Kontonummer */
			left join `tabAccount` acc_pa
			on pa.account = acc_pa.name

			/* Statistische Gegenkonto-Nummer */
			left join `tabAccount` acc_against_pa 
			on pa.account = acc_against_pa.name

<<<<<<< HEAD
		WHERE gl.company = %(company)s 
		AND DATE(gl.posting_date) >= %(from_date)s
		AND DATE(gl.posting_date) <= %(to_date)s
		ORDER BY 'Belegdatum', gl.voucher_no""", filters, as_dict=as_dict, as_utf8=1)
=======
		where gl.company = %(company)s 
		and DATE(gl.posting_date) >= %(from_date)s
		and DATE(gl.posting_date) <= %(to_date)s
		order by 'Belegdatum', gl.voucher_no""", filters, as_dict=as_dict)
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2

	return gl_entries


<<<<<<< HEAD
def get_customers(filters):
	"""
	Get a list of Customers.

	Arguments:
	filters -- dict of filters to be passed to the sql query
	"""
	return frappe.db.sql("""
		SELECT

			acc.account_number as 'Konto',
			cus.customer_name as 'Name (Adressatentyp Unternehmen)',
			case cus.customer_type when 'Individual' then 1 when 'Company' then 2 else 0 end as 'Adressatentyp',
			adr.address_line1 as 'Straße',
			adr.pincode as 'Postleitzahl',
			adr.city as 'Ort',
			UPPER(country.code) as 'Land',
			adr.address_line2 as 'Adresszusatz',
			con.email_id as 'E-Mail',
			coalesce(con.mobile_no, con.phone) as 'Telefon',
			cus.website as 'Internet',
			cus.tax_id as 'Steuernummer',
			ccl.credit_limit as 'Kreditlimit (Debitor)'

		FROM `tabParty Account` par

			left join `tabAccount` acc
			on acc.name = par.account

			left join `tabCustomer` cus
			on cus.name = par.parent

			left join `tabAddress` adr
			on adr.name = cus.customer_primary_address

			left join `tabCountry` country
			on country.name = adr.country

			left join `tabContact` con
			on con.name = cus.customer_primary_contact

			left join `tabCustomer Credit Limit` ccl
			on ccl.parent = cus.name
			and ccl.company = par.company

		WHERE par.company = %(company)s
		AND par.parenttype = 'Customer'""", filters, as_dict=1, as_utf8=1)


def get_suppliers(filters):
	"""
	Get a list of Suppliers.

	Arguments:
	filters -- dict of filters to be passed to the sql query
	"""
	return frappe.db.sql("""
		SELECT

			acc.account_number as 'Konto',
			sup.supplier_name as 'Name (Adressatentyp Unternehmen)',
			case sup.supplier_type when 'Individual' then '1' when 'Company' then '2' else '0' end as 'Adressatentyp',
			adr.address_line1 as 'Straße',
			adr.pincode as 'Postleitzahl',
			adr.city as 'Ort',
			UPPER(country.code) as 'Land',
			adr.address_line2 as 'Adresszusatz',
			con.email_id as 'E-Mail',
			coalesce(con.mobile_no, con.phone) as 'Telefon',
			sup.website as 'Internet',
			sup.tax_id as 'Steuernummer',
			case sup.on_hold when 1 then sup.release_date else null end as 'Zahlungssperre bis'

		FROM `tabParty Account` par

			left join `tabAccount` acc
			on acc.name = par.account

			left join `tabSupplier` sup
			on sup.name = par.parent

			left join `tabDynamic Link` dyn_adr
			on dyn_adr.link_name = sup.name
			and dyn_adr.link_doctype = 'Supplier'
			and dyn_adr.parenttype = 'Address'
			
			left join `tabAddress` adr
			on adr.name = dyn_adr.parent
			and adr.is_primary_address = '1'

			left join `tabCountry` country
			on country.name = adr.country

			left join `tabDynamic Link` dyn_con
			on dyn_con.link_name = sup.name
			and dyn_con.link_doctype = 'Supplier'
			and dyn_con.parenttype = 'Contact'

			left join `tabContact` con
			on con.name = dyn_con.parent
			and con.is_primary_contact = '1'

		WHERE par.company = %(company)s
		AND par.parenttype = 'Supplier'""", filters, as_dict=1, as_utf8=1)


def get_account_names(filters):
	return frappe.get_list("Account", 
		fields=["account_number as Konto", "name as Kontenbeschriftung"], 
		filters={"company": filters.get("company"), "is_group": "0"})


def get_datev_csv(data, filters, csv_class):
	"""
	Fill in missing columns and return a CSV in DATEV Format.

	For automatic processing, DATEV requires the first line of the CSV file to
	hold meta data such as the length of account numbers oder the category of
	the data.

	Arguments:
	data -- array of dictionaries
	filters -- dict
	csv_class -- defines DATA_CATEGORY, FORMAT_NAME and COLUMNS
	"""
	header = get_header(filters, csv_class)

	empty_df = pd.DataFrame(columns=csv_class.COLUMNS)
	data_df = pd.DataFrame.from_records(data)

	result = empty_df.append(data_df, sort=True)

	if csv_class.DATA_CATEGORY == DataCategory.TRANSACTIONS:
		result['Belegdatum'] = pd.to_datetime(result['Belegdatum'])

	if csv_class.DATA_CATEGORY == DataCategory.ACCOUNT_NAMES:
		result['Sprach-ID'] = 'de-DE'

	header = ';'.join(header).encode('latin_1')
	data = result.to_csv(
		# Reason for str(';'): https://github.com/pandas-dev/pandas/issues/6035
		sep=str(';'),
=======
def get_datev_csv(data):
	"""
	Fill in missing columns and return a CSV in DATEV Format.

	Arguments:
	data -- array of dictionaries
	"""
	columns = [
		# All possible columns must tbe listed here, because DATEV requires them to
		# be present in the CSV.
		# ---
		# Umsatz
		"Umsatz (ohne Soll/Haben-Kz)",
		"Soll/Haben-Kennzeichen",
		"WKZ Umsatz",
		"Kurs",
		"Basis-Umsatz",
		"WKZ Basis-Umsatz",
		# Konto/Gegenkonto
		"Kontonummer",
		"Gegenkonto (ohne BU-Schlüssel)",
		"BU-Schlüssel",
		# Datum
		"Belegdatum",
		# Belegfelder
		"Belegfeld 1",
		"Belegfeld 2",
		# Weitere Felder
		"Skonto",
		"Buchungstext",
		# OPOS-Informationen
		"Postensperre",
		"Diverse Adressnummer",
		"Geschäftspartnerbank",
		"Sachverhalt",
		"Zinssperre",
		# Digitaler Beleg
		"Beleglink",
		# Beleginfo
		"Beleginfo - Art 1",
		"Beleginfo - Inhalt 1",
		"Beleginfo - Art 2",
		"Beleginfo - Inhalt 2",
		"Beleginfo - Art 3",
		"Beleginfo - Inhalt 3",
		"Beleginfo - Art 4",
		"Beleginfo - Inhalt 4",
		"Beleginfo - Art 5",
		"Beleginfo - Inhalt 5",
		"Beleginfo - Art 6",
		"Beleginfo - Inhalt 6",
		"Beleginfo - Art 7",
		"Beleginfo - Inhalt 7",
		"Beleginfo - Art 8",
		"Beleginfo - Inhalt 8",
		# Kostenrechnung
		"Kost 1 - Kostenstelle",
		"Kost 2 - Kostenstelle",
		"Kost-Menge",
		# Steuerrechnung
		"EU-Land u. UStID",
		"EU-Steuersatz",
		"Abw. Versteuerungsart",
		# L+L Sachverhalt
		"Sachverhalt L+L",
		"Funktionsergänzung L+L",
		# Funktion Steuerschlüssel 49
		"BU 49 Hauptfunktionstyp",
		"BU 49 Hauptfunktionsnummer",
		"BU 49 Funktionsergänzung",
		# Zusatzinformationen
		"Zusatzinformation - Art 1",
		"Zusatzinformation - Inhalt 1",
		"Zusatzinformation - Art 2",
		"Zusatzinformation - Inhalt 2",
		"Zusatzinformation - Art 3",
		"Zusatzinformation - Inhalt 3",
		"Zusatzinformation - Art 4",
		"Zusatzinformation - Inhalt 4",
		"Zusatzinformation - Art 5",
		"Zusatzinformation - Inhalt 5",
		"Zusatzinformation - Art 6",
		"Zusatzinformation - Inhalt 6",
		"Zusatzinformation - Art 7",
		"Zusatzinformation - Inhalt 7",
		"Zusatzinformation - Art 8",
		"Zusatzinformation - Inhalt 8",
		"Zusatzinformation - Art 9",
		"Zusatzinformation - Inhalt 9",
		"Zusatzinformation - Art 10",
		"Zusatzinformation - Inhalt 10",
		"Zusatzinformation - Art 11",
		"Zusatzinformation - Inhalt 11",
		"Zusatzinformation - Art 12",
		"Zusatzinformation - Inhalt 12",
		"Zusatzinformation - Art 13",
		"Zusatzinformation - Inhalt 13",
		"Zusatzinformation - Art 14",
		"Zusatzinformation - Inhalt 14",
		"Zusatzinformation - Art 15",
		"Zusatzinformation - Inhalt 15",
		"Zusatzinformation - Art 16",
		"Zusatzinformation - Inhalt 16",
		"Zusatzinformation - Art 17",
		"Zusatzinformation - Inhalt 17",
		"Zusatzinformation - Art 18",
		"Zusatzinformation - Inhalt 18",
		"Zusatzinformation - Art 19",
		"Zusatzinformation - Inhalt 19",
		"Zusatzinformation - Art 20",
		"Zusatzinformation - Inhalt 20",
		# Mengenfelder LuF
		"Stück",
		"Gewicht",
		# Forderungsart
		"Zahlweise",
		"Forderungsart",
		"Veranlagungsjahr",
		"Zugeordnete Fälligkeit",
		# Weitere Felder
		"Skontotyp",
		# Anzahlungen
		"Auftragsnummer",
		"Buchungstyp",
		"USt-Schlüssel (Anzahlungen)",
		"EU-Land (Anzahlungen)",
		"Sachverhalt L+L (Anzahlungen)",
		"EU-Steuersatz (Anzahlungen)",
		"Erlöskonto (Anzahlungen)",
		# Stapelinformationen
		"Herkunft-Kz",
		# Technische Identifikation
		"Buchungs GUID",
		# Kostenrechnung
		"Kost-Datum",
		# OPOS-Informationen
		"SEPA-Mandatsreferenz",
		"Skontosperre",
		# Gesellschafter und Sonderbilanzsachverhalt
		"Gesellschaftername",
		"Beteiligtennummer",
		"Identifikationsnummer",
		"Zeichnernummer",
		# OPOS-Informationen
		"Postensperre bis",
		# Gesellschafter und Sonderbilanzsachverhalt
		"Bezeichnung SoBil-Sachverhalt",
		"Kennzeichen SoBil-Buchung",
		# Stapelinformationen
		"Festschreibung",
		# Datum
		"Leistungsdatum",
		"Datum Zuord. Steuerperiode",
		# OPOS-Informationen
		"Fälligkeit",
		# Konto/Gegenkonto
		"Generalumkehr (GU)",
		# Steuersatz für Steuerschlüssel
		"Steuersatz",
		"Land"
	]

	empty_df = pd.DataFrame(columns=columns)
	data_df = pd.DataFrame.from_records(data)

	result = empty_df.append(data_df)
	result["Belegdatum"] = pd.to_datetime(result["Belegdatum"])

	return result.to_csv(
		sep=b';',
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
		# European decimal seperator
		decimal=',',
		# Windows "ANSI" encoding
		encoding='latin_1',
		# format date as DDMM
		date_format='%d%m',
		# Windows line terminator
<<<<<<< HEAD
		line_terminator='\r\n',
		# Do not number rows
		index=False,
		# Use all columns defined above
		columns=csv_class.COLUMNS
	)

	if not six.PY2:
		data = data.encode('latin_1')

	return header + b'\r\n' + data


def get_header(filters, csv_class):
	header = [
		# A = DATEV format
		#   DTVF = created by DATEV software,
		#   EXTF = created by other software
		"EXTF",
		# B = version of the DATEV format
		#   141 = 1.41, 
		#   510 = 5.10,
		#   720 = 7.20
		"510",
		csv_class.DATA_CATEGORY,
		csv_class.FORMAT_NAME,
		# E = Format version (regarding format name)
		"",
		# F = Generated on
		datetime.datetime.now().strftime("%Y%m%d"),
		# G = Imported on -- stays empty
		"",
		# H = Origin (SV = other (?), RE = KARE)
		"SV",
		# I = Exported by
		frappe.session.user,
		# J = Imported by -- stays empty
		"",
		# K = Tax consultant number (Beraternummer)
		frappe.get_value("DATEV Settings", filters.get("company"), "consultant_number") or "",
		"",
		# L = Tax client number (Mandantennummer)
		frappe.get_value("DATEV Settings", filters.get("company"), "client_number") or "",
		"",
		# M = Start of the fiscal year (Wirtschaftsjahresbeginn)
		frappe.utils.formatdate(frappe.defaults.get_user_default("year_start_date"), "yyyyMMdd"),
		# N = Length of account numbers (Sachkontenlänge)
		"4",
		# O = Transaction batch start date (YYYYMMDD)
		frappe.utils.formatdate(filters.get('from_date'), "yyyyMMdd"),
		# P = Transaction batch end date (YYYYMMDD)
		frappe.utils.formatdate(filters.get('to_date'), "yyyyMMdd"),
		# Q = Description (for example, "January - February 2019 Transactions")
		"{} - {} {}".format(
				frappe.utils.formatdate(filters.get('from_date'), "MMMM yyyy"),
				frappe.utils.formatdate(filters.get('to_date'), "MMMM yyyy"),
				csv_class.FORMAT_NAME
		),
		# R = Diktatkürzel
		"",
		# S = Buchungstyp
		#   1 = Transaction batch (Buchungsstapel),
		#   2 = Annual financial statement (Jahresabschluss)
		"1" if csv_class.DATA_CATEGORY == DataCategory.TRANSACTIONS else "",
		# T = Rechnungslegungszweck
		"",
		# U = Festschreibung
		"",
		# V = Kontoführungs-Währungskennzeichen des Geldkontos
		frappe.get_value("Company", filters.get("company"), "default_currency")
	]
	return header

=======
		line_terminator=b'\r\n',
		# Do not number rows
		index=False,
		# Use all columns defined above
		columns=columns
	)

>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2

@frappe.whitelist()
def download_datev_csv(filters=None):
	"""
	Provide accounting entries for download in DATEV format.

	Validate the filters, get the data, produce the CSV file and provide it for
	download. Can be called like this:

	GET /api/method/erpnext.regional.report.datev.datev.download_datev_csv

	Arguments / Params:
	filters -- dict of filters to be passed to the sql query
	"""
	if isinstance(filters, string_types):
		filters = json.loads(filters)

<<<<<<< HEAD
	validate(filters)

	# This is where my zip will be written
	zip_buffer = BytesIO()
	# This is my zip file
	datev_zip = zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED)

	transactions = get_transactions(filters)
	transactions_csv = get_datev_csv(transactions, filters, csv_class=Transactions)
	datev_zip.writestr('EXTF_Buchungsstapel.csv', transactions_csv)

	account_names = get_account_names(filters)
	account_names_csv = get_datev_csv(account_names, filters, csv_class=AccountNames)
	datev_zip.writestr('EXTF_Kontenbeschriftungen.csv', account_names_csv)

	customers = get_customers(filters)
	customers_csv = get_datev_csv(customers, filters, csv_class=DebtorsCreditors)
	datev_zip.writestr('EXTF_Kunden.csv', customers_csv)

	suppliers = get_suppliers(filters)
	suppliers_csv = get_datev_csv(suppliers, filters, csv_class=DebtorsCreditors)
	datev_zip.writestr('EXTF_Lieferanten.csv', suppliers_csv)
	
	# You must call close() before exiting your program or essential records will not be written.
	datev_zip.close()

	frappe.response['filecontent'] = zip_buffer.getvalue()
	frappe.response['filename'] = 'DATEV.zip'
	frappe.response['type'] = 'binary'
=======
	validate_filters(filters)
	data = get_gl_entries(filters, as_dict=1)

	filename = 'DATEV_Buchungsstapel_{}-{}_bis_{}'.format(
		filters.get('company'),
		filters.get('from_date'),
		filters.get('to_date')
	)

	frappe.response['result'] = get_datev_csv(data)
	frappe.response['doctype'] = filename
	frappe.response['type'] = 'csv'
>>>>>>> 47a7e3422b04aa66197d7140e144b70b99ee2ca2
