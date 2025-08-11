import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from aiohttp import web
import aiofiles

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN", "7306932481:AAHuckrmMlk4qGicAxqTKfATyEUtNKKObyI")
        self.admin_id = int(os.getenv("ADMIN_ID", "6460744486"))
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/"
        self.webhook_url = os.getenv("WEBHOOK_URL")  # Render tomonidan beriladi
        
        # Courses data
        self.courses = {
            'math_basic': {
                'name': '🔢 0 dan Matematika',
                'description': 'Boshlang\'ich darajadan matematikani o\'rganish uchun maxsus dastur. Asosiy tushunchalardan tortib to murakkab masalalargacha.',
                'price': '500,000 so\'m',
                'duration': '3 oy',
                'features': [
                    '📚 Asosiy tushunchalar',
                    '📈 Step-by-step yondashuv',
                    '💡 Amaliy mashqlar',
                    '🎯 Individual yondashuv'
                ]
            },
            'president_school': {
                'name': '🏛️ Prezident Maktabiga tayyorlov',
                'description': 'Prezident maktablariga kirish imtihonlariga maxsus tayyorlov dasturi. Yuqori sifat va kafolatlangan natija.',
                'price': '800,000 so\'m',
                'duration': '4 oy',
                'features': [
                    '⚡ Intensiv dastur',
                    '📝 Maxsus testlar',
                    '🎖️ Kafolatlangan natija',
                    '👨‍🏫 Tajribali ustozlar'
                ]
            },
            'sat_prep': {
                'name': '🌍 SAT tayyorlov',
                'description': 'Xalqaro SAT imtihonlariga professional tayyorlov. Xorijiy universitetlarga kirish uchun eng yaxshi tayyorgarlik.',
                'price': '1,200,000 so\'m',
                'duration': '6 oy',
                'features': [
                    '🌐 International standart',
                    '📊 Mock testlar',
                    '🧠 Strategik yondashuv',
                    '📈 Yuqori ballar kafolati'
                ]
            },
            'national_cert': {
                'name': '🎓 Milliy Sertifikat tayyorlov',
                'description': 'Milliy sertifikat olish uchun to\'liq tayyorlov dasturi. Barcha yo\'nalishlarda professional tayyorgarlik.',
                'price': '700,000 so\'m',
                'duration': '3 oy',
                'features': [
                    '📖 Barcha mavzular',
                    '🔍 Amaliy testlar',
                    '👥 Ekspert maslahatlari',
                    '🏆 Yuqori o\'tish foizi'
                ]
            }
        }

    async def save_application(self, user_id: int, first_name: str, username: str, course_key: str) -> bool:
        """Save application to JSON file"""
        try:
            application = {
                'user_id': user_id,
                'first_name': first_name,
                'username': username,
                'course_key': course_key,
                'date': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Load existing applications
            applications = []
            try:
                async with aiofiles.open('applications.json', 'r', encoding='utf-8') as f:
                    content = await f.read()
                    applications = json.loads(content) if content else []
            except FileNotFoundError:
                pass
            
            applications.append(application)
            
            # Save updated applications
            async with aiofiles.open('applications.json', 'w', encoding='utf-8') as f:
                await f.write(json.dumps(applications, ensure_ascii=False, indent=2))
            
            return True
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return False

    async def get_applications_count(self) -> int:
        """Get total applications count"""
        try:
            async with aiofiles.open('applications.json', 'r', encoding='utf-8') as f:
                content = await f.read()
                applications = json.loads(content) if content else []
                return len(applications)
        except FileNotFoundError:
            return 0

    async def get_today_applications_count(self) -> int:
        """Get today's applications count"""
        try:
            async with aiofiles.open('applications.json', 'r', encoding='utf-8') as f:
                content = await f.read()
                applications = json.loads(content) if content else []
                today = datetime.now().date().isoformat()
                return sum(1 for app in applications if app['date'].startswith(today))
        except FileNotFoundError:
            return 0

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict:
        """Send message to Telegram"""
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}sendMessage", data=data) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {}

    async def send_photo(self, chat_id: int, photo_url: str, caption: str = '', reply_markup: Optional[Dict] = None) -> Dict:
        """Send photo to Telegram"""
        data = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}sendPhoto", data=data) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return {}

    async def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict:
        """Edit message in Telegram"""
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}editMessageText", data=data) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return {}

    async def set_webhook(self) -> bool:
        """Set webhook URL"""
        if not self.webhook_url:
            logger.warning("Webhook URL not set")
            return False
            
        data = {'url': f"{self.webhook_url}/webhook"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}setWebhook", data=data) as response:
                    result = await response.json()
                    if result.get('ok'):
                        logger.info("Webhook set successfully")
                        return True
                    else:
                        logger.error(f"Failed to set webhook: {result}")
                        return False
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False

    def get_main_keyboard(self) -> Dict:
        """Main menu keyboard"""
        return {
            'inline_keyboard': [
                [
                    {'text': '📚 Kurslar', 'callback_data': 'courses'},
                    {'text': '👨‍🏫 Ustoz haqida', 'callback_data': 'teacher_info'}
                ],
                [
                    {'text': '🏆 Sertifikatlar', 'callback_data': 'certificates'},
                    {'text': '💰 Narxlar', 'callback_data': 'prices'}
                ],
                [
                    {'text': '📞 Aloqa', 'callback_data': 'contact'},
                    {'text': '📝 Ariza qoldirish', 'callback_data': 'apply'}
                ]
            ]
        }

    def get_courses_keyboard(self) -> Dict:
        """Courses keyboard"""
        return {
            'inline_keyboard': [
                [{'text': '🔢 0 dan Matematika', 'callback_data': 'course_math_basic'}],
                [{'text': '🏛️ Prezident Maktabiga tayyorlov', 'callback_data': 'course_president_school'}],
                [{'text': '🌍 SAT tayyorlov', 'callback_data': 'course_sat_prep'}],
                [{'text': '🎓 Milliy Sertifikat tayyorlov', 'callback_data': 'course_national_cert'}],
                [{'text': '🔙 Orqaga', 'callback_data': 'back_to_main'}]
            ]
        }

    def get_course_details_keyboard(self, course_key: str) -> Dict:
        """Course details keyboard"""
        return {
            'inline_keyboard': [
                [{'text': '📝 Kursga yozilish', 'callback_data': f'apply_{course_key}'}],
                [{'text': '👨‍🏫 Ustoz bilan gaplashish', 'callback_data': 'contact_teacher'}],
                [
                    {'text': '🔙 Orqaga', 'callback_data': 'courses'},
                    {'text': '🏠 Bosh menyu', 'callback_data': 'back_to_main'}
                ]
            ]
        }

    def get_back_keyboard(self, back_to: str = 'back_to_main') -> Dict:
        """Back keyboard"""
        return {
            'inline_keyboard': [
                [{'text': '🔙 Orqaga', 'callback_data': back_to}]
            ]
        }

    def get_admin_keyboard(self) -> Dict:
        """Admin keyboard"""
        return {
            'inline_keyboard': [
                [
                    {'text': '📊 Statistika', 'callback_data': 'admin_stats'},
                    {'text': '📋 Arizalar', 'callback_data': 'admin_applications'}
                ],
                [
                    {'text': '📢 Xabar yuborish', 'callback_data': 'admin_broadcast'},
                    {'text': '⚙️ Sozlamalar', 'callback_data': 'admin_settings'}
                ]
            ]
        }

    async def process_message(self, message: Dict) -> None:
        """Process incoming message"""
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '')
        first_name = message['from'].get('first_name', '')
        username = message['from'].get('username', '')

        if text == '/start':
            welcome_text = (
                "🎓 <b>A+ Matematika Kurslariga xush kelibsiz!</b>\n\n"
                "👨‍🏫 <b>Ollashukur Sharofaddinov</b> - 5 yildan ortiq tajribaga ega professional matematik o'qituvchi\n\n"
                "🏆 <b>Bizning yutuqlarimiz:</b>\n"
                "• ⭐ A+ sertifikatli o'qituvchi\n"
                "• 👥 500+ muvaffaqiyatli talaba\n"
                "• 📊 86.31 o'rtacha ball\n"
                "• 💯 100% muvaffaqiyat foizi\n"
                "• 🎯 Individual yondashuv\n\n"
                "Quyidagi tugmalardan birini tanlang:"
            )
            
            await self.send_message(chat_id, welcome_text, self.get_main_keyboard())

        elif text == '/admin' and user_id == self.admin_id:
            admin_text = "🔐 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:"
            await self.send_message(chat_id, admin_text, self.get_admin_keyboard())

    async def process_callback_query(self, callback_query: Dict) -> None:
        """Process callback query"""
        chat_id = callback_query['message']['chat']['id']
        user_id = callback_query['from']['id']
        data = callback_query['data']
        message_id = callback_query['message']['message_id']
        first_name = callback_query['from'].get('first_name', '')
        username = callback_query['from'].get('username', '')

        # Main menu handlers
        if data == 'back_to_main':
            welcome_text = "🏠 <b>Bosh menyu</b>\n\nKerakli bo'limni tanlang:"
            await self.edit_message(chat_id, message_id, welcome_text, self.get_main_keyboard())
            
        elif data == 'courses':
            courses_text = (
                "📚 <b>Mavjud kurslar</b>\n\n"
                "Quyidagi kurslardan birini tanlang va batafsil ma'lumot oling:"
            )
            await self.edit_message(chat_id, message_id, courses_text, self.get_courses_keyboard())
            
        elif data == 'teacher_info':
            teacher_text = (
                "👨‍🏫 <b>Ollashukur Sharofaddinov</b>\n\n"
                "🎓 Professional matematik va tajribali pedagog\n\n"
                "📋 <b>Malakalar:</b>\n"
                "• 📈 5+ yil tajriba\n"
                "• 🏅 A+ sertifikat\n"
                "• ⭐ Oliy toifa\n"
                "• 👥 500+ muvaffaqiyatli talaba\n"
                "• 📊 86.31 o'rtacha ball\n"
                "• 💯 100% muvaffaqiyat foizi\n"
                "• 🎯 Individual yondashuv\n\n"
                "📞 <b>Aloqa:</b> +998 97 602 05 04\n"
                "📱 <b>Telegram:</b> @teacher_0502\n\n"
                "💡 <b>O'qitish metodikasi:</b>\n"
                "• Zamonaviy o'qitish usullari\n"
                "• Interaktiv darslar\n"
                "• Praktik mashqlar ko'pligi"
            )
            await self.edit_message(chat_id, message_id, teacher_text, self.get_back_keyboard())
            
        elif data == 'certificates':
            cert_text = (
                "🏆 <b>Sertifikatlar</b>\n\n"
                "Bizning o'qituvchimiz quyidagi sertifikatlarga ega:\n\n"
                "🏅 <b>Matematika A+ Sertifikati</b>\n"
                "O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi tomonidan berilgan\n\n"
                "🌍 <b>Milliy Sertifikat - Ingliz tili</b>\n"
                "Xalqaro standartlarga mos sertifikat"
            )
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '📄 Matematik sertifikatni ko\'rish', 'callback_data': 'view_math_cert'}],
                    [{'text': '📄 Ingliz tili sertifikatni ko\'rish', 'callback_data': 'view_eng_cert'}],
                    [{'text': '🔙 Orqaga', 'callback_data': 'back_to_main'}]
                ]
            }
            await self.edit_message(chat_id, message_id, cert_text, keyboard)
            
        elif data == 'view_math_cert':
            await self.send_photo(
                chat_id, 
                'https://ollashukur.uz/attached_assets/image_1754476092627.png',
                '🏅 <b>Matematika A+ Sertifikati</b>',
                self.get_back_keyboard()
            )
            
        elif data == 'view_eng_cert':
            await self.send_photo(
                chat_id,
                'https://ollashukur.uz/attached_assets/a5933a15-83b8-47df-83b3-c910a89bdd06_page-0001_1754557612977.jpg',
                '🌍 <b>Milliy Sertifikat - Ingliz tili</b>',
                self.get_back_keyboard()
            )
            
        elif data == 'prices':
            prices_text = "💰 <b>Kurs narxlari</b>\n\n"
            for course in self.courses.values():
                prices_text += f"📚 <b>{course['name']}</b>\n"
                prices_text += f"💵 {course['price']}\n"
                prices_text += f"⏰ Davomiyligi: {course['duration']}\n\n"
            
            prices_text += (
                "💳 <b>To'lov usullari:</b>\n"
                "• 💵 Naqd pul\n"
                "• 💳 Plastik karta\n"
                "• 📱 Click\n"
                "• 💰 Payme\n"
                "• 🏦 Bank o'tkazmasi\n\n"
                "🔥 <b>Chegirmalar:</b>\n"
                "• Bir nechta kursga yozilganda - 10% chegirma\n"
                "• Do'stingizni olib kelganda - 15% chegirma\n"
                "• Erta to'lov - 5% chegirma"
            )
            await self.edit_message(chat_id, message_id, prices_text, self.get_back_keyboard())
            
        elif data == 'contact':
            contact_text = (
                "📞 <b>Biz bilan bog'lanish</b>\n\n"
                "📱 <b>Telefon:</b> +998 97 602 05 04\n"
                "💬 <b>Telegram:</b> @teacher_0502\n"
                "🕐 <b>Ish vaqti:</b> Dushanba - Yakshanba: 8:00 - 21:00\n\n"
                "📍 <b>Manzil:</b> Toshkent shahar\n\n"
                "🆓 Bepul maslahat uchun hoziroq murojaat qiling!\n"
                "📞 Qo'ng'iroq qiling yoki Telegram orqali yozing."
            )
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '👨‍🏫 Ustoz bilan gaplashish', 'callback_data': 'contact_teacher'}],
                    [{'text': '📞 Qo\'ng\'iroq qilish', 'url': 'tel:+998976020504'}],
                    [{'text': '🔙 Orqaga', 'callback_data': 'back_to_main'}]
                ]
            }
            await self.edit_message(chat_id, message_id, contact_text, keyboard)
            
        elif data == 'contact_teacher':
            teacher_contact = (
                "👨‍🏫 <b>Ustoz bilan bevosita aloqa</b>\n\n"
                "Ustoz bilan to'g'ridan-to'g'ri bog'lanish uchun quyidagi havolalardan foydalaning:\n\n"
                "📱 <a href='tel:+998976020504'>+998 97 602 05 04</a>\n"
                "💬 <a href='https://t.me/teacher_0502'>@teacher_0502</a>\n\n"
                "🕐 <b>Javob berish vaqti:</b> 5-10 daqiqa ichida\n"
                "💡 <b>Bepul maslahat:</b> Dastlabki maslahat bepul"
            )
            await self.edit_message(chat_id, message_id, teacher_contact, self.get_back_keyboard())
            
        elif data == 'apply':
            apply_text = "📝 <b>Kursga ariza qoldirish</b>\n\nQaysi kursga yozilmoqchisiz?"
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔢 0 dan Matematika', 'callback_data': 'apply_math_basic'}],
                    [{'text': '🏛️ Prezident Maktabiga tayyorlov', 'callback_data': 'apply_president_school'}],
                    [{'text': '🌍 SAT tayyorlov', 'callback_data': 'apply_sat_prep'}],
                    [{'text': '🎓 Milliy Sertifikat tayyorlov', 'callback_data': 'apply_national_cert'}],
                    [{'text': '🔙 Orqaga', 'callback_data': 'back_to_main'}]
                ]
            }
            await self.edit_message(chat_id, message_id, apply_text, keyboard)

        # Course details
        elif data.startswith('course_'):
            course_key = data[7:]  # Remove 'course_' prefix
            if course_key in self.courses:
                course = self.courses[course_key]
                course_text = f"📚 <b>{course['name']}</b>\n\n"
                course_text += f"📋 <b>Tavsif:</b> {course['description']}\n\n"
                course_text += f"💰 <b>Narxi:</b> {course['price']}\n"
                course_text += f"⏰ <b>Davomiyligi:</b> {course['duration']}\n\n"
                course_text += "✅ <b>Kurs xususiyatlari:</b>\n"
                for feature in course['features']:
                    course_text += f"• {feature}\n"
                
                await self.edit_message(chat_id, message_id, course_text, self.get_course_details_keyboard(course_key))

        # Course applications
        elif data.startswith('apply_'):
            course_key = data[6:]  # Remove 'apply_' prefix
            if course_key in self.courses:
                if await self.save_application(user_id, first_name, username, course_key):
                    course = self.courses[course_key]
                    success_text = (
                        "✅ <b>Ariza muvaffaqiyatli yuborildi!</b>\n\n"
                        f"📚 <b>Kurs:</b> {course['name']}\n"
                        f"👤 <b>Ism:</b> {first_name}\n"
                        f"📅 <b>Vaqt:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                        "📞 Tez orada siz bilan bog'lanamiz!\n"
                        "📱 Yoki bevosita ustoz bilan bog'laning: @teacher_0502\n\n"
                        "⏰ <b>Kutish vaqti:</b> 1-2 soat\n"
                        "🎯 <b>Keyingi qadam:</b> Ustoz siz bilan aloqaga chiqadi"
                    )
                    
                    # Notify admin
                    admin_notification = (
                        "🔔 <b>Yangi ariza!</b>\n\n"
                        f"👤 <b>Ism:</b> {first_name}\n"
                        f"👤 <b>Username:</b> @{username}\n"
                        f"🆔 <b>User ID:</b> {user_id}\n"
                        f"📚 <b>Kurs:</b> {course['name']}\n"
                        f"💰 <b>Narx:</b> {course['price']}\n"
                        f"📅 <b>Vaqt:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    
                    await self.send_message(self.admin_id, admin_notification)
                    await self.edit_message(chat_id, message_id, success_text, self.get_back_keyboard())
                else:
                    error_text = (
                        "❌ <b>Xatolik yuz berdi!</b>\n\n"
                        "Iltimos qaytadan urinib ko'ring yoki ustoz bilan bog'laning:\n"
                        "📱 @teacher_0502"
                    )
                    await self.edit_message(chat_id, message_id, error_text, self.get_back_keyboard())

        # Admin functions
        elif user_id == self.admin_id:
            if data == 'admin_stats':
                total_applications = await self.get_applications_count()
                today_applications = await self.get_today_applications_count()
                
                stats_text = (
                    "📊 <b>Bot statistikasi</b>\n\n"
                    f"📋 <b>Jami arizalar:</b> {total_applications}\n"
                    f"📅 <b>Bugungi arizalar:</b> {today_applications}\n"
                    f"📈 <b>O'rtacha kunlik:</b> {total_applications // 30 if total_applications > 30 else total_applications}\n"
                    f"🕒 <b>Oxirgi yangilanish:</b> {datetime.now().strftime('%H:%M:%S')}"
                )
                
                await self.edit_message(chat_id, message_id, stats_text, self.get_back_keyboard())
                
            elif data == 'admin_applications':
                try:
                    async with aiofiles.open('applications.json', 'r', encoding='utf-8') as f:
                        content = await f.read()
                        applications = json.loads(content) if content else []
                        recent_applications = list(reversed(applications))[:10]  # Last 10
                        
                        if recent_applications:
                            apps_text = "📋 <b>So'nggi 10 ta ariza</b>\n\n"
                            for i, app in enumerate(recent_applications, 1):
                                course_name = self.courses.get(app['course_key'], {}).get('name', app['course_key'])
                                apps_text += f"<b>{i}.</b> 👤 {app['first_name']} (@{app['username']})\n"
                                apps_text += f"📚 {course_name}\n"
                                apps_text += f"📅 {app['date'][:16]}\n"
                                apps_text += f"📊 {app['status'].title()}\n\n"
                        else:
                            apps_text = "📋 <b>Hozircha arizalar yo'q</b>"
                except FileNotFoundError:
                    apps_text = "📋 <b>Hozircha arizalar yo'q</b>"
                
                await self.edit_message(chat_id, message_id, apps_text, self.get_back_keyboard())

    async def process_update(self, update: Dict) -> None:
        """Process webhook update"""
        try:
            if 'message' in update:
                await self.process_message(update['message'])
            elif 'callback_query' in update:
                await self.process_callback_query(update['callback_query'])
        except Exception as e:
            logger.error(f"Error processing update: {e}")

# Initialize bot
bot = TelegramBot()

# Web app setup
app = web.Application()

async def webhook_handler(request):
    """Handle webhook from Telegram"""
    try:
        update = await request.json()
        await bot.process_update(update)
        return web.Response(text='OK')
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text='Error', status=500)

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text='Bot is running!')

async def init_app():
    """Initialize application"""
    # Set webhook
    await bot.set_webhook()
    logger.info("Bot initialized successfully")

# Routes
app.router.add_post('/webhook', webhook_handler)
app.router.add_get('/health', health_check)
app.router.add_get('/', health_check)

# Startup
async def startup(app):
    await init_app()

app.on_startup.append(startup)

if __name__ == '__main__':
    # For local development
    port = int(os.getenv('PORT', 8000))
    web.run_app(app, host='0.0.0.0', port=port)