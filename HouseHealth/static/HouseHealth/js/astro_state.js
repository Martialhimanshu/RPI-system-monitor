$(document).ready(function () {

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
            xhr.setRequestHeader('X-CSRFToken',
                csrftoken);
        }
    });


    delete_house = function (element_id, house_id) {
        $(element_id).prop("disabled", true);
        console.log("function called");


        $.ajax({
            type: "POST",
            url: "/health/delete_house/",
            data: JSON.stringify({"house_id": house_id}),
            contentType: 'application/json',
            success: function (data) {
                $(element_id).prop("disabled", false);

                console.log("success");

            },
            error: function () {
                $(element_id).prop("disabled", false);

                console.log("Error");

            }


        });

    };
});
