BULOCHKA CONTROL — 1-bosqich prototipi

Bu boshlang'ich web-ilova: admin/ishchi login, do'kon qo'shish, GPS koordinatasini olish, Toshkent xaritasida do'konlarni ko'rsatish va audit jurnali.

MUHIM:
- Birinchi admin login: admin
- Vaqtinchalik parol: deploy paytida INITIAL_ADMIN_PASSWORD muhit o'zgaruvchisiga siz belgilaydigan parol.
- SECRET_KEY ni Render'da alohida, tasodifiy maxfiy qiymat qilib qo'ying.
- DATABASE_URL uchun Render PostgreSQL kerak. SQLite faqat mahalliy sinov uchun.
- Haqiqiy savdo/ombor/vazvrat/moliya modullari hali qo'shilmagan. Bu bosqichni sinovdan o'tkazgandan keyin navbatma-navbat qo'shiladi.
- GPS brauzerda faqat foydalanuvchi tugmani bosib ruxsat berganda olinadi.

Render sozlamalari:
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Environment:
SECRET_KEY = uzun tasodifiy maxfiy qiymat
INITIAL_ADMIN_PASSWORD = kamida 10 belgili kuchli parol
DATABASE_URL = Render PostgreSQL connection string

Eski Telegram bot repozitoriysini almashtirmang. Bu alohida yangi loyiha sifatida deploy qilinishi kerak.
