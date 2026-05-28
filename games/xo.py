# ═══════════════════════════════════════════
#  ❌⭕ ألعاب XO و Connect4
# ═══════════════════════════════════════════
import random
from kyodo import Router, EventType
from kyodo.objects import WSChatMessage

router = Router()

xo_games = {}
xo_bot_games = {}
connect4_games = {}

# ───────── أدوات XO ─────────
def xo_board(board):
    sym = {0: "⬜", 1: "❌", 2: "⭕"}
    rows = []
    for i in range(0, 9, 3):
        rows.append(" ".join(sym[board[i+j]] for j in range(3)))
    nums = "1️⃣2️⃣3️⃣  4️⃣5️⃣6️⃣  7️⃣8️⃣9️⃣"
    return "\n".join(rows)

def xo_winner(b):
    lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,c,d in lines:
        if b[a] == b[c] == b[d] != 0: return b[a]
    return -1 if all(x != 0 for x in b) else 0

def minimax(b, mx):
    w = xo_winner(b)
    if w == 2: return 10
    if w == 1: return -10
    if w == -1: return 0
    if mx:
        best = -999
        for i in range(9):
            if b[i] == 0: b[i] = 2; best = max(best, minimax(b, False)); b[i] = 0
        return best
    else:
        best = 999
        for i in range(9):
            if b[i] == 0: b[i] = 1; best = min(best, minimax(b, True)); b[i] = 0
        return best

def best_move(b):
    best_v, move = -999, -1
    for i in range(9):
        if b[i] == 0: b[i] = 2; v = minimax(b, False); b[i] = 0
        if v > best_v: best_v, move = v, i
    return move

