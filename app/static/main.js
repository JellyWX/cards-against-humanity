
var sock = io.connect("http://" + document.domain + ':' + location.port);
sock.emit('join');

var game_id = document.currentScript.getAttribute('game');
var uuid_self = document.currentScript.getAttribute('uuid');

var am_czar = false;

var players = {}


sock.on('ready', (uuid) =>
{
    console.log("player " + uuid + " has readied up");
    var user_item = document.getElementById(uuid);

    user_item.getElementsByTagName('span')[0].className = "badge badge-success badge-pill";

    create_show_card("", false, 0, 1);
});

sock.on('unready', function()
{
    var player_list = document.getElementById("players");

    for (element in player_list.children)
    {
        element.getElementsByTagName('span').className = "badge badge-warning badge-pill";
    }
});

sock.on('player_join', (nickname, uuid, czar, points) =>
{
    add_message("<strong>" + nickname + "</strong> has joined the game", "alert-success");

    if (!(uuid in players))
    {
        add_player(nickname, uuid, czar, points);
        players[uuid] = nickname;

        if (uuid == uuid_self)
        {
            am_czar = czar;

            if (czar)
            {
                for (var i = 0; i < 8; i++)
                {
                    document.getElementsByClassName("play-button")[i].style.opacity = 0
                }
            }
        }
    }
});

sock.on('player_leave', (uuid) =>
{
    add_message("<strong>" + players[uuid] + "</strong> has left the game", "alert-danger");

    player = document.getElementById(uuid);
    player.parentNode.removeChild(player);
});

sock.on('show_cards', (data) =>
{
    console.log("received show_cards event");

    drop("results");

    cards = data.split("\t")

    console.log(cards)
    for (var i = 0; i < cards.length; i++)
    {
        if (cards[i] != "")
        {
            single_cards = cards[i].split('\\');

            create_show_card(single_cards[0], am_czar, 0, single_cards.length);

            for (var j = 1; j < single_cards.length; j++)
            {
                create_show_card(single_cards[j], false, j, single_cards.length);
            }
        }
    }
});

sock.on('round_win', (data) =>
{
    console.log(players[data] + " has won the round");
    add_message("<strong>" + players[data] + "</strong> has won the round", "alert-warning")
});

sock.on('refresh', (cards, new_czar, new_black, points) =>
{
    console.log("refresh called")

    drop("players");
    drop("results");
    drop("deck");

    for (var uuid in points)
    {
        add_player(players[uuid], uuid, new_czar == uuid, points[uuid]);
    }

    hand = cards.split("\t");

    for (var i = 0; i < hand.length; i++)
    {
        create_hand_card(hand[i], i);
    }

    am_czar = (new_czar == uuid_self)

    if (am_czar)
    {
        for (var i = 0; i < 8; i++)
        {
            document.getElementsByClassName("play-button")[i].style.opacity = 0
        }
    }

    document.getElementById("blackcard").innerHTML = new_black.replace('_', '______');
});

function add_player(nickname, uuid, czar, points)
{
    var player_list = document.getElementById("players");

    var item = document.createElement("li");
    if (uuid == uuid_self)
    {
        item.className = "list-group-item d-flex justify-content-between align-items-center border border-success";
        item.style.zIndex = 9999;
    }
    else
    {
        item.className = "list-group-item d-flex justify-content-between align-items-center";
    }
    item.id = uuid;

    var icon = document.createElement("span");

    if (czar)
    {
        icon.className = "badge badge-info badge-pill";
    }
    else
    {
        icon.className = "badge badge-warning badge-pill";
    }

    var empty_badge = document.createTextNode(points);
    icon.appendChild(empty_badge);

    if (czar)
    {
        var text = document.createTextNode("(Czar)  " + nickname);
    }
    else
    {
        var text = document.createTextNode(nickname);
    }

    item.appendChild(icon);
    item.appendChild(text);

    player_list.appendChild(item);
}

function drop(element)
{
    var list = document.getElementById(element);
    while (list.firstChild)
    {
        list.removeChild(list.firstChild);
    }
}

function play(index)
{
    if (!am_czar)
    {
        sock.emit('play', index);

        for (
            var i = 0;
            i < 8;
            i++)
        {
            var el = document.getElementById("play_card_" + i);

            if (i == index)
            {
                el.style.setProperty("text-decoration", "line-through");
                el.style.setProperty("pointer-events", "none");
                el.parentNode.parentNode.style.opacity = 0.2;
            }
            else
            {
                el.style.setProperty("text-decoration", "");
                el.style.setProperty("pointer-events", "auto");
                el.parentNode.parentNode.style.opacity = 1;
            }
        }
    }
}

function create_show_card(text, czar, index, total)
{
    if (czar)
    {
        var choose = document.createTextNode("Choose");

        var link = document.createElement("a");
        link.href = "javascript:czar_select('" + text + "')";
        link.className = "card-link";
        link.appendChild(choose);

        var footer = document.createElement("div");
        footer.className = "card-footer";
        footer.appendChild(link);
    }

    var content = document.createElement("h5");
    content.className = "card-title"
    content.innerHTML = text;

    var br = document.createElement("br");

    var body = document.createElement("div");
    body.className = "card-body"
    body.appendChild(br);
    body.appendChild(content);

    var card = document.createElement("div");

    if (total == 1)
    {
        card.className = "card flip-card bg-light border-dark";
    }
    else if (index == 0)
    {
        card.className = "card flip-card bg-light border-dark border-right-0";
    }
    else if (index == (total - 1))
    {
        card.className = "card flip-card bg-light border-dark border-left-0";
    }
    else
    {
        card.className = "card flip-card bg-light border-dark border-top-0 border-bottom-0";
    }

    card.style.width = "14rem";
    card.style.minWidth = "14rem";
    card.style.height = "16rem";
    card.appendChild(body);

    if (czar)
    {
        card.appendChild(footer);
    }

    document.getElementById("results").appendChild(card);
}

function create_hand_card(text, index)
{
    var choose = document.createTextNode("Play Card");

    var link = document.createElement("a");
    link.href = "javascript:play(" + index + ")";
    link.className = "card-link";
    link.id = "play_card_" + index
    link.appendChild(choose);

    var footer = document.createElement("div");
    footer.className = "card-footer play-button";
    footer.appendChild(link);

    var content = document.createElement("h5");
    content.className = "card-title"
    content.innerHTML = text;
    content.id = "content_" + index

    var br = document.createElement("br");

    var body = document.createElement("div");
    body.className = "card-body"
    body.appendChild(br);
    body.appendChild(content);

    var card = document.createElement("div");
    card.className = "card bg-light";
    card.style.width = "100%"
    card.style.height = "12rem";
    card.style.minWidth = "12rem";
    card.appendChild(body);

    card.appendChild(footer);

    document.getElementById("deck").appendChild(card);
}

function czar_select(text)
{
    sock.emit('czar_select', text);
}



function send_message()
{
    tb = document.getElementById("message_box");

    text = tb.value;

    if (text == "")
    {
        return;
    }
    tb.value = "";

    sock.emit('send_message', text);
}

function add_message(text, style)
{
    s = document.createElement("div");
    s.className = "alert " + style;
    s.innerHTML = text;

    inbox = document.getElementById("inbox");
    inbox.insertBefore(s, inbox.firstChild);
}

var input = document.getElementById("message_box");

input.addEventListener("keyup", function(event) {
    event.preventDefault();

    if (event.keyCode === 13)
    {
        document.getElementById("send_message").click();
    }
});


sock.on('message', (uuid, message) =>
{
    add_message("<strong>" + players[uuid] + "</strong>: " + message, "alert-dark")
});
