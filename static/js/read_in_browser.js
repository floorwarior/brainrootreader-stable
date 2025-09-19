const synth = window.speechSynthesis;
function monkey_patch_reader(sentence,pausebtn){
    var funcplaceholder = pausebtn.onclick
    pausebtn.onclick = ()=>{
        if (!synth.paused){
            console.log("synth was not paused")
            synth.cancel()
            pauseaudio = true
            pausebtn.onclick = funcplaceholder
            //synth.pause()
        }
    }
    return new Promise((resolve,reject)=>{
        var utterThis = new SpeechSynthesisUtterance(sentence);
        utterThis.voice = localStorage.getItem("brainrootreader-browser-voice")
        synth.speak(utterThis);
        utterThis.onend = ()=>{
            pausebtn.onclick = funcplaceholder
            resolve(true)
        }
        utterThis.onerror = ()=>{
            pausebtn.onclick = funcplaceholder
            reject()
        } 
    })
}
