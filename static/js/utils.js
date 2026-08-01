

class Keys{

    async getkey(key){
        var url = `/api_v2/getkey?key=${key}`
        var response = await fetch(url,{
            method:"GET",
        })
        var result = await response.json()
        return result
    }


    async getkeys(){
        var url = `/api_v2/getkeys`
        var response = await fetch(url,{
            method:"GET"})
        var data = await  response.json()
        return data
    }

    async setkey(key,value){
        var url = `/api_v2/setkey`
        var data = {
            key:key,
            value:value,
        }
        var res =  await fetch(url,{
            method:"POST",
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify(data)
        })
        var result = await res.json()
        return result

    }

}




class VisitedPageTracker{


    constructor(safe_bookname){
        this.book_id = safe_bookname
        this.kv = new Keys()
    }

    async getlastvisited(){
        //var last_visited = JSON.parse(localStorage.getItem(`last-visited-${this.book_id}`))
        var last_visited = await this.kv.getkey(`last-visited-${this.book_id}`)
        console.log(last_visited)
        return last_visited
    }

    setlastvisited(page){
        //localStorage.setItem(`last-visited-${this.book_id}`,JSON.stringify(page))
        this.kv.setkey(`last-visited-${this.book_id}`,JSON.stringify(page))

    }

    setbookmark(page){
        //localStorage.setItem(`bookmark-${this.book_id}`,JSON.stringify(page))
        this.kv.setkey(`bookmark-${this.book_id}`,JSON.stringify(page))
        return
    }

    async getbookmark(){
        //var bookmark = localStorage.getItem(`bookmark-${this.book_id}`)
        var bookmark = await this.kv.getkey(`bookmark-${this.book_id}`)
        console.log(bookmark)
        return bookmark
    }
}



class TrackPage{
    constructor(starting_page,page_indicator1,page_indicator2){
        this.current_page = starting_page
        this.page_indicator1 = page_indicator1
        this.page_indicator2 = page_indicator2
        this.callbacks = {}
    }


    async onchange(callback){
       // can be used to dispatch the new current page to callbacks
        var uuid = crypto.randomUUID()
        this.callbacks[uuid] = callback
    }

    async cancelcallback(uuid){
        delete this.callbacks[uuid]
    }


    getnext(){
        this.current_page++
        this.page_indicator1.textContent = `[${this.current_page}]`
        this.page_indicator2.textContent = `Current Page: ${this.current_page}`

        Object.keys(this.callbacks).forEach(key=>{
            this.callbacks[key](this.current_page)
        })

        return this.current_page
    }

    getcurrent(){
        return this.current_page
    }




}


class AudioCache{
    //makes sure the next sentence is cashed before you get to it so the reading is much smoother
    audios = []
    current = 0
    current_to_use = 0
    inuse = {}
    onwatch = {}

    constructor(size){
        // makes a cache 
        for (let i = 0; i < size; i++){
            var aud = document.createElement("audio")
            aud.setAttribute("aria-hidden",true)
            aud.classList.add("hidden")
            this.audios.push(aud)
            document.body.append(aud)
            this.inuse[i.toString()] = false // making sure that after we used an audio we set it to false and setting it to true on fill 
        }
    }



    watch(callback){
        // watch for changes in the AudioCache, every callback recives the class instance
        var id = crypto.randomUUID()
        this.onwatch[id] = callback
        return id
    }

    unwatch(id){
        delete this.onwatch[id]
    }

    _onchange(){
        Object.keys(this.onwatch).forEach(key=>{
            var callback = this.onwatch[key]
            callback(this)
        })
    }

    getnextempty(){
        // returns the next index that should be free
        console.log("getting empty audio el")
        if (this.current_to_use >= this.audios.length){
            this.current_to_use = 0
        }

        if (this.inuse[this.current_to_use.toString()]){
            throw (new Error(
                "you have no free audio"
            ))
        }
        var crnt= this.current_to_use
        this.inuse[crnt.toString()] = true
        this.current_to_use++
        console.log(crnt)
        this._onchange() // calls all listeners
        return this.audios[crnt]
    }

