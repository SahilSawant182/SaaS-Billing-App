# Copyright (c) 2026, sahil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate


class SaaSSubscription(Document):

    def before_save(self):
        handle_subscription_update(self)

def handle_subscription_update(self):
	if not self.user:
		frappe.throw("User is required for subscription")

	# Run only when payment is payed
	if self.payment_status == "Paid":

		user = frappe.get_doc("User", self.user)
		if user.role_profile_name != "Paid Plan User":
			# Assignin role profile
			user.role_profile_name = "Paid Plan User"                                               

			user.save(ignore_permissions=True)  

			if not self.valid_till: 
				self.valid_till = add_days( 
					nowdate(), 30  
				)

			frappe.msgprint("User upgraded to Paid Plan")

