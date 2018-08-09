update_house = function (button_element) {

    $.ajax({
        type: "GET",
        url: "/health/update_all/",
        success: function (data) {
            console.log(data);
            location.reload();

        },
        error: function () {
            alert("Error in executing Update. Contact admin for support");

        }
    });

};

function load_restart_thumbnail(element, count) {
    console.log('function called');


    if (count > 3) {
        console.log('if statement called');

        $('#' + element).attr('src', '/static/HouseHealth/images/danger.png')
    }
    else if (count >= 1) {
        $('#' + element).attr('src', '/static/HouseHealth/images/warning.png')

    }
}

generate_report = function (house_id) {
    console.log('generate_astros_called')

    generate_report_url = "/health/generate_report/?house_id=" + house_id;

    window.open(generate_report_url, '_blank')


};