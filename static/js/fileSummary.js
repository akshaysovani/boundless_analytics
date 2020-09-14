
// Global variables
var header_row;
window.data_schema = {};

window.all_data = {};
window.attribute_type = {};

window.attribute_unique_data_values = {};

var summary_data;

var values_currently_selected = [];

var options_that_are_selected_by_user = [];

var file_name;

var ready = 0;

window.attributes_to_keep = {}

// Show list of datasets that are already loaded into mysql
var random_table_list = {};

var current_filename = window.location.href;
// current_filename = current_filename.replace('http://www.foreveranalytics.com/ba/dataset/', '');
current_filename = current_filename.substr(current_filename.lastIndexOf('/') + 1);
// current_filename = current_filename.replace('http://www.foreveranalytics.com/ba/dataset/', '');
// Set the filename value
// Store the attribute types in the input
var orig_filename = document.getElementById("filename");
orig_filename.value = current_filename;

random_table_list['table'] = current_filename;

// Call the function attribute_updater
attribute_updater(random_table_list);
// Call the function update_table
update_table(random_table_list);
deleteready();

// // Event listener for the datasets already loaded
// document.getElementById("list_group").addEventListener("click",function(e) {
//     console.log(e.target)
//     website_name = "http://www.foreveranalytics.com/ba/dataset/" + e.target.innerText;
//
//     $.get(website_name).done(function () {
//       // alert("success");
//     }).fail(function () {
//        alert("Please delete the dataset to continue.");
//        window.location.href = "http://www.foreveranalytics.com/ba/dataset/" + current_filename
//     });
//
//     // Navigate to the corresponding page
//     // window.location.href = "/ba/dataset/" + e.target.innerText;
// });

// Event based function for click on upload
$(function () {
    $("#upload").bind("click", function () {

        // Check if there is a file to upload
        var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.csv|.txt)$/;
        if (regex.test($("#fileUpload").val().toLowerCase())) {


            // Get the filename
            var files = document.getElementById("fileUpload");
            file_name = files.files[0].name;
            file_name = file_name.replace('.csv', '');
            file = files.files[0];
            var formdata = new FormData();
            formdata.append('file', files.files[0], file_name);
            $.ajax({
                url: '/validatecsv/',
                type: 'POST',
                data: formdata,
                processData: false,
                contentType: false,
                cache: false
            }).done(function(data) {
                tablecheck(file_name);
            }).fail(function(xhr) {
                var msg = $.parseJSON(xhr.responseText);
                $("#error_msg").text(msg.message);
                $("#error_dialog").css("display", "block");
            });
        }
        // If no file has been selected to upload
        else {
            alert("Please upload a valid CSV file.");
        }

    });
});

function tablecheck(file_name) {
    var table_list = {};
    table_list['table'] = file_name;
    var flag = 0;

    // Check the tables present in the database
    $.ajax({
        url: '/tablecheck/',
        type: 'POST',
        data: table_list,
        async: false
    }).done(function(data) {
        var all_data = data['tables'];
        for (var table in all_data) {
            if (file_name === all_data[table]) {
                flag = 1;
            }
        }
        // Check the flag value - If the dataset is already present
        if (flag === 1) {
            var modal = document.getElementById("reloadModal");
            var yes_span = document.getElementsByClassName("yes")[0];
            var no_span = document.getElementsByClassName("no")[0];
            modal.style.display = "block";
            yes_span.onclick = function () {
                modal.style.display = "none";
                // Clear the all_data variable
                window.all_data = {};
                file_and_data_loader();
            }
            no_span.onclick = function () {
                modal.style.display = "none";
                // Navigate to the corresponding page
                window.location.href = "/ba/dataset/" + file_name;
            }
        } else {
             window.all_data = {};
             file_and_data_loader();
        }
    }).fail(function(xhr){
         var msg = $.parseJSON(xhr.responseText);
         $("#error_msg").text(msg.message);
         $("#error_dialog").css("display", "block");
    });
}


