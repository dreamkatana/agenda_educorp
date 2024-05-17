// static/js/reload.js
function reloadPage() {
    setTimeout(function() {
        location.reload();
    }, 10000); // 10000 milliseconds = 10 seconds
}
window.onload = reloadPage;