//  if AJAX(ping) then  AJAX request() variable2 is true then CCOMPLETE AND DONE!!!



var ping = () => {

    $.ajax({
        url: '/dummy/',
        async: false
    }).done((status) => {

        console.log(status);

        if (status === "Progress1") {

            // Activate the progress header
            var progressCard = document.getElementById("progressCard");
            progressCard.setAttribute("style", "display: block;");

            // Activate the progress bar
            var progress = document.getElementById("progress");
            progress.setAttribute("style", "width: 700px; display: block;");

            // Deactivate the progress2 bar
            var progress2 = document.getElementById("progress2");
            progress2.setAttribute("style", "display: none;");
        } else if (status === "Progress2") {

            // Activate the progress header
            var progressCard = document.getElementById("progressCard");
            progressCard.setAttribute("style", "width: 400px; display: block;");

            // Activate the progress bar
            var progress = document.getElementById("progress");
            progress.setAttribute("style", "width: 350px; display: block;");

            // Deactivate the progress2 bar
            var progress2 = document.getElementById("progress2");
            progress2.setAttribute("style", "display: none;");

        } else if (status === "Stage1") {

            // Deactivate the progress bar
            var progress = document.getElementById("progress");
            progress.setAttribute("style", "display: none;");

            // Activate the progress2 bar
            var progress2 = document.getElementById("progress2");
            progress2.setAttribute("style", "width: 700px; display: block;");

            // Show pop-up
            var modal = document.getElementById("top100Modal");
            var span = document.getElementsByClassName("cool")[0];
            modal.style.display = "block";

            span.onclick = function () {
                modal.style.display = "none";
            }

            // Deactivate the progress card
            var progressCard = document.getElementById("progressCard");
            progressCard.setAttribute("style", "display: none;");

        } else if (status === "Stage2") {

            // Deactivate the progress bar
            var progress = document.getElementById("progress");
            progress.setAttribute("style", "display: none;");

            // Activate the progress2 bar
            var progress2 = document.getElementById("progress2");
            progress2.setAttribute("style", "width: 700px; display: block;");

            // Show pop-up
            var modal = document.getElementById("topModal");
            var span = document.getElementsByClassName("damncool")[0];
            modal.style.display = "block";

            span.onclick = function () {
                modal.style.display = "none";
            }

            // Deactivate the progress card
            var progressCard = document.getElementById("progressCard");
            progressCard.setAttribute("style", "display: none;");
            flag = false
        } else {

            // Deactivate the progress card
            var progressCard = document.getElementById("progressCard");
            progressCard.setAttribute("style", "display: none;");

        }
    });
}

var statusCheckFun = function runner() {
    ping()
    setTimeout(() => {
        if (flag)
            runner()
    }, 1000)
}