---
name: whatsapp-local-extract
description: Locate and extract local WhatsApp Desktop chats, groups, messages, and media from macOS backend storage. Use when Codex needs to find a WhatsApp conversation by contact name, phone number, group name, JID/LID, or date range; list messages and audio/media paths; or prepare local WhatsApp audio files for the whatsapp-transcription skill.
---

# WhatsApp Local Extract

## Scope

Use this skill to find local WhatsApp conversations before transcription or wiki ingest. Keep it separate from `$whatsapp-transcription`: this skill locates chats and media; `$whatsapp-transcription` transcribes audio once files are known.

Default macOS container:

```text
~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared
```

Core files:

- `ChatStorage.sqlite`: chats, messages, media metadata, group metadata.
- `ContactsV2.sqlite`: address book/contact names, phone numbers, JIDs, LIDs.
- `Message/Media/<jid-or-lid>/...`: local media files such as WhatsApp `.opus` audio.

## Standard Workflow

1. Locate the WhatsApp container.
2. Search `ContactsV2.sqlite` when the input is a person/contact name or phone number.
3. Search `ChatStorage.sqlite.ZWACHATSESSION` when the input is a chat title, group name, JID, or LID.
4. Resolve:
   - `Z_PK` as the chat session id;
   - `ZCONTACTJID` as the stable WhatsApp chat id;
   - `ZPARTNERNAME` as the visible chat/contact/group name;
   - group chats usually end with `@g.us`.
5. Extract messages by joining `ZWAMESSAGE` with `ZWAMEDIAITEM` on `ZWAMESSAGE.ZMEDIAITEM = ZWAMEDIAITEM.Z_PK`.
6. For audio, use `ZWAMEDIAITEM.ZMEDIALOCALPATH` and resolve relative paths under `Message/`.
7. Copy or reference audio files for `$whatsapp-transcription`.

Prefer the bundled script:

```bash
python path/to/skill/scripts/find_whatsapp_chat.py search "Matias"
python path/to/skill/scripts/find_whatsapp_chat.py search "Hnos" --groups-only
python path/to/skill/scripts/find_whatsapp_chat.py members --chat-session 841
python path/to/skill/scripts/find_whatsapp_chat.py messages --chat-session 891 --limit 50
```

## Known Working Example: Matias

Contact search in `ContactsV2.sqlite.ZWAADDRESSBOOKCONTACT` found:

- `ZFULLNAME`: `Mati Gomez Csher`
- `ZPHONENUMBER`: `+5491131724451`
- `ZWHATSAPPID`: `5491131724451@s.whatsapp.net`
- `ZLID`: `145487739015364@lid`

Chat search in `ChatStorage.sqlite.ZWACHATSESSION` found:

- `Z_PK`: `891`
- `ZCONTACTJID`: `5491131724451@s.whatsapp.net`
- `ZPARTNERNAME`: `Mati Gomez Csher`

Audio query:

```sql
SELECT
  m.Z_PK AS msg_pk,
  m.ZMESSAGETYPE AS type,
  m.ZISFROMME AS from_me,
  datetime(m.ZMESSAGEDATE + 978307200, 'unixepoch', 'localtime') AS msg_date,
  mi.ZFILESIZE AS bytes,
  mi.ZMOVIEDURATION AS duration,
  mi.ZMEDIALOCALPATH AS local_path
FROM ZWAMESSAGE m
JOIN ZWAMEDIAITEM mi ON mi.Z_PK = m.ZMEDIAITEM
WHERE m.ZCHATSESSION = 891
  AND mi.ZMEDIALOCALPATH LIKE '%.opus'
ORDER BY m.ZMESSAGEDATE DESC;
```

Media paths were relative to `Message/`, for example:

```text
Media/145487739015364@lid/0/2/02384707-e2bc-4036-b95d-3c3dae5f086e.opus
```

Resolve as:

```text
~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/Message/<relative-path>
```

## Group Search: Hnos Pattern

Group names are searched in the same chat session table:

```sql
SELECT
  Z_PK,
  ZCONTACTJID,
  ZPARTNERNAME,
  ZGROUPINFO,
  datetime(ZLASTMESSAGEDATE + 978307200, 'unixepoch', 'localtime') AS last_msg,
  ZMESSAGECOUNTER
FROM ZWACHATSESSION
WHERE ZCONTACTJID LIKE '%@g.us'
  AND lower(coalesce(ZPARTNERNAME,'') || ' ' || coalesce(ZCONTACTIDENTIFIER,'') || ' ' || coalesce(ZCONTACTJID,'')) LIKE '%hnos%'
ORDER BY ZLASTMESSAGEDATE DESC;
```

