import queue
import flask


class MessageAnnouncer:
    # Taken from https://github.com/MaxHalford/flask-sse-no-deps
    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=5))
        return self.listeners[-1]

    def announce(self, msg):
        # We go in reverse order because we might have to delete an element, which will shift the
        # indices backward
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
                print("put to queue")
            except queue.Full:
                del self.listeners[i]


app = flask.Flask(__name__)
announcer = MessageAnnouncer()

def format_sse(data: str, event=None) -> str:
    """Formats a string and an event name in order to follow the event stream convention.

    >>> format_sse(data=json.dumps({'abc': 123}), event='Jackson 5')
    'event: Jackson 5\\ndata: {"abc": 123}\\n\\n'

    """
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

@app.route('/')
def homepage():
    return 'Say Hi App!'

@app.route('/say-hi/', methods=['GET', 'POST'])
def say_hi():
    # endpoint for the webpage to call
    announcer.announce(msg=format_sse('on'))
    print("said hi!")
    return "You said hi!", 201

@app.route('/listen-for-hi/', methods=['GET'])
def listen():
    print("Hi listener connected")

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return flask.Response(stream(), mimetype='text/event-stream')


if __name__ == "__main__":

    app.run(debug=True)