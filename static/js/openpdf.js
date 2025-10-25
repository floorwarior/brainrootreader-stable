// opens the pdf you are reading to the page your are currently on it also automaticly changes the page you are on




function openpdf(bookname,page){
    if ("pdf" in bookname){
        window.open(`http://localhost:5003/uploads/${bookname}#page=${page}`,"pdfviewer")
    }
}