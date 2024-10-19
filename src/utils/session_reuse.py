from typing import Optional

from atproto_client import Session, SessionEvent

from .path import DATA_PATH


class SessionReuse:
    def __init__(self):
        self.session_file = DATA_PATH / "session.txt"

    def get_session(self) -> Optional[str]:
        try:
            with open(self.session_file, encoding="UTF-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def save_session(self, session_str) -> None:
        with open(self.session_file, "w", encoding="UTF-8") as f:
            f.write(session_str)

    async def on_session_change(self, event: SessionEvent, session: Session) -> None:
        if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
            self.save_session(session.export())
