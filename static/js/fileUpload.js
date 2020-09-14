
// Global variables
var header_row;
var file_name;

window.all_data = {};
window.attribute_type = {};
window.attributes_to_keep = {}

// Show list of datasets that are already loaded into mysql
var random_table_list = {};
random_table_list['table'] = "Some_random_data";
// Call the function update_table
update_table(random_table_list);

// // Event listener for the datasets already loaded
// document.getElementById("list_group").addEventListener("click",function(e) {
//
//     // Navigate to the corresponding page
//     window.location.href = "/ba/dataset/" + e.target.innerText;
// });

// Event listener for the search button
document.getElementById("btnSubmit").addEventListener("click",function(e) {
    alert("You cannot search anything here.");
    // window.location.href = "/";
});

// Event based function for click on upload
//$(function () {
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
            console.log(formdata);
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
//});

function tablecheck(file_name) {
    var table_list = {};
    table_list['table'] = file_name;
    var flag = 0;

    // Check the tables present in the database
    $.ajax({
        url: '/tablecheck/',
        type: 'POST',
        data: table_list,
        async: false,
    }).done(function (data) {
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
                console.log("called1");
                file_and_data_loader();
            }
            no_span.onclick = function () {
                modal.style.display = "none";
                // Navigate to the corresponding page
                window.location.href = "/ba/dataset/" + file_name;

            }
        } else {
            // Clear the all_data variable
            window.all_data = {};
            console.log("called2");
            file_and_data_loader();
        }
    }).fail(function(xhr) {
        var msg = $.parseJSON(xhr.responseText);
        $("#error_msg").text(msg.message);
        $("#error_dialog").css("display", "block");
    });


}

document.getElementById("itsokay").addEventListener("click", function(){
    var excludemodal = document.getElementById("requiredModal");
    excludemodal.style.display = "none";

    //update selectornot window variable. It contains an object of all the attributes.   
    var attributes_left = document.getElementById("attributesStuff");
    for (var i = 0; i < attributes_left.children.length; i++) {
        var name = attributes_left.children[i].children[0].value;
        var value = attributes_left.children[i].children[0].checked;
        window.attributes_to_keep[name] = (value).toString();
    }
    var selectedornot = document.getElementById("selectedornot");
    selectedornot.value = JSON.stringify(window.attributes_to_keep);

    var schema_tag = document.getElementById("schema");

    window.attribute_type = {};
    var number_of_numerical_count = 0;

    var namesOfAttributesToBeRemoved = [];

    var attributesStuffList = document.getElementById("attributesStuff");
    for (var i=0; i<attributesStuffList.children.length; i++){
        var currentChild = attributesStuffList.children[i];
        var currentCheckBox = currentChild.children[0];
        if (currentCheckBox.checked){
            console.log(currentCheckBox.value);
            namesOfAttributesToBeRemoved.push(currentCheckBox.value);
        }
    }

    for (var i = 0; i < schema_tag.children.length; i++) {
        var name = schema_tag.children[i].children[1].children[0].children[0].name;
        console.log(name);
        if (namesOfAttributesToBeRemoved.includes(name)){
            continue;
        }
        
        var isNumerical = (schema_tag.children[i].children[1].children[0].children[0].checked).toString();
        var isCategorical = (schema_tag.children[i].children[1].children[1].children[0].checked).toString();
        var isTimeSeries = (schema_tag.children[i].children[1].children[2].children[0].checked).toString();

        if (isNumerical === "true"){
            attribute_type[name] = "num";
        }else if (isCategorical === "true"){
            attribute_type[name] = "cat";
        }else{
            attribute_type[name] = "timeseries";
        }

        // Store the attribute types in the input
        //var cat_num = document.getElementById("cat_num");
        //cat_num.value = JSON.stringify(attribute_type);

        if (isNumerical === "true") {
            number_of_numerical_count += 1;
        }
    }

    // Store the attribute types in the input
    var cat_num = document.getElementById("cat_num");
    cat_num.value = JSON.stringify(attribute_type);

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
                $("#theform").submit();
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
                    $("#theform").submit();
                }).fail(function(xhr){
                    var msg = $.parseJSON(xhr.responseText)
                    $("#error_msg").text(msg.message);
                    $("#error_dialog").css("display", "block");
                });

                // Submit the form
                // document.getElementById('theform').submit();
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
                $("#theform").submit();
            }).fail(function(xhr){
                var msg = $.parseJSON(xhr.responseText)
                $("#error_msg").text(msg.message);
                $("#error_dialog").css("display", "block");
            });

            // Submit the form
            // document.getElementById('theform').submit();
            //document.theform.submit();
        }
    }
});




