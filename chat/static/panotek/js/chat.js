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


function showChat(to_user_id){
    console.log("to_user_id: ",to_user_id)
    console.log("from_user_id: ", from_user_id)
    $(".chat-users").addClass("hide");
    $(".chat-body").removeClass("hide");
    $(".chat-input").removeClass("hide");
    let room_id = from_user_id + "--" + to_user_id;
    getChatToken(room_id, from_user_id, to_user_id)
}


function getChatToken(room_id, from_user_id, to_user_id){
    $.getJSON(
        "/chat/token",
        {
            device: "browser",
            identity: room_id,
            from_user_id: from_user_id,
            to_user_id: to_user_id
        },
        function (data) {
            username = data.identity;
            channel_name = data.identity
            Twilio.Chat.Client.create(data.token).then(client => {
                chatClient = client;
                chatClient.getSubscribedChannels().then(createOrJoinChannel(channel_name));
            });
        }
    );
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
                child += `<li class="list-group-item">`
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
                child += `</div></div></div><hr></li>`
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
    e.preventDefault();
    if (roomChannel && message.trim().length > 0) {
        roomChannel.sendMessage(message);
        $("#message_text").val("");
    }
})

