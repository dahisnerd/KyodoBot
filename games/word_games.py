# ═══════════════════════════════════════════
#  📝 ألعاب الكلمات — كلام طبيعي
# ═══════════════════════════════════════════
import random
from kyodo import Router, EventType
from kyodo.objects import WSChatMessage

router = Router()

hangman_games = {}
scramble_games = {}
chain_games = {}
race_games = {}
hint_games = {}

WORDS = [
    "سيارة","بيت","كتاب","شمس","قمر","نجمة","بحر","جبل","شجرة","فراشة",
    "أسد","فيل","قلم","كرسي","مدرسة","طائرة","سفينة","قطار","حاسوب","هاتف",
    "تلفاز","ثلاجة","مصباح","نافذة","مطار","فندق","مطعم","ملعب","نهر","غابة",
    "تفاحة","موزة","برتقالة","عنب","فراولة","بطيخة","خبز","أرز","لحم","دجاج",
    "سمك","حليب","جبنة","طبيب","مهندس","طيار","شرطي","رسام","كرة","سباحة",
]

SENTENCES = [
    "السماء زرقاء وجميلة","أحب القراءة كثيراً","الرياضة مفيدة للصحة",
    "العلم نور والجهل ظلام","الوقت من ذهب","الصبر مفتاح الفرج",
    "العمل الجاد يؤتي ثماره","الطعام اللذيذ يسعد النفس",
]

HINTS = [
    ("أسد","ملك الغابة"), ("شمس","تشرق كل صباح"), ("كتاب","فيه أوراق ومعرفة"),
    ("طائرة","تطير في السماء"), ("سفينة","تسير على الماء"), ("هاتف","تتصل به بالناس"),
    ("تفاحة","فاكهة حمراء"), ("مدرسة","مكان الدراسة"), ("طبيب","يعالج المرضى"),
    ("بحر","ماء مالح واسع"), ("قمر","يضيء الليل"), ("قطار","يمشي على سكة"),
]

STAGES = [
    "```\n  ___\n |   |\n |\n |\n_|_```",
    "```\n  ___\n |   |\n |   O\n |\n_|_```",
    "```\n  ___\n |   |\n |   O\n |   |\n_|_```",
    "```\n  ___\n |   |\n |   O\n |  /|\n_|_```",
    "```\n  ___\n |   |\n |   O\n |  /|\\\n_|_```",
    "```\n  ___\n |   |\n |   O\n |  /|\\\n | / \\\n_|_```",
]

# ══════════════ المشنقة ══════════════
@router.command(["/مشنقة", "/hangman"])
def cmd_hm(data: WSChatMessage):
    cid = data.chatId
    word = random.choice(WORDS)
    hangman_games[cid] = {"word": word, "guessed": set(), "wrong": 0}
    hidden = " ".join("_" for _ in word)
    data.client.send_message(cid,
        f"🎮 لعبة المشنقة!\n{STAGES[0]}\nالكلمة: {hidden}\n\nاكتب حرف واحد للتخمين!\n❤️ 5 محاولات")

# ══════════════ كلمات مبعثرة ══════════════
@router.command(["/مبعثرة", "/scramble"])
def cmd_sc(data: WSChatMessage):
    cid = data.chatId
    word = random.choice(WORDS)
    s = list(word); random.shuffle(s)
    scramble_games[cid] = {"word": word}
    data.client.send_message(cid, f"🔀 رتّب الحروف!\n\n❓ {''.join(s)}\n\nاكتب الكلمة الصحيحة!")

# ══════════════ سلسلة الكلمات (جماعي) ══════════════
@router.command(["/سلسلة", "/wordchain"])
def cmd_chain(data: WSChatMessage):
    cid = data.chatId
    chain_games[cid] = {"last": None, "used": set(), "last_player": None}
    data.client.send_message(cid,
        "🔗 سلسلة الكلمات!\nكل كلمة تبدأ بآخر حرف من الكلمة السابقة!\n\nابدأ بأي كلمة عربية!")

