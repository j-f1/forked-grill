change_state = (state) ->
  $("#state")[0].innerText = state

hide_enqueue_button = (_) ->
  $("#join").css("display", "none")
  $("#closed").css("display", "inline")

add_user = (user) ->
  parts = user.split("\x01")

  li = document.createElement "li"
  li.innerHTML = '<a href="https://stackexchange.com/users/' + parts[0] + '">' + parts[1] + '</a>'

  $("#queue")[0].appendChild li

pop_user = (_) ->
  queue = $("#queue")[0]
  queue.removeChild queue.children[0]

@ws_hooks = {
  "p": pop_user,
  "s": change_state,
  "w": hide_enqueue_button,
  "q": add_user
}

@enqueue = ->
  $.ajax url: "/enqueue", method: "PUT", success: (response) ->
    if !window.sock || window.sock.readyState != WebSocket.OPEN
      add_user response

$ ->
  window.sock = new WebSocket("wss://" + window.location.host + "/ws")

  window.sock.onmessage = (message) ->
    window.ws_hooks[message.data[0]](message.data.substring(1))
