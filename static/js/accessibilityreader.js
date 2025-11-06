//reads any items aria-label



async function read_with_backend(text){
    await fetch("/api/speak",{
        method:"POST",
        body:JSON.stringify({
            "text":text
        })
    })
}




window.addEventListener("keypress",(event)=>{
    // 


    var the_key = event.key

    if (the_key == "r"){
        var current_text = document.activeElement.getAttribute("aria-label")
        if (current_text){
            read_with_backend(current_text)
        }
    }
})
