/*
Handles adding notes to the side pannel
*/


async function reload_notes(){
    var the_area = document.getElementById("notes_container")
    the_area.innerHTML = "";
    await add_note_cards("notes_container",bookname,current_page)
}

async function add_note_cards(area_id,book,page_number){
    var the_area = document.getElementById(area_id)
    var response = await pull_notes(book,page_number)
    var data = await response["success"]

    if (data == false){
        console.log("backend could not process your request.")
    }

    var sentence_keys = Object.keys(data)

    for (key in sentence_keys){
        var the_key = sentence_keys[key]
        console.log("this is the key:",the_key)
        var notes = data[the_key]
        console.log("these are the notes",notes)
        notes.forEach((note) => {
            console.log("this is the note:",note["note"])


            var note_card = document.createElement("div")
            var note_id = note["note_id"]
            note_card.id = `notes_id_${note_id}`
            note_card.classList.add("card", "body-color", "align-items-center", "border-bottom","border-top", "border-light", "border-1", "rounded-1", "border-opacity-25")
            console.log(note["note"])

            var note_card_body = document.createElement("div")
            note_card_body.classList.add("card-body", "text-light", "mx-1")

            var note_card_body_flex_container = document.createElement("div")
            note_card_body_flex_container.classList.add("d-flex", "justify-content-around", "align-items-center")

            var note_card_text_container = document.createElement("p")
            note_card_text_container.classList.add("mx-1")
            note_card_text_container.id = `note_card_text_container_${note_id}`


            note_card_text_container.textContent = note["note"]

            var note_card_edit_button = document.createElement("button")
            note_card_edit_button.classList.add("btn","btn-sm","text-light")
            note_card_edit_button.onclick = ()=>{
                // we want to load the data, open the dialog
                //console.log("[ NO OPENING FUNC DEFINED YET ]")
                open_edit_note_dialog(note_id,note["note"]) // TODO: define this function 
            }

            var note_card_delete_btn = document.createElement("button")
            note_card_delete_btn.classList.add("btn","btn-sm","text-light")
            note_card_delete_btn.innerHTML = `<i class="bi bi-trash h5"></i>`

            note_card_delete_btn.onclick = async ()=>{
                await del_note(bookname,note_id)
                close_make_edit_note_dialog()
                reload_notes()
            }


            note_card_edit_button.innerHTML = `<i class="bi bi-pen h5"></i>`
            // adding it all together
            note_card.append(note_card_body)
            note_card_body.append(note_card_body_flex_container)
            note_card_body_flex_container.append(note_card_text_container)
            note_card_body_flex_container.append(note_card_edit_button)
            note_card_body_flex_container.append(note_card_delete_btn)
            the_area.append(note_card)
            
        })    }
            
        };



function close_make_edit_note_dialog(){
    notes_modal_dialog = document.getElementById("notes_modal_dialog")
    keyboard_in_use = false
    notes_modal_dialog.close()
    
}


function open_make_note_dialog(){
    var notes_modal = document.getElementById("notes_modal_dialog")
    

    var make_or_edit_note_btn = document.getElementById("make_or_edit_note_btn")
    var notes_text_area = document.getElementById("note_modal_text_area")
    notes_text_area.value = "";

    make_or_edit_note_btn.onclick = async ()=>{
        await make_note(bookname,current_page,current_sentence,notes_text_area.value),
        close_make_edit_note_dialog()
        reload_notes()
    }
    keyboard_in_use = true
    notes_modal.showModal();
    console.log("implement opening the note edit dialog")
}


function open_edit_note_dialog(note_id,note){
    var notes_modal = document.getElementById("notes_modal_dialog")
    var make_or_edit_note_btn = document.getElementById("make_or_edit_note_btn")
    var notes_text_area = document.getElementById("note_modal_text_area")
    notes_text_area.value = note

    make_or_edit_note_btn.onclick = async ()=>{
        await update_note(bookname,note_id,notes_text_area.value)     
        close_make_edit_note_dialog()
        reload_notes()
    }
    keyboard_in_use = true
    notes_modal.showModal();
    console.log("implement opening the note edit dialog")

}