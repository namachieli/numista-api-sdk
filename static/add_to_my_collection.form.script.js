/* This file is for reference purposes, scraped from live on Mar 14 2022 */
function save_collection(add_again) {
    $('.modal .button').attr("disabled", "disabled");
    let collectibleType = $('#collec_form_ct').val();
    let coin = $('#collec_form_type').val();
    let version = $('#collec_form_coin').val();
    $.post('/vous/save_collection.php', {
        'coinId':       coin,
        'version':      version,
        'item':         $('#collec_form_item').val(),
        'quantity':     $('#collec_form_quantity').val(),
        'grade':        $('input[name=collec_form_grade]:checked').val(),
        'value':        $('#collec_form_value').val(),
        'comment':      $('#collec_form_comment').val(),
        'forSwap':      $('input[name=collec_form_swap]:checked').val(),
        'swapComment':  $('#collec_form_swap_comment').val(),
        'section':      $('#collec_form_section').val(),
        'pictures':     $('#collec_form_pictures').val()})
    .done(function(response) {
        if (response.substring(0, 5)==='LOGIN') {
            alert("You were disconnected. Please log in and try again.");
            $('.modal .button').removeAttr("disabled");
        }
        else if (response.substring(0, 3)==='ERR') {
            alert("An error occurred. Please try again.");
            $('.modal .button').removeAttr("disabled");
        }
        else {
            if (version && version!=='') {
                $('#collec_line' + version).html(response);
                version = parseInt(version)
            }
            else {
                $('#collec_line0_' + coin).html(response);
                show_undetermined_line(coin);
                version = null;
            }
            activate_thumbnails();
            refresh_collection_count(coin);
            collec_modal_close();
            if (add_again) collec_modal_new(collectibleType, coin, version);
        }
    })
    .fail(function() {
        alert("An error occurred. Please try again.");
        $('.modal .button').removeAttr("disabled");
    });
}

function refresh_collection_count(coin) {
    if ($('#affichage_qc' + coin).length) {
        let collec_count = 0;
        $('.collec_q.col' + coin).each(function() { collec_count += parseInt($(this).text()); });
        $('#affichage_qc' + coin).text(collec_count);
    }
    if ($('#affichage_qe' + coin).length) {
        let swap_count = 0;
        $('.collec_q.swa' + coin).each(function() { swap_count += parseInt($(this).text()); });
        $('#affichage_qe' + coin).text(swap_count);
        if (swap_count) $('#affichage_qe_cadre' + coin).css('display', 'inline');
    }
    if ($('#affichage_qt' + coin).length) {
        let total_count = 0;
        $('.collec_q.col' + coin).each(function() { total_count += parseInt($(this).text()); });
        $('.collec_q.swa' + coin).each(function() { total_count += parseInt($(this).text()); });
        $('#affichage_qt' + coin).text(total_count);
    }
}

function delete_collection_item(item, version, coin) {
    if(!confirm("Do you wish to remove this item from your collection?")) return;
    $.post('/vous/remove_collection_item.php', {'item':item, 'version':version, 'collectible':coin})
    .done(function(response) {
        if (response.substring(0, 5)==='LOGIN') {
            alert("You were disconnected. Please log in and try again.");
        }
        else if (response.substring(0, 3)==='ERR') {
            alert("An error occurred. Please try again.");
        }
        else {
            if (version) $('#collec_line' + version).html(response);
            else $('#collec_line0_' + coin).html(response);
            refresh_collection_count(coin);
        }
    })
    .fail(function() {
        alert("An error occurred. Please try again.");
    });
}

function show_undetermined_line(collectible_id) {
    $('.undetermined_line' + collectible_id).css('display', '');
    $('.undetermined_line' + collectible_id + ' button').attr('tabindex', '0');
    $('.undetermined_filler' + collectible_id).remove();
}

function collec_modal_close() {
    $('.modal').remove();
}

