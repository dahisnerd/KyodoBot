# ═══════════════════════════════════════════
#  🎲 ألعاب النرد — كلام طبيعي
# ═══════════════════════════════════════════
import random
from kyodo import Router, EventType
from kyodo.objects import WSChatMessage

router = Router()

dice_duel_games = {}
dice_race_games = {}
lucky7_games = {}
dice_sum_games = {}

def roll(n=1): return [random.randint(1, 6) for _ in range(n)]
def demoji(n): return {1:"1️⃣",2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣"}.get(n, str(n))

# ══════════════ رمي نرد (فردي) ══════════════
@router.command(["/نرد", "/roll"])
def cmd_roll(data: WSChatMessage):
    r = roll(2)
    e = " ".join(demoji(x) for x in r)
    data.client.send_message(data.chatId, f"🎲 رميت نردتين!\n{e}\nالمجموع: {sum(r)}")

# ══════════════ دوري النرد (2 لاعبين) ══════════════
@router.command(["/نرد_دوري", "/diceduel"])
def cmd_dd(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in dice_duel_games:
        g = dice_duel_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            g["p2"], g["p2_name"] = uid, name
            data.client.send_message(cid,
                f"🎲 {name} انضم!\n\nاكتب «رمي» لرمي نردك! (7 جولات)\nدور {g['p1_name']}")
        return
    dice_duel_games[cid] = {
        "p1": uid, "p1_name": name, "p2": None, "p2_name": None,
        "p1s": 0, "p2s": 0, "rounds": 0, "turn": uid
    }
    data.client.send_message(cid, f"🎲 {name} بدأ دوري النرد!\n⏳ اكتب /نرد_دوري للانضمام")

# ══════════════ سباق النرد (2+ لاعبين) ══════════════
@router.command(["/سباق", "/dicerace"])
def cmd_race(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in dice_race_games:
        g = dice_race_games[cid]
        if not g["started"] and uid not in g["players"]:
            g["players"][uid] = {"name": name, "pos": 0}
            data.client.send_message(cid,
                f"✅ {name} انضم! ({len(g['players'])} لاعبين)\nاكتب «ابدأ» لبدء السباق!")
        elif g["started"] and uid in g["players"]:
            _race_roll(data, g, uid, cid)
        return
    dice_race_games[cid] = {"players": {uid: {"name": name, "pos": 0}}, "started": False, "target": 50}
    data.client.send_message(cid,
        f"🏁 {name} بدأ سباق النرد! الهدف: 50\n⏳ اكتب /سباق للانضمام ثم «ابدأ» للبدء!")

def _race_roll(data, g, uid, cid):
    v = sum(roll(2))
    g["players"][uid]["pos"] += v
    name = g["players"][uid]["name"]
    board = "\n".join(
        f"{'🏆' if p['pos']>=g['target'] else '🏃'} {p['name']}: {p['pos']}/{g['target']}"
        for p in g["players"].values()
    )
    if g["players"][uid]["pos"] >= g["target"]:
        data.client.send_message(cid, f"🎲 {name} رمى {v}!\n\n{board}\n\n🏆 {name} فاز!")
        del dice_race_games[cid]
    else:
        data.client.send_message(cid, f"🎲 {name} رمى {v}!\n\n{board}\n\nاكتب «رمي» لدورك!")

# ══════════════ Lucky 7 (فردي) ══════════════
@router.command(["/محظوظ", "/lucky7"])
def cmd_l7(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    lucky7_games[cid] = {"player": uid, "score": 0, "rounds": 0}
    data.client.send_message(cid,
        "🍀 لعبة المحظوظ 7!\nإذا مجموع النردتين = 7 تكسب!\n\nاكتب «رمي» للرمي! (5 جولات)")

# ══════════════ تخمين مجموع النرد ══════════════
@router.command(["/مجموع", "/dicesum"])
def cmd_ds(data: WSChatMessage):
    cid = data.chatId
    n = random.randint(2, 4)
    total = sum(roll(n))
    dice_sum_games[cid] = {"a": total, "n": n}
    data.client.send_message(cid,
        f"🎲 {n} نردات مخفية!\nخمّن المجموع (بين {n} و {n*6})\n\nاكتب رقمك!")

# ═══════════════════════════════════════════
#  📨 معالج الرسائل
# ═══════════════════════════════════════════
@router.event(EventType.ChatTextMessage)
def on_dice_msg(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    txt = (data.message.content or "").strip()
    name = data.message.author.nickname or "لاعب"

    if txt == "انهاء":
        for s in [dice_duel_games, dice_race_games, lucky7_games, dice_sum_games]:
            if cid in s: del s[cid]; data.client.send_message(cid, "🚪 تم إنهاء اللعبة!"); return
        return

    # ─── دوري النرد ───
    if cid in dice_duel_games:
        g = dice_duel_games[cid]
        if g["p2"] is None: return
        if txt not in ("رمي", "ارمي", "roll"): return
        if uid != g["turn"]: return

        v = sum(roll(2))
        g["rounds"] += 1
        opp_v = sum(roll(2))
        opp_uid = g["p2"] if uid == g["p1"] else g["p1"]
        opp_name = g["p2_name"] if uid == g["p1"] else g["p1_name"]

        if v > opp_v:
            if uid == g["p1"]: g["p1s"] += 1
            else: g["p2s"] += 1
            w = name
        elif opp_v > v:
            if opp_uid == g["p1"]: g["p1s"] += 1
            else: g["p2s"] += 1
            w = opp_name
        else:
            w = "تعادل"

        score = f"{g['p1_name']} {g['p1s']} - {g['p2s']} {g['p2_name']}"
        res = f"🎲 {name}: {v} ⚔️ {opp_name}: {opp_v}\n{'🏅 '+w if w!='تعادل' else '🤝 تعادل'}\n{score}"

        g["turn"] = opp_uid

        if g["rounds"] >= 7:
            fw = g["p1_name"] if g["p1s"]>g["p2s"] else g["p2_name"] if g["p2s"]>g["p1s"] else None
            end = f"🏆 {fw} فاز!" if fw else "🤝 تعادل!"
            data.client.send_message(cid, f"{res}\n\n🏁 {end}")
            del dice_duel_games[cid]
        else:
            data.client.send_message(cid, f"{res}\n\nدور {opp_name} — اكتب «رمي» ({g['rounds']}/7)")
        return

    # ─── سباق النرد ───
    if cid in dice_race_games:
        g = dice_race_games[cid]
        if not g["started"]:
            if txt in ("ابدأ", "بدء", "start"):
                if len(g["players"]) < 2:
                    data.client.send_message(cid, "⚠️ تحتاج لاعبين على الأقل!")
                    return
                g["started"] = True
                names = ", ".join(p["name"] for p in g["players"].values())
                data.client.send_message(cid, f"🚀 بدأ السباق!\nاللاعبون: {names}\n\nاكتب «رمي» لدورك!")
            return
        if uid in g["players"] and txt in ("رمي", "ارمي", "roll"):
            _race_roll(data, g, uid, cid)
        return

    # ─── Lucky 7 ───
    if cid in lucky7_games:
        g = lucky7_games[cid]
        if uid != g["player"]: return
        if txt not in ("رمي", "ارمي", "roll"): return
        d = roll(2)
        total = sum(d)
        g["rounds"] += 1
        if total == 7: g["score"] += 1; r = "🎉 سبعة! نقطة!"
        else: r = f"😅 المجموع: {total}"
        if g["rounds"] >= 5:
            data.client.send_message(cid,
                f"🎲 {demoji(d[0])} + {demoji(d[1])} = {total}\n{r}\n\n🏁 النتيجة: {g['score']}/5")
            del lucky7_games[cid]
        else:
            data.client.send_message(cid,
                f"🎲 {demoji(d[0])} + {demoji(d[1])} = {total}\n{r}\n📊 {g['score']}/{g['rounds']}\n\nاكتب «رمي» ({g['rounds']}/5)")
        return

    # ─── تخمين المجموع ───
    if cid in dice_sum_games and txt.isdigit():
        g = dice_sum_games[cid]
        if int(txt) == g["a"]:
            data.client.send_message(cid, f"🏆 {name} خمّن! المجموع: {g['a']} 🎉")
            del dice_sum_games[cid]
        else:
            data.client.send_message(cid, "❌ غلط! حاول مرة ثانية!")
        return
