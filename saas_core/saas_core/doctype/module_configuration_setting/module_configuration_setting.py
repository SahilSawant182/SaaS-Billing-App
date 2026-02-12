# Copyright (c) 2026, sahil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ModuleConfigurationSetting(Document):

    # Load existing permissions ONLY when document is new
    def before_insert(self):
        self.load_existing_permissions()

    #Load existing permissions based on selected user and module
    def load_existing_permissions(self):

        if not self.user:
            return

        roles = frappe.get_roles(self.user)

        if not roles:
            return

        for row in self.doctypes:

            if not row.doctype_name:
                continue

            self.reset_row_permissions(row)

            # Standard DocPerm
            standard_perms = frappe.get_all(
                "DocPerm",
                filters={
                    "parent": row.doctype_name,
                    "role": ["in", roles],
                    "permlevel": 0
                },
                fields=self.get_permission_fields()
            )

            # Custom DocPerm
            custom_perms = frappe.get_all(
                "Custom DocPerm",
                filters={
                    "parent": row.doctype_name,
                    "role": ["in", roles],
                    "permlevel": 0
                },
                fields=self.get_permission_fields()
            )

            all_perms = standard_perms + custom_perms

            for p in all_perms:
                self.apply_permission_to_row(row, p)

    # Apply permission using OR logic 
    def apply_permission_to_row(self, row, p):

        row.perm_select = row.perm_select or p.get("select", 0)
        row.perm_read = row.perm_read or p.get("read", 0)
        row.perm_write = row.perm_write or p.get("write", 0)
        row.perm_create = row.perm_create or p.get("create", 0)
        row.perm_delete = row.perm_delete or p.get("delete", 0)
        row.perm_submit = row.perm_submit or p.get("submit", 0)
        row.perm_cancel = row.perm_cancel or p.get("cancel", 0)
        row.perm_amend = row.perm_amend or p.get("amend", 0)
        row.perm_print = row.perm_print or p.get("print", 0)
        row.perm_email = row.perm_email or p.get("email", 0)
        row.perm_report = row.perm_report or p.get("report", 0)
        row.perm_import = row.perm_import or p.get("import", 0)
        row.perm_export = row.perm_export or p.get("export", 0)
        row.perm_share = row.perm_share or p.get("share", 0)
        row.perm_if_owner = row.perm_if_owner or p.get("if_owner", 0)

    def reset_row_permissions(self, row):

        row.perm_select = 0
        row.perm_read = 0
        row.perm_write = 0
        row.perm_create = 0
        row.perm_delete = 0
        row.perm_submit = 0
        row.perm_cancel = 0
        row.perm_amend = 0
        row.perm_print = 0
        row.perm_email = 0
        row.perm_report = 0
        row.perm_import = 0
        row.perm_export = 0
        row.perm_share = 0
        row.perm_if_owner = 0

    def get_permission_fields(self):
        return [
            "select",
            "read",
            "write",
            "create",
            "delete",
            "submit",
            "cancel",
            "amend",
            "print",
            "email",
            "report",
            "import",
            "export",
            "share",
            "if_owner"
        ]

    #Apply permissions when the document is submitted

    def on_submit(self):
        self.apply_permissions()

    def apply_permissions(self):

        if not self.user:
            return

        role_name = f"Module Role - {self.name}"

        # Create role if not exists
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name
            }).insert(ignore_permissions=True)

        # Delete old custom permissions of this role
        frappe.db.delete("Custom DocPerm", {"role": role_name})

        # Create new Custom DocPerm based on edited checkboxes
        for row in self.doctypes:

            if not row.doctype_name:
                continue

            frappe.get_doc({
                "doctype": "Custom DocPerm",
                "parent": row.doctype_name,
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": role_name,
                "permlevel": 0,
                "select": row.perm_select,
                "read": row.perm_read,
                "write": row.perm_write,
                "create": row.perm_create,
                "delete": row.perm_delete,
                "submit": row.perm_submit,
                "cancel": row.perm_cancel,
                "amend": row.perm_amend,
                "print": row.perm_print,
                "email": row.perm_email,
                "report": row.perm_report,
                "import": row.perm_import,
                "export": row.perm_export,
                "share": row.perm_share,
                "if_owner": row.perm_if_owner
            }).insert(ignore_permissions=True)

        # Remove old roles (except system roles)
        user_roles = frappe.get_all(
            "Has Role",
            filters={"parent": self.user},
            fields=["name", "role"]
        )

        for ur in user_roles:
            if ur.role not in ["Administrator", "All", "Guest"]:
                frappe.delete_doc("Has Role", ur.name, ignore_permissions=True)

        # Assign new role to user
        frappe.get_doc({
            "doctype": "Has Role",
            "parent": self.user,
            "parenttype": "User",
            "parentfield": "roles",
            "role": role_name
        }).insert(ignore_permissions=True)

        frappe.db.commit()




































































