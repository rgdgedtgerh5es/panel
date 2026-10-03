# vpnstan

پنل مدیریت ساده و فارسی برای 3X-UI v2.9.0، بدون WireGuard.

## هدف

در داشبورد vpnstan مدیر می‌تواند:
- وارد 3X-UI شود
- Inboundها را ببیند
- نوع پروتکل را انتخاب کند
- نام، حجم و مدت اعتبار را وارد کند
- Client را از طریق API خود 3X-UI ایجاد کند
- اطلاعات Client و Subscription ID را ببیند
- Clientهای موجود را فهرست کند

3X-UI خودش credential مناسب پروتکل را ایجاد می‌کند. برای VLESS/VMess شناسهٔ UUID،
برای Trojan/SS/Hysteria2 فیلدهای مخصوص همان پروتکل استفاده می‌شوند.

## نکته مهم Railway

این پروژه از Dockerfile ریشه استفاده می‌کند و برای پنل مدیریت مناسب است.
برای ماندگاری دیتابیس `/etc/x-ui` یک Railway Volume با همین Mount Path اضافه کن.

اما «فقط ساختن دامنه» به تنهایی تضمین نمی‌کند کانفیگ VPN از اینترنت کار کند.
برای عبور ترافیک باید Xray روی یک نود قابل دسترسی اجرا شود و پورت/پروتکل آن
در شبکهٔ مقصد قابل دسترسی باشد. این پروژه عمداً IP، UUID، دامنهٔ جعلی یا لینک
ساختگی تولید نمی‌کند.

اگر 3X-UI روی همین سرویس Railway اجرا شود، محدودیت‌های شبکهٔ Railway باید با
پروتکل و پورت انتخابی سازگار باشد. برای یک نود واقعی، آدرس نود را در inbound
تنظیم کن.

## Deploy

1. محتوای این Repository را در GitHub قرار بده.
2. Railway → New Project → Deploy from GitHub Repo.
3. Repository `vpnstan` را انتخاب کن.
4. Railway باید `Dockerfile` ریشه را تشخیص دهد.
5. در Settings → Networking یک Domain بساز.
6. در Settings → Volumes یک Volume با Mount Path `/etc/x-ui` بساز.
7. دامنه را باز کن.

## Login

ورود داشبورد از همان حساب 3X-UI استفاده می‌کند. رمز در localStorage ذخیره نمی‌شود.

## API

پنل از API داخلی 3X-UI برای:
- `/panel/api/inbounds/list`
- `/panel/api/inbounds/addClient`
- `/panel/api/clients/list`
استفاده می‌کند.

ساختار Client شامل `totalGB`، `expiryTime` و `inboundIds` است؛ این فیلدها در
API رسمی 3X-UI مستند شده‌اند.

## امنیت

این پنل را عمومی و بدون احراز هویت رها نکن. برای حساب 3X-UI رمز قوی بگذار و
در صورت امکان دسترسی مدیریتی را محدود کن.
