# -*- coding: utf-8 -*-
# Copyright (c) 2018, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProductionJournal(Document):
	def before_save(self):
		if self.get("__islocal"):
			load_data(self)
			set_barcode(self)


def set_barcode(self):
	gtin = "0764018344"
	
	_product_code = self.p_o_item if self.p_o_item else 0
	product_code = str(_product_code).zfill(3)
	
	_barcode = addCheckDigit((gtin + product_code))
	
	lot_number = self.batch_no if self.batch_no else 0
	
	_expiry_date = {}
	exp_dates = get_expire(self.batch_no)
	for exp_date in exp_dates:
		_expiry_date["exp"] = str(exp_date.exp)
	if "exp" in _expiry_date:
		if _expiry_date["exp"] == None:
			expiry_date = "991231"
		else:
			expiry_date = _expiry_date["exp"]
	else:
		expiry_date = "2099-12-31"
	
	barcode = "(01){0}(10){1}(17){2}{3}{4}".format(_barcode, lot_number, expiry_date[2:4], expiry_date[5:7], expiry_date[8:10])
	self.barcode = barcode

def addCheckDigit(barcode):
	if len(barcode) in (7,11,12,13) and barcode.isdigit():
		digits = map(int, barcode)
		return barcode + str(__checkDigit(digits))
	return ''

def __checkDigit(digits):
	total = sum(digits) + sum(map(lambda d: d*2, digits[-1::-2]))
	return (10 - (total % 10)) % 10


def load_data(self):
	master_ste = get_master_stock_entry(self)
	for mste in master_ste:
		items = get_items_of_mste(mste.name)
		expirys = {}
		parents = {}
		supplier = {}
		for item in items:			
			if item.item_code != self.p_o_item:
				_expirys = get_expire(item.batch_no)
				for exp in _expirys:
					expirys[item.item_code] = exp.exp
				parent_stes = get_parent_ste(item.batch_no)
				for parent_ste in parent_stes:
					parents[item.item_code] = parent_ste.parent
				if item.item_code in parents:
					_suppliers = get_supplier(parents[item.item_code])
					for _supplier in _suppliers:
						supplier[item.item_code] = _supplier.supplier
					if item.item_code in expirys:
						add_item_to_row(self, item, expirys[item.item_code], supplier[item.item_code])
					else:
						add_item_to_row_empty_exp(self, item, supplier[item.item_code])
				else:
					if item.item_code in expirys:
						add_item_to_row_empty_supplier(self, item, expirys[item.item_code])
					else:
						add_item_to_row_empty_supplier_and_exp(self, item)
			else:
				self.batch_no = item.batch_no

def get_master_stock_entry(self):
	sql_query = """SELECT t1.name
		FROM `tabStock Entry` AS t1
		WHERE t1.production_order = '{0}'
		AND t1.purpose = 'Manufacture'
		AND t1.docstatus = '1'""".format(self.production_order)
	master_ste = frappe.db.sql(sql_query, as_dict=True)
	return master_ste
	
def get_items_of_mste(mste):
	sql_query = """SELECT t1.item_code, t1.transfer_qty, t1.batch_no
		FROM `tabStock Entry Detail` AS t1
		WHERE t1.parent = '{0}'""".format(mste)
	items = frappe.db.sql(sql_query, as_dict=True)
	return items
	
def add_item_to_row(self, item, exp_date, supplier):
	self.append('item_own', {
		'item': item.item_code,
		'batch': item.batch_no,
		'exp_date': exp_date,
		'supplier': supplier
	})
	
def add_item_to_row_empty_supplier(self, item, exp_date):
	self.append('item_own', {
		'item': item.item_code,
		'batch': item.batch_no,
		'exp_date': exp_date
	})
	
def add_item_to_row_empty_exp(self, item, supplier):
	self.append('item_own', {
		'item': item.item_code,
		'batch': item.batch_no,
		'supplier': supplier
	})
	
def add_item_to_row_empty_supplier_and_exp(self, item):
	self.append('item_own', {
		'item': item.item_code,
		'batch': item.batch_no
	})

def get_expire(batch_no):
	sql_query = """SELECT t1.expiry_date AS 'exp'
		FROM `tabBatch` AS t1
		WHERE t1.name = '{0}'""".format(batch_no)
	exp = frappe.db.sql(sql_query, as_dict=True)
	return exp
	
def get_parent_ste(batch_no):
	sql_query = """SELECT t1.parent
		FROM `tabPurchase Receipt Item` AS t1
		WHERE t1.batch_no = '{0}'""".format(batch_no)
	parent_ste = frappe.db.sql(sql_query, as_dict=True)
	return parent_ste
	
def get_supplier(parent):
	sql_query = """SELECT t1.supplier
		FROM `tabPurchase Receipt` AS t1
		WHERE t1.name = '{0}'""".format(parent)
	parents = frappe.db.sql(sql_query, as_dict=True)
	return parents