If this returns a row, `Z_PK` is the `--chat-session` value for message/media extraction. `ZCONTACTJID` is the group JID and should match a `Message/Media/<group-jid>/...` directory when the group has local media.

Members are usually reachable through `ZWAGROUPINFO` and `ZWAGROUPMEMBER`, but WhatsApp schema versions vary. Inspect first:

```bash
sqlite3 ChatStorage.sqlite '.schema ZWAGROUPINFO'
sqlite3 ChatStorage.sqlite '.schema ZWAGROUPMEMBER'
```

Then join on the group info foreign key and member JIDs. Do not assume group membership from media folders alone.

### Confirmed Example: Hnos

Search command:

```bash
python /Users/ezequielmrivero/.codex/skills/whatsapp-local-extract/scripts/find_whatsapp_chat.py search "Hnos" --groups-only --limit 20
```

Resolved chat:

- `Z_PK`: `841`
- `ZCONTACTJID`: `5491161683402-1522716712@g.us`
- `ZPARTNERNAME`: `Hnos`
- `ZGROUPINFO`: `15`
- `last_msg`: `2026-05-29 17:55:52`
- `ZMESSAGECOUNTER`: `9`

Members command:

```bash
python /Users/ezequielmrivero/.codex/skills/whatsapp-local-extract/scripts/find_whatsapp_chat.py members --chat-session 841
```

Resolved active members from `ZWAGROUPMEMBER` + `ContactsV2.sqlite`:

- `170158165336092@lid` -> `Ezequiel Rivero` (`34666367353@s.whatsapp.net`), active.
- `81449826910250@lid` -> `Cintia Rivero` (`5491161683402@s.whatsapp.net`), active admin.
- `39719907934455@lid` -> `Joni Rivero` (`5491131515107@s.whatsapp.net`), active.

Inactive legacy rows may also appear for older phone JIDs, for example `34666367353@s.whatsapp.net` and `5491161683402@s.whatsapp.net`. Prefer active LID rows for current membership.

Recent message/media extraction for `Hnos`:

```bash
python /Users/ezequielmrivero/.codex/skills/whatsapp-local-extract/scripts/find_whatsapp_chat.py messages --chat-session 841 --limit 5
```

Known local audio examples:

```text
Message/Media/5491161683402-1522716712@g.us/f/1/f1d9801f-c72c-460c-9d80-ab4baf41d3c0.opus
Message/Media/5491161683402-1522716712@g.us/1/d/1dab9793-3266-40bd-a8fe-9e4c8b69f3d0.opus
Message/Media/5491161683402-1522716712@g.us/2/8/2867d317-3544-4502-aa4c-df176a223ad0.opus
```

Assessment: group lookup is simpler than person lookup once the database is readable, because the visible group name is directly in `ZWACHATSESSION.ZPARTNERNAME` and group chats are identifiable by `@g.us`. Person lookup often needs the additional `ContactsV2.sqlite` step to map display names to `ZWHATSAPPID`/`ZLID`.

## Troubleshooting

Local WhatsApp databases can hang on content reads if WhatsApp extensions hold files or if macOS blocks background access.

Diagnostic commands:

```bash
lsof "$HOME/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/ChatStorage.sqlite"
sqlite3 ':memory:' 'select 1;'
```

If `lsof` shows `WhatsApp ServiceExtension`, close WhatsApp. If needed, stop the extension process with user approval, then retry.

If `sqlite3`, `cp`, `rg`, `xxd`, or `find` hang while reading WhatsApp files:

- do not keep stacking more readers;
- kill the stuck readers;
- try again after quitting WhatsApp completely;
- if the issue persists, restart WhatsApp or macOS and retry;
- document the run as blocked by local filesystem/WhatsApp DB access, not as “chat not found.”

Use short `--limit` queries first. Avoid broad scans over `Message/Media` until the target chat JID is known.

## Wiki Handling

For the Riveros Wiki:

- Do not treat local WhatsApp backend files as ingested sources by themselves.
- Export/copy only the specific conversation assets requested by the user.
- Keep original audio/media intact.
- Store extraction manifests separately from transcripts.
- Use `$whatsapp-transcription` for audio files after extraction.
