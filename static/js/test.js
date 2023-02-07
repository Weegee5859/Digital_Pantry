function returnPdfsAsBase64() {
    pdfs = []
    compile = []
    
    for (const value in myDropzone.files) {
        var reader = new FileReader();
        reader.readAsDataURL(myDropzone.files[value]);
        console.log(myDropzone.files[value]['name'])
        console.log(myDropzone.files.length)
        console.log(value)
        await getDropzoneFile(myDropzone.files,value,pdfs);
        console.log("--done--")
    }
    
    function getDropzoneFile(dropzone_files,value,pdfs) {
        return new Promise((resolve, reject)=>{
            await reader.onload = function(event) {
                var base64String = event.target.result;
                var fileName = dropzone_files[value].name;
                pdfs.push({name: fileName,data: base64String});
                console.log(fileName)
                resolve();
            }
        })
    }

    setTimeout(function() {
        console.log("---pdfs---")
        console.log(pdfs)
        console.log("---stri---")
        console.log(JSON.stringify(pdfs))
        return pdfs;   
    }, 1000)
    return null
    
}