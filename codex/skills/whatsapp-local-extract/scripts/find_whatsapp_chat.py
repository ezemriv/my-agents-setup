#!/usr/bin/env python3
"""Find local WhatsApp chats and media metadata on macOS."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

APPLE_EPOCH = 978_307_200
DEFAULT_CONTAINER = (
    Path.home()
    / "Library/Group Containers/group.net.whatsapp.WhatsApp.shared"
)


def connect(db_path: Path) -> sqlite3.Connection:
    uri = db_path.resolve().as_uri() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=5)
    con.row_factory = sqlite3.Row
    return con


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]


def search_contacts(container: Path, term: str, limit: int) -> list[dict]:
    db = container / "ContactsV2.sqlite"
    if not db.exists():
        return []
    like = f"%{term.lower()}%"
    sql = """
    SELECT
      Z_PK, ZFULLNAME, ZGIVENNAME, ZLASTNAME, ZHIGHLIGHTEDNAME,
      ZLOCALIZEDPHONENUMBER, ZPHONENUMBER, ZWHATSAPPID, ZLID, ZIDENTIFIER
    FROM ZWAADDRESSBOOKCONTACT
    WHERE lower(
      coalesce(ZFULLNAME,'') || ' ' ||
      coalesce(ZGIVENNAME,'') || ' ' ||
      coalesce(ZLASTNAME,'') || ' ' ||
      coalesce(ZHIGHLIGHTEDNAME,'') || ' ' ||
      coalesce(ZSEARCHTOKENLIST,'') || ' ' ||
      coalesce(ZPHONENUMBER,'') || ' ' ||
      coalesce(ZWHATSAPPID,'') || ' ' ||
      coalesce(ZLID,'')
    ) LIKE ?
    LIMIT ?;
    """
    with connect(db) as con:
        return rows_to_dicts(con.execute(sql, (like, limit)).fetchall())


def search_chats(container: Path, term: str, limit: int, groups_only: bool) -> list[dict]:
    db = container / "ChatStorage.sqlite"
    like = f"%{term.lower()}%"
    group_clause = "AND ZCONTACTJID LIKE '%@g.us'" if groups_only else ""
    sql = f"""
    SELECT
      Z_PK, ZCONTACTJID, ZPARTNERNAME, ZCONTACTIDENTIFIER, ZGROUPINFO,
      datetime(ZLASTMESSAGEDATE + {APPLE_EPOCH}, 'unixepoch', 'localtime') AS last_msg,
      ZMESSAGECOUNTER, ZLASTMESSAGETEXT
    FROM ZWACHATSESSION
    WHERE lower(
      coalesce(ZPARTNERNAME,'') || ' ' ||
      coalesce(ZCONTACTIDENTIFIER,'') || ' ' ||
      coalesce(ZCONTACTJID,'')
    ) LIKE ?
    {group_clause}
    ORDER BY ZLASTMESSAGEDATE DESC
    LIMIT ?;
    """
    with connect(db) as con:
        return rows_to_dicts(con.execute(sql, (like, limit)).fetchall())


def list_messages(container: Path, chat_session: int, limit: int) -> list[dict]:
    db = container / "ChatStorage.sqlite"
    sql = f"""
    SELECT
      m.Z_PK AS msg_pk,
      m.ZMESSAGETYPE AS message_type,
      m.ZISFROMME AS from_me,
      datetime(m.ZMESSAGEDATE + {APPLE_EPOCH}, 'unixepoch', 'localtime') AS msg_date,
      m.ZFROMJID AS from_jid,
      m.ZTOJID AS to_jid,
      m.ZPUSHNAME AS push_name,
      m.ZTEXT AS text,
      mi.ZFILESIZE AS media_bytes,
      mi.ZMOVIEDURATION AS media_duration,
      mi.ZMEDIALOCALPATH AS media_local_path,
      CASE
        WHEN mi.ZMEDIALOCALPATH IS NULL THEN NULL
        ELSE '{str((container / "Message").resolve())}/' || mi.ZMEDIALOCALPATH
      END AS media_full_path
    FROM ZWAMESSAGE m
    LEFT JOIN ZWAMEDIAITEM mi ON mi.Z_PK = m.ZMEDIAITEM
    WHERE m.ZCHATSESSION = ?
    ORDER BY m.ZMESSAGEDATE DESC
    LIMIT ?;
    """
    with connect(db) as con:
        return rows_to_dicts(con.execute(sql, (chat_session, limit)).fetchall())


def contact_lookup(container: Path, jid: str | None) -> dict | None:
    if not jid:
        return None
    db = container / "ContactsV2.sqlite"
    if not db.exists():
        return None

    phone = jid.split("@", 1)[0] if "@" in jid else jid
    sql = """
    SELECT
      ZFULLNAME, ZGIVENNAME, ZLASTNAME, ZHIGHLIGHTEDNAME,
      ZLOCALIZEDPHONENUMBER, ZPHONENUMBER, ZWHATSAPPID, ZLID
    FROM ZWAADDRESSBOOKCONTACT
    WHERE ZLID = ?
       OR ZWHATSAPPID = ?
       OR ZPHONENUMBER = ?
    LIMIT 1;
    """
    with connect(db) as con:
        row = con.execute(sql, (jid, jid, phone)).fetchone()
    return dict(row) if row else None


def list_members(container: Path, chat_session: int) -> list[dict]:
    db = container / "ChatStorage.sqlite"
    sql = """
    SELECT
      Z_PK, ZISACTIVE, ZISADMIN, ZCONTACTIDENTIFIER, ZCONTACTNAME,
      ZFIRSTNAME, ZMEMBERJID
    FROM ZWAGROUPMEMBER
    WHERE ZCHATSESSION = ?
    ORDER BY ZISACTIVE DESC, ZISADMIN DESC, ZCONTACTNAME, ZMEMBERJID;
    """
    with connect(db) as con:
        members = rows_to_dicts(con.execute(sql, (chat_session,)).fetchall())

    for member in members:
        member["contact"] = contact_lookup(container, member.get("ZMEMBERJID"))
    return members


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--container",
        default=str(DEFAULT_CONTAINER),
        help="WhatsApp shared group container path",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search")
    search.add_argument("term")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--groups-only", action="store_true")

    messages = sub.add_parser("messages")
    messages.add_argument("--chat-session", type=int, required=True)
    messages.add_argument("--limit", type=int, default=50)

    members = sub.add_parser("members")
    members.add_argument("--chat-session", type=int, required=True)

    args = parser.parse_args()
    container = Path(args.container).expanduser()

    if args.command == "search":
        result = {
            "contacts": [] if args.groups_only else search_contacts(container, args.term, args.limit),
            "chats": search_chats(container, args.term, args.limit, args.groups_only),
        }
    elif args.command == "messages":
        result = {
            "messages": list_messages(container, args.chat_session, args.limit),
        }
    else:
        result = {
            "members": list_members(container, args.chat_session),
        }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
