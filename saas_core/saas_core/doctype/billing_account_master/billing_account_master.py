# Copyright (c) 2026, sahil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BillingAccountMaster(Document):


    def after_insert(self):
        try:
            # Create and Link Company
            company_exists = frappe.db.exists("Company", self.company_name)

            if company_exists:
                frappe.log_error(      
                    f"Company {self.company_name} found in DB. Linking...",
                    "Debug: Create Company"
                )
                self.linked_company = self.company_name
                self.db_update()
            else:
                try:
                    new_company = frappe.get_doc({
                        "doctype": "Company",
                        "company_name": self.company_name,
                        "abbr": self.abbr or self.company_name[:3].upper(),
                        "default_currency": self.default_currency or "INR",
                        "country": self.country or "India",
                        "create_chart_of_accounts_based_on": "Standard Template"
                    })

                    new_company.insert(ignore_permissions=True)
                    self.linked_company = new_company.name
                    self.db_update()

                except Exception as e:
                    frappe.log_error(f"Error creating company: {str(e)}", "Debug: Create Company")
                    frappe.throw(f"Failed to create Company: {str(e)}")

            # Create and link user
            if not self.linked_user:
                if frappe.db.exists("User", self.email):
                    self.linked_user = self.email
                    self.db_update()
                else:
                    user = frappe.get_doc({
                        "doctype": "User",
                        "email": self.email,
                        "first_name": self.first_name,
                        "middle_name": self.middle_name,
                        "last_name": self.last_name,
                        "enabled": 1,
                        "send_welcome_email": 1,
                        "company": self.linked_company
                    })

                    if self.role_profile_name:
                        user.role_profile_name = self.role_profile_name

                    user.insert(ignore_permissions=True)
                    self.linked_user = user.name
                    self.db_update()

            # Set Permissions and User Password on initial insert
            if self.linked_user:
                # Set User Permissions
                if self.linked_company and not frappe.db.exists("User Permission", {"user": self.linked_user, "allow": "Company", "for_value": self.linked_company}):
                    frappe.get_doc({
                        "doctype": "User Permission",
                        "user": self.linked_user,
                        "allow": "Company",
                        "for_value": self.linked_company
                    }).insert(ignore_permissions=True)

                # PASSWORD LOGIC FOR NEW INSERTEED USEfr
                if self.user_password:
                    from frappe.utils.password import update_password
                    update_password(self.linked_user, self.user_password)
                    self.db_set("user_password", None)
                    frappe.db.commit()
            
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Billing Account Creation Failed")
            frappe.throw(str(e))

    def on_update(self):
        try:
            self.sync_user_and_company()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Billing Sync Failed")
            frappe.throw(str(e))

    def sync_user_and_company(self):

        #User Doc Changes matching

        if self.linked_user and frappe.db.exists("User", self.linked_user):
            user = frappe.get_doc("User", self.linked_user)

            user.first_name = self.first_name
            user.middle_name = self.middle_name
            user.last_name = self.last_name
            user.email = self.email
            user.company = self.linked_company

            if self.role_profile_name:
                user.role_profile_name = self.role_profile_name

            user.save(ignore_permissions=True)
 
            #Setting the password if the field is not empty and not masked
            pwd_to_set = str(self.user_password).strip() if self.user_password else None

            if pwd_to_set and pwd_to_set != "None" and "********" not in pwd_to_set:
                from frappe.utils.password import update_password
                
                # Update secure auth table
                update_password(user.name, pwd_to_set)
                
                # Clear plain text field for security
                self.db_set("user_password", None)
                
                # Commit to ensure the login works immediately
                frappe.db.commit()
                
                frappe.msgprint(f"User {user.name} synchronized and password updated.")

        # 2. Company Doc Changes matching
        if self.linked_company and frappe.db.exists("Company", self.linked_company):
            company = frappe.get_doc("Company", self.linked_company)
            company.company_name = self.company_name
            company.abbr = self.abbr or company.abbr
            company.default_currency = self.default_currency or company.default_currency
            company.country = self.country or company.country
            company.save(ignore_permissions=True)