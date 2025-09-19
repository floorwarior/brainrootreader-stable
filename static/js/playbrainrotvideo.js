
// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;


function onYouTubeIframeAPIReady() {
    player = new YT.Player('thevideo', {
        playerVars: {
        'playsinline': 1
        },
        events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
    console.log("player is ready")
}

// 5. The API calls this function when the player's state changes.
//    The function indicates that when playing a video (state=1),
//    the player should play for six seconds and then stop.
var done = false;
function onPlayerStateChange(event) {
    console.log(event.data)
}

function playVideo(){
    if (navigator.onLine){
        player.playVideo();    
    }
}


function stopVideo() {
    if (navigator.onLine){
        player.stopVideo();
    }
}


function pauseVideo(){
    if (navigator.onLine){
        player.pauseVideo();
    }
}