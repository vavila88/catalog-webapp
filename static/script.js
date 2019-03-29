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

$(document).ready(function(){optionHandler();});
