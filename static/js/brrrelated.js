/*
Allows the making of cards and notes on the page
*/



async function pull_notes(book,page_number){
    /*
    returns the notes of a page
    /api/pull_notes/<book>/<page>
    data format : 
    {"success":{
            "2":[
                    {
                        "sentence_number":"2",
                        "page_number":"7",
                        "note":"This is a test"
                    }
                ],
            "15":[
                    {
                        "sentence_number":"2",
                        "page_number":"7",
                        "note":"This is a test"
                    }
            
            
                ]
            }
        }

    for (sentence_id in sentence_ids){
        for (note in sentence_id)
    
    }


    data["2"][0]["note"] -> "This is a test"
    */

    var url = `/api/pull_notes/${book}/${page_number}`
    var response = await fetch(url)
    var data = await response.json()
    console.log(data)
    return data
}



async function make_note(book,page_number,sentence_number,note){
    // takes some text, and the page number
    // api/make_note/<book>/<page>
    var url = `/api/make_note/${book}/${page_number}`
    fetch(url,{
        method:"POST",
        headers: {
            "Content-Type": "application/json",
        },
        body:JSON.stringify({
            note:note,
            sentence_number:sentence_number
        }
        )
    })

}


async function del_note(book,note_id){
    // /api/del_note/<book>/<note_id>
    var url = `/api/del_note/${book}/${note_id}`
    var response = await fetch(url)
    var data = await response.json()
    return data
}




async function pull_cards(book,page_number){
    //get the cards that were made on a page
    // /api/pull_cards/<book>/<page_number>
    var url = `/api/pull_cards/${book}/${page_number}`

    var response = await fetch(url)
    var data =  await response.json()
    return data
}


async function update_card(book,card_id,front_side_text,back_side_text){
    // pushes the update to the server, once it goes through it updates the card in the browser
    // /api/update_card/<book>/card_id
    var url = `/api/update_card/${book}/${card_id}`
    var response = await fetch(url,{
        method:"POST",
        body:JSON.stringify(
            {
                "front_side_text":front_side_text,
                "back_side_text":back_side_text
            }
        )
    })

    var data = await response.json()
    return data
}



async function make_card(book,page_number,front_side_text,back_side_text){
    // /api/make_new_card/<book>/<page_number>
    var url = `/api/make_new_card/${book}/${page_number}`

    var response = await fetch(url,{
        method:"POST",
        body:JSON.stringify(
            {
                "fron_side_text":front_side_text,
                "back_side_text":back_side_text
            }
        )
    })
    var data = await response.json()
    return data
}



async function del_card(book,card_id){
    // /api/delele_card/<book>/<card_id>
    var url = `/api/delete_card/${book}/${card_id}`

    var response = await fetch(url)
    var data = await response.json()

    return data
}



async function update_note(book,note_id,note){
    // sends the new note data to the server
    // /api/update_note/<book>/<note_id>

    var url = `/api/update_note/${book}/${note_id}`
    
    await fetch(url,{
        method:"POST",
        body:JSON.stringify(
            {
                note:note
            }
        )
    })

}