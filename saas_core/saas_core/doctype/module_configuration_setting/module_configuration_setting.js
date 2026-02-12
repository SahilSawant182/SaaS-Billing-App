// Copyright (c) 2026, sahil and contributors
// For license information, please see license.txt

frappe.ui.form.on('Module Configuration Setting', {

    select_doctype: function(frm) {

        //Check module selected
        if (!frm.doc.module) {
            frappe.msgprint(__('Please select a Module first.'));
            return;
        }
        //Fetch doctypes for selected module
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "DocType",
                fields: ["name"],
                filters: {
                    module: frm.doc.module,
                    istable: 0
                },
                limit_page_length: 1000
            },
            callback: function(r) {

                if (!r.message || r.message.length === 0) {
                    frappe.msgprint(__('No Doctypes found for this module.'));
                    return;
                }

                let all_doctypes = r.message.map(d => d.name);

                //Create dialog
                let dialog = new frappe.ui.Dialog({
                    title: __('Select Doctypes'),
                    size: 'large',
                    fields: [
                        {
                            fieldtype: 'Data',
                            fieldname: 'search',
                            label: __('Search')
                        },
                        {
                            fieldtype: 'HTML',
                            fieldname: 'doctype_list'
                        }
                    ],
                    primary_action_label: __('Add Doctypes'),
                    primary_action() {

                        let selected = [];

                        dialog.$wrapper.find('.doctype-check:checked').each(function() {
                            selected.push($(this).val());
                        });

                        if (!selected.length) {
                            frappe.msgprint(__('Select at least one Doctype.'));
                            return;
                        }

                        //Append to child table
                        selected.forEach(dt => {

                            let exists = (frm.doc.doctypes || []).some(row =>
                                row.doctype_name === dt
                            );

                            if (!exists) {
                                let row = frm.add_child('doctypes');
                                row.doctype_name = dt;
                            }
                        });

                        frm.refresh_field('doctypes');
                        dialog.hide();
                    }
                });

                //Render checkbox list
                function render(filter="") {

                    let html = `<div style="max-height:400px; overflow:auto;">`;

                    all_doctypes
                        .filter(d => d.toLowerCase().includes(filter.toLowerCase()))
                        .forEach(d => {
                            html += `
                                <div style="padding:4px 0;">
                                    <input type="checkbox"
                                           class="doctype-check"
                                           value="${d}">
                                    ${d}
                                </div>
                            `;
                        });

                    html += `</div>`;

                    dialog.fields_dict.doctype_list.$wrapper.html(html);
                }

                dialog.fields_dict.search.$input.on('input', function() {
                    render(this.value);
                });

                render();
                dialog.show();
            }
        });
    }
});
