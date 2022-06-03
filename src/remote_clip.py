from pyre import Pyre 

from pyre import zhelper 
import zmq 
import uuid
import logging
import sys
import json
import time
from pprint import pprint
import pyperclip

debug = False

def chat_task(ctx, pipe):
    n = Pyre("CHAT")
    n.set_header("CHAT_Header1","example header1")
    n.set_header("CHAT_Header2","example header2")
    n.join("CHAT")
    n.start()

    poller = zmq.Poller()
    poller.register(pipe, zmq.POLLIN)
    debug and print(n.socket())
    poller.register(n.socket(), zmq.POLLIN)
    debug and print(n.socket())
    while(True):
        items = dict(poller.poll())
        debug and print(n.socket(), items)
        if pipe in items and items[pipe] == zmq.POLLIN:
            message = pipe.recv()
            # message to quit
            if message.decode('utf-8') == "$$STOP":
                break
            #print("CHAT_TASK: %s" % message)
            n.shouts("CHAT", message.decode('utf-8'))
        else:
            cmds = n.recv()
            msg_type = cmds.pop(0).decode('utf-8')
            msg_peer = uuid.UUID(bytes=cmds.pop(0))
            msg_name = cmds.pop(0).decode('utf-8')

            debug and print("NODE_MSG TYPE: %s" % msg_type)
            debug and print("NODE_MSG PEER: %s" % msg_peer)
            debug and print("NODE_MSG NAME: %s" % msg_name)

            if msg_type == 'JOIN':
                pass
                msg_cont = cmds.pop(0).decode('utf-8')
                debug and print("NODE_MSG CONT: %s" % msg_cont)
            elif msg_type == "SHOUT":
                msg_group = cmds.pop(0).decode('utf-8')
                debug and print("NODE_MSG GROUP: %s" % msg_group)
                msg_cont = cmds.pop(0).decode('utf-8')
                # Output contents of remote clipboard
                print("From Remote Clipboard: \n%s" % msg_cont)
                print()
            elif msg_type == "ENTER":
                msg_headers = cmds.pop(0).decode('utf-8')
                headers = json.loads(msg_headers)
                debug and print("NODE_MSG HEADERS: %s" % headers)
                for key in headers:
                    debug and print("key = {0}, value = {1}".format(key, headers[key]))
                msg_cont = cmds.pop(0).decode('utf-8')
                debug and print("NODE_MSG CONT: %s" % msg_cont)
    n.stop()


if __name__ == '__main__':
    # Create a StreamHandler for debugging
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.ERROR)
    logger.addHandler(logging.StreamHandler())
    logger.propagate = False

    ctx = zmq.Context()
    chat_pipe = zhelper.zthread_fork(ctx, chat_task)
    # input in python 2 is different
    if sys.version_info.major < 3:
        input = raw_input
    last_value = ""
    while True:
        try:
            tmp_value = pyperclip.paste()
            if last_value != tmp_value:
                msg = tmp_value
                #msg = input()
                chat_pipe.send(msg.encode('utf_8'))
            time.sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
            break
    chat_pipe.send("$$STOP".encode('utf_8'))
    print("FINISHED")