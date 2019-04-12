// creates an input field when a new category is being selected for a new item
function optionHandler() {
    // Get the category dropdown element
    let selection = document.getElementById('category_select');
    // If the element exists, proceed to pick the necessary data.
    if (selection !== null) {
        let sel = selection[selection.selectedIndex].value;

        // Set the hidden input value to the value selected by the dropdown
        // $('#cat_name_input').val(sel);
        // report for debugging purpose
        // console.log($('#cat_name_input').val());

        // If the dropdown selection was to add a new category, provide an input
        // for adding it
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

// Function to populate the available categories in the database. Used in the
// item edit page
function showCategoryOptions() {
    // if the placeholder div exists, then we haven't selected the "change
    // category" button and are doing so now. Replace the placeholder div with
    // the category selection code.
    if ($("div#edit-category").length) {
        $.ajax({
            url : "/api/v1/catalog/category/JSON",
            type : "GET",
            dataType : "json",
        }).done(function(result) {
            let sel_hdr ='<select name="category_select" id="category_select" '+
                         'class="selectpicker" data-style="btn-default" ' +
                         'onchange="optionHandler()">' +
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


// Register event handlers only after the entire document has been parsed
$(document).ready(function(){
    // optionHandler();
    // Changes the value of the bootstrap dropdown so the selected option is
    // displayed
    $('.cat-dropdown-menu > button').click(function (){
        // console.log('in the callback');

        // Change the value in the button, including the caret
        $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');

        // Change the value of the button
        let sel = $(this).data('value')

        // Set the hidden input value to the value selected by the dropdown
        $('#cat_name_input').val(sel);

        // report for debugging purpose
        // console.log($('#cat_name_input').val());

        // If the dropdown selection was to add a new category, provide an input
        // for adding it
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
    });
});
