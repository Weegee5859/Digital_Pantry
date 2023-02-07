$(document).ready(function(){
    console.log("starting...");
    // redorange #ff5d10
    // orange #ff8d00
    $("#modal").iziModal({
        headerColor: '#ff8d00',
        fullscreen: false
    });
    $("#modal2").iziModal({
        headerColor: '#ff8d00'
    });
    $("#modal3").iziModal({
        fullscreen: false,
        openFullscreen: true,
       headerColor: '#ff8d00',
        iconColor: 'black',
    });
    $("#modal4").iziModal({
        openFullscreen: true,
        headerColor: '#ff8d00'
    });
    Dropzone.autoDiscover = false;
    //Dropzone
    var myDropzone = new Dropzone("#my_dropzone", {
        autoProcessQueue: false,
        url: "/file",
        uploadMultiple: true,
        maxFiles: 99,
        acceptedFiles: ".pdf",
        addRemoveLinks: true,
        "error": function(file, message, xhr) {
            if (xhr == null) this.removeFile(file); // perhaps not remove on xhr errors
                console.log(message);
         }
    });
    // Create Recipe Window
    $(document).on('click', '#create_recipe', function (event) {
        event.preventDefault();
        $('#modal').iziModal('open');
    });
    // Test View Recipe Window
    $(document).on('click', '#edit_recipe', function (event) {
        event.preventDefault();
        $('#modal2').iziModal('open');
    });
    // View Recipe
    $(document).on('click', '#view_recipe', function (event) {
        event.preventDefault();
        viewRecipeBook()
    });
    /////////////////////////////////////////////////////////////////////
    $(document).on('click', '#swiping', function (event) {
        swipetest();
    });
    /////////////////////////////////////////////////////////////////////
    //Add Website to ul list
    $(document).on('click', 'button#create_website', function (event) {
        addWebsiteToList();
    });
    //Add Website to ul list with Enter Key
    $('input#create_website').keypress(function(e) {
        if(e.keyCode == 13) {
            addWebsiteToList();
        }
    });
    //Close Button
    $(function (){
        $(document).on("click", "#website_ul_close", function(e){
            $(this).parent().remove(); //find parent entry of clicked "X" button
        });
    });
    //Submit Websites / PDFs to be formatted in with Python
    $(document).on('click', '#submit', function (event) {
        submitRecipe()
    });

    $(document).on('input', '#mymy', function (event) {
        console.log(foodtype.currentFood)
      recipeSearch(currentFoodType=foodtype.returnCurrentFood()) 
    });
    function recipeSearch(currentFoodType="all") {
       var value = document.getElementById("mymy").value.toLowerCase();
        var container = document.getElementById("recipe_book_container");
        var container_recipes = document.getElementsByClassName("recipe_card")
        for(var i = 0; i < container_recipes.length; i++) {
            recipe = container_recipes[i]
            recipe_title = recipe.getElementsByClassName("recipe_title")[0].innerHTML.toLowerCase();
            recipe_type = container_recipes[i].getElementsByClassName("food_type")[0].innerHTML.toLowerCase()
            if (currentFoodType == 'favorite') {
                favorite_status = recipe.getElementsByClassName('favorite_banner')[0].style.display
               if (favorite_status == 'none' || !recipe_title.includes(value)) {
                recipe.style.display = 'none';
                continue
               }
               recipe.style.display = '';
               continue
            }
            //if Current tab isn't "All" and the currentFoodType doesn't match hide
            if (recipe_type != currentFoodType && currentFoodType != "all") {
                //console.log(recipe_type)
                //console.log(currentFoodType)
                recipe.style.display = 'none';
                continue;
            }
            //If Search Can't find matching text hide
            if (!recipe_title.includes(value)) {
                recipe.style.display = 'none';
                continue;
            }
            //Display Recipe
            recipe.style.display = '';
        } 
    }
    function addWebsiteToList() {
        event.preventDefault();
        var site = $('input#create_website').val()
        //Check if input is empty
        if ( site == "" ) {
            swal.fire({icon: "error", title:"Textbox Empty"})
            document.getElementById('create_website').style.border = "1px solid red";
            return false
        }
        //Check if url is valid
        if ( !validURL(site)) {
            swal.fire({icon: "error", title:"Invalid URL", text:`"${shortenString(site,length=35)}" is not a valid URL.`})
            document.getElementById('create_website').style.border = "1px solid red";
            return false
        }
        //Check if any other websites match current input
        var matching = false
        $("ul#create_website ul").each(function() {
            if ( $(this).find("p").text() == site ) {
                swal.fire({icon: "error", title:"Website Conflict", text:`"${shortenString(site,length=35)}" is already on the list.`})
                document.getElementById('create_website').style.border = "1px solid red";
                matching = true
                return false
            }
        });
        if (matching) { return false }
        //$("ul#create_website").append('<ul><p>'+site+'</p><i class="fas fa-bookmark" onclick="this.parentElement.style.display='+"'none'"+'"</i> </ul>')
        document.getElementById('create_website').style.border = "2px solid rgba(190,190,190,1)";
        $("ul#create_website").append('<ul><p>'+site+'</p><i class="far fa-times-circle" id="website_ul_close"></i> </ul>')
        $('input#create_website').val("")
        return true  
    }
    function deleteRecipe(title=null,prompt=true) {
        Swal.fire({
            icon: 'info',
            title: "Delete this Recipe?",
            text: `Are you sure you want to delete the "${title}" recipe?`,
            showCancelButton: true,
            confirmButtonColor: "#ff3c2e",
            confirmButtonText: "Delete",
            cancelButtonText: "Cancel",
            buttonsStyling: true,
            showLoaderOnConfirm: true,
            preConfirm: () => {
                $.ajax({
                    url: "/delete_recipe",
                    type: "POST",
                    contentType: "application/json",
                    dataType: 'json',
                    data: JSON.stringify({recipe_name: title}),
                    success: function (recipe_deleted) {
                        icon = "error"
                        msg = "Recipe was not Found and Could not be Deleted"
                        if (recipe_deleted) msg="Recipe was Successfully Deleted", icon = "success";
                        Swal.fire({icon: icon,text: msg}).then(function () {viewRecipeBook()} );     
                    }
                })
            }
        })
    }
    function editRecipe(title=null) {
        edit_card = document.getElementById("recipe_edit_card")
        //card.style.display = "";
        clone_edit_card = edit_card.cloneNode(true)
        name_btn = clone_edit_card.getElementsByClassName("edit_button")[0]
        name_btn.onclick = event => {
            event.stopPropagation();
            editRecipeUpdateTitle(title=title)
        }
        image_btn = clone_edit_card.getElementsByClassName("edit_button")[1]
        image_btn.onclick = event => {
            event.stopPropagation();
            editRecipeLoadImages(title=title)
        }
        type_btn = clone_edit_card.getElementsByClassName("edit_button")[2]
        type_btn.onclick = event => {
            event.stopPropagation();
            editRecipeFoodType(title=title)
        }

        Swal.fire({
            icon: 'info',
            title: `Select an option to begin editing your "${shortenString(title,length=35)}" recipe`,
            showCancelButton: true,
            showConfirmButton: false,
            cancelButtonText: "Cancel",
            html: clone_edit_card,
        })
    }
    function editRecipeUpdateTitle(title=null) {
        swal.fire({
            icon: 'info',
            title: `Rename your Recipe!`,
            text: `Update your "${shortenString(title,length=35)}" Recipe's Title`,
            input: 'text',
            inputPlaceholder: 'Enter New Recipe Name',
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: true,
            showCancelButton: true,
        })
        .then((result) => {
            if (result.value == "" || result.value == null) {
                swal.fire({
                    icon: "error",
                    title: "Invalid Value",
                    text: `Your value was either empty or invalid`,
                })
            }
            if (result.value) {
                Swal.fire({
                    icon: 'info',
                    title: "Update Recipe Title",
                    text: `Would you like to rename your Recipe to "${shortenString(result.value)}"`,
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    showConfirmButton: true,
                    showCancelButton: true,
                    showLoaderOnConfirm: true,
                    preConfirm: () => {
                        $.ajax({
                            url: "/update_recipe_title",
                            type: "POST",
                            contentType: "application/json",
                            dataType: 'json',
                            data: JSON.stringify({title: title,new_title: result.value}),
                            success: function (recipe) {
                                console.log(recipe)
                                icon = "error"
                                msg = "Unable to Rename your Recipe's Title..."
                                if (recipe) msg="Your Recipe's Title was Successfully Updated!", icon = "success";
                                if (recipe) $('#modal3').iziModal('close');
                                Swal.fire({icon: icon,text: msg}).then(function () {viewRecipeBook()} );
                            }
                        })
                    }
                });
                return true
            }
        });
    }
    function editRecipeFoodType(title=null) {
        type_element = document.getElementById('recipe_edit_type')
        clone_type_element = type_element.cloneNode(true)
        select = clone_type_element.getElementsByClassName("type_select")[0]

        Swal.fire({
            icon: 'info',
            title: `"${shortenString(title,length=25)}"`,
            text: `Please select your new food Category for your "${title}" recipe`,
            showCancelButton: true,
            showConfirmButton: true,
            cancelButtonText: "Cancel",
            html: clone_type_element,
            preConfirm: () => {
                selected_value = select.options[ select.selectedIndex ].value
                console.log(select.options[ select.selectedIndex ].value)
                $.ajax({
                    url: "/update_recipe_type",
                    type: "POST",
                    contentType: "application/json",
                    dataType: 'json',
                    data: JSON.stringify({name: title,type: selected_value}),
                    success: function (recipe) {
                        console.log(recipe)
                        icon = "error"
                        msg = "Unable to Update your Recipe's Food Type..."
                        if (recipe) msg="Your Recipe's Food Type was Successfully Updated! Please reopen this window to see your changes!", icon = "success";
                        if (recipe) $('#modal3').iziModal('close');
                        Swal.fire({icon: icon,text: msg}).then(function () {viewRecipeBook()} );
                    }
                })
            }
        })
    }
    function editRecipeLoadImages(title=null) {
        swal.fire({
            title: "Loading Recipe Images",
            text: "Please wait...",
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            showCancelButton: true,
            cancelButtonText: "Cancel",
            didOpen: () => {
                $.ajax({
                    url: "/return_recipe_image",
                    type: "POST",
                    contentType: "application/json",
                    dataType: 'json',
                    data: JSON.stringify({recipe_name: title}),
                    success: function (recipe) {
                        if (!recipe['result']) {
                            swal.fire({icon: 'error',title: "Recipe Image(s) Not Found",text: "Connection with server lost..."})
                            return false
                        }
                        if (recipe['result'].length<1) {
                            swal.fire({icon: 'warning',title: "Recipe Image(s) Not Found",text: "No Images found in the PDF"})
                            return false
                        }
                        console.log(recipe)
                        mySwipe.editRecipeViewImages(images=recipe['result'],title=title)
                    },
                    error: function (data) {
                        console.log("Could not find Recipe Images")
                        swal.fire({
                            icon: 'error',
                            title: "Recipe Image(s) Not Found",
                            text: "Connection with server lost..."
                        })
                    }
                });
                
            }
        })
    }
    var mySwipe = (function() {
        //Variables
        var mySwipeCount = 0
        let mySwipeArray = [];

        function editRecipeUpdateText() {
            clone.getElementsByClassName("mySwipeImageText")[0].innerHTML = `${mySwipeCount+1} of ${mySwipeArray.length} Images`;
        }
        function editRecipeUpdateSwipe(clone=null) {
            clone.getElementsByClassName("mySwipeImage")[0].setAttribute('src', 'data:;base64,'+mySwipeArray[mySwipeCount])
        }
        
        return {
            editRecipeReturnCurrentImageBase64: function () {
                return mySwipeArray[mySwipeCount];
            },
            editRecipeViewImages: function (images=null,title=null) {
                var count = 0
                edit_img = document.getElementById('recipe_edit_images')
                clone_edit_img = edit_img.cloneNode(true)
                mySwipeArray = images
                mySwipeCount = 0
                //current_slide = document.getElementsByClassName("mySwipeImage")
                editRecipeUpdateSwipe(clone=clone_edit_img)
                clone_edit_img.style.display = "";
                editRecipeUpdateText()

                leftArrow = clone_edit_img.getElementsByClassName("mySwipeLeftArrow")[0]
                leftArrow.onclick = event => {
                    event.stopPropagation();
                    mySwipe.editRecipeArrows(direction="left",clone=clone_edit_img)
                }

                rightArrow = clone_edit_img.getElementsByClassName("mySwipeRightArrow")[0]
                rightArrow.onclick = event => {
                    event.stopPropagation();
                    mySwipe.editRecipeArrows(direction="right",clone=clone_edit_img)
                }

                swal.fire({
                    title: `Select a new Image for your "${title}" Recipe`,
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    showConfirmButton: true,
                    showCancelButton: true,
                    cancelButtonText: "Cancel",
                    html: clone_edit_img,
                    preConfirm: () => {
                        Swal.fire({
                            title: "Are you sure you want to Update your Image?",
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            showConfirmButton: true,
                            showCancelButton: true,
                            showLoaderOnConfirm: true,
                            preConfirm: () => {
                                $.ajax({
                                    url: "/update_recipe_image",
                                    type: "POST",
                                    contentType: "application/json",
                                    dataType: 'json',
                                    data: JSON.stringify({image: mySwipe.editRecipeReturnCurrentImageBase64(),name: title}),
                                    success: function (recipe_deleted) {
                                        icon = "error"
                                        msg = "Recipe Image could not be updated..."
                                        if (recipe_deleted) msg="Recipe Image was Successfully Updated", icon = "success";
                                        Swal.fire({icon: icon,text: msg}).then(function () {viewRecipeBook()} );     
                                    }
                                })
                            }
                        })
                    }
                })
            },
            editRecipeArrows: function (direction="right",clone=null) {
                if (direction=="right") {
                    mySwipeCount+=1
                    if (mySwipeCount>mySwipeArray.length-1) mySwipeCount=0;
                    console.log("right "+mySwipeCount)
                    console.log("total "+mySwipeArray.length-1)
                    editRecipeUpdateSwipe(clone=clone)
                    editRecipeUpdateText()
                    return 0
                }
                if (direction=="left") {
                    mySwipeCount-=1
                    if (mySwipeCount<0) mySwipeCount=mySwipeArray.length-1;
                    console.log("left "+mySwipeCount)
                    console.log("total "+mySwipeArray.length-1)
                    editRecipeUpdateSwipe(clone=clone)
                    editRecipeUpdateText()
                    return 0
                }
            }
        }
    })();
    var foodtype = (function() {
        var foodTypeColorArray = ["#f7d1a3","#f4846e","#b9f7ef","#a949dd","#d68017","#d1124b","#6373e8"]
        var foodTypeArray = []
        var currentFood = "all"
        return {
            returnFoodTypeArray: function () {
                return foodTypeArray;
            },
            returnCurrentFood: function () {
                return currentFood;
            },
            updateFoodTypeArray: function(myArray=null) {
                foodTypeArray = myArray;
            },
            createFoodTab: function (text=null,color=null,type=null,icon="fas fa-pizza-slice") {
                var tab = document.createElement("div");
                tab.style.background=color;
                tab.className = "food_tab";

                tab_text = document.createElement("p")
                tab_text.innerHTML = text

                var tab_icon = document.createElement("i");
                tab_icon.className = icon

                tab.appendChild(tab_icon)
                tab.appendChild(tab_text)

                tab.onclick = event => {
                    event.stopPropagation();
                    recipeSearch(currentFoodType=type)
                    updateRecipeBookBackgroundIcons(color=color,newIcon=icon);
                    currentFood = type
                    console.log(currentFood)
                }
                document.getElementById("food_type_selector_container").appendChild(tab)
            },
            loadFoodTypes: function () {
                //Variables
                all_icon = "fas fa-utensil-spoon"
                all_color = "rgba(242, 83, 25, 1)"
                favorite_color = "rgba(250,220,20,1)";
                favorite_icon = "fas fa-star"

                //Clear Food Selection Container
                $("#food_type_selector_container").html('')
                //Update RecipeBook Background
                updateRecipeBookBackgroundIcons(color=all_color,icon=all_icon);
                //All Tab
                foodtype.createFoodTab(text="All",color=all_color,type="all",icon=all_icon)
                //Favorite Tab
                foodtype.createFoodTab(text="Favorites",color=favorite_color,type="favorite",icon=favorite_icon)

                //Load all Food Types as Tabs
                for (let i=0; i < foodTypeArray.length; i++) {
                    icon = "fas fa-pizza-slice"
                    text = foodTypeArray[i].charAt(0).toUpperCase() + foodTypeArray[i].slice(1) + "'s";
                    color = foodTypeColorArray[i];
                    type = foodTypeArray[i].toLowerCase()
                    if (text=="Dessert's") {icon="fas fa-ice-cream"}
                    if (text=="Breakfast's") {icon="fas fa-bacon"}
                    if (text=="Appetizer's") {icon="fas fa-cookie"}
                    if (text=="Drink's") {icon="fas fa-wine-glass-alt"}
                    if (text=="Meal's") {icon="fas fa-hamburger"}
                    foodtype.createFoodTab(text=text,color=color,type=type,icon=icon)
                }
            },
            loadRecipeCards: function (recipes=null) {
                //Clear currently viewable recipes
                $("#recipe_book_container").html('')
                //Create clone of recipe form
                card = document.getElementById("recipe_card")
                card.style.display = "";
                container = document.getElementById("recipe_book_container")
                //iterate through recipes (data)
                for (let i = 0; i < recipes.length; i++) {
                    clone_card = card.cloneNode(true)
                    //Title
                    clone_card.getElementsByClassName("recipe_title")[0].innerHTML = recipes[i]['title']
                    //Images
                    clone_card.getElementsByClassName("recipe_image")[0].setAttribute('src', 'data:;base64,'+recipes[i]['avatar'])
                    //Food Type
                    clone_card.getElementsByClassName("food_type")[0].innerHTML = recipes[i]['food_type'].charAt(0).toUpperCase() + recipes[i]['food_type'].slice(1);
                    clone_card.getElementsByClassName("food_type")[0].style.background = foodTypeColorArray[foodTypeArray.indexOf(recipes[i]['food_type'].toLowerCase())]
                    //Favorites
                    favorite_banner = clone_card.getElementsByClassName("favorite_banner")[0]
                    if (!recipes[i]['favorite']) favorite_banner.style.display = 'none';
                    //Open Recipe PDF
                    clone_card.onclick = event => {
                        event.stopPropagation();
                        updatePdfWindow(title=recipes[i]['title'])
                    }
                    //Get all edit_buttons
                    edit_buttons = clone_card.getElementsByClassName("recipe_option_container")[0]
                    //Close Button
                    close_card = edit_buttons.getElementsByTagName("i")[0]
                    close_card.onclick = event => {
                        event.stopPropagation();
                        deleteRecipe(title=recipes[i]['title'])
                    }
                    //Edit Button
                    edit_card = edit_buttons.getElementsByTagName("i")[1]
                    edit_card.onclick = event => {
                        event.stopPropagation();
                        editRecipe(title=recipes[i]['title'])
                    }
                    //Favorite Button
                    favorite_card = edit_buttons.getElementsByTagName("i")[2]
                    favorite_card.onclick = event => {
                        event.stopPropagation();
                        toggleRecipeFavorite(title=recipes[i]['title'],favorite_enabled=recipes[i]['favorite']);
                    }
                    container.appendChild(clone_card)
                }    
            }
        }
    })();
    function noFiles() {
        var dropzone_files = myDropzone.files.length;
        var website_list = $("ul#create_website ul").length;
        if (dropzone_files>0) {return false}
        if (website_list>0) {return false}
        return true
    }
    function toggleRecipeFavorite(title=null,favorite_enabled=null) {
        console.log(favorite_enabled)
        msg = `Would you like to remove your "${shortenString(title,length=35)}" recipe from your Favorites?`;
        btn_txt = "Remove";
        btn_color = "red";
        if (!favorite_enabled) {
            msg = `Would you like to add your "${shortenString(title,length=35)}" recipe tp your Favorites?`;
             btn_txt = "Add";
             btn_color ="#1FAB45";
        }
        swal.fire({
            icon: "info",
            title: "Update Recipe Favorites",
            text: msg,
            showCancelButton: true,
            confirmButtonColor: btn_color,
            confirmButtonText: btn_txt,
            cancelButtonText: "Cancel",
            buttonsStyling: true,
            preConfirm: () => {
                $.ajax({
                    url: "/toggle_recipe_favorite",
                    type: "POST",
                    contentType: "application/json",
                    dataType: 'json',
                    data: JSON.stringify({name: title}),
                    success: function (favorite_status) {
                        icon = "error"
                        msg = "Recipe Favorites could not be Updated"
                        if (favorite_status['result']) msg="Recipe Favorites has Successfully been Updated! Please reopen this window to see your changes!", icon = "success";
                        if (favorite_status['result']) $('#modal3').iziModal('close');
                        Swal.fire({icon: icon,text: msg}).then(function () {viewRecipeBook()});
                        console.log(favorite_enabled)
                    }
                })
                
            }
        })

    }
    function returnPdfsAsBase642() {
        pdfs = []
        const result = async(dropzone_files,value) => {
            return new Promise( (resolve, reject) => {           
                console.log("processing resolve...")
                var reader = new FileReader();
                reader.onload = function(event) {
                    var base64String = event.target.result;
                    var fileName = dropzone_files[value].name;

                    pdfs.push( {"type": "pdf",title: fileName,pdf: base64String} )
                }
                reader.readAsDataURL(dropzone_files[value]);
                resolve(pdfs)
            });   
        }
    }
        
    function returnPdfsAsBase64() {
            pdfs = []
            compile = []
            const result = async(dropzone_files,value) => {
                await new Promise( (resolve, reject) => {
                    
                        console.log("processing resolve...")
                        var reader = new FileReader();
                        reader.onload = function(event) {
                            //resolve(dropzone_files);
                            var base64String = event.target.result;
                            var fileName = dropzone_files[value].name;
                            //console.log(base64String)
                            //console.log(fileName)
                            pdfs.push({"type": "pdf",title: fileName,pdf: base64String} )
                            resolve( {"type": "website",title: fileName,pdf: base64String} );
                            //if (value == myDropzone.files.length) {
                               // console.log("all")
                           //}
                        }
                        reader.readAsDataURL(dropzone_files[value]);
                    
                });   
            }
            
            console.log("starting pdf...")
            for (const value in myDropzone.files) {
                result(myDropzone.files, value).then((myResult) => {
                    console.log(myResult)
                })
                console.log(myDropzone.files[value]['name'])
                //console.log(myDropzone.files.length)
                ///pdfs.push(result)
            }
            console.log("ALLLLL DONE")
            console.log(pdfs)
            //resolve(pdfs)
            return pdfs
    }      
    function returnWebsites() {
        var websites = [];
        $("ul#create_website ul").each(function() {
            websites.push({
                "type": "website",
                "site": $(this).find("p").text() 
            })
        });
        return websites
    }
    function shortenString(str, length, ending) {
        if (length == null) length = 100;
        if (ending == null) ending = '...';
        if (str.length > length) return str.substring(0, length - ending.length) + ending;
        return str;
    };
    function submitRecipe() {
        if (noFiles()) {
            Swal.fire({
                icon: 'warning',
                title: "No Recipes Found!",
                text: "Please add your recipe files/websites before submitting to uploading."
            })
            return false;
        }
        var my_data = []
        websitesReturned = returnWebsites()
        pdfsReturned = returnPdfsAsBase64()
        console.log( JSON.stringify(my_data) )
        Swal.fire({
            icon: 'info',
            title: "Submit Recipes?",
            text: "Are you sure you would like to submit these recipe(s)?",
            showCancelButton: true,
            confirmButtonColor: "#1FAB45",
            confirmButtonText: "Upload",
            cancelButtonText: "Cancel",
            buttonsStyling: true,
            showLoaderOnConfirm: true,
            didOpen: () => {
                swal.showLoading()
                setTimeout(() => {
                    swal.hideLoading()
                    for (let i = 0; i < websitesReturned.length; i++) {
                        my_data.push(websitesReturned[i])
                    }
                    for (let i = 0; i < pdfsReturned.length; i++) {
                        my_data.push(pdfsReturned[i])
                    }
                }, 3000)
            },
            preConfirm: () => {
                Swal.fire({
                    title: "Loading your Recipe(s)",
                    text: "Please wait...",
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    showConfirmButton: false,
                    showCancelButton: false,
                    didOpen: () => {
                        submitRecipeUpload(my_data)
                        Dropzone.forElement('#my_dropzone').removeAllFiles(true);
                        $('ul#create_website').empty()
                        swal.hideLoading()
                    }
                })
            }
        })
    }
    function submitRecipeUpload(my_data=null) {
        swal.showLoading()
        $.ajax({
            url: "/upload_automatic",
            type: "POST",
            contentType: "application/json",
            dataType: 'json',
            data: JSON.stringify(my_data),
            success: function (data) {
                if (!data['success']) {
                    Swal.fire({
                        icon: 'error',
                        title: "Recipes Submittal Overload!",
                        text: "Server is currently taking too many requests, please try again later"
                    })
                    return false
                }
                var total = data['success'].length+data['error'].length 
                console.log(total)
                console.log(data)
                if (data['error'].length>0) {
                    error_text = "The following recipes were not added...<br>"
                    for (let i = 0; i < data['error'].length; i++) {
                        error_text += `<div id="sweet_alert_error"><p id="name">${shortenString(data['error'][i]['name'],25)}</p><p id="error">${data['error'][i]['error']}</p></div>`
                    }
                    Swal.fire({
                        icon: 'info',
                        title: data['success'].length+"/"+total+" Recipes were submitted!",
                        html: error_text
                    })
                    return true  
                }
                Swal.fire({
                    icon: 'success',
                    title: "All Recipes successfully submitted!",
                    text: "Go to the Gallery to view your recipes"
                })
                //alert(data)
                //$('#preview').attr('src', "data:image/png;base64, "+data[0]['previews'][0]);
                //swal("Done!","It was succesfully sent!","success");
            },
            error: function (data) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error when submitting Recipe(s)!',
                    text: "No data returned..."
                })
            }
        });
    }
    function swipetest() {
        console.log($('.recipe_avatars .swiper-slide.swiper-slide-active').html())
        console.log($('.recipe_swiper .swiper-slide.swiper-slide-active').html())
    }
    function updatePdfWindow(title=null,prompt=true) {
        obj = document.getElementById("recipe_pdf_object")
        emb = document.getElementById("recipe_pdf_embed")
        clone_obj = obj.cloneNode(true)
        clone_emb = emb.cloneNode(true);
        //frame.setAttribute('src', `/recipe/${recipes[i]['title']}.pdf`)
        //$( "#recipe_pdf_object param[name=flashvars]" ).attr("value", `/recipe/${recipes[i]['title']}.pdf`)
        clone_obj.setAttribute('data', `/recipe/${title}.pdf`)
        clone_obj.setAttribute('id', `recipe_pdf_object`)

        clone_emb.setAttribute('ng-src', `/recipe/${title}.pdf`)
        clone_emb.setAttribute('id', `recipe_pdf_embed`)

        clone_obj.innerHTML = '';
        clone_obj.appendChild(clone_emb)

        obj.parentNode.replaceChild(clone_obj,obj)

        if (prompt) {
            $('#recipe_pdf_object').contents().find('a').click(function(event) {
                alert("demo only");

                event.preventDefault();
            });
           $('#modal4').iziModal('open'); 
        }
    }
    function updateRecipeBookBackgroundIcons(color="lightblue",newIcon="fas fa-pizza-slice") {
        icons = ["recipeIcon1","recipeIcon2","recipeIcon3","recipeIcon4","recipeIcon5"]
        recipe_book_container = document.getElementById("recipe_book_main_container")
        //Set Background Color
        recipe_book_container.style.background=color;
        //Set Icons
        for (let i = 0; i < icons.length; i++) {
            console.log(newIcon)
            console.log(icons[i])
            document.getElementById(icons[i]).className = newIcon 
        }
        console.log(newIcon)
    }
    function validURL(str) {
        var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
        '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
        '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
        '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
        return !!pattern.test(str);
    }
    function viewRecipeBook() {
        swal.fire({
            title: "Loading Recipes",
            text: "Please wait...",
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            showCancelButton: true,
            didOpen: () => {
                $.ajax({
                    url: "/return_database",
                    type: "GET",
                    success: function (recipes) {
                        foodtype.loadFoodTypes()
                        document.getElementById("mymy").value = "";
                        foodtype.loadRecipeCards(recipes)
                        //Close loading alert, open window
                        Swal.close()
                        $('#modal3').iziModal('open');
                    },
                    error: function (data) {
                        console.log("Error, no recipe data found.")
                        swal.fire({
                            title: "Recipe(s) Not Found",
                            text: "Connection with server lost..."
                        })
                    }
                });
            }
        })
    }
    //Create slide element
    var slide = document.createElement("div")
    slide.setAttribute("class", "swiper-slide")

    //Create clone of recipe form
    form = document.getElementById("recipe_form_container")
    var clone = form.cloneNode(true)

    //Append recipe form to slide element
    slide.append(clone)

    //Add finished slide to Swiper
    //swiper2.appendSlide(slide);

    var swiper = new Swiper('.recipe_avatars', {
        // Optional parameters
        observer: true,
        observeParents: true,
        direction: 'vertical',
        loop: true,
        // If we need pagination
        pagination: {
            el: '.swiper-pagination',
        },
        // Navigation arrows
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        }
    });
    var swiper2 = new Swiper('.recipe_swiper', {
        // Optional parameters
        observer: true,
        observeParents: true,
        direction: 'horizontal',
        loop: true,
        allowTouchMove: false,
        // If we need pagination
        pagination: {
            el: '.swiper-pagination',
        },
        // Navigation arrows
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        }
    });
    $( ".sampleSlider" ).slider({
        range: true,
        min: 1,
        max: 99,
        step: 1,
        values: [1, 10],
        slide: function(event, ui) {
            console.log(ui.values[0])
            const slider_container = document.getElementsByClassName("sampleSlider")
            const sliders = slider_container[0].getElementsByTagName("span")
            console.log(sliders)
            sliders[0].setAttribute("content", ui.values[0])
            sliders[0].innerHTML = ui.values[0]
            sliders[1].setAttribute("content", ui.values[0])
            //sliders[2].setAttribute("content", ui.values[0])
            $( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
        }
    });
    $.ajax({
        url: "/return_food_types",
        type: "GET",
        contentType: "application/json",
        success: function(food_types) {
            icon = "error"
            msg = "Food Types were not Found..."
            if (food_types) msg="Food Types were Successfully Loaded", icon = "success";
            //Swal.fire({icon: icon,text: food_types["types"]});
            //Update foodtype Array
            foodtype.updateFoodTypeArray(food_types["types"])
            //return foodtype Array
            foodTypeArray = foodtype.returnFoodTypeArray()
            for (let i=0; i < foodTypeArray.length; i++) {
                var opt = document.createElement("option")
                opt.innerHTML = foodTypeArray[i].charAt(0).toUpperCase() + foodTypeArray[i].slice(1);
                opt.value = foodTypeArray[i].charAt(0).toUpperCase() + foodTypeArray[i].slice(1);
                document.getElementById("type_select").appendChild(opt)
            }
        }
    })

    function initBack() {
        for (i=0; i<maxItems; i++) {
            item = document.createElement("img")
            item.className = "mainMenuIcon"
            //item.setAttribute("src", '/static/apple.png')
            var body = document.getElementById('home');

            body.append(item)
        }
        //Once initalized update variable
        allItems = document.querySelectorAll(".mainMenuIcon");
    }
    function animateBack(item=null,count=null) {
        function addFinishHandler(anim, element) {
            anim.addEventListener('finish', function(e) {
                animateBack(element);
            }, false);
        }
        colorsArray = ["orangered","purple","yellow","green"]
        food = ["carrot","grapes","banana","lemon","strawberry","burger","ice_cream","cupcake","bread","cheesecake","pear","popsicle","tomato","pizza"]
        //random num 1-20
        var randomFood = Math.floor(Math.random() * food.length)
        var rndInt = Math.floor(Math.random() * 100) + 1
        //randomX = ((window.innerWidth / 100) + rndInt)
        randomX = Math.random() * window.innerWidth-200
        randomY = ((window.innerHeight)+(rndInt*3))
        randomBegin = Math.random() * 50 + 1
        //console.log(myY)
        //console.log(window.innerHeight)
        //console.log(allItems.length)

        item.setAttribute("src", '/static/food/'+food[randomFood]+'.png')

        item.keyframes = [{
            transform: "translate3d("+randomX+"px, -"+randomBegin+"vh, 0px)",
        }, {
            opacity: 1
        }, {
            opacity: 1,
            transform: "translate3d("+randomX+"px, "+randomY+"px, 0px) rotate(359deg)"
            
        }];
        item.animProps = {
            duration: 30000 + Math.random() * 6000,
            easing: "ease-out",
            iterations: 1
        }

        var animationPlayer = item.animate(item.keyframes, item.animProps);
        addFinishHandler(animationPlayer, item);
    }

    var maxItems = 15
    var allItems = document.querySelectorAll(".mainMenuIcon");

    initBack()
    for (var i = 0; i < allItems.length; i++) {
        animateBack(allItems[i],i)
    }

    
});