    getnextfull(){
        // returns the next audio object that is full
        console.log("getting full audio el")
        if (this.current >= this.audios.length){
            this.current = 0
        }

        if (!this.inuse[this.current.toString()]){
            throw (new Error(
                "Threre is no audio loaded ahead"
            ))
        }

        var tmp = this.current
        this.current++
        this._onchange()
        return {
            "index":tmp,
            "audio":this.audios[tmp]
        }
        //this way the user can call free
    }

    any(){
        // returns true if any audio is already cached 
        var f = false
        Object.keys(this.inuse).forEach(key=>{
            if (this.inuse[key]){
                f = true
            }
        })

        return f
    }


    clear(){
        Object.keys(this.inuse).forEach(key=>{
            this.inuse[key] = false
        })
        this._onchange()
    }


    free(idx){
        this.inuse[idx] = false
        this._onchange()
    }
}


class BookReader{

    constructor(safe_bookname,
            page,audio_elem,
            sentences_tab,
            sentence_display,
            getautoscroll,
            bookmark
            )
                {
        this.safe_bookname = safe_bookname
        this.current_page = page
        this.audio_elem = audio_elem
        this.sentences_tab = sentences_tab
        this.sentence_display = sentence_display
        this.getautoscroll = getautoscroll // checks if the sentence part is hovered and should not be scrollable
        this.bookmark = bookmark
        
        this.component = NaN

        // cache
        this.audio_cache = new AudioCache(2)
    }


    async generate(page,blocking){
        var url = `/api/makepage/${this.safe_bookname}/${page}`
        if (blocking){
            url = url + '?blocking=1'
        }
        try{
            var response = await fetch(url,{
                method:"GET"
            })
            var data = await response.json()
            return data
        }
        catch(e){
            console.log(e)
            return false
        }
    }





    set_sentence_data(data){
        console.log("setting setence data")
        this.sentences_tab.innerHTML = ""
        //return
        for (let i = 0; i < Object.keys(data.sentence_data).length ; i++){
            var sentence = data.sentence_data[i]
            var sent = document.createElement("p")
            sent.setAttribute("data-id",i)
            sent.textContent = sentence.sentence
            this.sentences_tab.append(
                sent
            )
        }
    }

    set_current_sentece(sentence){
        this.sentence_display.textContent = sentence
    }


    scroll_to_sentence(index){
        if (!this.getautoscroll()){
            return
        }
        // Scope?
        var elem = document.querySelector(`[data-id="${index}"]`)
        // TODO figure out how to show the sentence better
        elem.scrollIntoView({behavior:"smooth"})
    }





    async read_data(data){
        console.log("read data called")
        //this.audio_cache.clear()
        for (let i = 0; i < Object.keys(data["sentence_data"]).length; i++){
            var sentence = data.sentence_data[i]
            console.log("reading sentence:",sentence)
            setTimeout(()=>{this.scroll_to_sentence(i)},0)
            this.set_current_sentece(sentence.sentence)

            if (!this.audio_cache.any()){
                this.audio_cache.getnextempty().setAttribute("src",sentence.filename)
            }

            //this.audio_elem.setAttribute("src",sentence.filename)
            var aud_cache = this.audio_cache.getnextfull()
            this.audio_elem = aud_cache.audio
            this.audio_elem.volume = this.component.volume

            // try getting the next also
            if(i+1 < Object.keys(data["sentence_data"]).length){
                setTimeout(()=>{
                    var n = this.audio_cache.getnextempty()
                    n.setAttribute("src",data.sentence_data[i+1].filename)
                },500)
            }

            // instead of setting the audio src we could just get the current audio and add the eventlisteners
            await new Promise((resolve,reject)=>{
                this.audio_elem.addEventListener("ended",()=>{
                    console.log("finished playing the audio")
                    resolve()
                },{once:true})
                console.log("playing the audio now")
                try{
                    this.audio_elem.play()
                }
                catch(e){
                    console.log(e)
                    reject()
                }

            })
            this.audio_cache.free(aud_cache.index)
        }
    }