function htmlEncode(value) {
    return value.replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function collec_modal_new(collectibleType, coinId, selected_version, item, quantity, grade, forSwap, value, comment, swapComment, section, pictures) {
    selected_version = typeof selected_version!=='undefined'? selected_version: null;
    item = typeof item!=='undefined'? item: null;
    quantity = typeof quantity!=='undefined'? quantity: null;
    grade = typeof grade!=='undefined'? grade: null;
    forSwap = typeof forSwap!=='undefined'? forSwap: null;
    value = typeof value!=='undefined'? value: null;
    comment = typeof comment!=='undefined'? comment: null;    
    swapComment = typeof swapComment!=='undefined'? swapComment: null;
            section = (typeof section!=='undefined' && section!=0)? section: 43707;
            pictures = typeof pictures!=='undefined'? pictures: null;
    let modal = document.createElement('section');
    let action = item==null?'create':'edit';
    modal.className = 'modal';
    let modal_title = action==='create'? 'Add to my collection': 'Edit items in my collection';

    let content = '<div class="modal-content" role="dialog" aria-labelledby="modal_title" aria-modal="true"><form action="" method="get">\
        <input type="button" class="close" title="Close" onclick="collec_modal_close();" value="&times" />\
        <header id="modal_title">' + modal_title + '</header>\
        \
        <div id="collec_form">\
        <input type="hidden" name="collec_form_ct" id="collec_form_ct" value="' + collectibleType +'">\
        <input type="hidden" name="collec_form_type" id="collec_form_type" value="' + coinId +'">\
            <input type="hidden" name="collec_form_item" id="collec_form_item" value="' + (item==null?'':item) + '">';
        
    if (typeof coin_data!='undefined') {
        let versions = coin_data['c'+coinId].versions
        content = content + '\
            <div>\
                <label for="collec_form_coin">' + (collectibleType==='coin'?'Coin:':(collectibleType==='banknote'?'Banknote:':'Version:')) + '</label>\
                <span class="form_value">\
                    <select name="collec_form_coin" id="collec_form_coin"';
    if (action==='edit') content = content + ' disabled="disabled"';
    content = content + '>';
    if (versions.length > 1) {
        let selected = selected_version==null? 'selected="selected"': '';
        content = content  + '<option value="" ' + selected + '>Undetermined</option>';
    }
    for (let i = 0; i < versions.length; i++) {
        let version = versions[i];
        let selected = version[0]===selected_version? 'selected="selected"': '';
        content = content  + '<option value="' + version[0] + '" ' + selected + '>' + version[1] + ' ' + version[2] + ' ' + version[3] +  '</option>';
    }
    content = content + '\
                    </select>\
                </span>\
            </div>';
    }

    else {
        content = content + '\
            <input type="hidden" name="collec_form_coin" id="collec_form_coin" value="' + selected_version + '" />';
    }

    content = content + '\
            <div>\
                <span class="form_name">Grade:</span>\
                <span class="form_value">\
                    <input type="radio" name="collec_form_grade" value="ab" id="collec_form_grade_ab"' + (grade==='ab'?' checked="checked"':'') + ' /><label for="collec_form_grade_ab"><abbr title="' + (collectibleType==='coin'?'Good':(collectibleType==='banknote'?'Good':'Good')) + '">' + (collectibleType==='coin'?'G':(collectibleType==='banknote'?'G':'G')) + '</abbr></label>\<input type="radio" name="collec_form_grade" value="b" id="collec_form_grade_b"' + (grade==='b'?' checked="checked"':'') + ' /><label for="collec_form_grade_b"><abbr title="' + (collectibleType==='coin'?'Very good':(collectibleType==='banknote'?'Very good':'Very good')) + '">' + (collectibleType==='coin'?'VG':(collectibleType==='banknote'?'VG':'VG')) + '</abbr></label>\<input type="radio" name="collec_form_grade" value="tb" id="collec_form_grade_tb"' + (grade==='tb'?' checked="checked"':'') + ' /><label for="collec_form_grade_tb"><abbr title="' + (collectibleType==='coin'?'Fine':(collectibleType==='banknote'?'Fine':'Fine')) + '">' + (collectibleType==='coin'?'F':(collectibleType==='banknote'?'F':'F')) + '</abbr></label>\<input type="radio" name="collec_form_grade" value="ttb" id="collec_form_grade_ttb"' + (grade==='ttb'?' checked="checked"':'') + ' /><label for="collec_form_grade_ttb"><abbr title="' + (collectibleType==='coin'?'Very Fine':(collectibleType==='banknote'?'Very Fine':'Very Fine')) + '">' + (collectibleType==='coin'?'VF':(collectibleType==='banknote'?'VF':'VF')) + '</abbr></label>\<input type="radio" name="collec_form_grade" value="sup" id="collec_form_grade_sup"' + (grade==='sup'?' checked="checked"':'') + ' /><label for="collec_form_grade_sup"><abbr title="' + (collectibleType==='coin'?'Extremely Fine':(collectibleType==='banknote'?'Extremely Fine':'Extremely Fine')) + '">' + (collectibleType==='coin'?'XF':(collectibleType==='banknote'?'XF':'XF')) + '</abbr></label>\<input type="radio" name="collec_form_grade" value="spl" id="collec_form_grade_spl"' + (grade==='spl'?' checked="checked"':'') + ' /><label for="collec_form_grade_spl"><abbr title="' + (collectibleType==='coin'?'Almost Uncirculated':(collectibleType==='banknote'?'Almost Uncirculated':'Almost Uncirculated')) + '">' + (collectibleType==='coin'?'AU':(collectibleType==='banknote'?'AU':'AU')) + '</abbr></label>\<input type="radio" name="collec_form_grade" value="fdc" id="collec_form_grade_fdc"' + (grade==='fdc'?' checked="checked"':'') + ' /><label for="collec_form_grade_fdc"><abbr title="' + (collectibleType==='coin'?'Uncirculated':(collectibleType==='banknote'?'Uncirculated':'Uncirculated')) + '">' + (collectibleType==='coin'?'UNC':(collectibleType==='banknote'?'UNC':'UNC')) + '</abbr></label>\                    </span>\
            </div>\
            \
            <div>\
                <label class="form_name" for="collec_form_quantity">Quantity:</label>\
                <span class="form_value"><input type="number" name="collec_form_quantity" id="collec_form_quantity" min="1" value="' + (quantity==null?'1':quantity) + '" /></span>\
            </div>\
            \
            <div>\
                <label class="form_name" for="collec_form_value">Buying value (USD):</label>\
                <span class="form_value"><input type="number" name="collec_form_value" id="collec_form_value" step="0.01" min="0"' + (value==null?'':' value="'+value+'"') + ' /></span>\
            </div>\
            \
            <div>\
                <label class="form_name" for="collec_form_comment">Private comment:</label>\
                <span class="form_value"><input type="text" name="collec_form_comment" id="collec_form_comment" value="' + (comment==null?'':htmlEncode(comment)) + '" /></span>\
            </div>\
            \
            <div>\
                <span class="form_name">For exchange:</span>\
                <span class="form_value">\
                    <input type="radio" name="collec_form_swap" value="1" id="collec_form_swap_yes"' + (forSwap==1?' checked="checked"':'') + ' /><label for="collec_form_swap_yes">yes</label>\
                    <input type="radio" name="collec_form_swap" value="0" id="collec_form_swap_no"' + (forSwap!=1?' checked="checked"':'') + ' /><label for="collec_form_swap_no">no</label>\
                </span>\
            </div>\
            \
            <div>\
                <label class="form_name" for="collec_form_swap_comment">Public comment:</label>\
                <span class="form_value"><input type="text" name="collec_form_swap_comment" id="collec_form_swap_comment" value="' + (swapComment==null?'':htmlEncode(swapComment)) + '" /></span>\
            </div>\
            \
                            <div>\
                <label class="form_name" for="collec_form_section">Collection:</label>\
                <span class="form_value">\
                    <select name="collec_form_section" id="collec_form_section">\
                        <option value="43709"' + (section==43709?' selected="selected"':'') + '>Misc - Non-US</option><option value="43708"' + (section==43708?' selected="selected"':'') + '>Misc - US</option><option value="43706"' + (section==43706?' selected="selected"':'') + '>Type - France</option><option value="43705"' + (section==43705?' selected="selected"':'') + '>Type - Mexico</option><option value="43707"' + (section==43707?' selected="selected"':'') + '>Type - US</option>\
                    </select>\
                </span>\
            </div>\
                            \
            <div>\
                <label class="collec_form_pictures" for="collec_form_pictures">Pictures or<br />private PDF documents:</label>\
                <span class="form_value">\
                    <div style="display:none;"><select multiple="multiple" name="collec_form_pictures" id="collec_form_pictures">';
    if (pictures) {
        for (var i=0; i<pictures.length; i++) {
            content = content + '<option value="' + pictures[i] +  '" selected="selected">' + pictures[i] +  '</option>';
        }
    }
    content = content + '</select></div>\
                    <div id="collec_form_dropzone" class="dropzone" style="display:block; position:relative"></div>\
                </span>\
            </div>\
            \
        </div>\
        <div class="collec_form_submit">\
            <input type="submit" class="button" value="Save" onclick="save_collection(false); return false;">';
    if(action=='create') content = content +'\
            <input type="button" class="button secondary" value="Save and add again" onclick="save_collection(true); return false;">';
    content = content +'\
        </div>\
    </form></div>';
    modal.innerHTML = content;
    $('body').append(modal);

    let myDropzone = new Dropzone('#collec_form_dropzone', {
        url: '/vous/upload_picture.php', 
        acceptedFiles: '.jpeg,.jpg,.png,.gif,.pdf',
        addRemoveLinks: true,
        dictDefaultMessage: 'Click or drop files here to upload.',
        dictInvalidFileType: 'Only JPEG, PNG, GIF and PDF files are accepted.',
        dictCancelUpload: 'Cancel upload',
        dictUploadCanceled: 'Upload canceled.',
        dictCancelUploadConfirmation: 'Are you sure you want to cancel this upload?',
        dictRemoveFile: 'Remove',
        dictRemoveFileConfirmation: 'Are you sure you want to remove this file?'});
    myDropzone.on("success", function(file, response) {
        if (response.substr(0,2)!=='OK') {
            alert(response);
            myDropzone.removeFile(file);
        }
        else {
            let filename = response.substr(2);
            file.serverFileName = filename;
            $('#collec_form_pictures').append($('<option>', { value: filename, text: filename, selected: true }));
            if (filename.endsWith('.pdf')) {
                let thumbnail_url = filename.replace('.pdf','-360.png');
                this.emit('thumbnail', file, "https://en.numista.com/vous/pictures/237078/" + thumbnail_url);
            }
        }
    });
    myDropzone.on("removedfile", function(file) {
        if (file.serverFileName) {
            $('#collec_form_pictures option[value="'+file.serverFileName+'"]').prop('selected', false);
        }
    });
    myDropzone.on("addedfile", function(file) {
        $('.collec_form_submit input').prop('disabled', true);
    });
    myDropzone.on("queuecomplete", function() {
        $('.collec_form_submit input').prop('disabled', false);
    });
    if (pictures) {
        for (let i=0; i<pictures.length; i++) {
            let mockFile = { name: pictures[i], serverFileName: pictures[i] };
            let thumbnail_url = pictures[i].endsWith('.pdf')?pictures[i].replace('.pdf','-360.png'):pictures[i].replace('.','-360.');
            myDropzone.displayExistingFile(mockFile, "/vous/pictures/237078/"+thumbnail_url);
            myDropzone.files.push(mockFile);
        }
    }

    let checked_grade = $('input[name=collec_form_grade]:checked').val();
    $('input[name=collec_form_grade]').on("click", function() {
        if($(this).val() === checked_grade){
            $(this).prop("checked",false);
            checked_grade = null;
        }
        else {
            checked_grade = $(this).val();
        }
    });
    
    $('#collec_form_quantity').focus();
    $(document).keyup(function(e) {
        if (e.key === "Escape") collec_modal_close();
    });
}


function veux(checkbox) {
    let type = checkbox.className.replace('check_veux', '');
    let veux = $(checkbox).prop('checked');
    
    $('.check_veux'+type).prop('disabled', true);
    $('.check_veux_pas'+type).prop('disabled', true);
    $('.check_veux'+type).prop('checked', veux);
    $('.check_veux_pas'+type).prop('checked', false);
    
    $.get("/souhaits/modifier_veux.php", {type: type, veux: veux, veux_pas: 'false'})
        .done(function(reponse) {
            if (reponse!=="OK") alert("An error occurred. Please try again.");
            $('.check_veux'+type).prop('disabled', false);
            $('.check_veux_pas'+type).prop('disabled', false);
        });
}

function veux_pas(checkbox) {
    let type = checkbox.className.replace('check_veux_pas', '');
    let veux_pas = $(checkbox).prop('checked');
    
    $('.check_veux'+type).prop('disabled', true);
    $('.check_veux_pas'+type).prop('disabled', true);
    $('.check_veux'+type).prop('checked', false);
    $('.check_veux_pas'+type).prop('checked', veux_pas);
    
    $.get("/souhaits/modifier_veux.php", {type: type, veux: 'false', veux_pas: veux_pas})
        .done(function(reponse) {
            if (reponse!=="OK") alert("An error occurred. Please try again.");
            $('.check_veux'+type).prop('disabled', false);
            $('.check_veux_pas'+type).prop('disabled', false);
        });
}

function modifier(piece, etat, type_piece) {
    $("#"+etat+piece).css("background", "#FF99CC");
    let quantite = $("#"+etat+piece).val();
    
    $.get("/vous/save_collection_old_style.php", {piece: piece, etat: etat, quantite: quantite})
        .done(function(reponse) {
            if (reponse==="OK") {
                $("#"+etat+piece).css("background", "#FFFFFF");
                document.getElementById(etat+piece).style.background = "#FFFFFF";
                if (typeof type_piece!="undefined") {
                    let compte_collec = 0;
                    let compte_ech = 0;
                    let champs = document.getElementsByTagName("input");
                    let n = champs.length;
                    for (let i=0; i < n; i++) {
                        if (champs[i].className==="qc"+type_piece && parseInt(champs[i].value))
                            compte_collec += parseInt(champs[i].value);
                        else if (champs[i].className==="qe"+type_piece && parseInt(champs[i].value))
                            compte_ech += parseInt(champs[i].value);
                    }
                    self.document.getElementById("affichage_qc"+type_piece).innerHTML = compte_collec;
                    let display = compte_ech===0? 'none' : 'inline';
                    self.document.getElementById("affichage_qe_cadre"+type_piece).style.display = display;
                    self.document.getElementById("affichage_qe"+type_piece).innerHTML = compte_ech;
                }
            }
            else alert("An error occurred. Please try again.");
        });
}

function comm_perso(piece) {
    let ancienCommentaire = $('#comm'+piece).text();
    let nouveauCommentaire = prompt("Enter your personal comment.\nYou may register varieties, errors...", ancienCommentaire);
    if (nouveauCommentaire!=null) {
        $.get("/vous/save_comment.php", {piece: piece, texte: nouveauCommentaire})
            .done(function(reponse) {
                if (reponse==="OK") {
                    $("#comm"+piece).html(htmlEncode(nouveauCommentaire));
                    $("#lien_comm"+piece)[0].onclick = function () { comm_perso(piece, nouveauCommentaire); }
                }
                else if (reponse==='NO_ITEMS') {
                    // pass
                }
                else alert("An error occurred. Please try again.");
            });
    }
}
