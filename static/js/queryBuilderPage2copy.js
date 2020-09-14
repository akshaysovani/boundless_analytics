
var values_currently_selected = [];
var options_that_are_selected_by_user = [];

var attribute_unique_data_values = {};

var attribute_type = {};
// Just setting some random data
attribute_type['test'] = 'something';

// Global variables for Plot Zero Explore dialog.
var all_record_keeper = [];
var all_record_keeper_current_index = -1;
var charts_per_score_global = [];
var score_charts_global = [];
var score_charts_global_supervised = [];
var score_metadata_charts_global = [];
var score_metadata_charts_global_supervised = [];
var chart_index = 0;
var chart_index_supervised = 0;
var chart_type_global;
var columnsGlobal;
var plotLineScoreGlobal;
var hasPlotLine = false;
var scoreChart;
var numChartPerBin = 0;
var plotZeroGlobal;
var plotZeroMetadataGlobal;
var diff_score_global = [];
var chartsScaleGlobal;
var charts_slice_global = [];
var charts_slice_global_supervised = [];
var slice_size_global = [];
var slice_size_global_supervised = [];
const attributeSet = new Set();
const optionsAllowedSet = new Set();
const optionsAllowedSetToAddToSelectBox = new Set();
var chartType;
var chartTypeSupervised;
var supervisedModeOn = false;
var all_keys_in_slice_arr = [] //array which holds keys of current plot zero
var endReachedFlag = false;
var histogramPlotZeroData = []

// Global variables for Horizontal Explore dialog.
var compare_chart_index = 0;
var sliceMapGlobal;
var referenceChartGlobal;
var comparisonResultsGlobal;