    async read(){
        while (true){
            setTimeout(()=>{
                this.component.setState("generating")
                //console.log("this somehow bugs out")
            },0)
            var current_p = this.current_page.getcurrent()
            var data = await this.generate(current_p,true)
            console.log(data)
            if (data.success == false){
                // if the next sentence errors out we pause the reading
                this.component.setState("paused")
                if(data.error == undefined){
                    //document.body.innerHTML = "<h1 class='test-center text-3xl text-gray-11 font-semibold'>The End</h1>"
                    this.set_current_sentece("The End")
                }
                else{
                    this.set_current_sentece(data.error)
                }
                return
            } 
            console.log(data.sentence_data)
            setTimeout(()=>{
                this.component.setState("playing")
            })
            this.bookmark.setlastvisited(current_p)
            this.generate(this.current_page.getcurrent()+2,false)
            this.generate(this.current_page.getcurrent()+1,false)
            setTimeout(()=>{this.set_sentence_data(data)},0)
            //this.set_sentence_data(data)
            await this.read_data(data)
            this.current_page.getnext()
        }
    }


    pause(){
        this.audio_elem.pause()
    }

}





/*
Allows you to register a key and add a handler for it
usege:


register_key_event({
    key:"+",
    key_code:"",
    callback(){
        console.log("+ pressed")
    }
})
*/
function register_key_event(data){
    window.addEventListener("keypress",async (event)=>{
        var the_key = event.key
        var key_code = event.keyCode
        //console.log(the_key)
        //console.log(key_code)
        var active = document.activeElement
        if (active.hasAttribute("data-no-keys")){
            return
        }
        if (the_key == data.key || key_code == data.key_code){
            data.callback()
        }
    })
}


class Configure{


    async cfg(){
        var url = `/api_v2/config`
        var res = await fetch(url)
        var data = await res.json()
        return data
    }


    async setconfigfield(dotnotation,value){
        var url = "/api_v2/setconfig"
        var data = {
            dotnotation:dotnotation,
            value:value,
        }
        var res =  await fetch(url,{
            method:"POST",
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify(data)
        })
    }


    async setconfigfields(data){
        // Accepts data like this:
        // data = {"app.port":5003,"app.host":"localhost"}
        var url = "/api_v2/setconfigs"
        var res = fetch(url,
            {
                method:"POST",
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify(data)
            }
        )
    }


    async getconfigfield(dotnotation){
        var url = `/api_v2/getconfig/${dotnotation}`
        var res = await fetch(url)
        var data = await res.json()
        console.log(data)
        return data
    }
}



async function reload_backend(){
    // calls up the backend and does a full reload
    var url = `/api/reload_app`
    try{
        var res = await fetch(url,
            {method:"POST"}
        )
        var data = res.json()
        return data
    }
    catch (error){
        console.log(error)
        return false
    }
}

async function stop_app(){
    // calls server kill to stop the backend
    var url = `/api/killserver`
    await fetch(url,{
        method:"POST"
    })
    window.location = "api/killserver"
}

class InstallTools{

    async check_reader(reader){
        /* 
        takes a reader and checks if it is intalled
        */

        var url = `/api_v2/is_installed`
        var data
        try{
            var response = await fetch(url,{
                method:"POST",
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify(
                    {
                        "reader":reader
                    }
                )
            })
            data = await response.json()
        }
        catch (e){
            console.log(e)
        }
        return data
    }

    async install_reader(reader,where){
        var url = `/api_v2/install_reader`
        var data
        try{
            var res = await fetch(url,{
                method:"POST",
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify(
                    {
                        "reader":reader,
                        "where":where
                    }
                )
            })
            data = await res.json()
        }
        catch(e){
            console.log(e)
            return e
        }
        return data
    }

