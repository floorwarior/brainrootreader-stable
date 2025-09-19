


function break_page(page_data){
    let words = page_data.split(" ")
    return words
}


function broken_page_boundary_hook(word){
    // the on boundary logic here
    console.log(word)
}


function on_broken_page_end(){
    //
    console.log("page is over")
}



function read_broken_page(speak_synth,page_data){
    page_data_words = break_page(page_data)
    for (let i = 0; i < page_data_words.length; i++){
        let word = page_data_words[i]
        var utterance = new SpeechSynthesisUtterance(word)
        utterance.rate = 1.2
        utterance.lang = selected_lang
            speak_synth.speak(utterance)
            utterance.onstart = ()=>{
                broken_page_boundary_hook(word)

            }
        if (i == page_data_words.length){
            on_broken_page_end()
        }
    }
}