document.getElementById("okay").addEventListener("click", function(){

    var schema_tag = document.getElementById("schema");

    window.attribute_type = {};
    window.data_schema = {};
    var number_of_numerical_count = 0;

    for (var i = 0; i < schema_tag.children.length; i++) {
        var name = schema_tag.children[i].children[1].children[0].children[0].name;
        var chosen_or_not = (schema_tag.children[i].children[1].children[0].children[0].checked).toString();
        attribute_type[name] = chosen_or_not;

        // Store the attribute types in the input
        var cat_num = document.getElementById("cat_num");
        cat_num.value = JSON.stringify(attribute_type);

        if (chosen_or_not !== "false") {
            number_of_numerical_count += 1;
        }
    }

    // Check to see if the user has selected all categorical variables
    if (number_of_numerical_count === 0) {
        // Throw a warning to the user that all categorical variables have been selected
        var modal = document.getElementById("categoryModal");
        var yes_span = document.getElementsByClassName("ohyeah")[0];
        var no_span = document.getElementsByClassName("ohno")[0];
        modal.style.display = "block";

        yes_span.onclick = function () {
            modal.style.display = "none";

            // Ask the user for the minimum support
            var minsupmodal = document.getElementById("minsupModal");
            var minsupyeah = document.getElementsByClassName("minsupyeah")[0];
            minsupmodal.style.display = "block";

            minsupyeah.onclick = function () {
                minsupmodal.style.display = "none";

                // Data for the file uploaded
                var file_data = {};
                var timestamp = (new Date().getTime()).toString();
                file_data['filename'] = file_name + timestamp;
                file_data['actual_filename'] = file_name;
                file_data['status'] = 'Uploaded';
                file_data['timestamp'] = timestamp;
                file_data['progress'] = '0';

                var actual_file_data = JSON.parse(JSON.stringify(file_data));

                $.ajax({
                    url: '/tableadd/',
                    type: 'POST',
                    data: actual_file_data,
                    //dataType: "json",
                    async: false,
                }).done(function (message) {
                    console.log(message);
                    $("#theform").attr("action", "/upload/");
                    $("#theform").submit();
                }).fail(function(xhr){
                    try {
                        var msg = $.parseJSON(xhr.responseText)
                        $("#error_msg").text(msg.message);
                        $("#error_dialog").css("display", "block");
                    } catch(e) {
                        $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
                        $("#error_dialog").css("display", "block");
                    }
                });

                // Set action to /upload/
                //var theform = document.getElementById("theform");
                //theform.setAttribute("action", "/upload/");

                // Submit the form
                //document.theform.submit();
            }
        }
        no_span.onclick = function () {
            modal.style.display = "none";
            window.all_data = {};
            file_and_data_loader();
        }
    }

    else {

        // Ask the user for the minimum support
        var minsupmodal = document.getElementById("minsupModal");
        var minsupyeah = document.getElementsByClassName("minsupyeah")[0];
        minsupmodal.style.display = "block";

        minsupyeah.onclick = function () {
            minsupmodal.style.display = "none";

            // Data for the file uploaded
            var file_data = {};
            var timestamp = (new Date().getTime()).toString();
            file_data['filename'] = file_name + timestamp;
            file_data['actual_filename'] = file_name;
            file_data['status'] = 'Uploaded';
            file_data['timestamp'] = timestamp;
            file_data['progress'] = '0';

            var actual_file_data = JSON.parse(JSON.stringify(file_data));

            $.ajax({
                url: '/tableadd/',
                type: 'POST',
                data: actual_file_data,
                //dataType: "json",
                async: false,
            }).done(function (message) {
                console.log(message);
                $("#theform").attr("action", "/upload/");
                $("#theform").submit();
            }).fail(function(xhr){
                try {
                    var msg = $.parseJSON(xhr.responseText)
                    $("#error_msg").text(msg.message);
                    $("#error_dialog").css("display", "block");
                } catch(e) {
                    $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
                    $("#error_dialog").css("display", "block");
                }
            });

            // Set action to /upload/
            // var theform = document.getElementById("theform");
            // theform.setAttribute("action", "/upload/");

            // Submit the form
            // document.theform.submit();
        }
    }
});

//------------------------------------------------------------------------------

//*********************************************************************
// Standlone functions

// Loading the file and data
function file_and_data_loader() {

    var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.csv|.txt)$/;
    if (regex.test($("#fileUpload").val().toLowerCase())) {
        if (typeof (FileReader) != "undefined") {
            var reader = new FileReader();
            reader.onload = function (e) {

                var rows = e.target.result.split("\n");

                // Get the header
                header_row = rows[0].split(",");
                var new_header_list = [];

                // Get attributes to put in the exclusion list, that will be selected by the user
                var exclude_list = document.getElementById("attributesStuff");

                while(exclude_list.hasChildNodes()) {
                    exclude_list.removeChild(exclude_list.firstChild);
                }

                for(var i = 0; i < header_row.length; i++) {
                    var label = document.createElement("label");
                    var input = document.createElement("input");

                    label.setAttribute("class", "checkbox-inline");
                    label.setAttribute("style", "font-size: medium");
                    label.textContent = header_row[i];

                    input.setAttribute("type", "checkbox");
                    input.value = header_row[i];
                    input.setAttribute("name", "Checkbox[]");

                    label.appendChild(input);

                    exclude_list.appendChild(label);
                }

                // Show the user the attributes to exclude
                var excludemodal = document.getElementById("requiredModal");
                var okay_span = document.getElementsByClassName("itsokay")[0];
                excludemodal.style.display = "block";

                okay_span.onclick = function() {
                    excludemodal.style.display = "none";

                    window.attributes_to_keep = {};

                    var attributes_left = document.getElementById("attributesStuff");

                    for (var i = 0; i < attributes_left.children.length; i++) {
                        var name = attributes_left.children[i].children[0].value;
                        var value = attributes_left.children[i].children[0].checked;
                        window.attributes_to_keep[name] = (value).toString();

                        // Create a list of all attributes that need to be included
                        if (value === false) {
                            new_header_list.push(name);
                        }
                    }

                    // Store the attributes that need to be included/excluded in the input
                    var selectedornot = document.getElementById("selectedornot");
                    selectedornot.value = JSON.stringify(window.attributes_to_keep);

                    var pop_up_list = document.getElementById("schema");

                    while(pop_up_list.hasChildNodes()) {
                        pop_up_list.removeChild(pop_up_list.firstChild);
                    }

                    for(var i = 0; i < new_header_list.length; i++) {

                        var fieldset = document.createElement("fieldset");

                        var para = document.createElement("p");
                        var text_content = document.createTextNode(new_header_list[i] + " :  ")
                        para.appendChild(text_content);
                        para.setAttribute("style", "display:inline-block");

                        fieldset.appendChild(para);

                        var para = document.createElement("p")
                        para.setAttribute("style", "display:inline-block");

                        var label = document.createElement("label");
                        var input = document.createElement("input");
                        input.setAttribute("type", "radio");
                        input.setAttribute("name", new_header_list[i]);
                        input.setAttribute("value", new_header_list[i]+"_num");
                        // input.setAttribute("checked", true);

                        var text_content = document.createTextNode("Numerical")
                        label.appendChild(input);
                        label.appendChild(text_content);

                        para.appendChild(label);

                        var label = document.createElement("label");
                        var input = document.createElement("input");
                        input.setAttribute("type", "radio");
                        input.setAttribute("name", new_header_list[i]);
                        input.setAttribute("value", new_header_list[i]+"_cat");
                        input.setAttribute("checked", true);

                        var text_content = document.createTextNode("Categorical")
                        label.appendChild(input);
                        label.appendChild(text_content);

                        para.appendChild(label);

                        fieldset.appendChild(para);

                        pop_up_list.appendChild(fieldset);
                    }

                    var modal = document.getElementById("myModal");
                    var span = document.getElementsByClassName("close")[0];
                    modal.style.display = "block";

                    span.onclick = function () {
                        modal.style.display = "none";
                    }

                    // All data including the header
                    for (var i = 0; i < rows.length; i++) {
                        if (rows[i] !== "") {
                            var cells = rows[i].splitCSV();
                            window.all_data[i] = cells.toString();
                        }
                    }

                }
            }
            // reader.readAsText($("#fileUpload")[0].files[0]);
            reader.readAsBinaryString($("#fileUpload")[0].files[0]);
        } else {
            alert("This browser does not support HTML5.");
        }
    } else {
        alert("Please upload a valid CSV file.");
    }
}