# ══════════════ سباق الكتابة (2 لاعبين) ══════════════
@router.command(["/سباق_كتابة", "/typerace"])
def cmd_race(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    name = data.message.author.nickname or "لاعب"
    if cid in race_games:
        g = race_games[cid]
        if g["p2"] is None and g["p1"] != uid:
            import time
            g["p2"], g["p2_name"] = uid, name
            g["start"] = time.time()
            data.client.send_message(cid,
                f"🏁 {name} انضم! اللعبة بدأت!\n\n📝 اكتب هذه الجملة:\n\n{g['sentence']}")
        return
    sentence = random.choice(SENTENCES)
    race_games[cid] = {"sentence": sentence, "p1": uid, "p1_name": name,
                        "p2": None, "p2_name": None, "done": [], "start": None}
    data.client.send_message(cid, f"⌨️ {name} بدأ سباق الكتابة!\n⏳ اكتب /سباق_كتابة للانضمام")

# ══════════════ تخمين الكلمة ══════════════
@router.command(["/تخمين", "/wordhint"])
def cmd_hint(data: WSChatMessage):
    cid = data.chatId
    word, hint = random.choice(HINTS)
    hint_games[cid] = {"word": word}
    data.client.send_message(cid, f"🔍 خمّن الكلمة!\n\n💡 {hint}\n\nاكتب إجابتك!")

# ═══════════════════════════════════════════
#  📨 معالج الرسائل
# ═══════════════════════════════════════════
@router.event(EventType.ChatTextMessage)
def on_word_msg(data: WSChatMessage):
    cid, uid = data.chatId, data.message.author.userId
    txt = (data.message.content or "").strip()
    name = data.message.author.nickname or "لاعب"

    if txt == "انهاء":
        for s in [hangman_games, scramble_games, chain_games, race_games, hint_games]:
            if cid in s: del s[cid]; data.client.send_message(cid, "🚪 تم إنهاء اللعبة!"); return
        return

    if txt.startswith("/"): return

    # ─── المشنقة (حرف واحد) ───
    if cid in hangman_games and len(txt) == 1:
        g = hangman_games[cid]
        g["guessed"].add(txt)
        if txt not in g["word"]: g["wrong"] += 1
        hidden = " ".join(c if c in g["guessed"] else "_" for c in g["word"])
        stage = STAGES[min(g["wrong"], 5)]
        if "_" not in hidden:
            data.client.send_message(cid, f"{stage}\n\n✅ الكلمة: {g['word']}\n🏆 فزت!")
            del hangman_games[cid]
        elif g["wrong"] >= 5:
            data.client.send_message(cid, f"{stage}\n\n💀 خسرت! الكلمة: {g['word']}")
            del hangman_games[cid]
        else:
            gs = " ".join(sorted(g["guessed"]))
            data.client.send_message(cid, f"{stage}\nالكلمة: {hidden}\nالحروف: {gs}\n❤️ {5-g['wrong']} محاولات")
        return

    # ─── كلمات مبعثرة ───
    if cid in scramble_games and len(txt) > 1:
        g = scramble_games[cid]
        if txt == g["word"]:
            data.client.send_message(cid, f"✅ صح! الكلمة: {g['word']} 🏆")
            del scramble_games[cid]
        else:
            data.client.send_message(cid, "❌ غلط! حاول مرة ثانية!")
        return

    # ─── سلسلة الكلمات ───
    if cid in chain_games and len(txt) > 1:
        g = chain_games[cid]
        if not all('\u0600' <= c <= '\u06FF' or c == ' ' for c in txt): return
        word = txt.split()[0]
        if word in g["used"]:
            data.client.send_message(cid, f"⛔ الكلمة '{word}' مستخدمة!")
            return
        if g["last"] and word[0] != g["last"]:
            data.client.send_message(cid, f"❌ الكلمة لازم تبدأ بحرف: {g['last']}")
            return
        if uid == g["last_player"]:
            return  # لا تلعب مرتين ورا بعض
        g["used"].add(word); g["last"] = word[-1]; g["last_player"] = uid
        data.client.send_message(cid, f"✅ {name}: {word}\n📝 الحرف الجاي: {g['last']}")
        return

    # ─── سباق الكتابة ───
    if cid in race_games:
        import time
        g = race_games[cid]
        if g["p2"] is None or g["start"] is None: return
        if uid not in (g["p1"], g["p2"]) or uid in g["done"]: return
        if txt == g["sentence"]:
            elapsed = round(time.time() - g["start"], 2)
            g["done"].append(uid)
            place = "🥇" if len(g["done"]) == 1 else "🥈"
            data.client.send_message(cid, f"{place} {name} أنهى في {elapsed} ثانية!")
            if len(g["done"]) == 2: del race_games[cid]
        return

    # ─── تخمين الكلمة ───
    if cid in hint_games and len(txt) > 1:
        g = hint_games[cid]
        if txt == g["word"]:
            data.client.send_message(cid, f"✅ {name} أصاب! الكلمة: {g['word']} 🏆")
            del hint_games[cid]
        else:
            data.client.send_message(cid, "❌ غلط! حاول مرة ثانية!")
        return
