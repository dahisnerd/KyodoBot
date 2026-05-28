# ═══════════════════════════════════════════
#  🔢 ألعاب الأرقام — كلام طبيعي بدون أوامر
# ═══════════════════════════════════════════
import random, operator, time
from kyodo import Router, EventType
from kyodo.objects import WSChatMessage

router = Router()

guess_games = {}
higher_lower_games = {}
math_duel_games = {}
count_up_games = {}
sequence_games = {}
quick_math_games = {}

def _math_q():
    ops = [("+", operator.add), ("-", operator.sub), ("×", operator.mul)]
    s, f = random.choice(ops)
    a, b = (random.randint(1,12), random.randint(1,12)) if s == "×" else (random.randint(1,30), random.randint(1,30))
    if s == "-" and a < b: a, b = b, a
    return f"{a} {s} {b}", f(a, b)

# ══════════════ خمّن الرقم ══════════════
@router.command(["/خمن", "/guess"])
def cmd_guess(data: WSChatMessage):
    cid = data.chatId
    num = random.randint(1, 100)
    guess_games[cid] = {"num": num, "tries": 0}
    data.client.send_message(cid, "🎯 خمّن رقم بين 1 و 100!\n\nاكتب رقمك...")

# ══════════════ أعلى أم أقل (2 لاعبين) ══════════════
@router.command(["/اعلى", "/higher"])
def cmd_higher(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in higher_lower_games:
        g = higher_lower_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            data.client.send_message(cid,
                f"🎲 {name} انضم!\n\nالرقم: {g['current']}\n"
                f"الرقم الجاي أعلى ولا أقل؟\n\n"
                f"دور {g['p1_name']} — اكتب «أعلى» أو «أقل»")
        return
    higher_lower_games[cid] = {
        "current": random.randint(1,100), "p1": uid, "p1_name": name,
        "p2": None, "p2_name": None, "turn": uid,
        "p1_score": 0, "p2_score": 0, "rounds": 0
    }
    data.client.send_message(cid, f"🎲 {name} بدأ أعلى/أقل!\n⏳ ننتظر لاعب ثاني — اكتب /اعلى")

# ══════════════ دوري الرياضيات (2 لاعبين) ══════════════
@router.command(["/رياضيات", "/mathduel"])
def cmd_math(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in math_duel_games:
        g = math_duel_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            q, a = _math_q()
            g["q"], g["a"] = q, a
            data.client.send_message(cid,
                f"🧮 {name} انضم! بدأ الدوري!\n\n❓ {q} = ؟\n\nأسرع واحد يجاوب!")
        return
    math_duel_games[cid] = {
        "p1": uid, "p1_name": name, "p2": None, "p2_name": None,
        "p1_score": 0, "p2_score": 0, "rounds": 0, "q": None, "a": None
    }
    data.client.send_message(cid, f"🧮 {name} بدأ دوري الرياضيات!\n⏳ اكتب /رياضيات للانضمام")

# ══════════════ العد الجماعي ══════════════
@router.command(["/عد", "/counting"])
def cmd_count(data: WSChatMessage):
    cid = data.chatId
    count_up_games[cid] = {"n": 0, "last": None}
    data.client.send_message(cid, "🔢 بدأ العد الجماعي!\nالقاعدة: كل واحد يكتب الرقم التالي!\n⚠️ ما تعد مرتين ورا بعض!\n\nابدأ من 1!")

# ══════════════ أكمل المتسلسلة ══════════════
SEQS = [
    ([2,4,6,8,10], 12), ([1,3,5,7,9], 11), ([1,4,9,16,25], 36),
    ([1,1,2,3,5], 8), ([2,4,8,16,32], 64), ([5,10,15,20,25], 30),
    ([1,8,27,64,125], 216), ([100,90,80,70,60], 50),
    ([3,6,9,12,15], 18), ([10,20,30,40,50], 60),
]

@router.command(["/متسلسلة", "/sequence"])
def cmd_seq(data: WSChatMessage):
    cid = data.chatId
    seq, ans = random.choice(SEQS)
    sequence_games[cid] = {"a": ans}
    s = " ، ".join(str(x) for x in seq)
    data.client.send_message(cid, f"🔢 أكمل المتسلسلة!\n\n{s} ، ؟\n\nاكتب الرقم التالي!")

# ══════════════ حساب سريع ══════════════
@router.command(["/حساب", "/quickmath"])
def cmd_qm(data: WSChatMessage):
    cid = data.chatId
    q, a = _math_q()
    quick_math_games[cid] = {"a": a}
    data.client.send_message(cid, f"⚡ حساب سريع!\n\n{q} = ؟\n\nأول واحد يجاوب يكسب!")

# ═══════════════════════════════════════════
#  📨 معالج الرسائل — كل الإجابات هنا
# ═══════════════════════════════════════════
@router.event(EventType.ChatTextMessage)
def on_number_msg(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    txt = (data.message.content or "").strip()
    name = data.message.author.nickname or "لاعب"

    # ─── انهاء أي لعبة ───
    if txt == "انهاء":
        for store in [guess_games, higher_lower_games, math_duel_games, count_up_games, sequence_games, quick_math_games]:
            if cid in store:
                del store[cid]
                data.client.send_message(cid, "🚪 تم إنهاء اللعبة!")
                return
        return

    # ─── خمّن الرقم ───
    if cid in guess_games and txt.lstrip("-").isdigit():
        g = guess_games[cid]
        g["tries"] += 1
        n = int(txt)
        if n == g["num"]:
            data.client.send_message(cid, f"🏆 {name} خمّن الرقم {n} في {g['tries']} محاولة! 🎉")
            del guess_games[cid]
        elif n < g["num"]:
            data.client.send_message(cid, f"⬆️ أكبر! (محاولة {g['tries']})")
        else:
            data.client.send_message(cid, f"⬇️ أصغر! (محاولة {g['tries']})")
        return

    # ─── أعلى أم أقل (كلام طبيعي) ───
    if cid in higher_lower_games:
        g = higher_lower_games[cid]
        if g["p2"] is None:
            return
        if uid != g["turn"]:
            return
        choice = None
        if txt in ("أعلى", "اعلى", "فوق", "higher", "up"):
            choice = True
        elif txt in ("أقل", "اقل", "تحت", "lower", "down"):
            choice = False
        if choice is None:
            return

        old = g["current"]
        new = random.randint(1, 100)
        g["current"] = new
        g["rounds"] += 1
        correct = (choice == (new > old))

        if correct:
            if uid == g["p1"]: g["p1_score"] += 1
            else: g["p2_score"] += 1
            res = "✅ صح!"
        else:
            res = "❌ غلط!"

        g["turn"] = g["p2"] if uid == g["p1"] else g["p1"]
        next_n = g["p2_name"] if uid == g["p1"] else g["p1_name"]
        score = f"{g['p1_name']} {g['p1_score']} - {g['p2_score']} {g['p2_name']}"

        if g["rounds"] >= 10:
            w = g["p1_name"] if g["p1_score"] > g["p2_score"] else g["p2_name"] if g["p2_score"] > g["p1_score"] else None
            end = f"🏆 {w} فاز!" if w else "🤝 تعادل!"
            data.client.send_message(cid, f"{res} ({old} → {new})\n{score}\n\n🏁 {end}")
            del higher_lower_games[cid]
        else:
            data.client.send_message(cid,
                f"{res} ({old} → {new})\n📊 {score}\n\n"
                f"الرقم الحالي: {new}\n"
                f"دور {next_n} — اكتب «أعلى» أو «أقل»")
        return

    # ─── دوري الرياضيات ───
    if cid in math_duel_games:
        g = math_duel_games[cid]
        if g["p2"] is None or g["a"] is None:
            return
        if uid not in (g["p1"], g["p2"]):
            return
        try:
            ans = int(txt)
        except:
            return
        if ans != g["a"]:
            return

        if uid == g["p1"]: g["p1_score"] += 1
        else: g["p2_score"] += 1
        g["rounds"] += 1
        score = f"{g['p1_name']} {g['p1_score']} - {g['p2_score']} {g['p2_name']}"

        if g["rounds"] >= 10:
            w = g["p1_name"] if g["p1_score"] > g["p2_score"] else g["p2_name"] if g["p2_score"] > g["p1_score"] else None
            end = f"🏆 {w} فاز!" if w else "🤝 تعادل!"
            data.client.send_message(cid, f"✅ {name} أجاب!\n{score}\n\n🏁 {end}")
            del math_duel_games[cid]
        else:
            q, a = _math_q()
            g["q"], g["a"] = q, a
            data.client.send_message(cid, f"✅ {name} أجاب! +1\n{score}\n\n❓ {q} = ؟")
        return

    # ─── العد الجماعي ───
    if cid in count_up_games and txt.isdigit():
        g = count_up_games[cid]
        if uid == g["last"]:
            return
        if int(txt) == g["n"] + 1:
            g["n"] += 1
            g["last"] = uid
            if g["n"] % 50 == 0:
                data.client.send_message(cid, f"🎉 وصلتوا {g['n']}! ماشاء الله!")
        elif int(txt) != g["n"]:
            data.client.send_message(cid, f"⛔ {name} كسر السلسلة عند {g['n']}!\n🔄 نبدأ من الصفر!")
            g["n"], g["last"] = 0, None
        return

    # ─── متسلسلة ───
    if cid in sequence_games and txt.lstrip("-").isdigit():
        g = sequence_games[cid]
        if int(txt) == g["a"]:
            data.client.send_message(cid, f"🏆 {name} أصاب! الجواب: {g['a']} 🎉")
            del sequence_games[cid]
        else:
            data.client.send_message(cid, "❌ غلط! حاول مرة ثانية!")
        return

    # ─── حساب سريع ───
    if cid in quick_math_games and txt.lstrip("-").isdigit():
        g = quick_math_games[cid]
        if int(txt) == g["a"]:
            data.client.send_message(cid, f"⚡ {name} هو الأسرع! الجواب: {g['a']} 🏆")
            del quick_math_games[cid]
        return
