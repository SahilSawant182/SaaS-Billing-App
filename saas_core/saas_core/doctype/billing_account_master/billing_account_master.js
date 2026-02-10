// Copyright (c) 2026, sahil and contributors
// For license information, please see license.txt


frappe.ui.form.on('Billing Account Master', {
    refresh: function(frm) {
        frm.set_df_property('user_password', 'fieldtype', 'Password');
        
        // Target the actual HTML input to ensure it stays dots   
        const input = frm.get_field('user_password').$input;
        if (input) {
            input.attr('type', 'password');
        }
    }
});
