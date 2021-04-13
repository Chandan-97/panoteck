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
    console.log("to_user_id: ",to_user_id)
    console.log("from_user_id: ", from_user_id)
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
            
            var height = 1000;
            $('#chat-body .chat-bubble').each(function(i, value){
                height += parseInt($(this).height());
            });
            
            height += '';
            
            $('#chat-body').animate({scrollTop: height});
        }
    })

    $(".chat-users").addClass("hide");
    $(".chat-body").removeClass("hide");
    $(".chat-input").removeClass("hide");
}


function listChatUsers(){
    $.ajax({
        type: "GET",
        data: {},
        url: "/chat/chat_users/",
        success: function(resp){
            console.log("Response: ", resp)
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
                    child += `<div class="online-status"></div>`
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
            $(".chat-users").addClass('hide');
            $(".chat-mail").removeClass('hide');
            $(".chat-header-options").addClass('hide');
            $(".chat-body").addClass('hide');
            $(".chat-input").addClass('hide');
            $("#email").val("")
        },
        error: function(err){
            console.log("Error: ", err.responseText);
        }
    })
})


$("#message_send").click(function(e){
    let message = $("#message_text").val();
    console.log(current_user_id)
    console.log(to_user_id)
    console.log(message)
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
            console.log(resp);
            createChatBubble(resp, "me");
            $("#message_text").val("")

            var height = 1000;
            $('#chat-body .chat-bubble').each(function(i, value){
                height += parseInt($(this).height());
            });
            height += '';
            $('#chat-body').animate({scrollTop: height});
        }
    })
})