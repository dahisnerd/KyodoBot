# ═══════════════════════════════════════════
#  🃏 ألعاب الورق — كلام طبيعي
# ═══════════════════════════════════════════
import random
from kyodo import Router, EventType
from kyodo.objects import WSChatMessage

router = Router()

SUITS = ["♠️","♥️","♦️","♣️"]
RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
VAL = {"A":11,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":10,"Q":10,"K":10}
RANK_ORDER = {"A":14,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":11,"Q":12,"K":13}

def deck():
    d = [(r,s) for r in RANKS for s in SUITS]; random.shuffle(d); return d
def cstr(c): return f"{c[0]}{c[1]}"
def hval(h):
    t = sum(VAL[c[0]] for c in h); a = sum(1 for c in h if c[0]=="A")
    while t > 21 and a: t -= 10; a -= 1
    return t

bj_games = {}
war_games = {}
rb_games = {}
hc_games = {}

# ══════════════ بلاك جاك ══════════════
@router.command(["/بلاك", "/blackjack"])
def cmd_bj(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    d = deck()
    ph, dh = [d.pop(), d.pop()], [d.pop(), d.pop()]
    bj_games[cid] = {"player": uid, "deck": d, "ph": ph, "dh": dh}
    data.client.send_message(cid,
        f"🃏 بلاك جاك!\n\n🎴 ورقك: {' '.join(cstr(c) for c in ph)} ({hval(ph)})\n"
        f"🤵 الديلر: {cstr(dh[0])} + ؟\n\nاكتب «سحب» أو «وقوف»")

# ══════════════ حرب الورق (2 لاعبين) ══════════════
@router.command(["/حرب", "/cardwar"])
def cmd_war(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in war_games:
        g = war_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            data.client.send_message(cid,
                f"⚔️ {name} انضم!\n\nاكتب «سحب» لبدء الجولة! (10 جولات)")
        return
    war_games[cid] = {"p1": uid, "p1_name": name, "p2": None, "p2_name": None,
                       "p1s": 0, "p2s": 0, "rounds": 0, "deck": deck()}
    data.client.send_message(cid, f"⚔️ {name} بدأ حرب الورق!\n⏳ اكتب /حرب للانضمام")

# ══════════════ أحمر أو أسود ══════════════
@router.command(["/لون", "/redblack"])
def cmd_rb(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    rb_games[cid] = {"player": uid, "score": 0, "rounds": 0}
    data.client.send_message(cid, "🔴⚫ لون الورقة الجاية أحمر ولا أسود؟\n\nاكتب «أحمر» أو «أسود» (7 جولات)")

# ══════════════ أعلى ورقة (2 لاعبين) ══════════════
@router.command(["/ورقة", "/highcard"])
def cmd_hc(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in hc_games:
        g = hc_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            data.client.send_message(cid, f"🃏 {name} انضم!\nاكتب «سحب» لبدء الجولة!")
        return
    hc_games[cid] = {"p1": uid, "p1_name": name, "p2": None, "p2_name": None,
                      "p1s": 0, "p2s": 0, "rounds": 0}
    data.client.send_message(cid, f"🃏 {name} بدأ أعلى ورقة!\n⏳ اكتب /ورقة للانضمام")

# ═══════════════════════════════════════════
#  📨 معالج الرسائل
# ═══════════════════════════════════════════
@router.event(EventType.ChatTextMessage)
def on_card_msg(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    txt = (data.message.content or "").strip()
    name = data.message.author.nickname or "لاعب"

    if txt == "انهاء":
        for s in [bj_games, war_games, rb_games, hc_games]:
            if cid in s: del s[cid]; data.client.send_message(cid, "🚪 تم إنهاء اللعبة!"); return
        return

    # ─── بلاك جاك ───
    if cid in bj_games:
        g = bj_games[cid]
        if uid != g["player"]: return

        if txt in ("سحب", "hit", "كارت"):
            g["ph"].append(g["deck"].pop())
            pv = hval(g["ph"])
            ph_str = " ".join(cstr(c) for c in g["ph"])
            if pv > 21:
                data.client.send_message(cid, f"🎴 {ph_str} ({pv})\n💥 تجاوزت 21! خسرت!")
                del bj_games[cid]
            elif pv == 21:
                data.client.send_message(cid, f"🎴 {ph_str} ({pv})\n🎉 بلاك جاك!")
                del bj_games[cid]
            else:
                data.client.send_message(cid, f"🎴 {ph_str} ({pv})\n\nاكتب «سحب» أو «وقوف»")
            return

        if txt in ("وقوف", "stand", "كفاية"):
            while hval(g["dh"]) < 17: g["dh"].append(g["deck"].pop())
            pv, dv = hval(g["ph"]), hval(g["dh"])
            ph_str = " ".join(cstr(c) for c in g["ph"])
            dh_str = " ".join(cstr(c) for c in g["dh"])
            if dv > 21 or pv > dv: res = "🏆 فزت!"
            elif pv == dv: res = "🤝 تعادل!"
            else: res = "💔 الديلر فاز!"
            data.client.send_message(cid,
                f"🎴 ورقك: {ph_str} ({pv})\n🤵 الديلر: {dh_str} ({dv})\n\n{res}")
            del bj_games[cid]
            return

    # ─── حرب الورق ───
    if cid in war_games:
        g = war_games[cid]
        if g["p2"] is None: return
        if txt not in ("سحب", "draw", "جولة"): return
        if not g["deck"] or len(g["deck"]) < 2: g["deck"] = deck()
        c1, c2 = g["deck"].pop(), g["deck"].pop()
        v1, v2 = RANK_ORDER[c1[0]], RANK_ORDER[c2[0]]
        g["rounds"] += 1
        if v1 > v2: g["p1s"] += 1; w = g["p1_name"]
        elif v2 > v1: g["p2s"] += 1; w = g["p2_name"]
        else: w = "تعادل"
        score = f"{g['p1_name']} {g['p1s']} - {g['p2s']} {g['p2_name']}"
        res = f"🃏 {g['p1_name']}: {cstr(c1)} ⚔️ {g['p2_name']}: {cstr(c2)}\n"
        res += f"{'🏅 '+w if w!='تعادل' else '🤝 تعادل'}\n{score}"
        if g["rounds"] >= 10:
            fw = g["p1_name"] if g["p1s"]>g["p2s"] else g["p2_name"] if g["p2s"]>g["p1s"] else None
            end = f"\n\n🏆 {fw} فاز بالمباراة!" if fw else "\n\n🤝 تعادل بالمباراة!"
            data.client.send_message(cid, res + end); del war_games[cid]
        else:
            data.client.send_message(cid, f"{res}\n\nاكتب «سحب» للجولة التالية ({g['rounds']}/10)")
        return

    # ─── أحمر أو أسود ───
    if cid in rb_games:
        g = rb_games[cid]
        if uid != g["player"]: return
        choice = None
        if txt in ("أحمر", "احمر", "red"): choice = "red"
        elif txt in ("أسود", "اسود", "black"): choice = "black"
        if choice is None: return
        card = (random.choice(RANKS), random.choice(SUITS))
        actual = "red" if card[1] in ["♥️","♦️"] else "black"
        g["rounds"] += 1
        if choice == actual: g["score"] += 1; r = "✅ صح!"
        else: r = "❌ غلط!"
        ac = "أحمر 🔴" if actual == "red" else "أسود ⚫"
        if g["rounds"] >= 7:
            data.client.send_message(cid,
                f"{r} الورقة: {cstr(card)} ({ac})\n\n🏁 النتيجة: {g['score']}/7 {'🏆' if g['score']>=5 else '😅'}")
            del rb_games[cid]
        else:
            data.client.send_message(cid,
                f"{r} الورقة: {cstr(card)} ({ac})\n📊 {g['score']}/{g['rounds']}\n\n«أحمر» أو «أسود»؟ ({g['rounds']}/7)")
        return

    # ─── أعلى ورقة ───
    if cid in hc_games:
        g = hc_games[cid]
        if g["p2"] is None: return
        if txt not in ("سحب", "draw", "جولة"): return
        c1 = (random.choice(RANKS), random.choice(SUITS))
        c2 = (random.choice(RANKS), random.choice(SUITS))
        v1, v2 = RANK_ORDER[c1[0]], RANK_ORDER[c2[0]]
        g["rounds"] += 1
        if v1 > v2: g["p1s"] += 1; w = g["p1_name"]
        elif v2 > v1: g["p2s"] += 1; w = g["p2_name"]
        else: w = "تعادل"
        score = f"{g['p1_name']} {g['p1s']} - {g['p2s']} {g['p2_name']}"
        msg = f"🃏 {g['p1_name']}: {cstr(c1)} | {g['p2_name']}: {cstr(c2)}\n{'🏅 '+w if w!='تعادل' else '🤝 تعادل'}\n{score}"
        if g["rounds"] >= 10:
            fw = g["p1_name"] if g["p1s"]>g["p2s"] else g["p2_name"] if g["p2s"]>g["p1s"] else None
            end = f"\n\n🏆 {fw} فاز!" if fw else "\n\n🤝 تعادل!"
            data.client.send_message(cid, msg + end); del hc_games[cid]
        else:
            data.client.send_message(cid, f"{msg}\n\nاكتب «سحب» ({g['rounds']}/10)")
        return
