@skip_state = ->
  $.ajax url: "/skip", method: "DELETE", success: ->
    if !window.sock || window.sock.readyState != WebSocket.OPEN
      window.location.reload

@wrap_up = ->
  $.ajax url: "/wrapup", method: "DELETE", success: ->
    if !window.sock || window.sock.readyState != WebSocket.OPEN
      window.location.reload

@send_chat_msg = (key) ->
  if !key || key.which == 13
    input = $("#chat_input")[0]

    window.sock.send(input.value)
    input.value = ""

    return false
  else
    return true

$ ->
  window.ws_hooks["m"] = (msg) ->
    $("#sidechat")[0].value += msg
