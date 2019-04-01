function optionHandler() {
    let selection = document.getElementById('category_select');
    if (selection !== null) {
        let sel = selection[selection.selectedIndex].value;
        if (sel == 'new_cat') {
            let nc_str =`<label class="new_cat_label"for="add_new_cat">New Category:</label>
                        <input type ="text" maxlength="32" class="form-control new_cat_textbox" name="new_cat_title" placeholder="New category name" required>`
            $('#category_select').after(nc_str);
        }
        else {
            // remove the input box from the form if we navigate away from the "add
            // new category" option
            $('.new_cat_label').remove();
            $('.new_cat_textbox').remove();
        }
    }
};

function showCategoryOptions() {
    // if the placeholder div exists, then we haven't selected the "change
    // category" button and are doing so now. Replace the placeholder div with
    // the category selection code.
    if ($("div#edit-category").length) {
        $.ajax({
            url : "/api/v1/catalog/categories/JSON",
            type : "GET",
            dataType : "json",
        }).done(function(result) {
            let sel_hdr ='<select name="category_select" id="category_select" onchange="optionHandler()">' +
                          '<option value="temp_cat">temp cat</option>';
                            //{% for c in category_list%}
            let opt_str = '';
            // console.log(result['Category']);
            for (var key in result['Category']) {
                // console.log(result['Category'][key]);
                opt_str = opt_str + '<option name="'+result['Category'][key]['name']+'">'+result['Category'][key]['name']+'</option>';
            }
                            //{% endfor %}
            let sel_ftr = '<option value="new_cat">-- Add a new category --</option>'+
                        '</select>';

            $("div#edit-category").replaceWith(sel_hdr+opt_str+sel_ftr);
            $('button#btn-change-cat').text('Keep Category');
            // console.log(sel_hdr+opt_str+sel_ftr);
        });
    }
    // Else, the div is gone and we clicked the "change category" button again,
    // thereby indicating that we don't want to change the category and
    // requiring us to hide the cat info.
    else {
        let div_str = '<div id="edit-category" style="display:none;"></div>'
        $('select#category_select').replaceWith(div_str);
        $('button#btn-change-cat').text('Change Category');

    }
};

$(document).ready(function(){optionHandler();});