//------------------------------------------------------------------------------

//*********************************************************************
// Standlone functions

$("#errorDialogButton").on("click", function(e){
    $("#error_dialog").css("display", "none");
});

function renderDatasetTemplateFromData(dataset) {
    console.log("dadadadad ---- " + dataset)
    console.log("dadadadad ---- " + dataset['summary']['rank'][0])
    $.ajax({
        url: '/render/',
        type: 'POST',
        data: dataset,
        contentType: 'application/json',
    }).done(function(data){
        console.log("template rendered");
    }).fail(function(xhr){
        alert("Failure")
    });
}

function loadDatasetAfterUpload(datasetUrl) {
    $.ajax({
        url: datasetUrl,
        //accepts: 'application/json',
    }).done(function(data){
        console.log("Dataset loaded successfully.");
        var summa = data['summary'];
        console.log("summa - " + summa);
        renderDatasetTemplateFromData(data)
    
        //window.location.href = datasetUrl;
    }).fail(function(xhr){
        try {
            var msg = $.parseJSON(xhr.responseText);
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
}

$("#theform").on("submit", function(e){
       e.preventDefault();
       console.log("in submit");
       var formdata = new FormData(this);
       $.ajax({
           url: '/upload/',
           type: 'POST',
           data: formdata,
           processData: false,
           //async: false,
           contentType: false,
           cache: false,
        }).done(function(data){
            console.log("File uploaded successfully");
            var redirectUrl = data['url'];
            //tableadd(redirectUrl);
            window.location.href = redirectUrl; 
        }).fail(function(xhr){
           try {
               //deleteTable();
               var msg = $.parseJSON(xhr.responseText)
               $("#error_msg").text(msg.message);
               $("#error_dialog").css("display", "block");
           } catch(e) {
               $("#error_msg").text("Unexpected error occurred. Please check system logs. " + e);
               $("#error_dialog").css("display", "block");
           }
       });
});

function deleteTable() {
    // Data for the file uploaded
    var files = document.getElementById("fileUpload");
    file_name = files.files[0].name;
    file_name = file_name.replace('.csv', '');
    console.log(file_name);
    var file_data = {};
    file_data['filename'] = file_name;
    file_data['page'] = "Page1";
    var actual_file_data = JSON.parse(JSON.stringify(file_data));
    $.ajax({
        url: '/tabledelete/',
        type: 'POST',
        data: actual_file_data,
        async: false
    }).done(function (message){
        //window.location.href = redirectUrl;
    }).fail(function(xhr) {
        var msg = $.parseJSON(xhr.responseText);
        $("#error_msg").text(msg.message);
        $("#error_dialog").css("display", "block");
    });

}

// Loading the file and data
function file_and_data_loader() {
    var regex = /^([a-zA-Z0-9\s_\\.\-:])+(.csv|.txt)$/;
    if (regex.test($("#fileUpload").val().toLowerCase())) {
        console.log("inside fileupload function");
        if (typeof (FileReader) != "undefined") {
            console.log("inside filereader function");
            var reader = new FileReader();
            reader.onload = function (e) {
                console.log("inside onload function");
                var rows = e.target.result.split("\n");

                // Get the header
                header_row = rows[0];
                console.log(header_row);
                //header_row = header_row.replace(/,{1,}$/, '');
                //header_row = header_row.split(",");
                header_row = header_row.split(',')
                                 .filter(function(val,b){
                                    return val.length
                                 });
                //header_row = header_row.filter(item => item);
                /*for (var i=0; i<header_row.length; i++){
                    console.log("next ele");
                    console.log(header_row[i]);
                    console.log(header_row[i].length)
                }*/
                while (header_row[header_row.length-1].length === 1){ 
                    header_row.pop();
                }

                console.log(header_row);
                var new_header_list = [];
                var pop_up_list = document.getElementById("schema");
                while(pop_up_list.hasChildNodes()) {
                    pop_up_list.removeChild(pop_up_list.firstChild);
                }

                //First, allow the user to choose CAT/NUM variable
                for(var i = 0; i < header_row.length; i++) {
                    var fieldset = document.createElement("fieldset");
                    var para = document.createElement("p");
                    var text_content = document.createTextNode(header_row[i] + " :  ")
                    para.appendChild(text_content);
                    para.setAttribute("style", "display:inline-block");

                    fieldset.appendChild(para);

                    var para = document.createElement("p")
                    para.setAttribute("style", "display:inline-block");

                    var label = document.createElement("label");
                    var input = document.createElement("input");
                    input.setAttribute("type", "radio");
                    input.setAttribute("name", header_row[i]);
                    input.setAttribute("value", header_row[i]+"_num");

                    var text_content = document.createTextNode("Numerical")
                    label.appendChild(input);
                    label.appendChild(text_content);

                    para.appendChild(label);

                    var label = document.createElement("label");
                    var input = document.createElement("input");
                    input.setAttribute("type", "radio");
                    input.setAttribute("name", header_row[i]);
                    input.setAttribute("value", header_row[i]+"_cat");
                    input.setAttribute("checked", true);

                    var text_content = document.createTextNode("Categorical")
                    label.appendChild(input);
                    label.appendChild(text_content);

                    para.appendChild(label);
                    
                    var label = document.createElement("label");
                    var input = document.createElement("input");
                    input.setAttribute("type", "radio");
                    input.setAttribute("name", header_row[i]);
                    input.setAttribute("value", header_row[i]+"_timeseries");

                    var text_content = document.createTextNode("Time Series")
                    label.appendChild(input);
                    label.appendChild(text_content);

                    para.appendChild(label);
                    
                    fieldset.appendChild(para);
                    pop_up_list.appendChild(fieldset);
                }
                
                var modal = document.getElementById("myModal");
                var span = document.getElementsByClassName("close")[0];
                console.log("here");
                modal.style.display = "block";
                
                //Function on click of ok button of NUM/CAT selection
                span.onclick = function () {
                    modal.style.display = "none";
                    
                    var categoricalAttributeList = [];
                    var timeseriesnumberofattributes = 0;

                    var schema_tag = document.getElementById("schema");
                    for (var i = 0; i < schema_tag.children.length; i++) {
                        var name = schema_tag.children[i].children[1].children[0].children[0].name;
                        var categoricalattribute = (schema_tag.children[i].children[1].children[1].children[0].checked).toString();
                        var timeseriesattribute = (schema_tag.children[i].children[1].children[2].children[0].checked).toString();
                        if (categoricalattribute === "true") { //pushing CAT attribute name to list
                            categoricalAttributeList.push(name);
                        }
                        if (timeseriesattribute === "true"){
                            timeseriesnumberofattributes += 1;
                        }
                    }
                        
                    
                    /*var files = document.getElementById("fileUpload");
                    file_name = files.files[0].name;
                    file_name = file_name.replace('.csv', '');
                    //file = files.files[0];
                    var formdata = new FormData();
                    formdata.append('file', files.files[0], file_name);
                    console.log(formdata); 
                    //AJAX call to get names of those CAT attributes to mark checked
                    $.ajax({
                        url: '/checknecessarycheckbox/',
                        type: 'POST',
                        data: formdata,
                        processData: false,
                        contentType: false,
                        //contentType: 'application/json'
                        //async: false,
                    }).done(function(data){    
                        attribute_names_to_be_marked_checked = data['attribute_names'];
                    }).fail(function(xhr){
                        var msg = $.parseJSON(xhr.responseText)
                        $("#error_msg").text(msg.message);
                        $("#error_dialog").css("display", "block");
                    });
                    */

                    //show next screen of atribute removal
                    
                    if (timeseriesnumberofattributes > 0){  //at least 1 time series attribute is present. Need to show middle menu
                       var time_series_exclude_list = document.getElementById("timeseriesattributesStuff"); 

                       while(time_series_exclude_list.hasChildNodes()){
                           time_series_exclude_list.removeChild(time_series_exclude_list.firstChild);
                       }

                       for(var i = 0; i < categoricalAttributeList.length; i++) {
                           var label = document.createElement("label");
                           var input = document.createElement("input");

                           label.setAttribute("class", "checkbox-inline");
                           label.setAttribute("style", "font-size: medium");
                           label.textContent = categoricalAttributeList[i];

                           input.setAttribute("type", "checkbox");
                           input.value = header_row[i];
                           input.setAttribute("name", "Checkbox[]");

                           label.appendChild(input);
                           time_series_exclude_list.appendChild(label);
                       }

                       var timeseriesexcludemodal = document.getElementById("timeseriesModal");
                       var timeseriesokaybutton = document.getElementsByClassName("timeseriesitsokay")[0];
                       timeseriesexcludemodal.style.display = "block";
                       
                       timeseriesokaybutton.onclick = function () {
                           timeseriesexcludemodal.style.display = "none";
                           
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
                           var excludemodal = document.getElementById("requiredModal");
                           //var okay_span = document.getElementsByClassName("itsokay")[0];
                           excludemodal.style.display = "block";
                       }
                    }
                    else {  //no time series attribute present. Continue as usual..

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
                    
                        var excludemodal = document.getElementById("requiredModal");
                        var okay_span = document.getElementsByClassName("itsokay")[0];
                        excludemodal.style.display = "block";
                    }
                }
                //reader.readAsText($("#fileUpload")[0].files[0]);
                //reader.readAsBinaryString($("#fileUpload")[0].files[0]);
            }
            reader.readAsText($("#fileUpload")[0].files[0]);
        } else {
            alert("This browser does not support HTML5.");
        }
    }else{
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

                var div = document.createElement("div");
                div.setAttribute("class", "row");
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
                div.append(button);
                li.append(button);

                list_group.appendChild(li);
            }
        }
    }).fail(function(xhr) {
        var msg = $.parseJSON(xhr.responseText);
        $("#error_msg").text(msg.message);
        $("#error_dialog").css("display","block");
    });
}

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
                file_data['page'] = "Page1";

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
                    console.log(message['url']);
                    window.location.href = "/ba/loadHomePage/";
                }).fail(function(xhr) {
                    var msg = $.parseJSON(xhr.responseText);
                    $("#error_msg").text(msg.message);
                    $("#error_dialog").css("display", "block");
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
// This is the javascript query for the standalone select/search bar

$("#all_attributes").select2({
    placeholder: 'Select Attributes/Graphs',
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


//Calling runner once
// runner();

// // Function to ping continuously and inform the user that the disk is full
// var diskfull_count = -1;
//
// function ping() {
//     diskfull_count = 0;
//     // Call update table
//     update_table(random_table_list);
//     deleteready();
//
//     var modal = document.getElementById("diskfullModal");
//     modal.style.display = "block";
//
//     // Wait for 5 seconds and then stop the display
//     setTimeout(function(){modal.style.display = "none";}, 5000);
// }
// // Function to continuosly ping
// function runner(){
//     ping()
//     setTimeout( () => {
//         if (diskfull_count  != 0) {
//             runner();
//         }
//     }, 5000)
// }

// //Calling runner2 once
// runner2();
//
// // Function to ping continuously and inform the user that the disk is full
// var current_space_that_is_filled = "";
//
// function ping2() {
//
//     var some_data = {};
//     some_data['something'] = 'something_else';
//
//     $.ajax({
//         url:'/diskcheck/',
//         type: 'POST',
//         data: some_data,
//         dataType: "json",
//         async: false
//     }).done((data)=> {
//
//         var current_amount_full = parseInt(data['value']);
//         current_space_that_is_filled = current_amount_full;
//
//         if (current_amount_full >= 97) {
//             // Show the user the pop-up to re-run the code again
//             var modal = document.getElementById("diskfullModal");
//             modal.style.display = "block";
//
//             // Wait for 5 seconds and then stop the display
//             setTimeout(function(){modal.style.display = "none";}, 5000);
//         }
//     });
// }
// // Function to continuosly ping
// function runner2(){
//     ping2()
//     setTimeout( () => {
//         if (current_space_that_is_filled >= 97) {
//             runner2();
//         }
//     }, 1000)
// }
