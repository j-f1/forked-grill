import collections
import enum
import os
import queue
import requests
import threading
from chatexchange.client import Client

import config
import web_worker


class EventState(enum.Enum):
    WAITING = 1
    IN_QUESTION = 2
    DISCUSSION = 3
    END = 4


waiting_users = collections.OrderedDict()
state = EventState.WAITING
skip_state = threading.Event()
new_question = threading.Event()
wrap_up = False


def start():
    client = Client("stackexchange.com")
    client.login(os.environ["USER"], os.environ["PASS"])

    room = client.get_room(config.room_id)

    _post_lines(room, config.preamble)

    skip_state.wait(config.preamble_time)
    skip_state.clear()

    while _voice_next(room):
        _change_state(EventState.DISCUSSION)

        if not skip_state.wait(config.waiting_time - 60):
            _post_lines(room, config.warning)

            skip_state.wait(60)
            skip_state.clear()

    _change_state(EventState.END)
    _post_lines(room, config.finale)


def _change_state(new_state):
    state = new_state
    broadcast_msg = "s{}".format(new_state.name)

    def callback():
        web_worker.GrillWS.broadcast(broadcast_msg)

        if state == EventState.IN_QUESTION:
            web_worker.GrillWS.broadcast("p")

    web_worker.ioloop.add_callback(callback)


def _voice_next(room):
    while len(waiting_users) == 0:
        if wrap_up:
            return False

        _post_lines(room, config.extension)

        new_question.wait()
        new_question.clear()

    _change_state(EventState.IN_QUESTION)

    _make_gallery(room)
    _post_lines(room, config.voice_intro)

    account_id, _ = waiting_users.popitem()
    next_user = requests.head("https://chat.stackexchange.com/accounts/{}".format(account_id)).headers["Location"].split("/")[2]

    _grant_write_access(room, next_user)
    room.send_message("@{}".format(room._client.get_user(next_user).name.replace(" ", "")))

    skip_state.wait(config.question_time)
    skip_state.clear()

    _post_lines(room, config.voice_end)
    _make_public(room)
    _revoke_write_access(room, next_user)

    return True


def _post_lines(room, lines):
    for line in lines.splitlines():
        room.send_message(line)


def _make_gallery(room):
    room._client._br.post_fkeyed("rooms/save", data={"roomId": room.id, "defaultAccess": "read-only"})


def _make_public(room):
    room._client._br.post_fkeyed("rooms/save", data={"roomId": room.id, "defaultAccess": "read-write"})


def _grant_write_access(room, user):
    route = "rooms/setuseraccess/{}".format(room.id)
    room._client._br.post_fkeyed(route, data={"userAccess": "read-write", "aclUserId": user})


def _revoke_write_access(room, user):
    route = "rooms/setuseraccess/{}".format(room.id)
    room._client._br.post_fkeyed(route, data={"userAccess": "remove", "aclUserId": user})