# Copyright (c) 2026, sahil and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class ModuleConfigurationSetting(Document):

#     #Load existing permissions when module and user is selected
#     def validate(self):
#         self.load_existing_permissions()

#     def load_existing_permissions(self):

#         if not self.user:
#             return

#         roles = frappe.get_roles(self.user)

#         for row in self.doctypes:

#             if not row.doctype_name:
#                 continue

#             for role in roles:

#                 perm = frappe.db.get_value(
#                     "DocPerm",
#                     {
#                         "parent": row.doctype_name,
#                         "role": role,
#                         "permlevel": 0
#                     },
#                     [
#                         "select",
#                         "read",
#                         "write",
#                         "create",
#                         "delete",
#                         "submit",
#                         "cancel",
#                         "amend",
#                         "print",
#                         "email",
#                         "report",
#                         "import",
#                         "export",
#                         "share",
#                         "if_owner"
#                     ],
#                     as_dict=True
#                 )

#                 if perm:
#                     row.perm_select = perm.get("select")
#                     row.perm_read = perm.get("read")
#                     row.perm_write = perm.get("write")
#                     row.perm_create = perm.get("create")
#                     row.perm_delete = perm.get("delete")
#                     row.perm_submit = perm.get("submit")
#                     row.perm_cancel = perm.get("cancel")
#                     row.perm_amend = perm.get("amend")
#                     row.perm_print = perm.get("print")
#                     row.perm_email = perm.get("email")
#                     row.perm_report = perm.get("report")
#                     row.perm_import = perm.get("import")
#                     row.perm_export = perm.get("export")
#                     row.perm_share = perm.get("share")
#                     row.perm_if_owner = perm.get("if_owner")
#                     break


#     #Apply permissions when the document is submitted
#     def on_submit(self):
#         self.apply_permissions()


#     def apply_permissions(self):

#         if not self.user:
#             return

#         role_name = f"Module Role - {self.name}"

#         #Create a new role for this module configuration
#         if not frappe.db.exists("Role", role_name):
#             frappe.get_doc({
#                 "doctype": "Role",
#                 "role_name": role_name
#             }).insert(ignore_permissions=True)

#         #Remove carunt Permissions for that  role
#         frappe.db.delete("Custom DocPerm", {"role": role_name})

#         #Adding new Custom Permissions based on the child table entries
#         for row in self.doctypes:

#             if not row.doctype_name:
#                 continue

#             frappe.get_doc({
#                 "doctype": "Custom DocPerm",
#                 "parent": row.doctype_name,
#                 "parenttype": "DocType",
#                 "parentfield": "permissions",
#                 "role": role_name,
#                 "permlevel": 0,
#                 "select": row.perm_select,
#                 "read": row.perm_read,
#                 "write": row.perm_write,
#                 "create": row.perm_create,
#                 "delete": row.perm_delete,
#                 "submit": row.perm_submit,
#                 "cancel": row.perm_cancel,
#                 "amend": row.perm_amend,
#                 "print": row.perm_print,
#                 "email": row.perm_email,
#                 "report": row.perm_report,
#                 "import": row.perm_import,
#                 "export": row.perm_export,
#                 "share": row.perm_share,
#                 "if_owner": row.perm_if_owner
#             }).insert(ignore_permissions=True)

#         #Remove existing roles assigned to user except Administrator will not be changed logic only for others 
#         user_roles = frappe.get_all(
#             "Has Role",
#             filters={"parent": self.user},
#             fields=["name", "role"]
#         )

#         for ur in user_roles:
#             if ur.role not in ["Administrator", "All", "Guest"]:
#                 frappe.delete_doc("Has Role", ur.name, ignore_permissions=True)

#         #Assign the new role to the user
#         frappe.get_doc({
#             "doctype": "Has Role",
#             "parent": self.user,
#             "parenttype": "User",
#             "parentfield": "roles",
#             "role": role_name
#         }).insert(ignore_permissions=True)

#         frappe.db.commit()

