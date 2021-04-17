function createChatBubble(msg, sender){
    let chat_body = document.getElementById("chat-body");
    let chatbubble = "";
    if(sender == "me"){
        chatbubble = `<div class="chat-bubble me">` + msg + `</div>`;
    }
    else{
        chatbubble = `<div class="chat-bubble you">` + msg + `</div>`;
    }
    let element = document.createRange().createContextualFragment(chatbubble);
    chat_body.appendChild(element);
}


function showChat(user_id){
    let from_user_id = current_user_id
    to_user_id = user_id
    $.ajax({
        type: "GET",
        data:{
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
        },
        url: "/chat/receive/",
        success: function(resp){
            let parent_element = document.getElementById("chat-body");
            parent_element.querySelectorAll('*').forEach(n => n.remove());

            let messages = JSON.parse(resp);
            for(let i=0; i<messages.length; ++i){
                let message = messages[i]
                if(message["from_user_id"] == from_user_id){
                    createChatBubble(message["body"], "me");
                }
                else{
                    createChatBubble(message["body"], "you");
                }
            }
            
            var height = 100000;
            $('#chat-body .chat-bubble').each(function(i, value){
                height += parseInt($(this).height());
            });
            
            height += '';
            
            $('#chat-body').animate({scrollTop: height});
            setInterval(function (){
                let from_user_id = user_id
                let to_user_id = current_user_id
            
                $.ajax({
                    type: "GET",
                    data:{
                        "from_user_id": from_user_id,
                        "to_user_id": to_user_id
                    },
                    url: "/chat/poll_new_messages/",
                    success: function(resp){
                        let messages = JSON.parse(resp)
                        for(let i=0; i<messages.length; ++i){
                            let message = messages[i]
                            createChatBubble(message["body"], "you");
                        }
                    }
                })
            }, 3000)
        }
    })

    $(".chat-header-bottom__name").text(current_user_fname)
    $(".chat-users").addClass("hide");
    $(".chat-body").removeClass("hide");
    $(".chat-input").removeClass("hide");
    $(".chat-header-bottom").removeClass("hide");
}


function listChatUsers(){
    $.ajax({
        type: "GET",
        data: {},
        url: "/chat/chat_users/",
        success: function(resp){
            let parent_element = document.getElementById("chat-users-list");
            parent_element.querySelectorAll('*').forEach(n => n.remove());
            let users = JSON.parse(resp);
            for(let i=0; i<users.length; ++i){
                user = users[i];
                let child = "";
                child += `<li class="list-group-item" id="user-chat-`+user.user_id+`">`
                child += `<div class="row">`
                child += `<div class="chat-profile-pic" onclick="showChat(`+user.user_id+`)">`
                child += `<img src="`+user.profile_pic+`" class="img-rounded">`
                if (user.is_online == true){
                    child += `<div class="online-status" id="online-status-`+user.user_id+`"></div>`
                }
                else{
                    child += `<div class="online-status hide" id="online-status-`+user.user_id+`"></div>`
                }
                child += `</div>`
                child += `<div class="">`
                child += `<div class="box">`
                child += `<div class="name">`+user.fname + " " + user.lname+`</div>`
                child += `<div class="place">`+user.country+`</div>`
                child += `<div class="timezone">`+user.timezone+`</div>`
                child += `</div></div>`
                if(user.pending_messages_count > 0){
                    child += `<div class="unread-message" id="unread-message-`+user.user_id+`">`+user.pending_messages_count+`</div>`
                }
                else{
                    child += `<div class="unread-message hide" id="unread-message-`+user.user_id+`">`+user.pending_messages_count+`</div>`
                }
                child += `</div><hr></li>`
                let childelement = document.createRange().createContextualFragment(child);
                parent_element.appendChild(childelement);
            }

        },
        error: function(err){
            console.log(err);
        }
    })
}


$("#logout").click(function (e){
    $.ajax({
        type: "POST",
        data: {
            "csrfmiddlewaretoken": '{{ csrf_token }}'
        },
        url: "/auth/logout/",
        success: function(resp){
            current_user_id = null;
            current_user_fname = null;
            $(".chat-users").addClass('hide');
            $(".chat-mail").removeClass('hide');
            $(".chat-header-options").addClass('hide');
            $(".chat-body").addClass('hide');
            $(".chat-input").addClass('hide');
            $(".chat-header-bottom").addClass("hide");
            $("#email").val("")
        },
        error: function(err){
            console.log("Error: ", err.responseText);
        }
    })
})


$("#message_send").click(function(e){
    let message = $("#message_text").val();
    // Send api for chat

    $.ajax({
        type: "POST",
        data:{
            "type": "chat",
            "from_user_id": current_user_id,
            "to_user_id": to_user_id,
            "body": message
        },
        url: "/chat/send/",
        success: function(resp){
            createChatBubble(resp, "me");
            $("#message_text").val("")
        }
    })
})

let poll_data = setInterval(() => {
    $.ajax({
        type: "GET",
        data: {},
        url: "/chat/poll_data/",
        success: function(resp){
            resp = JSON.parse(resp)
            if(resp["status"]){
                for(var user_id in resp["data"]){
                    let r = resp["data"][user_id]
                    let online_status = r["is_online"]
                    let pending_messages_count = r["pending_messages_count"]

                    let id = "#online-status-" + user_id
                    if(online_status){
                        $(id).removeClass('hide')
                    }
                    else{
                        $(id).addClass('hide')
                    }

                    id = "#unread-message-" + user_id
                    if(pending_messages_count > 0){
                        $(id).text(pending_messages_count)
                        $(id).removeClass('hide')
                    }
                    else{
                        $(id).addClass('hide')
                    }
                }
            }
        }
    })
}, (5000));

function loadLocations(){
    $.ajax({
        type: "GET",
        data: {},
        url: "/chat/list_office_loc/",
        success: function(resp){
            resp = JSON.parse(resp)
            console.log("LOCATIONS: ", resp)
            let parent = document.getElementById("location-options")
            for(let i=0; i<resp.length; ++i){
                let location = resp[i]
                let element = `<a class="dropdown-item" onclick=setLocation(`+location.id+`)>` +location.loc+ `</a>`

                element = document.createRange().createContextualFragment(element);
                parent.appendChild(element);
            }
        }
    })
}

function setLocation(loc_id){
    $.ajax({
        type: "GET",
        data: {"id": loc_id},
        url: "/chat/set_location/",
        success: function(resp){
            console.log(resp)
        }
    })
}

function moveback(){
    $('.chat-mail').addClass('hide');
    $('.chat-users').removeClass('hide');
    $('.chat-header-options').removeClass('hide');
    $(".chat-body").addClass("hide");
    $(".chat-input").addClass("hide")
    $(".chat-header-bottom").addClass("hide");
    listChatUsers();
}