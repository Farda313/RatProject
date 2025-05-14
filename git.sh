# نصب git
pkg install git

# پیکربندی اولیه
git config --global user.name "Farda313"
git config --global user.email "farda8106@gmail.com"

# ایجاد ریپوی جدید
cd RatProject
git init
git add .
git commit -m "اولین کامیت"

# اتصال به ریپوی GitHub (قبل از اجرا ریپو را در GitHub ایجاد کنید)
git remote add origin https://github.com/Farda313/Ratpy.git
git branch -M main
git push -u origin main