$.ajax({
    url:'/page2/',
    type: 'POST',
    data: attribute_type,
}).done(function (data) {
    var get_data = {};
    //  Get the data in the jSON format
    for (var summ_attr in data) {
        var curr_attribute = data[summ_attr];
        curr_attribute = curr_attribute.replace(/'/g, '"');
        curr_attribute = JSON.parse(curr_attribute);
        get_data[summ_attr] = curr_attribute;
    }

    attribute_unique_data_values = get_data;

    // var attributes = document.getElementById("attributesSchema");
    var attributes = document.getElementById("all_attributes");

    while(attributes.hasChildNodes()) {
        attributes.removeChild(attributes.firstChild);
    }

    // Create the options group for each attribute
    var optgroup = document.createElement("optgroup");
    optgroup.label = "Attributes";
    optgroup.id = "Attributes";
    for (var attr in attribute_unique_data_values) {
        var option = document.createElement("option");
        option.setAttribute("class", "l1");
        var actual_text = attr + ":" + attr;
        option.setAttribute("value", actual_text);
        option.text = attr;
        optgroup.appendChild(option);

        for (var unique_value in attribute_unique_data_values[attr]) {
            var option = document.createElement("option");
            option.setAttribute("class", "l2");
            var actual_text = attr + ":" + attribute_unique_data_values[attr][unique_value];
            option.setAttribute("value", actual_text);
            option.text = actual_text;
            optgroup.appendChild(option);
        }
    }
    attributes.appendChild(optgroup);

    // Create the optgroup for graphs
    var optgroup = document.createElement("optgroup");
    optgroup.label = "GraphType";
    optgroup.id = "Graph"
    var graph_types = ['bargraph', 'groupedBargraph', 'heatmap', 'histogram', 'scatter', 'boxplot'];
    for (var i = 0; i< graph_types.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", graph_types[i]);
        option.text = graph_types[i];
        optgroup.appendChild(option);
    }
    attributes.appendChild(optgroup);

    // Create the optgroup for order by function
    var optgroup = document.createElement("optgroup");
    optgroup.label = "OrderBy(Default - Descending)";
    optgroup.id = "Ordering"
    var ordering = ['Score', 'Support'];
    for (var i = 0; i< ordering.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", ordering[i]);
        option.text = ordering[i];
        optgroup.appendChild(option);
    }
    attributes.appendChild(optgroup);
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

//------------------------------------------------------------------------------
// This is the javascript query for the standalone select/search bar

$("#all_attributes").select2({
    placeholder: 'Select Attributes/Graphs',
    allowClear: false,
    // maximumSelectionLength: 5,
    // maximumSelectionLength: (Object.keys(attribute_unique_data_values).length + 5),
    templateResult: function (data) {
        // We only really care if there is an element to pull classes from
        if (!data.element) {
            return data.text;
        }

        var $element = $(data.element);

        var $wrapper = $('<span></span>');
        $wrapper.addClass($element[0].className);

        $wrapper.text(data.text);
        console.log($wrapper);    
        return $wrapper;
    }
});

$(function () {
    $("#searchButton").on("click", function () {
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


// Always listening
// # If some of the tags are removed or added in the section - Top questions based on tags
// $( "#all_attributes" ).change(function() {
$( "#all_attributes" ).on('select2:select', function(e) {

    // Get the selected id and text, where id is the option value and text is the option text
    var selected_id = e.params.data.id;
    //console.log(e);
    //console.log(e.params);
    //console.log(e.params.data);
    var selected_text = e.params.data.text;
    console.log(selected_text);

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
            console.log(values_currently_selected);
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
        }

        else
        {
            // Add to search bar
            var main = document.getElementsByClassName("main");
            main.q.value += " " + selected_text;
            console.log(main.q.value);

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
            console.log(attributes_to_destroy);
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
            console.log(options_that_are_selected_by_user);    
            $('#all_attributes').val(options_that_are_selected_by_user);
            // $('#all_attributes').trigger ('change'); // Notify any JS components that the value changed
            // $('#all_attributes').select2('close');


            // Refresh button
            $("#all_attributes").select2({
                placeholder: 'Select Attributes/Graphs',
                allowClear: false,
                maximumSelectionLength: (Object.keys(attribute_unique_data_values).length + 5),
                templateResult: function (data) {

                    // We only really care if there is an element to pull classes from
                    if (!data.element) {
                        return data.text;
                    }

                    var $element = $(data.element);

                    var $wrapper = $('<span></span>');
                    $wrapper.addClass($element[0].className);

                    $wrapper.text(data.text);
                    console.log($wrapper);
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
    }

    else {

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
    console.log(selected_id);
    console.log(selected_text);

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

            if (attributes.children[i].value === selected_id) {
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
        for (var unique_value in attribute_unique_data_values[actual_id]) {
            var option = document.createElement("option");
            option.setAttribute("class", "l2");
            var actual_text = actual_id + ":" + attribute_unique_data_values[actual_id][unique_value];
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
            maximumSelectionLength: (Object.keys(attribute_unique_data_values).length + 5),
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

    else {

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

//$("#all_attributes_supervised").on('select2:select', function(e) {
//    console.log("g");
//});
//

function displayCharts(chartLabel, maxChart, col_names) {
    //console.log("Chart data - " + maxChart);
    var div1 = document.createElement("div");
    div1.className = 'column_max_min';
    var innerDiv1 = document.createElement("div");
    innerDiv1.className = 'col-xs-2';
    if (maxChart[5] !== undefined || maxChart[5] !== '') {
        var url = maxChart[5].replace("foreveranalytics.com", "foreveranalytics.com:8080");
        var urlTag = document.createElement("a");
        urlTag.target = "_blank";
        urlTag.href = url;
        var imageTag = document.createElement("img");
        imageTag.className = "chart-icon-graph";
        imageTag.alt = "";
        switch(maxChart[4]) {
            case "bargraph":
                imageTag.src = "/bargraph-icon.png";
                break;
            case "grouped-bargraph":
                imageTag.src = "/bargraph-icon.png";
                break;
            case "heatmap":
                imageTag.src = "/heatmap-icon.png";
                break;
            case "histogram":
                imageTag.src = "/hist-icon.png";
                break;
            case "scatter":
                imageTag.src = "/scatter-icon.png";
                break;
            case "boxplot":
                imageTag.src = "/boxplot-icon.png";
                break;
            default:
                console.log("Invalid plot type - " + maxChart[4]);
        }
        urlTag.appendChild(imageTag);
        innerDiv1.appendChild(urlTag);
    } else {
        // TO DO: handle this case later.
    }
    // Column div for plot related information.
    var innerDiv2 = document.createElement("div");
    innerDiv2.className = "col-xs-10";
    var table1 = document.createElement("table");
    var table2 = document.createElement("table");
    var tr1 = document.createElement("tr");
    var text1 = document.createTextNode("Plottype: " + maxChart[4]);
    tr1.appendChild(text1);
    var tr2 = document.createElement("tr");
    var text2 = document.createTextNode("Score: " + maxChart[2]);
    tr2.appendChild(text2);
    var tr3 = document.createElement("tr");
    var text3 = document.createTextNode("Support: " + maxChart[3]);
    tr3.appendChild(text3);
    var tr4 = document.createElement("tr");
    if (maxChart[1] !== 'NA') {
        var displayString = maxChart[0] + "(X-axis) vs " + maxChart[1] + "(Y-axis)";
        var text4 = document.createTextNode("Plot Attributes: " + displayString);
    } else {
        var text4 = document.createTextNode("Plot Attribute: " + maxChart[0]);
    }
    var tr5 = document.createElement("tr");
    // show slice information.
    value_arr = [];
    for (var i = 6; i < col_names.length; i++) {
        if (maxChart[i] !== 'NA') {
            // add this slice.
            value_arr.push("(" + col_names[i] + " = " + maxChart[i] + ")");
        }
    }
    var textValue = value_arr.join(" | ");
    var text5 = document.createTextNode("Slices: " + textValue);
    tr4.appendChild(text4);
    tr5.appendChild(text5);
    tr5.style.wordBreak = "break-all";
    table2.appendChild(tr1);
    table2.appendChild(tr2);
    table2.appendChild(tr3);
    table2.appendChild(tr4);
    table2.appendChild(tr5);
    table1.appendChild(table2);
    innerDiv2.appendChild(table1);
    innerDiv1.appendChild(innerDiv2);
    var chartLabelElement = document.createElement("p");
    var chartLabelText = document.createTextNode("Chart with " + chartLabel + " score ");
    chartLabelElement.appendChild(chartLabelText);
    chartLabelElement.style.fontWeight = "bold";
    chartLabelElement.style.textDecoration = "underline";
    div1.appendChild(chartLabelElement);
    div1.appendChild(innerDiv1);
    div1.style.marginTop = "20px";
    if ("MAXIMUM" === chartLabel) {
        div1.style.marginRight = "50px";
    } else {
        div1.style.marginLeft = "50px";
    }
    var mainContainer = document.getElementById("mainDiv");
    mainContainer.appendChild(div1);
}

function addButtonToContainer() {
    var div = document.createElement("div");
    div.className = "row";
    div.id = "buttonDiv";
    var button = document.createElement("input");
    button.type = "button";
    button.id = "chart_min_max_button";
    button.value = "Close";
    button.name = "chart_min_max_button";
    button.style.marginLeft = "30px";
    div.appendChild(button);
    $("#dialog_container").append(div);
}


function getSliceForChart(metadata) {
    //console.log(metadata)
    //console.log(columnsGlobal)    
    sliceArr = [];
    for (var i = 6; i < columnsGlobal.length; i++) {
        if (metadata[i] !== 'NA') {
            sliceArr.push("(" + columnsGlobal[i] + " = " + metadata[i] + ")");
        }
    }
    return sliceArr.join(" & ");
}

function addBarChart(data, metadata, showPlotZeroReference, slice_size_for_this_slice){
    console.log(data);
    categoriesList = [];
    valuesList = [];
    dataLabelsValue = {};
    for (var i = 0; i < data.length; i++) {
        categoriesList.push(data[i][0]);
        valuesList.push(data[i][1]);
        dataLabelsValue[data[i][0]] = data[i][1];
    }
    var slice_size_div = document.getElementById('NumberOfRecordsForThisSlice');
    slice_size_div.innerHTML = 'Slice size : ' + slice_size_for_this_slice;

    plotZeroValues = []
    for (val of plotZeroGlobal) {
        plotZeroValues.push(val[1]);
        if (val[0] in dataLabelsValue) {    
            currentVal = dataLabelsValue[val[0]];
            difference = ((currentVal - val[1]) / val[1]) * 100;
            dataLabelsValue[val[0]] = difference.toFixed(2);
        }
    }
    //var titleText = "Bargraph for attribute : " + metadata[0];
    var numberOfSlicesTotalDiv = document.getElementById('NumberOfSlices');
    numberOfSlicesTotalDiv.innerHTML = 'Bargraph for attribute : ' + metadata[0];
    var slices = getSliceForChart(metadata);
    var actual_slice_div = document.getElementById('actualSlice');
    if (slices.length != 0){
            actual_slice_div.innerHTML = 'Slice : ' + slices
    }else{
            actual_slice_div.innerHTML = '';
    }
    //console.log(slices)
    if (slices.length > 0) {
        //titleText += "<br/>Slice: " + slices;
    }
    plotLineScoreGlobal = metadata[2];
    Highcharts.chart('chartForScoreDiv', {
        title: {text: 'Chart for comparison'},
        chart: {
            type: 'column', 
            height: 360,
            events: {
                load: function() {
                    var c = this;
                    var textContent = "Score = " + metadata[2] + "<br/>Support = " + metadata[3];
                    c.renderer.text(textContent, 50, 435).css({
                        fontWeight: 'bold'
                    })
                    .add();
                    var points = this.series[0].points;
                    points.forEach(function(point) {
                        var clr = dataLabelsValue[point.category] >= 0 ? 'green' : 'red';
                        point.dataLabel.text.css({
                            'color': clr
                        });
                    });
                }
            }
        },
        xAxis: {categories: categoriesList},
        yAxis: {title: {text: 'Frequency'}, min: 0, max: chartsScaleGlobal['max']},
        plotOptions: {
            series: {
                events : {
                    legendItemClick: function() {
                        return false;
                    }
                },
                maxPointWidth: 70,
                dataLabels: {
                    style: {
                        fontSize: '12px'
                    },
                    enabled: true,
                    formatter : function() {
                        var value = dataLabelsValue[this.point.category];
                        return value >= 0 ? '+' + value + '%' : value + '%';
                    }
                }
            }
        },
        tooltip: {
            formatter: function() {
                return this.y.toFixed(2) + '%';
            }
        },
        series: [{
            data: valuesList,
            name: metadata[0],
            animation: false
        }],
        exporting: {
            buttons: {
                markFavorite: {
                    x: -10,
                    y: 410,
                    text: 'Mark Favorite',
                    onclick: function() {
                        markAsFavorite(metadata);
                    },
                    symbol: 'circle'
                }
            }
        }
    });
}

function addHeatMap(data, metadata) {
    var xCategoriesList = {};
    var yCategoriesList = {};
    var values = {};
    var xIndex = 0;
    var yIndex = 0;
    for (var i = 0; i < data.length; i++) {
        if (!(data[i][0] in xCategoriesList)) {
            xCategoriesList[data[i][0]] = xIndex++;
        }
        if (!(data[i][1] in yCategoriesList)) {
            yCategoriesList[data[i][1]] = yIndex++;
        }
        if (!(data[i] in values)) {
            values[data[i]] = 1;
        } else {
            var count = values[data[i]];
            values[data[i]] = count + 1;
        }
    }
    var dataValues = [];
    for (var key in values) {
        var innerList = [];
        var arr = key.split(",")
        innerList.push(xCategoriesList[arr[0]]);
        innerList.push(yCategoriesList[arr[1]]);
        innerList.push(values[key]);
        dataValues.push(innerList);
    }
    var titleText = "Heatmap for attributes : " + metadata[0] + " vs " + metadata[1];
    var slices = getSliceForChart(metadata);
    if (slices.length > 0) {
        titleText += "<br/>Slice : " + slices;
    }
    plotLineScoreGlobal = metadata[2];
    Highcharts.chart('chartForScoreDiv', {
        title: {text: titleText},
        chart: {
            type: 'heatmap',
            events: {
                load: function() {
                    var c = this;
                    var textContent = "Score = " + metadata[2] + "<br/>Support = " + metadata[3];
                    c.renderer.text(textContent, 50, 435).css({
                        fontWeight: 'bold'
                    })
                    .add();
                }
            }
        },
        xAxis: {
            title: {text: metadata[0]},
            categories: Object.keys(xCategoriesList) 
        },
        yAxis: {
            title: {text: metadata[1]},
            categories: Object.keys(yCategoriesList)
        },
        colorAxis: {
            min: 0
        },
        series: [{
            showInLegend: false,
            data: dataValues
        }],
        exporting: {
            buttons: {
                markFavorite: {
                    x: -90,
                    y: 410,
                    text: 'Mark Favorite',
                    onclick: function() {
                        markAsFavorite(metadata);
                    },
                    symbol: 'circle'
                }
            }
        }
    });
}

function addScatterPlot(divId, data, metadata, enableButtons) {
   dataValues = [];
   for (var i = 0; i < data.length; i++) {
       dataValues.push(data[i]);
   }
   var titleText = "Scatter Plot for attributes : " + metadata[0] + " vs " + metadata[1];
   var slices = getSliceForChart(metadata);
   if (slices.length > 0) {
       titleText += "<br/>Slice : " + slices;
   }
   plotLineScoreGlobal = metadata[2];
   var chart = Highcharts.chart(divId, {
       title: {text: titleText},
       chart: {
           type: 'scatter',
           events: {
               load: function() {
                   var c = this;
                   var textContent = "Score = " + metadata[2] + "<br/>Support = " + metadata[3];
                   c.renderer.text(textContent, 50, 435).css({
                       fontWeight: 'bold'
                   })
                   .add();
               }
           },

       },
       xAxis: {
           title: {text: metadata[0]}
       },
       yAxis: {
           title: {text: metadata[1]}
       },
       series : [{
           name: 'series1',
           data: dataValues,
           color: '#3354FF',
           showInLegend: false
       }],
       exporting: {
        buttons: {
            markFavorite: {
                x: -90,
                y: 410,
                text: 'Mark Favorite',
                onclick: function() {
                    markAsFavorite(metadata);
                },
                symbol: 'circle'
            }
        }
       }
   });
}

function addButtonsToCompareCharts() {
    var previousButton = document.createElement("input");
    previousButton.id = "comparePrevious";
    previousButton.type = "button";
    previousButton.value = " < ";
    previousButton.style.marginRight = "10px";
    previousButton.title = "Previous";
    var nextButton = document.createElement("input");
    nextButton.id = "compareNext";
    nextButton.type = "button";
    nextButton.value = " > ";
    nextButton.style.marginLeft = "10px";
    nextButton.title = "Next";
    var div = document.createElement("div");
    div.className = 'col-xs-2';
    div.appendChild(previousButton);
    div.appendChild(nextButton);

    var closeButtonDiv = document.createElement("div");
    closeButtonDiv.id = "closeButtonDiv";
    closeButtonDiv.style.marginTop = "10px";
    closeButtonDiv.className = "row";
    var closeButton = document.createElement("input");
    closeButton.type = "button";
    closeButton.id = "closeButton";
    closeButton.value = "Close";
    closeButtonDiv.appendChild(closeButton);
    $("#compare_charts_container").append(div);
    $("#compare_charts_container").append(closeButtonDiv);
    if (comparisonResultsGlobal.length == 1) {
        previousButton.disabled = true;
        nextButton.disabled = true;
    }
}

function addChartsForComparison(createDiv) {
    if (createDiv) {    
        var compareChartsDiv = document.createElement("div");
        compareChartsDiv.id = "compare_charts";
        compareChartsDiv.style.marginTop = "20px";
        compareChartsDiv.style.height = "350px";
        $("#compare_charts_container").append(compareChartsDiv);
        addButtonsToCompareCharts();
    }
    if (compare_chart_index == 0 && comparisonResultsGlobal.length > 1) {
        $("#comparePrevious").prop("disabled",  true);
        $("#compareNext").prop("disabled",  false);
    } else if (compare_chart_index != 0 && compare_chart_index == comparisonResultsGlobal.length - 1) {
        $("#comparePrevious").prop("disabled",  false);
        $("#compareNext").prop("disabled",  true);
    } else if (compare_chart_index > 0 && compare_chart_index < comparisonResultsGlobal.length - 1){
        $("#comparePrevious").prop("disabled",  false);
        $("#compareNext").prop("disabled",  false);
    }
    var chartData = comparisonResultsGlobal[compare_chart_index];
    addScatterPlot("compare_charts", chartData['chart_data'], chartData['metadata'], false);
}

$("#attribute_names_list").change(function() {
    var selectedAttribute = $("#attribute_names_list").val();
    dataMap = {}
    dataMap['slice'] = sliceMapGlobal;
    dataMap['variable'] = selectedAttribute;
    dataMap['reference'] = referenceChartGlobal;

    $.ajax({
        url: '/ba/search/slices/compare/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(dataMap)
    }).done(function(data) {
        $("#compare_charts_container").empty();
        comparisonResultsGlobal = data['results']; 
        compare_chart_index = 0;
        addChartsForComparison(true);
    }).fail(function(xhr) {
        try {
            var msg = $.parseJSON(xhr.responseText);
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Failed to explore the plot horizontally. Please check system logs for more details. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
});

$("#compare_charts_container").on("click", "#closeButton", function(){
    $("#horizontal_explore_dialog").css("display", "none");
});

$("#compare_charts_container").on("click", "#compareNext", function(){
    compare_chart_index++;
    addChartsForComparison(false);
});

$("#compare_charts_container").on("click", "#comparePrevious", function(){
    compare_chart_index--;
    addChartsForComparison(false);
});


function addHistogram(data, metadata, not_used, slice_size_for_this_slice) {
    console.log(slice_size_for_this_slice);
    //var titleText = "Histogram for attribute : " + metadata[0];
    var slices = getSliceForChart(metadata);
    var actual_slice_div = document.getElementById('actualSlice');
    if (slices.length != 0){
            actual_slice_div.innerHTML = 'Slice : ' + slices
    }else{
            actual_slice_div.innerHTML = '';
    }
    //console.log(slices)
    //if (slices.length > 0) {
    //    titleText += "<br/>Slice : " + slices;
    //}

    var numberOfSlicesTotalDiv = document.getElementById('NumberOfSlices');
    numberOfSlicesTotalDiv.innerHTML = 'Histogram for attribute : ' + metadata[0];

    var slice_size_div = document.getElementById('NumberOfRecordsForThisSlice');
    slice_size_div.innerHTML = 'Slice size : ' + slice_size_for_this_slice;

    dataLabelsList = [];
    var offset = 0;
    if (data.length > 1) {
        offset = data[1][0] - data[0][0];
    }

    var databkp = JSON.parse(JSON.stringify(data));
    dataLabelsValue = {};

    for (var i = 0; i < data.length; i++) {
        dataLabelsValue[data[i][0]] = data[i][1];
    }

    for (val of histogramPlotZeroData) {
        if (val[0] in dataLabelsValue) {
            currentVal = dataLabelsValue[val[0]];
            difference = ((currentVal - val[1]) / val[1]) * 100;
            dataLabelsValue[val[0]] = difference.toFixed(2);
        }
    }
    console.log(dataLabelsValue);
    
    
    /* 
    leftSideOnes = [];
    rightSideOnes = [];


    console.log(data);

    for (val of data){
        rightSideOnes.push(val[1]);
    }

    for (val of histogramPlotZeroData){
        leftSideOnes.push(val[1]);
    }
    
    console.log(leftSideOnes);
    console.log(rightSideOnes);
    var result = [];
    for (var i=0; i<leftSideOnes.length; i++){
        if (leftSideOnes[i] === 0 || rightSideOnes[i] === 0){
            result.push(0)
            continue;
        }
        if (leftSideOnes[i] > rightSideOnes[i]){
            var res = leftSideOnes[i] / rightSideOnes[i];
            if (res >= 3){
                result.push(1);
            }else{
                result.push(0);
            }
        }else{
            var res = rightSideOnes[i] / leftSideOnes[i];
            if (res >= 3){
                result.push(1);
            }else{
                result.push(0);
            }
        }
    }
    console.log(result);
    var positionOfOnesInResult = [];
    for (var i=0; i<result.length; i++){
        if (result[i] === 1){
            positionOfOnesInResult.push(i);
        }
    } 
    console.log(positionOfOnesInResult);
    var datadup = JSON.parse(JSON.stringify(data));

    dataObject = datadup.map(function(x){
        return {
            "x": x[0],
            "y": x[1],
            //"color": 'Green'
        }
    })
    
    var counter=0;
    dataObject.forEach(function(element){
        if (positionOfOnesInResult.includes(counter)){
            element.color = 'Red';
        }
        counter++;
    });
    
    console.log(dataObject);
    */


    plotLineScoreGlobal = metadata[2];
    Highcharts.chart('chartForScoreDiv', {
        title : {text: 'Chart for comparison'},
        xAxis: {title: {text: metadata[0]}, max: chartsScaleGlobal['max_x']},
        yAxis: {title: {text: 'Frequency'}, max: chartsScaleGlobal['max']},
        chart: {
            height: 360,
            events: {
                load: function() {
                    var c = this;
                    var textContent = "Score = " + metadata[2] + "<br/>Support = " + metadata[3];
                    c.renderer.text(textContent, 50, 435).css({
                        fontWeight: 'bold'
                    })
                    .add();
                    var points = this.series[0].points;
                    points.forEach(function(point) {
                        var clr = dataLabelsValue[point.category] >= 0 ? 'green' : 'red';
                        point.dataLabel.text.css({
                            'color': clr
                        });
                    });
                }
            }
        },
        series: [{
            name: 'Data',
            showInLegend: false,
            pointPlacement: 'between',
            type: 'column',
            data: data,
            animation: false
        }],
        plotOptions: {
            column: {
                pointPadding: 0,
                borderWidth: 1,
                groupPadding: 0
            },
            series: {
                dataLabels: {
                    style: {
                        fontSize: '10px'
                    },
                    enabled: true,
                    formatter : function() {
                        var value = dataLabelsValue[this.point.category];
                        if (value >= 200) {
                            return '+' + value + '%';
                        }
                        else if (value <= -200){
                            return value + '%';
                        }else{
                            return '';
                        }
                        //return value >= 200 ? '+' + value + '%' : value + '%';
                    }
                }
            }
        },
        tooltip: {
            stickOnContact: true,
            formatter: function() {
                var p_x = Math.round(this.point.x);
                var p_x_plus_offset = Math.round(this.point.x + offset);
                var flag_x = '';
                var flag_x_plus_offset = '';

                if (Math.abs(p_x) > 999999){
                    var x_new = Math.sign(p_x)*((Math.abs(p_x)/1000000).toFixed(1));
                    flag_x = 'M';
                }else if(Math.abs(p_x) > 999){
                    var x_new = Math.sign(p_x)*((Math.abs(p_x)/1000).toFixed(1));
                    flag_x = 'K';
                }else{
                    var x_new = p_x;
                    flag_x = '';
                }

                if (Math.abs(p_x_plus_offset) > 999999){
                    p_x_plus_offset = Math.sign(p_x_plus_offset)*((Math.abs(p_x_plus_offset)/1000000).toFixed(1));
                    flag_x_plus_offset = 'M';
                }else if (Math.abs(p_x_plus_offset) > 999){
                    p_x_plus_offset = Math.sign(p_x_plus_offset)*((Math.abs(p_x_plus_offset)/1000).toFixed(1));
                    flag_x_plus_offset = 'K';
                }else{
                    flag_x_plus_offset = '';
                }
                return x_new + flag_x + "-" + p_x_plus_offset + flag_x_plus_offset +  " : <b>" + this.point.y + "</b>";
            }
        },
        exporting: {
            buttons: {
                markFavorite: {
                    x: -90,
                    y: 410,
                    text: 'Mark Favorite',
                    onclick: function() {
                        markAsFavorite(metadata);
                    },
                    symbol: 'circle'
                }
            }
        }
    });
    /*Highcharts.chart('chartForScoreDiv', {
        series: [{
            type: 'histogram',
            xAxis: 0,
            zAxis: -1,
            baseSeries: 'series1',
            showInLegend: false,
            color: '#3354FF',
            animation: false,
            binsNumber: 16
        },
        {
            type: 'scatter',
            name: 'Data',
            data: data,
            id: 'series1',
            visible: false,
            showInLegend: false
        }],
    });*/
}

function addBoxPlot(data, metadata, slice, slice_size_for_this_slice){
    //var titleText = "Box plot for attribute: " + metadata[0];
    sliceArr = []
    //console.log(slice)    
    Object.keys(slice).forEach(function(key){
        sliceArr.push("(" + key + " = " + slice[key] + ")");
    })    
    var slices = sliceArr.join(" & ");
    var actual_slice_div = document.getElementById('actualSlice');
    if (slices.length != 0){
            actual_slice_div.innerHTML = 'Slice : ' + slices
    }else{
            actual_slice_div.innerHTML = '';
    }
    //if (slices.length > 0){
    //    titleText += "<br/>Slice : "+slices; 
    //}
    var slice_size_div = document.getElementById('NumberOfRecordsForThisSlice');    
    slice_size_div.innerHTML = 'Slice size : ' + slice_size_for_this_slice;

    var numberOfSlicesTotalDiv = document.getElementById('NumberOfSlices');
    numberOfSlicesTotalDiv.innerHTML = 'Boxplot for attribute : ' + metadata[0];

    dataValues = [];
    //data.forEach(function(val){
    // dataValues.push(val); 
    //})
    dataValues.push(data);
    plotLineScoreGlobal = metadata[2];
    Highcharts.chart('chartForScoreDiv',{
        title: {text: 'Chart for comparison'},
        chart: {type: 'boxplot', height: 360},
        //xAxis: {title: {text: 'Box Plots'}},
        yAxis: {title: {text: metadata[0]}, min: chartsScaleGlobal['min'], max: chartsScaleGlobal['max']},
        plotOptions: {
            boxplot: {
                fillColor: '#FFCCCC',
                lineWidth: 3,
                medianColor: '#0C5DA5',
                medianWidth: 3,
                stemDashStyle: 'dot',
                stemWidth: 2
            }
        },
        tooltip: {
            stickOnContact: true,
            formatter: function(){
                var t_high = typeof this.point.high;
                if (t_high === "number"){
                    var p_high = Math.round(this.point.high);
                    var p_q_three = Math.round(this.point.q3);
                    var p_median = Math.round(this.point.median);
                    var p_q_one = Math.round(this.point.q1);
                    var p_low = Math.round(this.point.low);

                    if (Math.abs(p_high) > 999999){
                        this.point.high = Math.sign(p_high)*((Math.abs(p_high)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_high) > 999){
                        this.point.high = Math.sign(p_high)*((Math.abs(p_high)/1000).toFixed(1))+'K';
                    }else{
                        this.point.high = p_high;
                    }

                    if (Math.abs(p_q_three) > 999999){
                        this.point.q3 = Math.sign(p_q_three)*((Math.abs(p_q_three)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_q_three) > 999){
                        this.point.q3 = Math.sign(p_q_three)*((Math.abs(p_q_three)/1000).toFixed(1))+'K';
                    }else{
                        this.point.q3 = p_q_three;
                    }    

                    if (Math.abs(p_median) > 999999){
                        this.point.median = Math.sign(p_median)*((Math.abs(p_median)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_median) > 999){
                        this.point.median = Math.sign(p_median)*((Math.abs(p_median)/1000).toFixed(1))+'K';
                    }else{
                        this.point.median = p_median;
                    }

                    if (Math.abs(p_q_one) > 999999){
                        this.point.q1 = Math.sign(p_q_one)*((Math.abs(p_q_one)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_q_one) > 999){
                        this.point.q1 = Math.sign(p_q_one)*((Math.abs(p_q_one)/1000).toFixed(1))+'K';
                    }else{
                        this.point.q1 = p_q_one;
                    }
                    
                    if (Math.abs(p_low) > 999999){
                        this.point.low = Math.sign(p_low)*((Math.abs(p_low)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_low) > 999){
                        this.point.low = Math.sign(p_low)*((Math.abs(p_low)/1000).toFixed(1))+'K';
                    }else{
                        this.point.low = p_low;
                    }
                }
                return this.series.name + "</b><br/>Maximum: " + this.point.high + "<br/>Upper quartile: " + this.point.q3 + "<br/>Median: " + this.point.median + "<br/>Lower               quartile: " + this.point.q1 + "<br/>Minimum: " + this.point.low + "<br/>";
            }
        },
        series: [{
            name: 'Box Plot',
            data: dataValues,
            //showInLegend: false,
            animation: false
        }],
        exporting: {
            buttons: {
                markFavorite: {
                    x: -90,
                    y: 425,
                    text: 'Mark Favorite',
                    onclick: function() {
                        markAsFavorite(metadata)
                    },
                    symbol: 'circle'
                }
            }
        }
    });
}

function addTimeSeriesPlot(data, metadata, slice, slice_size_for_this_slice){
    console.log(data);
    sliceArr = [];
    var newbiglist = []
    Object.keys(slice).forEach(function(key) {
        sliceArr.push("(" + key + " = " + slice[key] + ")");
    })
    var slices = sliceArr.join(" & ");
    var actual_slice_div = document.getElementById('actualSlice');
    if (slices.length != 0){
        actual_slice_div.innerHTML = 'Slice : ' + slices;
    }else{
        actual_slice_div.innerHTML = '';
    }
    var slice_size_div = document.getElementById('NumberOfRecordsForThisSlice');
    slice_size_div.innerHTML = 'Slice size : ' + slice_size_for_this_slice;

    var numberOfSlicesTotalDiv = document.getElementById('NumberOfSlices');
    numberOfSlicesTotalDiv.innerHTML = 'Time series plot:  X-Axis: ' + metadata[0] + ' , Y-Axis: ' + metadata[1] ;
    var datacopy = JSON.parse(JSON.stringify(data));
    console.log(datacopy);
    var localmaxy = -100000;
    var localminy = 100000;
    datacopy.forEach(function(point) {
        point[0] = Date.parse(point[0]);
        if (point[1] > localmaxy){
            localmaxy = point[1];
        }
        if (point[1] < localminy){
            localminy = point[1];
        }
    });
    console.log(localmaxy);
    //localmaxy += 200;
    var counter=0;
    for (var i=0; i<datacopy.length; i++){
        if (counter<6){
            counter+=1;
            continue;
        }
        var newlist = JSON.parse(JSON.stringify(datacopy[i]));
        newbiglist.push(newlist);
    }

    //console.log(metadata);
    //console.log(metadata);
    Highcharts.stockChart('chartForScoreDiv', {
        rangeSelector: {
            selected: 5
        },
        title: {text: 'Chart for comparison'},
        chart: {
         // zoomType: 'x',
            height: 360
        },
        /*subtitle: {
            text: document.ontouchstart === undefined ? 'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in' 
        },*/
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: metadata[1]
            },
            //min: chartsScaleGlobal['min'],
            min: localminy,
            //max: chartsScaleGlobal['max']
            max: localmaxy
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            /*area: {
                fillColor: {
                    
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 2,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                //threshold: null
            }*/
            series: {
                showInNavigator: true
            }
        },

        tooltip: {
            pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y} </b><br/>',
            valueDecimals: 2
        },

        series: [{
            //type: 'area',
            data: newbiglist
        }]
    });
}

function addPercentilePlot(data, metadata, slice, slice_size_for_this_slice) {
    //var titleText = "Percentile plot for attribute : " + metadata[0];
    sliceArr = [];
    //console.log(slice)
    Object.keys(slice).forEach(function(key) {
        sliceArr.push("(" + key + " = " + slice[key] + ")");
    })
    var slices = sliceArr.join(" & ");
    var actual_slice_div = document.getElementById('actualSlice');
    if (slices.length != 0){
        actual_slice_div.innerHTML = 'Slice : ' + slices
    }else{
        actual_slice_div.innerHTML = ''; 
    }

    //if (slices.length > 0) {
    //    titleText += "<br/>Slice : " + slices;
    //}
    var slice_size_div = document.getElementById('NumberOfRecordsForThisSlice');
    slice_size_div.innerHTML = 'Slice size : ' + slice_size_for_this_slice;

    var numberOfSlicesTotalDiv = document.getElementById('NumberOfSlices');
    numberOfSlicesTotalDiv.innerHTML = 'Percentile plot for attribute : ' + metadata[0];

    //console.log(titleText);
    categoriesList = [95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]
    dataValues = [];
    data.forEach(function(val) {
        dataValues.push(val);
    });
    //plotLineScoreGlobal = metadata[2];
    Highcharts.chart('chartForScoreDiv', {
        title: {text: 'Chart for comparison'},
        chart: {
            type: 'line',
            height: 360,
            /*events: {
                load: function(){ 
                    var c = this;
                    var textContent = "Score = " + metadata[2] + "<br/>Support = " + metadata[3];
                    c.renderer.text(textContent, 50, 435).css({
                        fontWeight: 'bold'
                    })
                    .add();
                }
            }*/
        },
        xAxis: {
            categories: categoriesList,
            labels: {
                format: '{value}%'
            },
            title : {text: 'Percentiles'}
        },
        yAxis: {
            title: {
                text: metadata[0]
            },
            //min: chartsScaleGlobal['min'],
            //max: chartsScaleGlobal['max']
        },
        /*,
        plotOptions: {
            boxplot: {
                fillColor: 'lightgray',
                lineWidth: 3,
                medianColor: 'darkblue',
                medianWidth: 3,
                stemDashStyle: 'dot',
                stemWidth: 2
            }
        },*/
        series: [{
            name: 'Line Plot',
            data: dataValues,
            showInLegend: false,
            animation: false
        }],
        exporting: {
            buttons: {
                markFavorite: {
                    x: -90,
                    y: 425,
                    text: 'Mark Favorite',
                    onclick: function() {
                        markAsFavorite(metadata);
                    },
                    symbol: 'circle'
                }
            }
        }
    });
}

var metadataPersist;
function markAsFavorite(metadata) {
    $("#comments_dialog").css("display", "block");
    metadataPersist = metadata;
}

$("#commentsDialogButtonDiv").on("click", "#okButton", function() {
    var comments = $("#commentsText").val();
    $("#comments_dialog").css("display", "none");
    persistFavoriteFlagWithComments(comments);
});

$("#commentsDialogButtonDiv").on("click", "#cancelButton", function() {
    $("#comments_dialog").css("display", "none");
});

function persistFavoriteFlagWithComments(comments) {
    requestData = {};
    requestData['cols'] = columnsGlobal;
    requestData['metadata'] = metadataPersist;
    requestData['comments'] = comments;
    $.ajax({
        url: '/ba/search/markfavorite/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData)
    }).done(function(data){
        $("#success_msg").text("SUCCESS!! Chart marked as favorite.");
        $("#success_dialog").css("display", "block");
    }).fail(function(xhr){
        try {
            var msg = $.parseJSON(xhr.responseText);
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("ERROR!! Failed to explore plot. Please check system logs for more details. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
}

function addChartOnHistogramClick(scoreChart, chartType) {
    $("#chartForScoreDiv").empty();
    data = score_charts_global[chart_index];
    metadata = score_metadata_charts_global[chart_index];
    //console.log("score - " + diff_score_global[chart_index]);
    slice_size_for_this_slice = slice_size_global[chart_index]
    switch(chartType) {
        case "bargraph":
            addBarChart(data, metadata, true, slice_size_for_this_slice);
            break;
        case "grouped-bargraph":
            addBarChart(data, metadata, true);
            break;
        case "heatmap":
            addHeatMap(data, metadata);
            break;
        case "histogram":
            console.log("before: ",slice_size_for_this_slice)
            addHistogram(data, metadata, true, slice_size_for_this_slice);
            break;
        case "scatter":
            addScatterPlot('chartForScoreDiv', data, metadata, true);
            break;
        case "percentile":
            slice = charts_slice_global[chart_index];
            addPercentilePlot(data, metadata, slice, slice_size_for_this_slice);
            break;
        case "boxplot":
            slice = charts_slice_global[chart_index];
            addBoxPlot(data, metadata,slice, slice_size_for_this_slice);
            break;
        case "timeseries":
            slice = charts_slice_global[chart_index];
            addTimeSeriesPlot(data, metadata,slice, slice_size_for_this_slice);
            break;
        default:
            console.log("invalid plot type - " + chartType);
    }
    
    if (chart_index == 0 && score_metadata_charts_global.length > 1) {
        $("#previousButton").prop("disabled", true);
        $("#nextButton").prop("disabled", false);
        $("#minChartButton").prop("disabled", true);
        $("#maxChartButton").prop("disabled", false);
    } else if (chart_index == score_metadata_charts_global.length - 1) {
        if (chart_index == 0) {
            $("#previousButton").prop("disabled", true);
            $("#nextButton").prop("disabled", true);
            $("#minChartButton").prop("disabled", true);
            $("#maxChartButton").prop("disabled", true);
        } else {
        $("#previousButton").prop("disabled", false);
        $("#nextButton").prop("disabled", true);
        $("#minChartButton").prop("disabled", false);
        $("#maxChartButton").prop("disabled", true);
        }
    } else {
        $("#nextButton").prop("disabled", false);
        $("#previousButton").prop("disabled", false);
        $("#minChartButton").prop("disabled", false);
        $("#maxChartButton").prop("disabled", false);
    }
}

function addChartOnHistogramClickSupervised(){
    $("#chartForScoreDiv").empty();
    data_supervised = score_charts_global_supervised[chart_index_supervised];
    metadata_supervised = score_metadata_charts_global_supervised[chart_index_supervised];
    slice_size_for_this_slice_supervised = slice_size_global_supervised[chart_index_supervised];
    switch(chartTypeSupervised) {
        case "bargraph":
            addBarChart(data_supervised, metadata_supervised, true, slice_size_for_this_slice_supervised);
            break;
        case "histogram":
            addHistogram(data_supervised, metadata_supervised, true,slice_size_for_this_slice_supervised);
            break;
        case "percentile":
            slice = charts_slice_global_supervised[chart_index_supervised];
            addPercentilePlot(data_supervised, metadata_supervised, slice, slice_size_for_this_slice_supervised);
            break;
        case "boxplot":
            slice = charts_slice_global_supervised[chart_index_supervised];
            addBoxPlot(data_supervised, metadata_supervised, slice, slice_size_for_this_slice_supervised);
            break;
        case "timeseries":
            slice = charts_slice_global_supervised[chart_index_supervised];
            addTimeSeriesPlot(data_supervised, metadata_supervised, slice, slice_size_for_this_slice_supervised);
            break;
        default:
            console.log("invalid plot type - " + chartTypeSupervised);
    }

    if (chart_index_supervised == 0 && score_metadata_charts_global_supervised.length > 1) {
        $("#previousButton").prop("disabled", true);
        $("#nextButton").prop("disabled", false);
        $("#minChartButton").prop("disabled", true);
        $("#maxChartButton").prop("disabled", false);
    } else if (chart_index_supervised == score_metadata_charts_global_supervised.length - 1) {
        if (chart_index_supervised == 0){
            $("#previousButton").prop("disabled", true);
            $("#nextButton").prop("disabled", true);
            $("#minChartButton").prop("disabled", true);
            $("#maxChartButton").prop("disabled", true);
        }else{    
            $("#previousButton").prop("disabled", false);
            $("#nextButton").prop("disabled", true);
            $("#minChartButton").prop("disabled", false);
            $("#maxChartButton").prop("disabled", true);
        }
    }else{
        $("#nextButton").prop("disabled", false);
        $("#previousButton").prop("disabled", false);
        $("#minChartButton").prop("disabled", false);
        $("#maxChartButton").prop("disabled", false);
    }            
}

function addPlotLineToScoreChart(scoreChart) {
   scoreChart.xAxis[0].addPlotLine({
       value: plotLineScoreGlobal,
       width: 1,
       color: 'red',
       id: 'plotLine',
       zIndex: 0
   });
}

function getPreviousPlotZero(){
    if (all_record_keeper_current_index > 0){
        endReachedFlag = false;

        all_record_keeper_current_index--;
        
        console.log(all_record_keeper);
        all_record_keeper.pop();

        var plotOneObjectAtZero = JSON.parse(JSON.stringify(charts_slice_global_supervised[charts_slice_global_supervised.length - 1]));
        var slice_arr = Object.keys(plotOneObjectAtZero).map(function(key){
            return [key, slice[key]];
        });

        var all_keys = [];
        for (var i=0;i<slice_arr.length;i++){
            all_keys.push(slice_arr[i][0]);
        }

        //console.log(all_record_keeper[all_record_keeper_current_index]);
        //console.log(all_record_keeper[all_record_keeper_current_index][1][0]);
        //console.log(all_record_keeper.length);
        
        score_charts_global.length = 0;
        score_metadata_charts_global.length = 0;
        charts_slice_global.length = 0;
        slice_size_global.length = 0;
        
        //console.log(all_record_keeper_current_index);
        score_charts_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][0]));
        //console.log(score_charts_global);
        score_metadata_charts_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][1]));
        charts_slice_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][2]));
        slice_size_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][3]));
        charts_per_score_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][4]));

        //console.log(all_record_keeper);
        
        score_charts_global_supervised.length = 0;
        score_metadata_charts_global_supervised.length = 0;
        charts_slice_global_supervised.length = 0;
        slice_size_global_supervised.length = 0;

        for (var index=0; index<charts_slice_global.length; index++){
            score_charts_global_supervised[index] = score_charts_global[index];
            score_metadata_charts_global_supervised[index] = score_metadata_charts_global[index];
            charts_slice_global_supervised[index] = charts_slice_global[index];
            slice_size_global_supervised[index] = slice_size_global[index];
        }
            
        plotZeroGlobal.length = 0;
        plotZeroGlobal = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][0][0]));
        var slice_for_plot_zero = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][0][1]));

        chart_index_supervised = 0;
        addChartOnHistogramClickSupervised();
        if (all_record_keeper_current_index === 0){
            switch(chartType) {
                case 'bargraph':
                    addBarChartPlotZero(true);
                    break;
                case 'histogram':
                    addHistogramPlotZero(true);
                    break;
                case 'percentile':
                    addPercentileChartPlotZero(true);
                    break;
                case 'boxplot':
                    addBoxPlotZero(true);
                    break;
                case 'timeseries':
                    addTimeSeriesPlotZero(true);
                    break;
                default:
                    console.log("invalid plot type");
            }
        }else{
            switch(chartType) {
                case 'bargraph':
                    addBarChartPlotZero(false, slice_for_plot_zero);
                    break;
                case 'histogram':
                    addHistogramPlotZero(false, slice_for_plot_zero);
                    break;
                case 'percentile':
                    addPercentileChartPlotZero(false, slice_for_plot_zero);
                    break;
                case 'boxplot':
                    addBoxPlotZero(false, slice_for_plot_zero);
                    break;
                case 'timeseries':
                    addTimeSeriesPlotZero(false, slice_for_plot_zero);
                    break;
                default:
                    console.log("invalid plot type");
            }
        }
        
        //Pop required number of elements from all_keys_in_slice_arr (i.e no of keys in right side before pressing button "previous plot" - no of keys in current plotzero)
        var plotZeroKeys = [];
        Object.keys(slice_for_plot_zero).forEach(function(key){
            plotZeroKeys.push(key);
        });

        var noOfItemsToPopFromAllKeysInSliceArr = all_keys.length - plotZeroKeys.length;
        for (var i=0;i<noOfItemsToPopFromAllKeysInSliceArr;i++){
            all_keys_in_slice_arr.pop();
        } 

        //adding necessary options to dropdown
        optionsAllowedSetToAddToSelectBox.clear();
        for (var index=0; index<charts_slice_global_supervised.length; index++){
            var sliceObject = charts_slice_global_supervised[index];
            var keysArray = Object.keys(sliceObject);
            for (var key=0; key<keysArray.length; key++){
                optionsAllowedSetToAddToSelectBox.add(keysArray[key]);
            }
        } 
        
        //get keys of charts_slice_global_supervised[0] slice
        var plotOneObjectAtZeroNewKeys = [];
        var plotOneObjectAtZeroNew = JSON.parse(JSON.stringify(charts_slice_global_supervised[charts_slice_global_supervised.length - 1]));
        Object.keys(plotOneObjectAtZeroNew).forEach(function(key){
            plotOneObjectAtZeroNewKeys.push(key);
        });
        
        var options = $('#all_attributes_supervised_selectbox option');
        var all_options_values = $.map(options ,function(option) {
            return option.value;
        });
        
        var all_attributes_supervised_selectbox = document.getElementById('all_attributes_supervised_selectbox');
        var valuesObject = optionsAllowedSetToAddToSelectBox.values();    
        for(var i=0; i<optionsAllowedSetToAddToSelectBox.size; i++) {
            var setElement = valuesObject.next().value;
            if(!all_options_values.includes(setElement)){ //if the selected value is not already an option in the selectbox, then add it
                if (!plotOneObjectAtZeroNewKeys.includes(setElement)){
                    var optionToAddToSelectBox = document.createElement('option');
                    optionToAddToSelectBox.value = setElement;
                    optionToAddToSelectBox.text = setElement;
                    all_attributes_supervised_selectbox.appendChild(optionToAddToSelectBox);
                }
            }    
        }
        $("#all_attributes_supervised_selectbox option:first").prop("selected", "selected");
    }else{
        alert("Original plot zero has already been loaded!!");
    }
}

function shiftPlotZero(){
    if (endReachedFlag){
        alert("This plot is already the current plot zero!!");
        return;
    }

    if (($('#supervised_checkbox').is(":checked")) || (!($('#supervised_checkbox').is(":checked")) && chart_index !== charts_slice_global.length-1)){ //no last chart  if unsupervised
        if (!($('#supervised_checkbox').is(":checked"))){
            slice = charts_slice_global[chart_index];//current selected slice to be made plot zero
        }else{
            slice = charts_slice_global_supervised[chart_index_supervised];
        }
        
        //console.log(JSON.stringify(slice));
        var slice_arr = Object.keys(slice).map(function(key){
            return [key, slice[key]];
        });
        console.log(slice_arr[0]);
        //$('#all_attributes_supervised_selectbox').children();
        var options = $('#all_attributes_supervised_selectbox option');
        var all_options_values = $.map(options ,function(option) {
            return option.value;
        });
        console.log(all_options_values);
        all_keys_in_slice_arr.length = 0;
        for (var i=0;i<slice_arr.length;i++){
            all_keys_in_slice_arr.push(slice_arr[i][0]);    
        }
        console.log(all_keys_in_slice_arr);
        var options_to_remove = [];
        for (var i=0;i<all_options_values.length;i++){
            if (all_keys_in_slice_arr.includes(all_options_values[i])){ //checks whether this option is present in current selected slice to be made plot zero
                    options_to_remove.push(all_options_values[i]);
            }
        }
        console.log(options_to_remove);
        if (options_to_remove.length !== 0){
            for (var i=0;i<options_to_remove.length;i++){
                var val_to_remove = options_to_remove[i];
                console.log(val_to_remove);
                $('#all_attributes_supervised_selectbox option[value="'+val_to_remove+'"]').remove()
                    //each(function(){
                    //if ($(this).val === val_to_remove){
                      //  console.log('in there');
                       // $(this).remove();
                   // }    
            }
        }        
        //console.log(values);
        switch(chartType) {
            case 'bargraph':
                addBarChartPlotZero(false, slice);
                break;
            case 'histogram':
                addHistogramPlotZero(false, slice);
                break;
            case 'percentile':
                addPercentileChartPlotZero(false, slice);
                break;
            case 'boxplot':
                addBoxPlotZero(false, slice);
                break;
            case 'timeseries':
                addTimeSeriesPlotZero(false, slice);
                break;
            default:
                console.log("invalid plot type");
        }
        var new_plot_zero_data = [];
        if (!($('#supervised_checkbox').is(":checked"))){
            new_plot_zero_data = score_charts_global[chart_index]; //data of current selected slice to be made plot zero
        }else{
            new_plot_zero_data = score_charts_global_supervised[chart_index_supervised];
        }
        var current_global_charts_per_score = JSON.parse(JSON.stringify(charts_per_score_global));
        console.log(current_global_charts_per_score);
        var new_global_charts_per_score = [];
        var x = slice_arr.length;
        if (x === 1){
            for (var counter=0; counter<current_global_charts_per_score.length; counter++){
                var current_slice_arr = Object.keys(current_global_charts_per_score[counter][2]).map(function(key){
                    return [key, current_global_charts_per_score[counter][2][key]]
                });
                var y = current_slice_arr.length;
                var foundFlag = false;
                for (var y_counter=0;y_counter<y;y_counter++){
                    //console.log(JSON.stringify(slice_arr[0]));
                    //console.log(JSON.stringify(current_slice_arr[y_counter]));
                    if (JSON.stringify(slice_arr[0]) == JSON.stringify(current_slice_arr[y_counter])){
                        //console.log('in here');
                        foundFlag = true;
                        break;
                    }
                }
                if (foundFlag){
                    new_global_charts_per_score.push(current_global_charts_per_score[counter]);
                }
            }
        }else{
            for (var counter=0; counter<current_global_charts_per_score.length; counter++){
                var current_slice_arr = Object.keys(current_global_charts_per_score[counter][2]).map(function(key){
                    return [key, current_global_charts_per_score[counter][2][key]]
                });
                var y = current_slice_arr.length;
                //var foundFlag = false;
                var x_found_in_y_arr = [];
                for (var i=0;i<slice_arr.length;i++){
                    var foundFlag = false;
                    var current_slice_arr_element_in_x = slice_arr[i];
                    for (var j=0;j<current_slice_arr.length;j++){
                        if (JSON.stringify(current_slice_arr_element_in_x) == JSON.stringify(current_slice_arr[j])){
                            foundFlag = true;
                            break;
                        }
                    }
                       // break;  //did not find current x element in current y at all, so dont add this y to new_global_charts_per_score 
                    //}else{
                    if (foundFlag){   
                        x_found_in_y_arr.push(true);    //push true for each found x. 
                    }
                }

                if (x_found_in_y_arr.length === x){
                    new_global_charts_per_score.push(current_global_charts_per_score[counter]);
                } 
            }
        }
        console.log(new_global_charts_per_score);
        var objToSend = {};
        objToSend['new_global_charts_per_score'] = new_global_charts_per_score;
        objToSend['plotZeroData'] = new_plot_zero_data;
        $.ajax({
            url: '/ba/search/bounds/plotzeroshift/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(objToSend)
        }).done(function(data){
            charts_per_score_global.length = 0;
            charts_per_score_global = data['new_global_charts_per_score'];
            console.log(charts_per_score_global);
            
            
            score_charts_global.length = 0;
            score_metadata_charts_global.length = 0;
            charts_slice_global.length = 0;
            slice_size_global.length = 0;

            for (var index in charts_per_score_global){
                score_charts_global.push(charts_per_score_global[index][0][0]);
                score_metadata_charts_global.push(charts_per_score_global[index][1]);
                charts_slice_global.push(charts_per_score_global[index][2]);
                slice_size_global.push(charts_per_score_global[index][3])
            }
            //console.log(charts_slice_global);
            

            //pushing the upcoming record to record keeper
            var record = [];
            var plotzerorecord = [];
            var plotonerecord = [];

            var plotZeroGlobalFirstToSend = JSON.parse(JSON.stringify(new_plot_zero_data));
            var plotZeroGlobalSecondToSend = JSON.parse(JSON.stringify(slice));

            plotzerorecord.push(plotZeroGlobalFirstToSend);
            plotzerorecord.push(plotZeroGlobalSecondToSend);

            var score_charts_global_to_send = JSON.parse(JSON.stringify(score_charts_global));
            var score_metadata_charts_global_to_send = JSON.parse(JSON.stringify(score_metadata_charts_global));
            var charts_slice_global_to_send = JSON.parse(JSON.stringify(charts_slice_global));
            var slice_size_global_to_send = JSON.parse(JSON.stringify(slice_size_global));
            var charts_per_score_global_to_send = JSON.parse(JSON.stringify(charts_per_score_global));

            plotonerecord.push(score_charts_global_to_send);
            plotonerecord.push(score_metadata_charts_global_to_send);
            plotonerecord.push(charts_slice_global_to_send);
            plotonerecord.push(slice_size_global_to_send);
            plotonerecord.push(charts_per_score_global_to_send);

            var plotzerorecordtosend = JSON.parse(JSON.stringify(plotzerorecord));
            var plotonerecordtosend = JSON.parse(JSON.stringify(plotonerecord));

            record.push(plotzerorecordtosend);
            record.push(plotonerecordtosend);

            all_record_keeper_current_index++;

            var recordtosend = JSON.parse(JSON.stringify(record));
            all_record_keeper.push(recordtosend);

            console.log(all_record_keeper);


            score_charts_global_supervised.length = 0;
            score_metadata_charts_global_supervised.length = 0;
            charts_slice_global_supervised.length = 0;
            slice_size_global_supervised.length = 0;

            /*for (var index in charts_per_score_global){
                score_charts_global_supervised.push(charts_per_score_global[index][0][0]);
                score_metadata_charts_global_supervised.push(charts_per_score_global[index][1]);
                charts_slice_global_supervised.push(charts_per_score_global[index][2]);
                slice_size_global_supervised.push(charts_per_score_global[index][3]);
            }*/

            for (var index=0; index<charts_slice_global.length; index++){
                score_charts_global_supervised[index] = score_charts_global[index];
                score_metadata_charts_global_supervised[index] = score_metadata_charts_global[index];
                charts_slice_global_supervised[index] = charts_slice_global[index];
                slice_size_global_supervised[index] = slice_size_global[index];
            }
            console.log(charts_slice_global_supervised);
            
            //Remove those options from dropdown which are absent in new charts_slice_global
            optionsAllowedSet.clear();
            
            //var optionToAddToSelectBox = document.createElement('option');
            //optionToAddToSelectBox.value = "Please select one option from below ";
            //optionToAddToSelectBox.text = "Please select one option from below";
            optionsAllowedSet.add("Please select one option from below ");

            for (var index=0; index<charts_slice_global_supervised.length; index++){
                sliceObject = charts_slice_global_supervised[index];
                keysArray = Object.keys(sliceObject);
                for (var key=0; key<keysArray.length; key++){
                    optionsAllowedSet.add(keysArray[key]);
                }
            }
            options = $('#all_attributes_supervised_selectbox option');
            all_options_values.length = 0;
            all_options_values = $.map(options ,function(option) {
                return option.value;
            });
            options_to_remove.length = 0;
            for (var i=0;i<all_options_values.length;i++){
                if (!optionsAllowedSet.has(all_options_values[i])){
                    options_to_remove.push(all_options_values[i]);
                }
            }
            if (options_to_remove.length !== 0){
                for (var i=0;i<options_to_remove.length;i++){
                    var val_to_remove = options_to_remove[i];
                    $('#all_attributes_supervised_selectbox option[value="'+val_to_remove+'"]').remove()
                }
            }
            supervisedModeOn = true;
            chart_index_supervised = 0;
            addChartOnHistogramClickSupervised();

            options = $('#all_attributes_supervised_selectbox option');
            if (options.length === 1){ //defualt option will still remain the select box
                endReachedFlag = true;
            }
            //all_options_values.length = 0;
            //all_options_values = $.map(options ,function(option) {
            //    return option.value;
            //});
            $("#supervised_checkbox").prop("checked", true);
            $('#only_checkbox_and_label').hide();
            $('#supervised_all').show();
            //document.getElementById("col-xs-2").style.visibility='hidden';        
            //document.getElementById("plotzerobutton").style.visibility='hidden';
            $("#all_attributes_supervised_selectbox option:first").prop("selected", "selected");
        });
        $("#all_attributes_supervised_selectbox option:first").prop("selected", "selected");
    }else{
        alert("This plot is already plot zero!!");
    }
} 

$('#all_attributes_supervised_selectbox').change(function(){
    var currentOptionSelected=$(this).val();
    document.getElementById("plotzerobutton").style.visibility='visible';
    filterOnAttribute(currentOptionSelected);
});

function filterOnAttribute(c){
   document.getElementById("col-xs-2").style.visibility='visible';
   var counter = 0;
   score_charts_global_supervised.length = 0;
   score_metadata_charts_global_supervised.length = 0;
   charts_slice_global_supervised.length = 0;
   slice_size_global_supervised.length = 0; 

   
   console.log(all_keys_in_slice_arr.length + 1);
   console.log(score_charts_global.length);

   for (var index in charts_slice_global){
       sliceObject = charts_slice_global[index]; 
       keysArray = Object.keys(sliceObject); //array of keys of current index of right side charts
       if (keysArray.length === all_keys_in_slice_arr.length + 1){
           console.log('length matched');
           if (keysArray.includes(c)){
               score_charts_global_supervised[counter] = score_charts_global[index];
               score_metadata_charts_global_supervised[counter] = score_metadata_charts_global[index];
               charts_slice_global_supervised[counter] = charts_slice_global[index];
               slice_size_global_supervised[counter] = slice_size_global[index];
               counter += 1;
           }
       }
   } 
   console.log(score_charts_global_supervised.length);
   console.log(score_metadata_charts_global_supervised);
   console.log(charts_slice_global_supervised);
   chart_index_supervised = 0;
   addChartOnHistogramClickSupervised();
}

function updateDropDownContent(attributeSet){
    all_attributes_supervised_selectbox = document.getElementById('all_attributes_supervised_selectbox');
    var optionToAddToSelectBox = document.createElement('option');
    optionToAddToSelectBox.value = "Please select one option from below ";
    optionToAddToSelectBox.text = "Please select one option from below";
    optionToAddToSelectBox.disabled = true;
    optionToAddToSelectBox.selected = true;
    all_attributes_supervised_selectbox.appendChild(optionToAddToSelectBox);

    for (let c of attributeSet){
        var optionToAddToSelectBox = document.createElement('option');
        optionToAddToSelectBox.value = c;
        optionToAddToSelectBox.text = c;
        all_attributes_supervised_selectbox.appendChild(optionToAddToSelectBox);
    } 
}

function getUniqueAttributesFromSlices(charts_slice_global){
    for (var index in charts_slice_global){
        sliceObject = charts_slice_global[index];
        keysArray = Object.keys(sliceObject);
        if (keysArray.length == 1){
            attributeSet.add(keysArray[0]);
        }
    }
    updateDropDownContent(attributeSet);
}

function onHistogramClicked(chartType, score, chartsMap, chartsMetadataMap, colNames) {
    $("#innerDiv").empty();
    var charts = [];
    var charts_metadata = [];
    
    // Set size of the global lists to zero, so that we populate it again for the new bin.
    score_charts_global.length = 0;
    score_metadata_charts_global.length = 0;
    charts_slice_global = []
    slice_size_global = []    
    for (var index in chartsMap) {
        score_charts_global.push(chartsMap[index][0][0]); 
        score_metadata_charts_global.push(chartsMap[index][1]);
        diff_score_global.push(chartsMap[index][0][1]);
        //if (chartType == 'percentile' || chartType == 'boxplot') {
            // get the slice for charts object.
        charts_slice_global.push(chartsMap[index][2]);
        slice_size_global.push(chartsMap[index][3])
        //}
    }
    
    var record = [];
    var plotzerorecord = [];
    var plotonerecord = [];
    
    var plotZeroGlobalFirstToSend = JSON.parse(JSON.stringify(plotZeroGlobal));
    //var plotZeroGlobalToSend = JSON.parse(JSON.stringify(plotZeroGlobal));
    var emptyObject = {};
    var plotZeroGlobalSecondToSend = JSON.parse(JSON.stringify(emptyObject));
    plotzerorecord.push(plotZeroGlobalFirstToSend);
    plotzerorecord.push(plotZeroGlobalSecondToSend);
    //plotzerorecord.push(plotZeroMetadataGlobal);


    var score_charts_global_to_send = JSON.parse(JSON.stringify(score_charts_global));
    var score_metadata_charts_global_to_send = JSON.parse(JSON.stringify(score_metadata_charts_global));
    var charts_slice_global_to_send = JSON.parse(JSON.stringify(charts_slice_global));
    var slice_size_global_to_send = JSON.parse(JSON.stringify(slice_size_global));
    var charts_per_score_global_to_send = JSON.parse(JSON.stringify(charts_per_score_global));

    plotonerecord.push(score_charts_global_to_send);
    plotonerecord.push(score_metadata_charts_global_to_send);
    plotonerecord.push(charts_slice_global_to_send);
    plotonerecord.push(slice_size_global_to_send);
    plotonerecord.push(charts_per_score_global_to_send);

    var plotzerorecordtosend = JSON.parse(JSON.stringify(plotzerorecord));
    var plotonerecordtosend = JSON.parse(JSON.stringify(plotonerecord));
    
    record.push(plotzerorecordtosend);
    record.push(plotonerecordtosend);

    all_record_keeper_current_index++;

    var recordtosend = JSON.parse(JSON.stringify(record));
    all_record_keeper.push(recordtosend);

    //console.log(all_record_keeper);

    //console.log(score_charts_global);
    //console.log(score_metadata_charts_global);
    //var numberOfSlicesTotalDiv = document.getElementById('NumberOfSlices');
    //numberOfSlicesTotalDiv.innerHTML = charts_slice_global.length + ' plots sorted by distance from plot zero';
    console.log(charts_slice_global);
    getUniqueAttributesFromSlices(charts_slice_global);

    columnsGlobal = colNames;
    chart_index = 0;
    numChartsPerBin = chartsMap.length;

    var div = document.createElement("div");
    div.id = "chartForScoreDiv";
    //div.style.marginTop = "20px";
    div.style.height = "360px";
    chart_type_global = chartType;
    
    var closeButtonAndArrowsDiv = document.createElement("div");
    closeButtonAndArrowsDiv.id = 'closeButtonAndArrowsDiv';
    closeButtonAndArrowsDiv.className = 'closeButtonAndArrowsDiv';
    closeButtonAndArrowsDiv.style.display = "flex";
    
    var columnDiv = document.createElement("div");
    columnDiv.id = 'col-xs-2';
    columnDiv.className = 'col-xs-2';
    var previousButton = document.createElement("input");
    previousButton.id = "previousButton";
    previousButton.value = " < ";
    previousButton.type = "button";
    previousButton.title = "Previous";
    previousButton.style.marginRight = "10px";
    previousButton.style.height = "30px";
    previousButton.disabled = true;
    var nextButton = document.createElement("input");
    nextButton.id = "nextButton";
    nextButton.value = " > ";
    nextButton.type = "button";
    nextButton.title = "Next";
    nextButton.style.marginLeft = "10px";
    
    var minChartButton = document.createElement("input");
    minChartButton.id = "minChartButton";
    minChartButton.value = " |< ";
    minChartButton.type = "button";
    minChartButton.title = "Get Minimum score chart";
    minChartButton.style.marginRight = "10px";
    minChartButton.disabled = true;
    var maxChartButton = document.createElement("input");
    maxChartButton.id = "maxChartButton";
    maxChartButton.value = " >| ";
    maxChartButton.type = "button";
    maxChartButton.title = "Get Maximum score chart";
    maxChartButton.style.marginLeft = "10px";

    columnDiv.appendChild(minChartButton);
    columnDiv.appendChild(previousButton);
    columnDiv.appendChild(nextButton);
    columnDiv.appendChild(maxChartButton);
    columnDiv.style.marginTop = "12px";
    columnDiv.style.width = "50%";
    if (score_metadata_charts_global.length == 1) {
        nextButton.disabled = true;
        previousButton.disabled = true;
        minChartButton.disabled = true;
        maxChartButton.disabled = true;
    }
    $("#innerDiv").append(div);

    var closeButtonDiv = document.createElement("div");
    closeButtonDiv.className = "row";
    closeButtonDiv.id = "buttonDiv";
    var button = document.createElement("input");
    button.type = "button";
    button.id = "chart_min_max_button";
    button.value = "Close";
    button.name = "chart_min_max_button";
    button.style.marginLeft = "50px";
    closeButtonDiv.appendChild(button);
    closeButtonDiv.style.width = "50%";
    closeButtonDiv.style.marginTop = "12px";

    closeButtonAndArrowsDiv.appendChild(closeButtonDiv);
    closeButtonAndArrowsDiv.appendChild(columnDiv);
    
    $("#dialog_container").append(closeButtonAndArrowsDiv);
    addChartOnHistogramClick(scoreChart, chartType);
    //$("#innerDiv").append(columnDiv);
}

function disablePage(disable) {
    if (disable) {
        $("#searchResultsDiv").css("pointerEvents", "none");
        $("#loading").css("display", "block");
    } else {
        $("#loading").css("display", "none");
        $("#searchResultsDiv").css("pointerEvents", "auto");
        
    }
}

function addPlotZeroChart(chartType) {
    var plotZeroDiv = document.createElement("div");
    plotZeroDiv.id = "plotZeroDiv";
    plotZeroDiv.style.width = "50%";
    var div = document.createElement("div");
    div.id = "scoreHistogramDiv";
    //div.style.marginTop = "20px";
    div.style.height = "420px"; 
    plotZeroDiv.appendChild(div);
    $("#mainDiv").append(plotZeroDiv);
    var innerDiv = document.createElement("div");
    innerDiv.id = "innerDiv";
    innerDiv.style.width = "50%";
    //innerDiv.style.height = "420px";
    $("#mainDiv").append(innerDiv);
    switch(chartType) {
        case 'bargraph':
            addBarChartPlotZero(true);
            break;
        case 'histogram':
            addHistogramPlotZero(true);
            break;
        case 'scatter':
            addScatterChartPlotZero();
            break;
        case 'percentile':
            addPercentileChartPlotZero(true);
            break;
        case 'boxplot':
            addBoxPlotZero(true);
            break;
        case 'timeseries':
            addTimeSeriesPlotZero(true);
            break;
        default:
            console.log("invalid plot type");
    }
}

function addBarChartPlotZero(isOrig, slice) {
    categoriesList = [];
    valuesList = [];
    if(isOrig){
        for (val of plotZeroGlobal) {
            categoriesList.push(val[0]);
            valuesList.push(val[1]);
        }
        var titleText = "Plot zero reference chart";
    }else{
        if (!($('#supervised_checkbox').is(":checked"))){
            for (val of score_charts_global[chart_index]) {
                categoriesList.push(val[0]);
                valuesList.push(val[1]);
            }
        }else{
            for (val of score_charts_global_supervised[chart_index_supervised]) {
                categoriesList.push(val[0]);
                valuesList.push(val[1]);
            }
        }
        sliceArr = [];
        Object.keys(slice).forEach(function(key){
            sliceArr.push("(" + key + " = " + slice[key] + ")");
        });
        var titleText = sliceArr.join(" & ");
    }
    Highcharts.chart('scoreHistogramDiv', {
        title: {text: titleText},
        chart: {type: 'column', borderColor: 'black', borderWidth: 1, height: 360},
        xAxis: {categories: categoriesList},
        yAxis: {title: {text: 'Frequency'}, min: 0, max: chartsScaleGlobal['max']},
        plotOptions: {
            series: {
                maxPointWidth: 70,
                events : {
                    legendItemClick: function() {
                        return false;
                    }
                }
            }
        },
        tooltip: {
            formatter : function() {
                return this.y.toFixed(2) + '%';
            }
        },
        series: [{
            data: valuesList,
            name: plotZeroMetadataGlobal[0],
            animation: false
        }]
    });
}

function addHistogramPlotZero(isOrig, slice) {
    var offset = 0;
    if (isOrig){
        if (plotZeroGlobal.length > 1) {
            offset = plotZeroGlobal[1][0] - plotZeroGlobal[0][0];
        }
        var titleText = "Plot zero reference chart";
        var dataForPlot = plotZeroGlobal;
    }else{
        if (!($('#supervised_checkbox').is(":checked"))){
            if (score_charts_global[chart_index].length > 1) {
                offset = score_charts_global[chart_index][1][0] - score_charts_global[chart_index][0][0];
                var dataForPlot = score_charts_global[chart_index];
            }
        }else{
            if (score_charts_global_supervised[chart_index_supervised].length > 1) {
                offset = score_charts_global_supervised[chart_index_supervised][1][0] - score_charts_global_supervised[chart_index_supervised][0][0];
                var dataForPlot = score_charts_global_supervised[chart_index_supervised];
            }
        }
        sliceArr = [];
        Object.keys(slice).forEach(function(key){
            sliceArr.push("(" + key + " = " + slice[key] + ")");
        });
        var titleText = sliceArr.join(" & ");
    }
    console.log(dataForPlot);
    histogramPlotZeroData = [];
    histogramPlotZeroData = JSON.parse(JSON.stringify(dataForPlot));
    Highcharts.chart('scoreHistogramDiv', {
        title: {text: titleText},
        chart: {type: 'column', borderColor: 'black', borderWidth: 1, height: 360},
        xAxis: {title: {text: plotZeroMetadataGlobal[0]}, max: chartsScaleGlobal['max_x']},
        yAxis: {title: {text: 'Frequency'}, max: chartsScaleGlobal['max']},
        series: [{
            name: 'Data',
            showInLegend: false,
            data: dataForPlot,
            pointPlacement: 'between',
            animation: false
        }],
        plotOptions: {
            column: {
                pointPadding: 0,
                borderWidth: 1,
                groupPadding: 0
            }
        },
        tooltip: {
            stickOnContact: true,
            formatter: function() {
                var p_x = Math.round(this.point.x);
                var p_x_plus_offset = Math.round(this.point.x + offset);
                var flag_x = '';
                var flag_x_plus_offset = '';

                if (Math.abs(p_x) > 999999){
                    var x_new = Math.sign(p_x)*((Math.abs(p_x)/1000000).toFixed(1));
                    flag_x = 'M';
                }else if(Math.abs(p_x) > 999){
                    var x_new = Math.sign(p_x)*((Math.abs(p_x)/1000).toFixed(1));
                    flag_x = 'K';
                }else{
                    var x_new = p_x;
                    flag_x = '';
                }

                if (Math.abs(p_x_plus_offset) > 999999){
                    p_x_plus_offset = Math.sign(p_x_plus_offset)*((Math.abs(p_x_plus_offset)/1000000).toFixed(1));
                    flag_x_plus_offset = 'M';
                }else if (Math.abs(p_x_plus_offset) > 999){
                    p_x_plus_offset = Math.sign(p_x_plus_offset)*((Math.abs(p_x_plus_offset)/1000).toFixed(1));
                    flag_x_plus_offset = 'K';
                }else{
                    flag_x_plus_offset = '';
                }
                return x_new + flag_x + "-" + p_x_plus_offset + flag_x_plus_offset +  " : <b>" + this.point.y + "</b>";
            }
        }
    });
}

function addScatterChartPlotZero() {
    Highcharts.chart('scoreHistogramDiv', {
        title: {text: 'Plot zero reference chart'},
        chart: {type: 'scatter'},
        xAxis: {title: {text: plotZeroMetadataGlobal[0]}},
        yAxis: {title: {text: plotZeroMetadataGlobal[1]}},
        series : [{
            name: 'series1',
            data: plotZeroGlobal,
            color: '#3354FF',
            showInLegend: false
        }]
    });
}

function addTimeSeriesPlotZero(isOrig, slice){
    dataValues = [];
    var newbiglist = []
    if(isOrig){
        dataValues.push(plotZeroGlobal);
        var titleText = "Plot zero reference chart";
    }else{
        if (!($('#supervised_checkbox').is(":checked"))){
            dataValues.push(score_charts_global[chart_index]);
        }else{
            dataValues.push(score_charts_global_supervised[chart_index_supervised]);
        }
        sliceArr = [];
        Object.keys(slice).forEach(function(key){
            sliceArr.push("(" + key + " = " + slice[key] + ")");
        });
        var titleText = sliceArr.join(" & ");
    }
    console.log(titleText);
    console.log(plotZeroMetadataGlobal[1]);
    var data = dataValues[0];
    data.forEach(function(point) {
        point[0] = Date.parse(point[0])
    });
    
    var counter=0;
    for (var i=0; i<data.length; i++){
        if (counter<6){
            counter+=1;
            continue;    
        }
        var newlist = JSON.parse(JSON.stringify(data[i]));
        newbiglist.push(newlist);
    }
    console.log(newbiglist);
    console.log(chartsScaleGlobal['min']);
    console.log(chartsScaleGlobal['max']);
    
    Highcharts.stockChart('scoreHistogramDiv', {
        //navigator: {enabled: false},
        title: {text: titleText},
        chart: {height: 360},
        //subtitle: {text: document.ontouchstart === undefined ? 'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in' },
        xAxis: {type: 'datetime'},
        yAxis: {title: {text: plotZeroMetadataGlobal[1]}, min: chartsScaleGlobal['min'], max: chartsScaleGlobal['max']},
        legend: {enabled: false},
        plotOptions: {
                        /*area: {fillColor: {stops: [[0, Highcharts.getOptions().colors[0]],[1, Highcharts.color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]]},
                             marker: {radius: 2},
                             lineWidth: 2,
                             states: {hover: {lineWidth: 1}},
                            }
                    */
                        series: {showInNavigator: true}     
                    },
        /*tooltip: {
            formatter: function(){
                var p_x = Math.round(this.point.x);

            }
        }*/
        tooltip: {pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y} </b><br/>', valueDecimals: 2},
        series: [{
            //type: 'area',
            data: newbiglist}]
    });
}

function addPercentileChartPlotZero(isOrig, slice) {
    dataValues = [];
    if(isOrig){
        plotZeroGlobal.forEach(function(val) {
            dataValues.push(val);
        });
        var titleText = "Plot zero reference chart";
    }else{
        //dataValues.push(score_charts_global_supervised[chart_index_supervised]);
        if (!($('#supervised_checkbox').is(":checked"))){
            score_charts_global[chart_index].forEach(function(val) {
                dataValues.push(val);
            });
        }else{
            score_charts_global_supervised[chart_index_supervised].forEach(function(val) {
                dataValues.push(val);
            });
        }
        sliceArr = [];
        Object.keys(slice).forEach(function(key){
            sliceArr.push("(" + key + " = " + slice[key] + ")");
        });
        var titleText = sliceArr.join(" & ");
    }
    categoriesList = [95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5];
    
    //plotZeroGlobal.forEach(function(val) {
    //   dataValues.push(val);
    //})
    //dataValues = [];
    //dataValues.push(plotZeroGlobal);
    Highcharts.chart('scoreHistogramDiv', {
        title: {text: titleText},
        chart: {type: 'line', borderColor: 'black', borderWidth: 1, height: 360},
        xAxis: {title: {text: 'percentiles'}, labels: {format: "{value}%"}, categories: categoriesList},
        yAxis: {title: {text: plotZeroMetadataGlobal[0]}}, //, min: chartsScaleGlobal['min'], max: chartsScaleGlobal['max']},
        /*plotOptions: {
            boxplot: {
                fillColor: 'lightgray',
                lineWidth: 3,
                medianColor: 'darkblue',
                medianWidth: 3,
                stemDashStyle: 'dot',
                stemWidth: 2
            }
        },*/
        series: [{
            name: 'Line Chart',
            data: dataValues,
            showInLegend: false,
            animation: false
        }]
    });
}

function addBoxPlotZero(isOrig,slice){
    dataValues = [];
    //plotZeroGlobal.forEach(function(val){
    if (isOrig){
        dataValues.push(plotZeroGlobal);
        var titleText = "Plot zero reference chart";
    }else{
        if (!($('#supervised_checkbox').is(":checked"))){
            dataValues.push(score_charts_global[chart_index]);
        }else{
            dataValues.push(score_charts_global_supervised[chart_index_supervised]); 
        }
        sliceArr = [];
        Object.keys(slice).forEach(function(key){
            sliceArr.push("(" + key + " = " + slice[key] + ")");
        })
        var titleText = sliceArr.join(" & ");
    }
    //dataValues.push(plotZeroGlobal);
    //})
    
    //var titleText = "Plot zero reference chart";
    console.log(dataValues);
    Highcharts.chart('scoreHistogramDiv',{
        chart: {type: 'boxplot', height: 360},
        title: {text: titleText},
        legend: {enabled: false},
        //xAxis: {title: {text: plotZeroMetadataGlobal[0]}},
        yAxis: {title: {text: plotZeroMetadataGlobal[0]}, min: chartsScaleGlobal['min'], max: chartsScaleGlobal['max']},
        plotOptions: {
            boxplot: {
                fillColor: '#F0F0E0',
                lineWidth: 4,
                medianColor: '#0C5DA5',
                medianWidth: 3,
                stemWidth: 2,
                stemDashStyle: 'dot'
            }
        },
        tooltip: {
            stickOnContact: true,
            formatter: function(){
                var t_high = typeof this.point.high;
                //var t_q_three = typeof this.point.q3;
                //var t_median = typeof this.point.median;
                //var t_q_one = typeof this.point.q1;
                //var t_low = typeof this.point.low;
                
                if (t_high === "number"){
                    var p_high = Math.round(this.point.high);
                    var p_q_three = Math.round(this.point.q3);
                    var p_median = Math.round(this.point.median);
                    var p_q_one = Math.round(this.point.q1);
                    var p_low = Math.round(this.point.low);

                    if (Math.abs(p_high) > 999999){
                        this.point.high = Math.sign(p_high)*((Math.abs(p_high)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_high) > 999){
                        this.point.high = Math.sign(p_high)*((Math.abs(p_high)/1000).toFixed(1))+'K';
                    }else{
                        this.point.high = p_high;
                    }

                    if (Math.abs(p_q_three) > 999999){
                        this.point.q3 = Math.sign(p_q_three)*((Math.abs(p_q_three)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_q_three) > 999){
                        this.point.q3 = Math.sign(p_q_three)*((Math.abs(p_q_three)/1000).toFixed(1))+'K';
                    }else{
                        this.point.q3 = p_q_three;
                    }    

                    if (Math.abs(p_median) > 999999){
                        this.point.median = Math.sign(p_median)*((Math.abs(p_median)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_median) > 999){
                        this.point.median = Math.sign(p_median)*((Math.abs(p_median)/1000).toFixed(1))+'K';
                    }else{
                        this.point.median = p_median; 
                    }    

                    if (Math.abs(p_q_one) > 999999){
                        this.point.q1 = Math.sign(p_q_one)*((Math.abs(p_q_one)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_q_one) > 999){
                        this.point.q1 = Math.sign(p_q_one)*((Math.abs(p_q_one)/1000).toFixed(1))+'K';
                    }else{
                        this.point.q1 = p_q_one;
                    }

                    if (Math.abs(p_low) > 999999){
                        this.point.low = Math.sign(p_low)*((Math.abs(p_low)/1000000).toFixed(1))+'M';
                    }else if(Math.abs(p_low) > 999){
                        this.point.low = Math.sign(p_low)*((Math.abs(p_low)/1000).toFixed(1))+'K';
                    }else{
                        this.point.low = p_low;
                    }
                }    
                return this.series.name + "</b><br/>Maximum: " + this.point.high + "<br/>Upper quartile: " + this.point.q3 + "<br/>Median: " + this.point.median + "<br/>Lower quartile: " + this.point.q1 + "<br/>Minimum: " + this.point.low + "<br/>";
            }
        },
        series: [{
            name: 'Box Plot',
            data: dataValues,
            marker: {lineWidth: 1}
        }]
    });
}

$(".plusButton").on("click", function(){
    disablePage(true);
    var labelText = $("#selectedLabelText").text();
    var queryParts = labelText.split("->")[1].split(";");
    var sliceQuery = [];
    for (i = 0; i < queryParts.length; i++) {
        if (queryParts[i].includes(":")) {
            // query has slice.
            sliceQuery.push(queryParts[i]);
        }
    }
    var id = $(this).attr("id")
    var attributesLabel = $("#"+id).find('label[id^="lab"]').attr("id");
    var attributes = $("#"+attributesLabel).text().split(":");
    var scoreLabel = $("#"+id).find('label[id^="score"]').attr("id");
    var plotZeroChartScore = $("#"+scoreLabel).text().split(":");
    var chartTypeLabel = $("#"+id).find('label[id^="type"]').attr("id");
    chartType = $("#"+chartTypeLabel).text();
    chartTypeSupervised = chartType;
    
    var attributesMap = {};
    attributesMap['firstAttr'] = attributes[0];
    attributesMap['secondAttr'] = (attributes.length == 2) ? attributes[1] : 'NA';
    //console.log(attributesMap['secondAttr']);
    attributesMap['slices'] = sliceQuery;
    attributesMap['chartType'] = chartType;
    //console.log(attributesMap);
    
    $.ajax({
        url: '/ba/search/bounds/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(attributesMap)
    }).done(function(data){
        $("#supervised_checkbox").prop("checked", false);
        disablePage(false);
        $('#searchresultsdiv').css({'visibility':'hidden'});
        //$('#searchresultsdiv').css({'background-color': '#A9A9A9'});
        //$('#searchresultsdiv').css({'background-color':'#A9A9A9'});
        $('#searchresultsdiv>#chart_min_max_dialog').css({'visibility':'visible'});
        plotZeroGlobal = data['plotzero_chart'];
        console.log(plotZeroGlobal);
        plotZeroMetadataGlobal = data['plotzero_metadata'];
        console.log(plotZeroMetadataGlobal);
        chartsScaleGlobal = data['scale']
        console.log(chartsScaleGlobal);
        addPlotZeroChart(chartType);
        charts_per_score_global = data['charts_per_score']; 
        console.log(data['charts_per_score']);
        onHistogramClicked(chartType, plotZeroChartScore, data['charts_per_score'], data['charts_metadata_per_score'], data['columns']);
        //addScoreHistogram(chartType, plotZeroChartScore, data['scores'], data['charts_per_score'], data['charts_metadata_per_score'], data['columns']);
        //addButtonToContainer();
        //
        $("#chart_min_max_dialog").css("display", "block");
    }).fail(function(xhr){
        disablePage(false);
        try {
            var msg = $.parseJSON(xhr.responseText);
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Failed to explore plot. Please check system logs for more details. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
});

$("#dialog_container").on("click", "#chart_min_max_button", function(e){
    $("#mainDiv").empty();
    $("div").remove("#buttonDiv");
    $("div").remove("#col-xs-2");
    $("div").remove("#innerDiv");
    $("div").remove("#scoreHistogramDiv");
    $("#chart_min_max_dialog").css("display", "none");
    attributeSet.clear();
    optionsAllowedSet.clear();
    optionsAllowedSetToAddToSelectBox.clear();
    $('#all_attributes_supervised_selectbox').children().remove();
    $('#only_checkbox_and_label').show();
    $('#supervised_all').hide();
    $("#supervised_checkbox").prop("checked", false);
    $("#only_supervised_checkbox").prop("checked", false);
    supervisedModeOn = false;
    chart_index = 0;
    all_keys_in_slice_arr.length = 0;
    all_record_keeper.length = 0;
    all_record_keeper_current_index = -1;
    endReachedFlag = false;
    $('#searchresultsdiv').css({'visibility':'visible'});
});

$("#dialog_container").on("click", "#previousButton", function(e) {
    if (supervisedModeOn){
        chart_index_supervised--;
        addChartOnHistogramClickSupervised();
    }else{
        chart_index--;
        addChartOnHistogramClick(scoreChart, chart_type_global);
    }
});

$("#dialog_container").on("click", "#nextButton", function(e) {
    if (supervisedModeOn){
        chart_index_supervised++;
        addChartOnHistogramClickSupervised();
    }else{
        chart_index++;
        addChartOnHistogramClick(scoreChart, chart_type_global);
    }
});

$("#dialog_container").on("click", "#minChartButton", function(e) {
    if (supervisedModeOn){
        chart_index_supervised = 0;
        addChartOnHistogramClickSupervised();
    }else{
        chart_index = 0;
        addChartOnHistogramClick(scoreChart, chart_type_global);
    }
});

$("#dialog_container").on("click", "#maxChartButton", function(e) {
    if (supervisedModeOn){
        chart_index_supervised = score_charts_global_supervised.length - 1; 
        addChartOnHistogramClickSupervised();
    }else{
        chart_index = numChartsPerBin - 1;
        addChartOnHistogramClick(scoreChart, chart_type_global);
    }
});


$("#errorDialogButton").on("click", function(e){
    $("#error_dialog").css("display", "none");
});

$("#successDialogButton").on("click", function(e) {
    $("#success_dialog").css("display", "none");
});

$("#theform").on("submit", function(e){
    e.preventDefault();
    var formdata = new FormData(this);
    $.ajax({
        url: '/ba/search/internal',
        type: 'POST',
        data: formdata,
        processData: false,
        contentType: false,
    }).done(function(data){
        console.log("Search query executed successfully");
        var q = data['q'];
        var show = data['show'];
        var boxname = data['boxname'];
        console.log(boxname);
        window.location.href = '/ba/search/?q=' + q + "&show=" + show + "&boxname=" + boxname;
    }).fail(function(xhr){
        try {
            var msg = $.parseJSON(xhr.responseText);
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Failed to search based on the specified criteria. Please check system logs for more details. " + e);
            $("#error_dialog").css("display", "block");
        }
    });
});

function showOrHideDropDown() {
    if ($('#supervised_checkbox').is(":checked")){
        supervisedModeOn = true;
        document.getElementById("col-xs-2").style.visibility='hidden';        
        document.getElementById("plotzerobutton").style.visibility='hidden';
        $("#all_attributes_supervised_selectbox option:first").prop("selected", "selected");
    }else{
        document.getElementById("col-xs-2").style.visibility='visible';
        supervisedModeOn = false;
        
        for (var i=all_record_keeper_current_index;i>0;i--){
            all_record_keeper.pop();
            all_record_keeper_current_index--;
        }

        all_keys_in_slice_arr.length = 0;
        
        plotZeroGlobal = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][0][0]));
        switch(chartType) {
            case 'bargraph':
                addBarChartPlotZero(true);
                break;
            case 'histogram':
                addHistogramPlotZero(true);
                break;
            case 'percentile':
                addPercentileChartPlotZero(true);
                break;
            case 'boxplot':
                addBoxPlotZero(true);
                break;
            default:
                console.log("invalid plot type");
        }

        score_charts_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][0]));
        score_metadata_charts_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][1]));
        charts_slice_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][2]));
        slice_size_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][3]));
        charts_per_score_global = JSON.parse(JSON.stringify(all_record_keeper[all_record_keeper_current_index][1][4]));

        chart_index = 0;
        addChartOnHistogramClick(scoreChart,chart_type_global);
        
        //update all options in dropdown
        var options = $('#all_attributes_supervised_selectbox option');
        if (options.length === 0){
            updateDropDownContent(attributeSet);
        }else{
            var all_options_values = $.map(options ,function(option) {
                return option.value;
            });
            var all_attributes_supervised_selectbox = document.getElementById('all_attributes_supervised_selectbox');
            var valuesObject = attributeSet.values();
            for(var i=0; i<attributeSet.size; i++) {
                var setElement = valuesObject.next().value;
                if(!all_options_values.includes(setElement)){
                    var optionToAddToSelectBox = document.createElement('option');
                    optionToAddToSelectBox.value = setElement;
                    optionToAddToSelectBox.text = setElement;
                    all_attributes_supervised_selectbox.appendChild(optionToAddToSelectBox);
                }
            }
        }

        $('#only_supervised_checkbox').prop('checked', false);
        onlyShowOrHideDropDown();
        //$('#all_attributes_supervised_selectbox').children().remove();
        endReachedFlag = false;
    }
}


function onlyShowOrHideDropDown(){
    if ($('#only_supervised_checkbox').is(":checked")){ //if initial checkbox is checked
        $('#only_checkbox_and_label').hide();
        $('#supervised_all').show();
        $('#supervised_checkbox').prop('checked', true);
        showOrHideDropDown();
    }else{
        $('#only_checkbox_and_label').show();
        $('#supervised_all').hide();
    }
}

function mouseDown(){
    if(endReachedFlag){
        alert("Slice can't be narrowed down further!!!");
    }
}

$(document).ready(function(){
        var title = "This tells how interesting a particular plot with given attributes is on the scale of 0-5.\nThe interestingness of a plot is determined by the spread between its MAX score and MIN score.";
        $(".starsOuter").attr("title", title);
        if ($("#display_type").val() == 'favorites') {
            $(".commentsDiv").css("display", "inline-block");
        }
        $('#supervised_all').hide();
});
