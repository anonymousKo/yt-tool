$(document).ready(function() {
    $('#info-form').submit(function(event) {
        event.preventDefault();
        var url = $('#url').val();
        $('#info-result').empty();
        showLoadingSpinner('#info-result');
        $.get('/info?url=' + url, function(data) {
            $('#info-result').text(data);
        }).fail(function() {
            $('#info-result').text('Error occurred.');
        }).always(function() {
            hideLoadingSpinner('#info-result');
        });
    });

    $('#download-form').submit(function(event) {
        event.preventDefault();
        var url = $('#url').val();
        var videoId = $('#video-id').val();
        $('#download-result').empty();
        showLoadingSpinner('#download-result');
        $.get('/download?url=' + url + '&id=' + videoId, function(data) {
            $('#download-result').text(data);
        }).fail(function() {
            $('#download-result').text('Error occurred.');
        }).always(function() {
            hideLoadingSpinner('#download-result');
        });
    });

    $('#list-form').submit(function(event) {
        event.preventDefault();
        $('#file-list').empty();
        showLoadingSpinner('#file-list');
        $.get('/list', function(data) {
            $('#file-list').text(data);
        }).fail(function() {
            $('#file-list').text('Error occurred.');
        }).always(function() {
            hideLoadingSpinner('#file-list');
        });
    });

    $('#getFile-form').submit(function(event) {
        event.preventDefault();
        var fileId = $('#file-id').val();
        $('#get-file-result').empty();
        showLoadingSpinner('#get-file-result');
        $.get('/getFile?id=' + fileId, function(data) {
            if (data !== 'File not found.') {
                window.location.href = '/getFile?id=' + fileId;
            } else {
                $('#get-file-result').text(data);
            }
        }).fail(function() {
            $('#get-file-result').text('Error occurred.');
        }).always(function() {
            hideLoadingSpinner('#get-file-result');
        });
    });

    $('#get-form').submit(function(event) {
        event.preventDefault();
        var url = $('#direct-url').val();
        var videoId = $('#direct-video-id').val();
        window.location.href = '/get?url=' + url + '&video_id=' + videoId;
    });
});

function showLoadingSpinner(elementId) {
    var spinnerHtml = '<div class="spinner">' +
        '<div class="rect1"></div>' +
        '<div class="rect2"></div>' +
        '<div class="rect3"></div>' +
        '<div class="rect4"></div>' +
        '<div class="rect5"></div>' +
        '</div>';
    $(elementId).html(spinnerHtml);
}

function hideLoadingSpinner(elementId) {
    $(elementId).find('.spinner').remove();
}
