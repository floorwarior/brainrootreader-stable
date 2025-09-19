function change_default_video(that){
    localStorage.setItem("prefered-video",that.value)
    console.log(that.value)
}

function set_video_source(elem_id){
    var elem = document.getElementById(elem_id)
    var video_link = localStorage.getItem("prefered-video")

    if (video_link[0] === "."){
        elem.id = ""
        var new_elem = document.createElement("video")
        new_elem.classList.add("cover-page-video")
        new_elem.setAttribute("autoplay",true)
        new_elem.setAttribute("loop",true)
        new_elem.setAttribute("muted",true)
        new_elem.id = "thevideo"
        new_elem.setAttribute("src",video_link)
        elem.replaceWith(new_elem)
    }
    else{
        elem.id = ""
        var new_elem = document.createElement("iframe")
        new_elem.classList.add("iframe-video-sizing")
       
        new_elem.id = "thevideo"
        new_elem.setAttribute("src",video_link)
        elem.replaceWith(new_elem) 
    }
}