// String reformatting for csv input
String.prototype.splitCSV = function() {
    var matches = this.match(/(\s*"[^"]+"\s*|\s*[^,]+|,)(?=,|$)/g);
    for (var n = 0; n < matches.length; ++n) {
        matches[n] = matches[n].trim();
        if (matches[n] == ',') matches[n] = '';
    }
    if (this[0] == ',') matches.unshift("");
    return matches;
}

$("#errorDialogButton").on("click", function(e){
    $("#error_dialog").css("display", "none");
});

$("#theform").on("submit", function(e){
    e.preventDefault();
    var formdata = new FormData(this);
    var action = $("#theform").attr("action");
    if (action === '/upload/') {
        $.ajax({
            url: action,
            type: 'POST',
            data: formdata,
            processData: false,
            contentType: false,
            cache: false
        }).done(function(data){
            console.log("File uploaded successfully");
            var redirect_url = data['url'];
            window.location.href = redirect_url;
        }).fail(function(xhr){
            try {
                var msg = $.parseJSON(xhr.responseText)
                $("#error_msg").text(msg.message);
                $("#error_dialog").css("display", "block");
            } catch(e) {
                $("#error_msg").text("Failed to upload file. Please check system logs for more details. " + e);
                $("#error_dialog").css("display", "block");
            }
        });
    } else {
        $.ajax({
            url: '/ba/search/internal',
            type: 'POST',
            data: formdata,
            processData: false,
            contentType: false,
            cache: false,
        }).done(function(data){
           console.log("Search query executed successfully");
           console.log("data - " + data);
           var q = data['q'];
           var show = data['show'];
           window.location.href = '/ba/search/?q=' + q + "&show=" + show;
        }).fail(function(xhr){
            try {
                var msg = $.parseJSON(xhr.responseText)
                $("#error_msg").text(msg.message);
                $("#error_dialog").css("display", "block");
            } catch(e) {
                $("#error_msg").text("Failed to search based on the specified criteria. Please check system logs for more details. " + e);
                $("#error_dialog").css("display", "block");
            }
        });
    }
});

       
// Function to update the attributes
function attribute_updater(filename) {
    $.ajax({
        url:'/query_attr/',
        type: 'POST',
        data: filename,
    }).done(function (data) {
        var get_data = {};
        //  Get the data in the jSON format
        for (var summ_attr in data) {
            var curr_attribute = data[summ_attr];
            curr_attribute = curr_attribute.replace(/'/g, '"');
            curr_attribute = JSON.parse(curr_attribute);
            get_data[summ_attr] = curr_attribute;
        }
        window.attribute_unique_data_values = get_data;
    }).fail(function(xhr) {
        try {
            var msg = $.parseJSON(xhr.responseText)
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
}

// Function to update the dataset list
function update_table(random_table_list) {
    $.ajax({
        url:'/tablecheck/',
        type: 'POST',
        data: random_table_list,
        async: false,
    }).done(function (data) {
        var all_data = data['tables'];
        var all_status = data['status'];
        var all_space = data['space'];

        var list_group = document.getElementById("list_group");

        while(list_group.hasChildNodes()) {
            list_group.removeChild(list_group.firstChild);
        }
        if (all_data.length > 0) {
            for (var table in all_data) {
                var li = document.createElement("li");
                var a = document.createElement("a");
                a.innerText = all_data[table];
                li.setAttribute("class", "list-group-item");
                li.setAttribute("style", "font-weight: bolder; font-size: small;  padding: 10px;");
                li.id = all_data[table];
                var link = "/ba/dataset/" + all_data[table]

                var span = document.createElement("span");

                // Set no link for disk full
                if (all_status[table] === "Out of Space") {
                    a.setAttribute("href", "#");
                    span.setAttribute("class", "home-description left disk-full")
                }
                else {
                    a.setAttribute("href", link);
                    span.setAttribute("class", "home-description left")
                }
                span.append(a);
                li.appendChild(span);

                var a = document.createElement("a");
                if (all_status[table] === "Uploaded") {
                    a.setAttribute("style", "color: blue");
                }
                else if (all_status[table] === "Processing") {
                    a.setAttribute("style", "color: orangered");
                    processing_count += 1;
                }
                else if (all_status[table] === "Error") {
                    a.setAttribute("style", "color: red");
                }
                else if (all_status[table] === "Out of Space") {
                    a.setAttribute("style", "color: red");
                }
                else {
                    a.setAttribute("style", "color: seagreen");
                }
                a.innerText = all_status[table];
                a.setAttribute("class", "right");
                var span = document.createElement("span");

                // Set no link for disk full
                if (all_status[table] === "Out of Space") {
                    a.setAttribute("href", "#");
                    span.setAttribute("class", "left disk-full");
                }
                else {
                    a.setAttribute("href", link);
                    span.setAttribute("class", "left");
                }

                span.setAttribute("style", "padding-left: inherit; margin-left: inherit;")
                span.append(a);
                li.appendChild(span);

                // Add the space left
                var span = document.createElement("span");
                span.setAttribute("class", "left");
                var a = document.createElement("a");
                a.innerText = all_space[table];
                span.setAttribute("style", "padding-left: inherit; margin-left: inherit;")
                span.append(a);
                li.appendChild(span);

                // Add the delete button
                var button = document.createElement("button");
                button.setAttribute("type", "button");
                // button.setAttribute("@click", "deleteItem(index)");
                button.setAttribute("class", "right delete");
                button.id = all_data[table];
                button.innerText = "X";
                li.append(button);

                list_group.appendChild(li);
            }
        }
    }).fail(function(xhr) {
        try {
            var msg = $.parseJSON(xhr.responseText)
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
}

// Function to make the button active for delete
function deleteready() {
    // Event listener for deleting datasets
    [...document.querySelectorAll('.delete')].forEach(function (item) {
        item.addEventListener('click', function () {
            // Get the name of the dataset to delete
            var data_to_delete = item.id;

            // Show the modal to confirm if the user wants to delete or not
            var modal = document.getElementById("confirmModal");
            var yes_span = document.getElementsByClassName("sadyeah")[0];
            var no_span = document.getElementsByClassName("sadno")[0];
            modal.style.display = "block";

            yes_span.onclick = function () {
                modal.style.display = "none";

                var file_data = {};
                file_data['filename'] = data_to_delete;
                file_data['page'] = "Page2";

                var actual_file_data = JSON.parse(JSON.stringify(file_data));

                // Call the ajax function to delete the dataset
                $.ajax({
                    url: '/tabledelete/',
                    type: 'POST',
                    data: actual_file_data,
                    dataType: "json",
                    async: false,
                }).done(function (message) {
                    // Refresh the dataset list
                    update_table(random_table_list);
                    window.location.href = message['url'];
                }).fail(function(xhr) {
                    try {
                        var msg = $.parseJSON(xhr.responseText)
                        $("#error_msg").text(msg.message);
                        $("#error_dialog").css("display", "block");
                    } catch(e) {
                        $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
                        $("#error_dialog").css("display", "block");
                    }
                });
            }
            no_span.onclick = function () {
                modal.style.display = "none";
            }

        });
    });

    // Event listener for datasets that have status = "Disk Full"
    [...document.querySelectorAll('.disk-full')].forEach(function (item) {
        item.addEventListener('click', function () {
            // Show alert
            alert("Please delete this dataset!!")
        });
    });
}

//------------------------------------------------------------------------------

//*********************************************************************
// On click of submit button
$(function () {
    $("#btnSubmit").on("click", function(e){
        var main = document.getElementsByClassName("main");
        main.q.value = "";

        var chosen_value = $('#all_attributes').val();
        console.log(chosen_value);
        for (var i = 0; i < chosen_value.length; i ++) {

            var actual_id = chosen_value[i].substr(0, chosen_value[i].indexOf(':'));
            var actual_text = chosen_value[i].substr(chosen_value[i].indexOf(':') + 1);

            if (actual_id === actual_text) {
                main.q.value += actual_text + ";";
            }
            else {
                main.q.value += chosen_value[i] + ";";
            }
        }
        if (main.q.value !== "") {
            main.q.value = main.q.value.slice(0, -1);
        }
        $("#theform").attr("action", "/ba/search/");
        $("#theform").submit();

    });
});

//------------------------------------------------------------------------------

//*********************************************************************
// For attributes, graphs and order by in the Query Builder (standalone)
/*
$(document).ready(function() {
    $("#attributesSchema").select2({
        placeholder: 'Select Attributes',
        allowClear: false,
        maximumSelectionLength: Object.keys(window.attribute_unique_data_values).length,
        templateResult: function (data) {

            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }
            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });
});

$(document).ready(function() {
    $("#graphType").select2({
        placeholder: 'Select Graphs',
        allowClear: false,
        templateResult: function (data) {

            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }
            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });
});

$(document).ready(function() {
    $("#orderType").select2({
        placeholder: 'Order By',
        allowClear: false,
        templateResult: function (data) {

            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }
            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });
});



//*********************************************************************
// On select/unselect functions for standalone query builder
//*********************************************************************
// On select/unselect for Attributes
$( "#attributesSchema" ).on('select2:select', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    //Separate the actual attribute name and attribute value
    var actual_id = selected_id.substr(0, selected_id.indexOf(':'));
    var actual_text = selected_text.substr(selected_text.indexOf(':') + 1);

    // Update the universal holder of items selected - essentially if an attribute is selected
    if (actual_text === actual_id) {
        values_currently_selected.push(actual_id);
    }

    // Give a warning to the user is more than two attributes are selected
    if (values_currently_selected.length > 2 && actual_id === actual_text) {
        alert("Cannot select more than two attributes!!!");

        // Remove the attribute that the user could not add
        var curr_index = values_currently_selected.indexOf(actual_id);
        if (curr_index !== -1) {
            values_currently_selected.splice(curr_index, 1);
        }

        //$('#attributesSchema').val(options_that_are_selected_by_user);
        //$('#attributesSchema').trigger('change'); // Notify any JS components that the value changed
        //$('#attributesSchema').select2('close');


        // Add to the main search/select bar
        $('#all_attributes').val(options_that_are_selected_by_user);
        $('#all_attributes').trigger('change'); // Notify any JS components that the value changed
        $('#all_attributes').select2('close');
    }

    else
    {
        // Add to search bar
        var main = document.getElementsByClassName("main");
        main.q.value += " " + selected_text;

        var attributes = document.getElementById("attributesSchema");

        var attributes_to_destroy = [];

        // Create the options group for each attribute
        for (var i = 0; i < attributes.children.length; i++) {

            var actual_attribute_value = attributes.children[i].value;
            actual_attribute_value = actual_attribute_value.substr(0, actual_attribute_value.indexOf(':'))

            if (actual_attribute_value === actual_id) {
                attributes_to_destroy.push(attributes.children[i].value);
            }
        }

        // Remove the attribute and its sub parts that were selected
        for (var i = 0; i < attributes_to_destroy.length; i++) {
            $("#attributesSchema option[value='" + attributes_to_destroy[i] + "']").remove();
        }

        // We have to add back the attribute that was selected
        // There are two cases - Attribute selected or sub-attribute selected
        if (actual_id === actual_text) {
            var option = document.createElement("option");
            option.setAttribute("class", "l1");
            option.setAttribute("value", selected_id);
            option.text = actual_id;
            attributes.appendChild(option);
        } else {
            var option = document.createElement("option");
            option.setAttribute("class", "l2");
            option.setAttribute("value", selected_id);
            option.text = selected_text;
            attributes.appendChild(option);
        }
        options_that_are_selected_by_user.push(selected_id);

        $('#attributesSchema').val(options_that_are_selected_by_user);

        // Refresh button
        $("#attributesSchema").select2({
            placeholder: 'Select Attributes',
            allowClear: false,
            maximumSelectionLength: Object.keys(window.attribute_unique_data_values).length,
            templateResult: function (data) {
                // We only really care if there is an element to pull classes from
                if (!data.element) {
                    return data.text;
                }

                var $element = $(data.element);

                var $wrapper = $('<span></span>');
                $wrapper.addClass($element[0].className);

                $wrapper.text(data.text);

                return $wrapper;
            }
        });

        // Add to the main search/select bar
        $('#all_attributes').val(options_that_are_selected_by_user);

        // Refresh button
        $("#all_attributes").select2({
            placeholder: 'Select Attributes/Graphs',
            allowClear: false,
            maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
            templateResult: function (data) {

                // We only really care if there is an element to pull classes from
                if (!data.element) {
                    return data.text;
                }

                var $element = $(data.element);

                var $wrapper = $('<span></span>');
                $wrapper.addClass($element[0].className);

                $wrapper.text(data.text);

                return $wrapper;
            }
        });

    }

});

$( "#attributesSchema" ).on('select2:unselect', function(e) {

    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    //Separate the actual attribute name and attribute value
    var actual_id = selected_id.substr(0, selected_id.indexOf(':'));
    var actual_text = selected_text.substr(selected_text.indexOf(':') + 1);

    // Remove from search bar
    var main = document.getElementsByClassName("main");
    main.q.value = main.q.value.trim();
    main.q.value = main.q.value.replace(selected_text, "");

    // For double surity
    if ($('#attributesSchema').val().length === 0) {
        main.q.value = "";
    }

    // Update the universal holder of items selected
    if (actual_id === actual_text) {
        var curr_index = values_currently_selected.indexOf(selected_id);
        if (curr_index !== -1) {
            values_currently_selected.splice(curr_index, 1);
        }
    }


    // Remove the attributes based on the selection made
    var attributes = document.getElementById("attributesSchema");

    // Create the options group for each attribute
    for (var i = 0; i < attributes.children.length; i++) {

        if (attributes.children[i].value === selected_id) {
            $("#attributesSchema option[value='" + attributes.children[i].value + "']").remove();
        }
    }
    // Add the attribute that was removed
    // Create the options group for each attribute
    var option = document.createElement("option");
    option.setAttribute("class", "l1");
    var attr_attr = actual_id + ":" + actual_id;
    option.setAttribute("value", attr_attr);
    option.text = actual_id;
    attributes.appendChild(option);
    for (var unique_value in window.attribute_unique_data_values[actual_id]) {
        var option = document.createElement("option");
        option.setAttribute("class", "l2");
        var updated_text = actual_id + ":" + window.attribute_unique_data_values[actual_id][unique_value];
        option.setAttribute("value", updated_text);
        option.text = updated_text;
        attributes.appendChild(option);
    }
    var curr_index = options_that_are_selected_by_user.indexOf(selected_id);
    if (curr_index !== -1) {
        options_that_are_selected_by_user.splice(curr_index, 1);
    }


    $('#attributesSchema').val(options_that_are_selected_by_user);

    // Refresh button
    $("#attributesSchema").select2({
        placeholder: 'Select Attributes',
        allowClear: false,
        maximumSelectionLength: Object.keys(window.attribute_unique_data_values).length,
        templateResult: function (data) {
            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }

            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });

    // Remove from the main search/select bar
    $('#all_attributes').val(options_that_are_selected_by_user);

    // Refresh button
    $("#all_attributes").select2({
        placeholder: 'Select Attributes/Graphs',
        allowClear: false,
        maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
        templateResult: function (data) {
            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }

            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });

});

//*********************************************************************
// On select/unselect for Graphs
$( "#graphType" ).on('select2:select', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    // Add to search bar
    var main = document.getElementsByClassName("main");
    main.q.value += " " + selected_text;

    options_that_are_selected_by_user.push(selected_id);

    $('#all_attributes').val(options_that_are_selected_by_user);

    // Refresh button
    $("#all_attributes").select2({
        placeholder: 'Select Attributes/Graphs',
        allowClear: false,
        maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
        templateResult: function (data) {

            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }

            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });
});

$( "#graphType" ).on('select2:unselect', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    // Remove from search bar
    var main = document.getElementsByClassName("main");
    main.q.value = main.q.value.trim();
    main.q.value = main.q.value.replace(selected_text, "");

    // For double surity
    if ($('#all_attributes').val().length === 0) {
        main.q.value = "";
    }

    var curr_index = options_that_are_selected_by_user.indexOf(selected_id);
    if (curr_index !== -1) {
        options_that_are_selected_by_user.splice(curr_index, 1);
    }


    $('#all_attributes').val(options_that_are_selected_by_user);

    // Refresh button
    $("#all_attributes").select2({
        placeholder: 'Select Attributes/Graphs',
        allowClear: false,
        maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
        templateResult: function (data) {
            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }

            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });

});
//*********************************************************************
// On select/unselect for Order By
$( "#orderType" ).on('select2:select', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    // Add to search bar
    var main = document.getElementsByClassName("main");
    main.q.value += " " + selected_text;

    options_that_are_selected_by_user.push(selected_id);

    $('#all_attributes').val(options_that_are_selected_by_user);

    // Refresh button
    $("#all_attributes").select2({
        placeholder: 'Select Attributes/Graphs',
        allowClear: false,
        maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
        templateResult: function (data) {

            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }

            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });
});

$( "#orderType" ).on('select2:unselect', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    // Remove from search bar
    var main = document.getElementsByClassName("main");
    main.q.value = main.q.value.trim();
    main.q.value = main.q.value.replace(selected_text, "");

    // For double surity
    if ($('#all_attributes').val().length === 0) {
        main.q.value = "";
    }

    var curr_index = options_that_are_selected_by_user.indexOf(selected_id);
    if (curr_index !== -1) {
        options_that_are_selected_by_user.splice(curr_index, 1);
    }


    $('#all_attributes').val(options_that_are_selected_by_user);

    // Refresh button
    $("#all_attributes").select2({
        placeholder: 'Select Attributes/Graphs',
        allowClear: false,
        maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
        templateResult: function (data) {
            // We only really care if there is an element to pull classes from
            if (!data.element) {
                return data.text;
            }

            var $element = $(data.element);

            var $wrapper = $('<span></span>');
            $wrapper.addClass($element[0].className);

            $wrapper.text(data.text);

            return $wrapper;
        }
    });

});


//------------------------------------------------------------------------------
// This is the javascript query for the standalone select/search bar

$("#all_attributes").select2({
    placeholder: 'Select Attributes/Graphs',
    allowClear: false,
    maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
    templateResult: function (data) {
        // We only really care if there is an element to pull classes from
        if (!data.element) {
            return data.text;
        }

        var $element = $(data.element);

        var $wrapper = $('<span></span>');
        $wrapper.addClass($element[0].className);

        $wrapper.text(data.text);

        return $wrapper;
    }
});

// Always listening
// # If some of the tags are removed or added in the section - Top questions based on tags
// $( "#all_attributes" ).change(function() {
$( "#all_attributes" ).on('select2:select', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    //Separate the actual attribute name and attribute value
    var actual_id = selected_id.substr(0, selected_id.indexOf(':'));
    var actual_text = selected_text.substr(selected_text.indexOf(':') + 1);


    // NOTE : Score and support have been added in graph types
    var graph_types = ['bargraph', 'groupedBargraph', 'heatmap', 'histogram', 'scatter', 'boxplot', 'Score', 'Support'];

    // NOTE : The second condition is for graphs and order by
    if (!graph_types.includes(actual_id) && actual_id !== "") {

        // Update the universal holder of items selected - essentially if an attribute is selected
        if (actual_id === actual_text) {
            values_currently_selected.push(actual_id);
        }

        // Give a warning to the user is more than two attributes are selected
        if (values_currently_selected.length > 2 && actual_text === actual_id) {
            alert("Cannot select more than two attributes!!!");

            // Remove the attribute that the user could not add
            var curr_index = values_currently_selected.indexOf(actual_id);
            if (curr_index !== -1) {
                values_currently_selected.splice(curr_index, 1);
            }

            $('#all_attributes').val(options_that_are_selected_by_user);
            $('#all_attributes').trigger('change'); // Notify any JS components that the value changed
            $('#all_attributes').select2('close');
        } else {
            // Add to search bar
            var main = document.getElementsByClassName("main");
            main.q.value += " " + selected_text;

            // $('#all_attributes optgroup[label="Attributes"] option[value="GRADE"]').remove()
            var attributes = document.getElementById("Attributes");

            var attributes_to_destroy = [];

            // Create the options group for each attribute
            for (var i = 0; i < attributes.children.length; i++) {

                var actual_attribute_value = attributes.children[i].value;
                actual_attribute_value = actual_attribute_value.substr(0, actual_attribute_value.indexOf(':'))

                if (actual_attribute_value === actual_id) {
                    attributes_to_destroy.push(attributes.children[i].value);
                }
            }

            // Remove the attribute and its sub parts that were selected
            for (var i = 0; i < attributes_to_destroy.length; i++) {
                $("#all_attributes optgroup[label='Attributes'] option[value='" + attributes_to_destroy[i] + "']").remove();
            }

            // We have to add back the attribute that was selected
            // There are two cases - Attribute selected or sub-attribute selected
            if (actual_id === actual_text) {
                var option = document.createElement("option");
                option.setAttribute("class", "l1");
                option.setAttribute("value", selected_id);
                option.text = actual_id;
                attributes.appendChild(option);
            } else {
                var option = document.createElement("option");
                option.setAttribute("class", "l2");
                option.setAttribute("value", selected_id);
                option.text = selected_text;
                attributes.appendChild(option);
            }
            options_that_are_selected_by_user.push(selected_id);

            $('#all_attributes').val(options_that_are_selected_by_user);
            // $('#all_attributes').trigger ('change'); // Notify any JS components that the value changed
            // $('#all_attributes').select2('close');


            // Refresh button
            $("#all_attributes").select2({
                placeholder: 'Select Attributes/Graphs',
                allowClear: false,
                maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
                templateResult: function (data) {

                    // We only really care if there is an element to pull classes from
                    if (!data.element) {
                        return data.text;
                    }

                    var $element = $(data.element);

                    var $wrapper = $('<span></span>');
                    $wrapper.addClass($element[0].className);

                    $wrapper.text(data.text);

                    return $wrapper;
                }
                // },
                // templateSelection: function(item) {
                //     var selected_id = item.id;
                //     var selected_text = item.text;
                //
                //     if (selected_text !== selected_id) {
                //         return selected_id + ":" + selected_text;
                //     }
                //     else {
                //         return selected_id;
                //     }
                // }
            });
        }
    } else {
        // Add to search bar
        var main = document.getElementsByClassName("main");
        main.q.value += " " + selected_text;

        options_that_are_selected_by_user.push(selected_id);

        $('#all_attributes').val(options_that_are_selected_by_user);
    }

});

$( "#all_attributes" ).on('select2:unselect', function(e) {

    var selected_id = e.params.data.id;
    var selected_text = e.params.data.text;

    //Separate the actual attribute name and attribute value
    var actual_id = selected_id.substr(0, selected_id.indexOf(':'));
    var actual_text = selected_text.substr(selected_text.indexOf(':') + 1);


    // NOTE : Score and support have been added in graph types
    var graph_types = ['bargraph', 'groupedBargraph', 'heatmap', 'histogram', 'scatter', 'boxplot', 'Score', 'Support'];

    // NOTE : The second condition is for graphs and order by
    if (!graph_types.includes(actual_id) && actual_id !== "") {

        // Remove from search bar
        var main = document.getElementsByClassName("main");
        main.q.value = main.q.value.trim();
        main.q.value = main.q.value.replace(selected_text, "");

        // For double surity
        if ($('#all_attributes').val().length === 0) {
            main.q.value = "";
        }

        // Update the universal holder of items selected
        if (actual_id === actual_text) {
            var curr_index = values_currently_selected.indexOf(actual_id);
            if (curr_index !== -1) {
                values_currently_selected.splice(curr_index, 1);
            }
        }


        // Remove the attributes based on the selection made
        var attributes = document.getElementById("Attributes");

        // Create the options group for each attribute
        for (var i = 0; i < attributes.children.length; i++) {

            if(attributes.children[i].value === selected_id) {
                $("#all_attributes optgroup[label='Attributes'] option[value='" + attributes.children[i].value + "']").remove();
            }
        }
        // Add the attribute that was removed
        // Create the options group for each attribute
        var option = document.createElement("option");
        option.setAttribute("class", "l1");
        var attr_attr = actual_id + ":" + actual_id;
        option.setAttribute("value", attr_attr);
        option.text = actual_id;
        attributes.appendChild(option);
        for (var unique_value in window.attribute_unique_data_values[actual_id]) {
            var option = document.createElement("option");
            option.setAttribute("class", "l2");
            var actual_text = actual_id + ":" + window.attribute_unique_data_values[actual_id][unique_value];
            option.setAttribute("value", actual_text);
            option.text = actual_text;
            attributes.appendChild(option);
        }
        var curr_index = options_that_are_selected_by_user.indexOf(selected_id);
        if (curr_index !== -1) {
            options_that_are_selected_by_user.splice(curr_index, 1);
        }


        $('#all_attributes').val(options_that_are_selected_by_user);
        // $('#all_attributes').trigger ('change'); // Notify any JS components that the value changed
        // $('#all_attributes').select2('close');

        // Refresh button
        $("#all_attributes").select2({
            placeholder: 'Select Attributes/Graphs',
            allowClear: false,
            maximumSelectionLength: (Object.keys(window.attribute_unique_data_values).length + 5),
            templateResult: function (data) {
                // We only really care if there is an element to pull classes from
                if (!data.element) {
                    return data.text;
                }

                var $element = $(data.element);

                var $wrapper = $('<span></span>');
                $wrapper.addClass($element[0].className);

                $wrapper.text(data.text);

                return $wrapper;
            }
        });

    } else {

        // Remove from search bar
        var main = document.getElementsByClassName("main");
        main.q.value = main.q.value.trim();
        main.q.value = main.q.value.replace(selected_text, "");

        var curr_index = options_that_are_selected_by_user.indexOf(selected_id);
        if (curr_index !== -1) {
            options_that_are_selected_by_user.splice(curr_index, 1);
        }

        $('#all_attributes').val(options_that_are_selected_by_user);
    }

});
*/

$('#download_link').on("click", function(e){
    e.preventDefault()
    var dataset_name = $('#dataset_name_placeholder').text().split(":")[1].trim();
    window.location.href = "/ba/download/" + dataset_name;
});

runner();

// Reset the select options
$('#all_attributes').val("").trigger('change');
//$("#attributesSchema").val("").trigger('change');
//$("#graphType").val("").trigger('change');
//$("#orderType").val("").trigger('change');

// $("#all_attributes").select2("val", "");
// $("#attributesSchema").select2("val", "");
// $("#graphType").select2("val", "");
// $("#orderType").select2("val", "");

// ------------------------------------------------------------------------------------

// Function that keeps pinging until a the processing is complete
var current_progress_status = "";
// Function call to start the ping for the first time


function ping(){

    var file_data = {};
    file_data['actual_filename'] = current_filename;
    file_data['status'] = "Uploaded";

    var actual_file_data = JSON.parse(JSON.stringify(file_data));

    $.ajax({
        url:'/progress_check/',
        type: 'POST',
        data: actual_file_data,
        datatype: "json",
        async: false
    }).done((data)=>{
        current_progress_status = data['status'];
        var progress = data['progress'];

        // Check if the progress is "Done"
        if (current_progress_status === "Done") {

            var progress_bar = document.getElementById("progress_bar");
            progress_bar.setAttribute("class", "progress-bar bg-success");
            progress_bar.setAttribute("style", "width: 100%;");
            progress_bar.setAttribute("aria-valuenow", "100");
            progress_bar.innerText = "Done"

            // Refresh the dataset list
            update_table(random_table_list);
            deleteready();

        }
        else if (current_progress_status === "Error") {

            var progress_bar = document.getElementById("progress_bar");
            progress_bar.setAttribute("class", "progress-bar bg-danger");
            progress_bar.setAttribute("style", "width: 100%;");
            progress_bar.setAttribute("aria-valuenow", "100");
            progress_bar.innerText = "Error"

            // Refresh the dataset list
            update_table(random_table_list);
            deleteready();

            // Show the user the pop-up to re-run the code again
            var modal = document.getElementById("rerunModal");
            var yes_span = document.getElementsByClassName("hmmmyeah")[0];
            var no_span = document.getElementsByClassName("hmmmno")[0];
            modal.style.display = "block";

            yes_span.onclick = function () {
                modal.style.display = "none";

                // Ask the user for the minimum support
                var minsupmodal = document.getElementById("minsupModal");
                var minsupyeah = document.getElementsByClassName("minsupyeah")[0];
                minsupmodal.style.display = "block";

                minsupyeah.onclick = function () {
                    minsupmodal.style.display = "none";

                    // Get the value of the minimum support
                    var minsup = document.getElementById("minsupvalue");

                    var file_data = {};
                    file_data['filename'] = current_filename;
                    file_data['minsup'] = minsup.value;

                    var actual_file_data = JSON.parse(JSON.stringify(file_data));

                    // Remove the relevant files and re-run with a smaller support
                    // Call the ajax function to rerun the dataset with a lower minimum support
                    $.ajax({
                        url: '/tablererun/',
                        type: 'POST',
                        data: actual_file_data,
                        dataType: "json",
                        async: false,
                    }).done(function (message) {
                        // Refresh the dataset list
                        window.location.href = message['url'];
                    }).fail(function(xhr){
                        try {
                            var msg = $.parseJSON(xhr.responseText)
                            $("#error_msg").text(msg.message);
                            $("#error_dialog").css("display", "block");
                        } catch(e) {
                            $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
                            $("#error_dialog").css("display", "block");
                        }
                    });
                }
            }

            no_span.onclick = function () {
                modal.style.display = "none";

                var file_data = {};
                file_data['filename'] = current_filename;
                file_data['page'] = "Page2";

                var actual_file_data = JSON.parse(JSON.stringify(file_data));

                // Remove the relevant files and redirect to homepage
                // Call the ajax function to delete the dataset
                $.ajax({
                    url: '/tabledelete/',
                    type: 'POST',
                    data: actual_file_data,
                    dataType: "json",
                    async: false,
                }).done(function (message) {
                    // Refresh the dataset list
                    update_table(random_table_list);
                    window.location.href = message['url'];
                }).fail(function(xhr){
                    try {
                        var msg = $.parseJSON(xhr.responseText)
                        $("#error_msg").text(msg.message);
                        $("#error_dialog").css("display", "block");
                    } catch(e) {
                        $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
                        $("#error_dialog").css("display", "block");
                    }
                });
            }
        }
        else if (current_progress_status === "Processing") {
            var percent_value = "width: " + progress + "%"

            var progress_bar = document.getElementById("progress_bar");
            progress_bar.setAttribute("style", percent_value);
            progress_bar.setAttribute("aria-valuenow", progress);
            progress_bar.innerText = "Loading...."

        }

        else if (current_progress_status === "Out of Space") {

            // Update the table list
            update_table(random_table_list);
            deleteready();

            var progress_bar = document.getElementById("progress_bar");
            progress_bar.setAttribute("class", "progress-bar bg-danger");
            progress_bar.setAttribute("style", "width: 100%;");
            progress_bar.setAttribute("aria-valuenow", "100");
            progress_bar.innerText = "Out of Space"


            var modal = document.getElementById("diskfullModal");
            modal.style.display = "block";



            var some_other_data = {};
            some_other_data['filename'] = current_filename;

            var some_data = JSON.parse(JSON.stringify(some_other_data));

            // Wait for 5 seconds and then stop the display
            setTimeout(function(){modal.style.display = "none";}, 5000);
            $.ajax({
                url: '/tabledeletebecauseofdisk/',
                type: 'POST',
                data: some_data,
                dataType: "json",
                async: false,
            }).done(function (message) {
                // Refresh the dataset list
                update_table(random_table_list);
                setTimeout(function(){window.location.href = message['url'];}, 5000);
                // window.location.href = message['url'];
            }).fail(function(xhr){
                try {
                    var msg = $.parseJSON(xhr.responseText)
                    $("#error_msg").text(msg.message);
                    $("#error_dialog").css("display", "block");
                } catch(e) {
                    $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
                    $("#error_dialog").css("display", "block");
                }
            });
        }

    }).fail(function(xhr){
        try {
            var msg = $.parseJSON(xhr.responseText)
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
}
// Function to continuosly ping
function runner(){
    ping()
    setTimeout( () => {
        if (current_progress_status !== "Done" && current_progress_status !== "Out of Space") {
            runner();
        }
    }, 1000)
}

//Calling runner2 once
runner2();

// Function to ping continuously and inform the user that the disk is full
var processing_count = 1;

function ping2() {
    processing_count = 0;
    // Call update table
    update_table(random_table_list);
    deleteready();
    // console.log(processing_count);
}
// Function to continuosly ping
function runner2(){
    ping2()
    setTimeout( () => {
        if (processing_count  != 0) {
            runner2();
        }
    }, 5000)
}
