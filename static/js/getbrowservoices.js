    
    
function getbrowservoices(selectid){
    const voices = synth.getVoices();
    var voiceSelect = document.getElementById(selectid)
        for (const voice of voices) {
            console.log(voice)
            const option = document.createElement("option");
            option.textContent = `${voice.name} (${voice.lang})`;
            option.value = voice.name
            option.setAttribute("data-lang", voice.lang);
            option.setAttribute("data-name", voice.name);
            voiceSelect.appendChild(option);
        }
}
//  getbrwoservoices