    async remove_reader(reader,from){
        var url = `/api_v2/uninstall_reader`
        var data
        try{
            var res = await fetch(url,{
                method:"POST",
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify({
                    "reader":reader,
                    "from":from
                })
            })
            data = await res.json()

        }
        catch (e){
            console.log(e)
        }
        return data
    }

}

class Notes{

    constructor(book_id){
        this.book_id = book_id
    }

    async getnotes(page){
        var url = "/api_v2/getnotes"
        try{
            var res = await fetch(
                url,{
                    method:"POST",
                    body:JSON.stringify(
                        {
                            "book_id":this.book_id,
                            "page":page
                        }
                    ),
                    headers:{
                        'Content-Type':'application/json'
                    },
                }
            )
            var r = await res.json()
            return r // should be a list of notes
        }
        catch(e){
            console.log(e)
            return false
        }
    }



    async setnote(data){
        var url = "/api_v2/setnote"
        try{
            var res = await fetch(url,{
                method:"POST",
                body:JSON.stringify(
                    {
                        "book_id":this.book_id,
                        "note":data.note,
                        "page":data.page
                    }
                ),
                headers:{
                    'Content-Type':'application/json'
                },
            })
            var r = await res.json()
            return r
        }
        catch (e){
            console.log(e)
            return false
        }
    }

    async update_note(data){
        var url = "/api_v2/updatenote"
        try{
            var res = await fetch(url,{
                headers:{
                    'Content-Type':'application/json'
                },
                method:"POST",
                body:JSON.stringify(
                    {   
                        "note":data.note,
                        "note_id":data.note_id
                    }
                )
            })
            var r = res.json()
            return r
        }
        catch (e){
            console.log(e)
            return false
        }
    }


    async del_note(note_id){
        var url = "/api_v2/deletenote"
        try{
            var res = await fetch(url,{
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify(
                    {
                        "note_id":note_id
                    }
                ),
                method:"POST"
            })
            var data = await res.json()
            return data
        }
        catch (e){
            console.log(e)
            return false
        }
    }
}


class Cards{

    constructor(book_id){
        this.book_id = book_id
    }


    async setcard(data){
        var url = "/api_v2/setcard"
        try{
            var res = await fetch(url,{
                method:"POST",
                body:JSON.stringify(
                    {
                        "page":data.page,
                        "book_id":this.book_id,
                        "question":data.question,
                        "answer":data.answer
                    }
                ),
                headers:{
                    'Content-Type':'application/json'
                }
            })
            return await res.json()
        }
        catch (e){
            console.log(e)
            return false
        }
    }

    async update_card(data){
        var url = "/api_v2/updatecard"
        try{
            var res = await fetch(url,{
                method:"POST",
                body:JSON.stringify(
                    {
                        "id":data.id,
                        "question":data.question,
                        "answer":data.answer
                    }
                ),
                headers:{
                    'Content-Type':'application/json'
                }
            })

        }
        catch(e){
            console.log(e)
        }
    }

    async del_card(card_id){
        var url = "/api_v2/deletecard"
        try{
            var res = await fetch(url,{
                method:"POST",
                body:JSON.stringify({
                    "card_id":card_id
                }),
                headers:{
                    'Content-Type':'application/json'
                }
            })
            var r = await res.json()
            return r
        }
        catch(e){
            console.log(e)
            return false
        }
    }

    async getcards(page){
        var url = "/api_v2/getcards"
        try{
            var res = await fetch(url,{
                method:"POST",
                body:JSON.stringify({"book_id":this.book_id,"page":page}),
                headers:{
                    'Content-Type':'application/json'
                }
            })
            var data = await res.json()
            return data
        }
        catch(e){
            console.log(e)
            return false
        }
    }
}



class AccessibilitySupport{
    read_text(text){
        var url = "/api/speak"
        fetch(url,{
            method:"POST",
            body:JSON.stringify(
                {
                    "text":text
                }
            ),headers:{
                'Content-Type':'application/json'
            }
        })
    }
}