# ───────── XO كلاسيكي (2 لاعبين) ─────────
@router.command(["/xo"])
def cmd_xo(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"

    if cid in xo_games:
        g = xo_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            data.client.send_message(cid,
                f"⭕ {name} انضم!\n\n{xo_board(g['board'])}\n\n"
                f"❌ دور {g['p1_name']} — اكتب رقم من 1 لـ 9")
        else:
            data.client.send_message(cid, "⚠️ اللعبة مشغولة!")
        return

    xo_games[cid] = {"board": [0]*9, "p1": uid, "p1_name": name,
                      "p2": None, "p2_name": None, "turn": uid}
    data.client.send_message(cid,
        f"❌ {name} بدأ لعبة XO!\n\n"
        f"1️⃣2️⃣3️⃣\n4️⃣5️⃣6️⃣\n7️⃣8️⃣9️⃣\n\n"
        f"⏳ ننتظر لاعب ثاني... اكتب /xo")

# ───────── XO ضد البوت ─────────
@router.command(["/xo_bot", "/xobot"])
def cmd_xo_bot(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    xo_bot_games[cid] = {"board": [0]*9, "player": uid, "name": name}
    data.client.send_message(cid,
        f"🤖 {name} ضد البوت!\n\n{xo_board([0]*9)}\n\n❌ دورك — اكتب رقم من 1 لـ 9")

# ───────── معالج رسائل XO ─────────
@router.event(EventType.ChatTextMessage)
def on_xo_msg(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    txt = (data.message.content or "").strip()
    name = data.message.author.nickname or "لاعب"

    if txt == "انهاء" and cid in xo_games:
        del xo_games[cid]
        data.client.send_message(cid, "🚪 تم إنهاء لعبة XO")
        return
    if txt == "انهاء" and cid in xo_bot_games:
        del xo_bot_games[cid]
        data.client.send_message(cid, "🚪 تم إنهاء لعبة XO")
        return

    if not txt.isdigit() or not (1 <= int(txt) <= 9):
        return

    pos = int(txt) - 1

    # XO كلاسيكي
    if cid in xo_games:
        g = xo_games[cid]
        if g["p2"] is None or uid != g["turn"]:
            return
        sym = 1 if uid == g["p1"] else 2
        if g["board"][pos] != 0:
            data.client.send_message(cid, "⚠️ الخانة مشغولة!")
            return
        g["board"][pos] = sym
        w = xo_winner(g["board"])
        b = xo_board(g["board"])
        if w == 1:
            data.client.send_message(cid, f"{b}\n\n🏆 {g['p1_name']} فاز! 🎉"); del xo_games[cid]
        elif w == 2:
            data.client.send_message(cid, f"{b}\n\n🏆 {g['p2_name']} فاز! 🎉"); del xo_games[cid]
        elif w == -1:
            data.client.send_message(cid, f"{b}\n\n🤝 تعادل!"); del xo_games[cid]
        else:
            g["turn"] = g["p2"] if uid == g["p1"] else g["p1"]
            nn = g["p2_name"] if uid == g["p1"] else g["p1_name"]
            e = "⭕" if uid == g["p1"] else "❌"
            data.client.send_message(cid, f"{b}\n\n{e} دور {nn}")
        return

    # XO ضد البوت
    if cid in xo_bot_games:
        g = xo_bot_games[cid]
        if uid != g["player"]:
            return
        if g["board"][pos] != 0:
            data.client.send_message(cid, "⚠️ الخانة مشغولة!"); return
        g["board"][pos] = 1
        w = xo_winner(g["board"])
        if w == 1:
            data.client.send_message(cid, f"{xo_board(g['board'])}\n\n🏆 فزت على البوت! 🎉")
            del xo_bot_games[cid]; return
        if w == -1:
            data.client.send_message(cid, f"{xo_board(g['board'])}\n\n🤝 تعادل!")
            del xo_bot_games[cid]; return
        bp = best_move(g["board"])
        g["board"][bp] = 2
        w = xo_winner(g["board"])
        b = xo_board(g["board"])
        if w == 2:
            data.client.send_message(cid, f"{b}\n\n🤖 البوت فاز! حاول مرة ثانية 😏")
            del xo_bot_games[cid]
        elif w == -1:
            data.client.send_message(cid, f"{b}\n\n🤝 تعادل!"); del xo_bot_games[cid]
        else:
            data.client.send_message(cid, f"{b}\n\n❌ دورك — اكتب رقم من 1 لـ 9")

# ═══════════════════════════════════════
#  🔵 Connect 4 — كونيكت فور (2 لاعبين)
# ═══════════════════════════════════════
R, C = 6, 7
def c4_new(): return [[0]*C for _ in range(R)]
def c4_str(b):
    sym = {0: "⚫", 1: "🔴", 2: "🟡"}
    return "\n".join("".join(sym[c] for c in row) for row in b) + "\n1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"

def c4_drop(b, col, p):
    for r in range(R-1, -1, -1):
        if b[r][col] == 0: b[r][col] = p; return r
    return -1

def c4_win(b, r, c, p):
    for dr, dc in [(0,1),(1,0),(1,1),(1,-1)]:
        cnt = 1
        for s in [1, -1]:
            rr, cc = r+dr*s, c+dc*s
            while 0 <= rr < R and 0 <= cc < C and b[rr][cc] == p: cnt += 1; rr += dr*s; cc += dc*s
        if cnt >= 4: return True
    return False

@router.command(["/connect4", "/c4", "/كونيكت"])
def cmd_c4(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in connect4_games:
        g = connect4_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            data.client.send_message(cid,
                f"🟡 {name} انضم!\n\n{c4_str(g['board'])}\n\n🔴 دور {g['p1_name']} — اكتب رقم العمود (1-7)")
        else:
            data.client.send_message(cid, "⚠️ اللعبة مشغولة!")
        return
    connect4_games[cid] = {"board": c4_new(), "p1": uid, "p1_name": name,
                           "p2": None, "p2_name": None, "turn": uid}
    data.client.send_message(cid,
        f"🔴 {name} بدأ كونيكت فور!\n\n{c4_str(c4_new())}\n\n⏳ ننتظر لاعب ثاني — اكتب /c4")

@router.event(EventType.ChatTextMessage)
def on_c4_msg(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    txt = (data.message.content or "").strip()
    if cid not in connect4_games: return
    g = connect4_games[cid]
    if txt == "انهاء":
        del connect4_games[cid]; data.client.send_message(cid, "🚪 تم إنهاء كونيكت فور"); return
    if g["p2"] is None or uid != g["turn"]: return
    if not txt.isdigit() or not (1 <= int(txt) <= 7): return
    col = int(txt) - 1
    p = 1 if uid == g["p1"] else 2
    r = c4_drop(g["board"], col, p)
    if r == -1: data.client.send_message(cid, "⚠️ العمود ممتلئ!"); return
    b = c4_str(g["board"])
    if c4_win(g["board"], r, col, p):
        wn = g["p1_name"] if p == 1 else g["p2_name"]
        data.client.send_message(cid, f"{b}\n\n🏆 {wn} فاز! 🎉"); del connect4_games[cid]
    elif all(g["board"][0][c] != 0 for c in range(C)):
        data.client.send_message(cid, f"{b}\n\n🤝 تعادل!"); del connect4_games[cid]
    else:
        g["turn"] = g["p2"] if uid == g["p1"] else g["p1"]
        nn = g["p2_name"] if uid == g["p1"] else g["p1_name"]
        e = "🟡" if uid == g["p1"] else "🔴"
        data.client.send_message(cid, f"{b}\n\n{e} دور {nn} — اكتب رقم العمود")
