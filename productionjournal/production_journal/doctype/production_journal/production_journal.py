# -*- coding: utf-8 -*-
# Copyright (c) 2018, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
#from six import iteritems

class ProductionJournal(Document):
	def onload(self):
		if not self.docstatus == 1:
			#general
			ref_master_stock_entry = frappe.db.sql("SELECT name FROM `tabStock Entry` WHERE purpose='Manufacture' AND production_order='{0}'".format(self.production_order), as_dict=True)
			if ref_master_stock_entry:
				master_batch = frappe.db.sql("SELECT batch_no FROM`tabStock Entry Detail` WHERE parent='{0}' AND item_code='{1}'".format(ref_master_stock_entry[0].name, self.p_o_item), as_dict=True)

			if master_batch:
				self.batch_no = master_batch[0].batch_no
				self.exp_date = frappe.db.sql("SELECT expiry_date FROM`tabBatch` WHERE name='{0}'".format(master_batch[0].batch_no), as_dict=True)[0].expiry_date

			#item section
			ref_stock_entry = frappe.db.sql("SELECT name FROM `tabStock Entry` WHERE `production_order`='{0}' AND `purpose`='Material Transfer for Manufacture'".format(self.production_order), as_dict=True)[0].name
			items = frappe.db.sql("SELECT item_code, batch_no FROM `tabStock Entry Detail` WHERE `parent`='{0}'".format(ref_stock_entry), as_dict=True)

			for item in items:
				exp_date = frappe.db.sql("SELECT expiry_date FROM `tabBatch` WHERE `name`='{0}'".format(item.batch_no), as_dict=True)[0].expiry_date
				supplier_booking = frappe.db.sql("SELECT parent FROM `tabPurchase Receipt Item` WHERE item_code='{0}' AND batch_no='{1}'".format(item.item_code, item.batch_no), as_dict=True)

				if supplier_booking:
					supplier = frappe.db.sql("SELECT supplier FROM `tabPurchase Receipt` WHERE name='{0}'".format(supplier_booking[0].parent), as_dict=True)[0].supplier
					self.append('item_own', {
						'item': item.item_code,
						'batch': item.batch_no,
						'exp_date': exp_date,
						'supplier': supplier
					})
				else:
					self.append('item_own', {
						'item': item.item_code,
						'batch': item.batch_no,
						'exp_date': exp_date,
						'supplier': "Own Production"
					})

			self.submit()