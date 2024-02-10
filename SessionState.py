class _SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def get(**kwargs):
    from streamlit.report_thread import get_report_ctx
    from streamlit.server.server import Server

    ctx = get_report_ctx()

    session_id = ctx.session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    this_session = session_info.session

    if not hasattr(this_session, "_custom_session_state"):
        this_session._custom_session_state = _SessionState(**kwargs)

    return this_session._custom_session_state
