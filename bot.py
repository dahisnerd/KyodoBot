# ═══════════════════════════════════════════════════════════════
#  🎮 بوت الألعاب — Kyodo Games Bot
#  بوت كيودو بالعربي مع ألعاب ثنائية وجماعية
#  يستخدم مكتبة kyodo الرسمية
# ═══════════════════════════════════════════════════════════════

import os
os.environ["PYTHONIOENCODING"] = "utf-8"

import kyodo
from kyodo import Router, EventType
from kyodo.objects import WSChatMessage

from config import EMAIL, PASSWORD, DEVICE_ID, TOKEN, PREFIX, CIRCLE_ID
from welcome import generate_welcome_image, generate_goodbye_image
from games import ALL_ROUTERS

import io
import time

# ═══════════════════════════════════════
#  🔧 إنشاء الراوتر الرئيسي
# ═══════════════════════════════════════
main_router = Router()

# ═══════════════════════════════════════
#  📋 قائمة الأوامر
# ═══════════════════════════════════════
HELP_TEXT = """
🎮 ═══ بوت الألعاب ═══ 🎮

❌⭕ ألعاب الطاولة:
  /xo — إكس أو (2 لاعبين)
  /xo_bot — إكس أو ضد البوت
  /c4 — كونيكت فور (2 لاعبين)

📝 ألعاب الكلمات:
  /مشنقة — لعبة المشنقة
  /مبعثرة — رتّب الحروف
  /سلسلة — سلسلة الكلمات (جماعي)
  /سباق_كتابة — سباق كتابة (2 لاعبين)
  /تخمين — خمّن الكلمة

🔢 ألعاب الأرقام:
  /خمن — خمّن الرقم
  /اعلى — أعلى أم أقل (2 لاعبين)
  /رياضيات — دوري الرياضيات (2 لاعبين)
  /عد — العد الجماعي
  /متسلسلة — أكمل المتسلسلة
  /حساب — حساب سريع

🃏 ألعاب الورق:
  /بلاك — بلاك جاك
  /حرب — حرب الورق (2 لاعبين)
  /لون — أحمر أم أسود
  /ورقة — أعلى ورقة (2 لاعبين)

🎲 ألعاب النرد:
  /نرد — رمي نرد
  /نرد_دوري — دوري النرد (2 لاعبين)
  /سباق — سباق النرد (جماعي)
  /محظوظ — Lucky 7
  /مجموع — خمّن مجموع النرد

💡 ملاحظات:
  • أثناء اللعب اكتب كلام عادي (أرقام، أعلى، أقل، سحب، وقوف...)
  • اكتب «انهاء» لإنهاء أي لعبة نشطة
  • ألعاب الثنائي: اكتب نفس أمر البدء للانضمام!
""".strip()

@main_router.command(["/help", "/مساعدة", "/أوامر", "/اوامر", "/start"])
def cmd_help(data: WSChatMessage):
    data.client.send_message(data.chatId, HELP_TEXT)

@main_router.command(["/ping"])
def cmd_ping(data: WSChatMessage):
    data.client.send_message(data.chatId, "🏓 بونق! البوت شغال!")

# ═══════════════════════════════════════
#  🖼️ ترحيب / توديع
# ═══════════════════════════════════════
import tempfile

def _send_image(client, chat_id, img_buf):
    """يحفظ الصورة بملف مؤقت ويرسلها عبر send_photo"""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(img_buf.read())
    tmp.close()
    try:
        with open(tmp.name, "rb") as f:
            client.send_photo(chat_id, f)
    finally:
        os.remove(tmp.name)

@main_router.event(EventType.ChatMemberJoin)
def on_member_join(data: WSChatMessage):
    try:
        cid = data.chatId
        msg = data.message
        username = msg.author.nickname or "عضو جديد"
        avatar_url = getattr(msg.author, 'icon', None) or getattr(msg.author, 'avatarUrl', None)

        img_buf = generate_welcome_image(username, avatar_url)
        _send_image(data.client, cid, img_buf)
        data.client.send_message(cid,
            f"🌟 أهلاً وسهلاً بك يا {username}!\n"
            f"اكتب /مساعدة لعرض الألعاب المتاحة 🎮")
    except Exception as e:
        print(f"[Welcome Error] {e}")

@main_router.event(EventType.ChatMemberLeave)
def on_member_leave(data: WSChatMessage):
    try:
        cid = data.chatId
        msg = data.message
        username = msg.author.nickname or "عضو"
        avatar_url = getattr(msg.author, 'icon', None) or getattr(msg.author, 'avatarUrl', None)

        img_buf = generate_goodbye_image(username, avatar_url)
        _send_image(data.client, cid, img_buf)
        data.client.send_message(cid, f"👋 {username} غادر المجموعة... نتمنى نشوفه مرة ثانية!")
    except Exception as e:
        print(f"[Goodbye Error] {e}")

# ═══════════════════════════════════════
#  🚀 تشغيل البوت
# ═══════════════════════════════════════
def main():
    print("""
╔═══════════════════════════════════════╗
║     🎮 بوت الألعاب — Kyodo Bot 🎮    ║
║                v1.0.0                ║
╚═══════════════════════════════════════╝
    """)

    # إنشاء العميل
    client = kyodo.Client(
        deviceId=DEVICE_ID,
        socket_enable=True,
        socket_trace=False,
        socket_daemon=False
    )

    # تسجيل الدخول
    print("🔐 جاري تسجيل الدخول...")
    try:
        if TOKEN:
            me = client.login_token(TOKEN)
        else:
            me = client.login(EMAIL, PASSWORD)
        print(f"✅ تم الدخول بنجاح: {me.nickname} ({me.userId})")
    except Exception as e:
        print(f"❌ فشل تسجيل الدخول: {e}")
        return

    # تسجيل الراوترات
    print("📦 جاري تحميل الألعاب...")
    client.add_router(main_router)
    for r in ALL_ROUTERS:
        client.add_router(r)
    print(f"✅ تم تحميل {len(ALL_ROUTERS) + 1} وحدة ألعاب!")

    print("═" * 40)
    print("🟢 البوت شغال! في انتظار الرسائل...")
    print("═" * 40)
    print("📌 اكتب Ctrl+C للإيقاف\n")

    # إبقاء البوت شغال
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🔴 جاري إيقاف البوت...")
        try:
            client.ws_disconnect()
        except:
            pass
        print("👋 البوت توقف. باي!")


if __name__ == "__main__":
    main()
