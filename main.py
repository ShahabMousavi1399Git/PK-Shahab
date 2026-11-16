# K.py
import os
import auth
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from bidi.algorithm import get_display
import arabic_reshaper
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy_garden.mapview import MapView
from plyer import gps
from kivy import Config
from kivy.clock import mainthread
from kivy.utils import platform
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.snackbar import MDSnackbarText
from kivy.metrics import dp
from kivy.core.text import LabelBase
import shutil
Window.size = (350, 600)

class LoginScreen(MDScreen):
    pass

class AdminScreen(MDScreen):
    pass

class UserScreen(MDScreen):
    pass

class GuestRegisterScreen(MDScreen):
    pass

class HostRegisterScreen(MDScreen):
    pass

class HostServicesScreen(MDScreen):
    pass

class HostDemandScreen(MDScreen):
    pass

class PersianInput(TextInput):
    def __init__(self, **kwargs):
        self._raw_text = kwargs.get('text', '')
        if self._raw_text:
            reshaped = arabic_reshaper.reshape(self._raw_text)
            bidi_text = get_display(reshaped)
            kwargs['text'] = bidi_text
        else:
            kwargs['text'] = ""
        super().__init__(**kwargs)
    def insert_text(self, substring, from_undo=False):
        current_raw = self._raw_text
        new_raw_text = current_raw + substring
        reshaped = arabic_reshaper.reshape(new_raw_text)
        bidi_text = get_display(reshaped)
        self.text = bidi_text
        self._raw_text = new_raw_text
        self.cursor = (len(bidi_text), 0)
    def do_backspace(self, from_undo=False, mode='bkspc'):
        self._raw_text = self._raw_text[:-1]
        reshaped = arabic_reshaper.reshape(self._raw_text)
        bidi_text = get_display(reshaped)
        self.text = bidi_text
        self.cursor = (len(bidi_text), 0)

class RestaurantApp(MDApp):
    current_user = None
    current_role = None
    selected_category = "رستوران"
    current_lat = None
    current_lon = None
    selected_image_path = None
    file_manager = None
    current_date_display = StringProperty("") 
    CONTRACT_HOST_TEXT = (
        "1. این قرارداد جهت رزرو می باشد.\n"
        "2. این قرارداد مبین تسویه نهایی توسط مهمان نمی باشد.\n"
        "3. در این قرارداد مبلغ دریافتی از میهمان بصورت پایه و اولیه می باشد\n و تسویه در هنگام حضور مهمان می باشد.\n"
        "4. پس از واریز از سوی مهمان در صورت عدم حضور مهمان\n مبلغ عودت به مهمان نخواهد شد.\n"
        "5. تمامی بندهای فوق به منزله آگاهی میزبان از شروط قرارداد می باشد."
    )
    CONTRACT_GUEST_TEXT = (
        "1. این قرارداد جهت رزرو می باشد.\n"
        "2. این قرارداد مبین تسویه نهایی توسط مهمان نمی باشد.\n"
        "3. در این قرارداد مبلغ دریافتی از میهمان بصورت پایه و اولیه می باشد\n و تسویه در هنگام حضور مهمان می باشد.\n"
        "4. پس از واریز از سوی مهمان در صورت عدم حضور مهمان\n مبلغ عودت به مهمان نخواهد شد.\n"
        "5. تمامی بندهای فوق به منزله آگاهی مهمان از شروط قرارداد می باشد."
    )
    LabelBase.register(
        name="Vazirmatn",
        fn_regular="Vazirmatn.ttf"
    )
    host_nav_text = StringProperty("میزبان شوید")
    host_nav_icon = StringProperty("home-plus-outline")
    def fa(self, text):
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
        english_numbers = "0123456789"
        translation_table = str.maketrans(english_numbers, persian_numbers)
        text_with_persian_nums = str(text).translate(translation_table)
        reshaped_text = arabic_reshaper.reshape(text_with_persian_nums)
        return get_display(reshaped_text)
    def build(self):
        from kivy.core.text import LabelBase
        from kivymd.font_definitions import theme_font_styles
        LabelBase.register(name="Vazirmatn", fn_regular="Vazirmatn.ttf")
        for category in theme_font_styles.values():
            for size_style in category.values():
                if "font-name" in size_style and size_style["font-name"] == "Roboto":
                    size_style["font-name"] = "Vazirmatn"
        self.root = Builder.load_file("k.kv")
        return self.root
    def show_message(self, text):
        from kivymd.uix.dialog import (
            MDDialog, 
            MDDialogSupportingText, 
            MDDialogButtonContainer
        )
        from kivymd.uix.button import MDButton, MDButtonText
        btn_confirm = MDButton(
            style="filled",
            on_release=lambda x: dialog.dismiss()
        )
        btn_confirm.add_widget(MDButtonText(text=self.fa("تایید"), font_name="Vazirmatn.ttf"))
        dialog = MDDialog(
            MDDialogSupportingText(
                text=self.fa(text),
                font_name="Vazirmatn.ttf",
                halign="center",
            ),
            MDDialogButtonContainer(
                btn_confirm
            ),
        )
        dialog.open()
    def login(self):
        login_screen = self.root.get_screen('login_screen')
        username = login_screen.ids.login_user.text.strip()
        password = login_screen.ids.login_pass.text.strip()
        try:
            role = auth.check_login(username, password)
        except Exception as e:
            self.show_message(f"خطای دیتابیس: {e}")
            return
        if role:
            self.current_user = username
            self.current_role = role
            if role == "admin":
                self.host_nav_text = "میزبانی کنید"
                self.host_nav_icon = "account-tie-outline"
            else:
                self.host_nav_text = "میزبان شوید"
                self.host_nav_icon = "home-plus-outline"
            login_screen.ids.login_user.text = ""
            login_screen.ids.login_pass.text = ""
            self.root.current = "user_screen"
            self.load_restaurants()
        else:
            self.show_message("نام کاربری یا رمز عبور اشتباه است!")
    def logout(self):
        self.current_user = None
        self.current_role = None
        self.host_nav_text = "میزبان شوید"
        self.host_nav_icon = "home-plus-outline"
        self.root.current = "login_screen"
    def handle_host_click(self):
        if self.current_role == "admin":
            self.go_host_services()
        else:
            self.go_host_register()
    def add_new_category(self):
        from kivy.uix.textinput import TextInput
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivy.uix.modalview import ModalView
        from kivy.metrics import dp
        from kivymd.uix.button import MDButton, MDButtonText
        self.new_cat_field = TextInput(
            font_name="Vazirmatn.ttf",
            halign="right",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0, 0, 0, 1),
            padding=[10, 10, 10, 10]
        )
        box = MDBoxLayout(
            orientation="vertical", 
            spacing="10dp",
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height="220dp"
        )
        title_label = MDLabel(
            text=self.fa("افزودن گروه جدید"),
            font_name="Vazirmatn.ttf",
            font_size="11sp",
            halign="right",
            size_hint_y=None,
            height="30dp",
        )
        field_label = MDLabel(
            text=self.fa("نام گروه جدید:"),
            font_name="Vazirmatn.ttf",
            font_size="11sp", 
            halign="right",
            size_hint_y=None,
            height="20dp",
        )
        btn_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="50dp",
            spacing="10dp",
            pos_hint={"center_x": .5}
        )
        def save_category(instance):
            if hasattr(self.new_cat_field, '_raw_text') and self.new_cat_field._raw_text:
                new_name = self.new_cat_field._raw_text.strip()
            else:
                new_name = self.new_cat_field.text.strip()
            if new_name:
                admin_screen = self.root.get_screen('admin_screen')
                category_btn = admin_screen.ids.category_button
                for child in category_btn.children:
                    if isinstance(child, MDButtonText):
                        child.text = self.fa(new_name)
                        break
                self.selected_category = new_name
                self.modal.dismiss()
            else:
                self.show_message("لطفا نام گروه را وارد کنید!")
        btn_cancel = MDButton(style="text", on_release=lambda x: self.modal.dismiss())
        btn_cancel.add_widget(MDButtonText(text=self.fa("انصراف"), font_name="Vazirmatn.ttf"))
        btn_save = MDButton(style="filled", on_release=save_category)
        btn_save.add_widget(MDButtonText(text=self.fa("ثبت"), font_name="Vazirmatn.ttf"))
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_save)
        box.add_widget(title_label)
        box.add_widget(field_label)
        box.add_widget(self.new_cat_field)
        box.add_widget(btn_box)
        self.modal = ModalView(size_hint=(0.9, None), height="250dp", background_color=(1, 1, 1, 1))
        card = MDCard(
            orientation="vertical",
            padding=dp(15),
            radius=[15, 15, 15, 15],
            elevation=0,
            md_bg_color=(1, 1, 1, 1),
            theme_bg_color="Custom"
        )
        card.add_widget(box)
        self.modal.add_widget(card)
        self.modal.open()
    def open_category_menu(self, button):
        from kivymd.uix.menu import MDDropdownMenu
        menu_items = [
            {
                "text": self.fa("رستوران"),
                "on_release": lambda x="رستوران": self.set_category(x),
            },
            {
                "text": self.fa("کافه"),
                "on_release": lambda x="کافه": self.set_category(x),
            },
            {
                "text": self.fa("باشگاه"),
                "on_release": lambda x="باشگاه": self.set_category(x),
            },
        ]
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=3,
        )
        self.menu.open()
    def set_category(self, text):
        import unicodedata
        clean_text = ''.join(c for c in text if unicodedata.category(c) != 'Cf')
        clean_text = clean_text.strip()
        clean_text = clean_text.replace("ك", "ک").replace("ي", "ی")
        self.selected_category = clean_text
        admin_screen = self.root.get_screen('admin_screen')
        category_btn = admin_screen.ids.category_button
        for child in category_btn.children:
            if isinstance(child, MDButtonText):
                child.text = self.fa(clean_text)
                break
        self.menu.dismiss()
    def add_restaurant(self):
        admin_screen = self.root.get_screen('admin_screen')
        name = admin_screen.ids.rest_name.text.strip()
        food = admin_screen.ids.rest_food.text.strip()
        cap = admin_screen.ids.rest_cap.text.strip()
        price = admin_screen.ids.rest_price.text.strip()
        address = admin_screen.ids.rest_address.text.strip()
        phone = admin_screen.ids.rest_phone.text.strip()
        date_start = getattr(self, 'selected_date_start_admin', None)
        date_finish = getattr(self, 'selected_date_finish_admin', None)
        time_start = getattr(self, 'selected_time_start_admin', None)
        time_finish = getattr(self, 'selected_time_finish_admin', None)
        raw_category = self.selected_category
        if raw_category:
            import unicodedata
            clean_category = ''.join(c for c in raw_category if unicodedata.category(c) != 'Cf')
            clean_category = clean_category.replace("ك", "ک").replace("ي", "ی")
            clean_category = clean_category.strip()
            clean_category = " ".join(clean_category.split())
        else:
            clean_category = "نامشخص"
        category_en = clean_category
        if name == "" or food == "" or cap == "":
            self.show_message("لطفا فیلدهای اجباری (نام، خدمات، ظرفیت) را پر کنید!")
            return
        try:
            capacity = int(cap)
        except ValueError:
            self.show_message("ظرفیت باید عدد باشد!")
            return
        price_val = price if price != "" else None
        if self.current_lat and self.current_lon:
            location = f"{self.current_lat},{self.current_lon}"
        else:
            location = None
        image_db_path = None
        if self.selected_image_path:
            import os
            import time
            import shutil
            images_dir = os.path.join(os.getcwd(), "uploads")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            ext = os.path.splitext(self.selected_image_path)[1]
            unique_filename = f"img_{int(time.time())}{ext}"
            final_image_path = os.path.join(images_dir, unique_filename)
            try:
                shutil.copy2(self.selected_image_path, final_image_path)
                image_db_path = final_image_path
            except Exception as e:
                self.show_message("خطا در ذخیره عکس!")
                return
        if auth.add_restaurant(
            name, food, capacity, category_en, 
            host_username=self.current_user,
            price=price_val, 
            address=address, 
            location=location, 
            phone=phone,
            image_path=image_db_path,
            date_start=date_start,
            date_finish=date_finish,
            time_start=time_start,
            time_finish=time_finish
        ):
            self.show_message(f"{category_en} با موفقیت اضافه شد.")
            admin_screen.ids.rest_name.text = ""
            admin_screen.ids.rest_food.text = ""
            admin_screen.ids.rest_cap.text = ""
            admin_screen.ids.rest_price.text = ""
            admin_screen.ids.rest_address.text = ""
            admin_screen.ids.rest_phone.text = ""
            admin_screen.ids.rest_date_start_btn.text = self.fa("انتخاب تاریخ")
            admin_screen.ids.rest_date_finish_btn.text = self.fa("انتخاب تاریخ")
            admin_screen.ids.rest_time_start_btn.text = self.fa("انتخاب ساعت")
            admin_screen.ids.rest_time_finish_btn.text = self.fa("انتخاب ساعت")
            self.selected_date_start_admin = None
            self.selected_date_finish_admin = None
            self.selected_time_start_admin = None
            self.selected_time_finish_admin = None
            try:
                admin_screen.ids.location_display.text = self.fa("لوکیشن ثبت نشده است")
                admin_screen.ids.image_preview.source = ""
                admin_screen.ids.image_preview.height = "0dp"
                admin_screen.ids.image_preview.opacity = 0
                admin_screen.ids.image_status.text = self.fa("عکسی انتخاب نشده است")
                admin_screen.ids.image_status.text_color = (0.5, 0.5, 0.5, 1)
            except:
                pass
            self.current_lat = None
            self.current_lon = None
            self.selected_image_path = None
        else:
            self.show_message("خطا در ثبت اطلاعات! لطفاً اتصال به دیتابیس را بررسی کنید.")
    def open_date_menu_admin(self, button, date_type):
        from kivy.metrics import dp
        from kivymd.uix.menu import MDDropdownMenu
        from datetime import datetime, timedelta
        import jdatetime
        now = datetime.now()
        menu_items = []
        for i in range(30):
            future_gregorian = now + timedelta(days=i)
            future_jalali = jdatetime.date.fromgregorian(date=future_gregorian)
            date_str = future_jalali.strftime("%Y/%m/%d")
            date_with_day = future_jalali.strftime("%A %d %B %Y")
            menu_items.append({
                "text": self.fa(date_with_day),
                "font_size": "12sp",
                "font_name": "Vazirmatn.ttf",
                "on_release": lambda x=date_str, t=date_type: self.set_date_value_admin(x, t)
            })
        self.date_menu_admin = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
            max_height=dp(250)
        )
        self.date_menu_admin.open()
    def set_date_value_admin(self, date_str, date_type):
        admin_screen = self.root.get_screen('admin_screen')
        if date_type == "start":
            admin_screen.ids.rest_date_start_btn.text = self.fa(date_str)
            self.selected_date_start_admin = date_str
        else:
            admin_screen.ids.rest_date_finish_btn.text = self.fa(date_str)
            self.selected_date_finish_admin = date_str
        self.date_menu_admin.dismiss()
    def open_time_menu_admin(self, button, time_type):
        from kivymd.uix.menu import MDDropdownMenu
        from kivy.metrics import dp
        menu_items = []
        for h in range(24):
            t = f"{h:02d}:00"
            menu_items.append({
                "text": self.fa(t),
                "font_size": "12sp",
                "font_name": "Vazirmatn.ttf",
                "on_release": lambda x=t, ty=time_type: self.set_time_value_admin(x, ty)
            })
        self.time_menu_admin = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=3,
            max_height=dp(250)
        )
        self.time_menu_admin.open()
    def set_time_value_admin(self, time_str, time_type):
        admin_screen = self.root.get_screen('admin_screen')
        if time_type == "start":
            admin_screen.ids.rest_time_start_btn.text = self.fa(time_str)
            self.selected_time_start_admin = time_str
        else:
            admin_screen.ids.rest_time_finish_btn.text = self.fa(time_str)
            self.selected_time_finish_admin = time_str
        self.time_menu_admin.dismiss()
    def go_home(self):
        self.root.current = "user_screen"
        self.load_restaurants()
    def load_restaurants(self):
        self.in_reservations_view = False
        try:
            restaurants = auth.get_restaurants()
        except Exception as e:
            self.show_message(f"خطای دیتابیس: {e}")
            return
        user_screen = self.root.get_screen('user_screen')
        user_screen.ids.restaurant_list.clear_widgets()
        
        try:
            user_screen.ids.user_screen_title.text = self.fa("رزرو کنید !")
        except KeyError:
            pass
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivy.uix.image import Image
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.widget import Widget
        from kivy.metrics import dp
        import os
        from bidi.algorithm import get_display
        import arabic_reshaper
        def fix_text(text):
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        if not restaurants:
            from kivymd.uix.list import MDListItem, MDListItemHeadlineText
            empty_item = MDListItem()
            empty_text = MDListItemHeadlineText(text=fix_text("هیچ مکانی ثبت نشده است."), font_name="Vazirmatn.ttf")
            empty_item.add_widget(empty_text)
            user_screen.ids.restaurant_list.add_widget(empty_item)
            return
        for r in restaurants:
            if r.get('category'):
                r['category'] = r['category'].strip()
        categories = list(set([r.get('category') for r in restaurants if r.get('category')]))
        for cat in categories:
            cat_container = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                spacing=dp(5),
            )
            cat_container.bind(minimum_height=cat_container.setter('height'))
            cat_title = MDLabel(
                text=fix_text(f"{cat}‌ها"),
                font_name="Vazirmatn.ttf",
                bold=True,
                halign="right",
                theme_text_color="Custom",
                text_color=(0.2, 0.2, 0.8, 1),
                size_hint_y=None,
                height=dp(30)
            )
            cat_title.font_size = "14sp"
            cat_container.add_widget(cat_title)
            cat_items = [r for r in restaurants if r.get('category') == cat]
            h_scroll = ScrollView(
                size_hint=(1, None),
                height=dp(240),
                do_scroll_y=False,
                do_scroll_x=True,
                bar_width=0,
                scroll_type=['bars', 'content'],
                effect_cls='ScrollEffect'
            )
            h_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_x=None,
                width=len(cat_items) * (dp(160) + dp(10)),
                spacing=dp(10),
                padding=dp(5)
            )
            for r in cat_items:
                card = MDCard(
                    orientation="vertical",
                    size_hint=(None, None),
                    size=(dp(160), dp(240)),
                    radius=[10, 10, 10, 10],
                    elevation=1,
                    padding=dp(5),
                    spacing=dp(2),
                    md_bg_color=(1, 1, 1, 1),
                    theme_bg_color="Custom",
                    ripple_behavior=True,
                    on_release=lambda x, name=r["name"]: self.reserve(name)
                )
                image_path = r.get("image_path")
                if image_path and os.path.exists(image_path):
                    img = Image(
                        source=image_path,
                        size_hint_y=None,
                        height=dp(120),
                        allow_stretch=True,
                        keep_ratio=False
                    )
                    card.add_widget(img)
                else:
                    placeholder = MDLabel(
                        text=fix_text("بدون عکس"),
                        halign="center",
                        theme_text_color="Custom",
                        text_color=(0.7, 0.7, 0.7, 1),
                        size_hint_y=None,
                        height=dp(120)
                    )
                    card.add_widget(placeholder)
                name_lbl = MDLabel(
                    text=fix_text(f"{r['name']} - {r['host_fullname']}"),
                    font_name="Vazirmatn.ttf",
                    bold=True,
                    halign="right",
                    text_size=(dp(150), None),
                    size_hint_y=None,
                    height=dp(20)
                )
                name_lbl.font_size = "10sp"
                card.add_widget(name_lbl)
                desc_text = f"خدمات: {r.get('food', '')} | مانده: {int(r.get('capacity', 0)) - int(r.get('reserved_capacity', 0))}"
                desc_lbl = MDLabel(
                    text=fix_text(desc_text),
                    font_name="Vazirmatn.ttf",
                    font_size="9sp",
                    halign="right",
                    text_size=(dp(150), None),
                    size_hint_y=None,
                    height=dp(18)
                )
                desc_lbl.font_size = "8sp"
                card.add_widget(desc_lbl)
                desc_text1 = f"قیمت: {r.get('price', '')} | آدرس: {r.get('address', '')}"
                desc_lbl1 = MDLabel(
                    text=fix_text(desc_text1),
                    font_name="Vazirmatn.ttf",
                    font_size="9sp",
                    halign="right",
                    text_size=(dp(150), None),
                    size_hint_y=None,
                    height=dp(18)
                )
                desc_lbl1.font_size = "8sp"
                card.add_widget(desc_lbl1)
                h_box.add_widget(card)
            h_scroll.add_widget(h_box)
            cat_container.add_widget(h_scroll)
            user_screen.ids.restaurant_list.add_widget(cat_container)
            spacer = Widget(size_hint_y=None, height=dp(15))
            user_screen.ids.restaurant_list.add_widget(spacer)
    def reserve(self, restaurant_name):
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivy.uix.modalview import ModalView
        from kivy.uix.image import Image
        from kivy.metrics import dp
        from kivymd.uix.menu import MDDropdownMenu
        from kivy.uix.textinput import TextInput
        from datetime import datetime, timedelta
        import jdatetime
        import os
        try:
            restaurants = auth.get_restaurants()
            restaurant = next((r for r in restaurants if r['name'] == restaurant_name), None)
        except:
            restaurant = None
        if not restaurant:
            self.show_message("خطا در دریافت اطلاعات رستوران!")
            return
        host_name = restaurant.get('host_fullname', 'نامشخص')
        food = restaurant.get('food', 'نامشخص')
        price_per_person = int(restaurant.get('price', 0)) if restaurant.get('price') else 0
        image_path = restaurant.get('image_path')
        now_gregorian = datetime.now()
        now_jalali = jdatetime.date.fromgregorian(date=now_gregorian)
        self.selected_date = "--:--"
        self.selected_time = "--:--"
        total_price = price_per_person * 1
        app_fee = int(total_price * 0.10)
        final_price = total_price + app_fee
        view = ModalView(size_hint=(0.95, 0.9),background_color=(0, 0, 0, 0))
        main_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            radius=[15, 15, 15, 15],
            elevation=0,
            md_bg_color=(1, 1, 1, 1),
            theme_bg_color="Custom",
            ripple_behavior=True,
            hover_visible=True,
            state_layer_color=(1, 1, 1, 1),
            state_hover=0
        )
        img_height = dp(120) if image_path and os.path.exists(image_path) else dp(0)
        if img_height > 0:
            img = Image(source=image_path, size_hint_y=None, height=img_height)
            main_card.add_widget(img)
        def create_row(label_text, value_text, is_bold=False):
            row = MDBoxLayout(
                orientation="horizontal", 
                size_hint_y=None, 
                height=dp(25),
                spacing=dp(10)
            )
            lbl_value = MDLabel(
                text=self.fa(str(value_text)), 
                font_name="Vazirmatn.ttf", 
                halign="center",
                valign="center",
                size_hint_x=None, 
                width=dp(200),
                bold=is_bold
            )
            lbl_value.font_size = "9sp"
            lbl_title = MDLabel(
                text=self.fa(label_text), 
                font_name="Vazirmatn.ttf", 
                halign="right",
                valign="center",
                size_hint_x=None,
                width=dp(100),
                theme_text_color="Custom", 
                text_color=(0.2, 0.2, 0.2, 1)
            )
            lbl_title.font_size = "9sp"
            row.add_widget(lbl_value)
            row.add_widget(lbl_title)
            return row
        main_card.add_widget(create_row("میزبان:", host_name, True))
        main_card.add_widget(create_row("خدمات:", food))
        date_start_service = restaurant.get('Date_Start_Service', None)
        date_finish_service = restaurant.get('Date_Finish_Service', None)
        if not date_start_service or not date_finish_service:
            date_start_service = now_jalali.strftime("%Y/%m/%d")
            date_finish_service = (now_jalali + timedelta(days=7)).strftime("%Y/%m/%d")
        try:
            start_jdate = jdatetime.datetime.strptime(date_start_service, "%Y/%m/%d").date()
            finish_jdate = jdatetime.datetime.strptime(date_finish_service, "%Y/%m/%d").date()
        except:
            start_jdate = now_jalali
            finish_jdate = now_jalali + timedelta(days=7)
        date_menu_items = []
        current_date = start_jdate
        while current_date <= finish_jdate:
            date_num = current_date.strftime("%Y/%m/%d")
            date_with_day = current_date.strftime("%A %d %B %Y")
            date_menu_items.append({
                "text": self.fa(date_with_day),
                "font_size": "12sp",
                "font_name": "Vazirmatn.ttf",
                "on_release": lambda x=date_num: self.set_date(x)
            })
            current_date += timedelta(days=1)
        def open_date_menu(instance):
            self.date_menu = MDDropdownMenu(
                caller=instance,
                items=date_menu_items,
                width_mult=4,
                max_height=dp(250)  # ← این خط را اضافه کنید
            )
            self.date_menu.open()
        date_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        self.date_card = MDCard(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(200),
            radius=[5, 5, 5, 5],
            elevation=0,
            md_bg_color=(0.95, 0.95, 0.95, 1),
            theme_bg_color="Custom",
            ripple_behavior=True,
            on_release=open_date_menu
        )
        self.date_label_display = MDLabel(
            text=self.fa(self.selected_date),
            font_name="Vazirmatn.ttf",
            halign="center",
            valign="center",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1)
        )
        self.date_label_display.font_size = "9sp"
        self.date_card.add_widget(self.date_label_display)
        date_label = MDLabel(
            text=self.fa("تاریخ رزرو:"), 
            font_name="Vazirmatn.ttf", 
            halign="right", 
            size_hint_x=None,
            width=dp(100)
        )
        date_label.font_size = "9sp"
        date_row.add_widget(self.date_card)
        date_row.add_widget(date_label)
        main_card.add_widget(date_row)
        time_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        self.time_card = MDCard(
            orientation="horizontal",
            size_hint_x=None,
            width=dp(200),
            radius=[5, 5, 5, 5],
            elevation=0,
            md_bg_color=(0.95, 0.95, 0.95, 1),
            theme_bg_color="Custom",
            ripple_behavior=True,
            on_release=lambda x: open_time_menu(x)
        )
        self.time_label_display = MDLabel(
            text=self.fa(self.selected_time),
            font_name="Vazirmatn.ttf",
            halign="center",
            valign="center",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1)
        )
        self.time_label_display.font_size = "9sp"
        self.time_card.add_widget(self.time_label_display)
        time_label = MDLabel(
            text=self.fa("ساعت رزرو:"), 
            font_name="Vazirmatn.ttf", 
            halign="right", 
            size_hint_x=None,
            width=dp(100),
        )
        time_label.font_size = "9sp"
        time_row.add_widget(self.time_card)
        time_row.add_widget(time_label)
        main_card.add_widget(time_row)
        start_time_str = restaurant.get('Start_Desk_Service')
        finish_time_str = restaurant.get('Finish_Desk_Service')
        if not start_time_str or not finish_time_str:
            start_hour = 8
            finish_hour = 23
        else:
            try:
                start_hour = int(start_time_str.split(':')[0])
                finish_hour = int(finish_time_str.split(':')[0])
            except:
                start_hour = 8
                finish_hour = 23
        time_menu_items = []
        for h in range(start_hour, finish_hour + 1):
            t = f"{h:02d}:00"
            time_menu_items.append({
                "text": self.fa(t),
                "font_size": "12sp",
                "font_name": "Vazirmatn.ttf",
                "on_release": lambda x=t: self.set_time(x)
            })
        def open_time_menu(instance):
            self.time_menu = MDDropdownMenu(
                caller=instance,
                items=time_menu_items,
                width_mult=3,
                max_height=dp(250)  # ← این خط را اضافه کنید
            )
            self.time_menu.open()
        qty_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(35), spacing=dp(10))
        self.qty_field = TextInput(
            text="1", 
            size_hint_x=None, 
            width=dp(200),
            multiline=False, 
            input_filter="int", 
            halign="center",
            font_name="Vazirmatn.ttf"
        )
        self.qty_field.font_size = "9sp"
        qty_label = MDLabel(
            text=self.fa("تعداد رزرو (نفر):"), 
            font_name="Vazirmatn.ttf", 
            halign="right", 
            size_hint_x=None,
            width=dp(100)
        )
        qty_label.font_size = "9sp"
        qty_box.add_widget(self.qty_field)
        qty_box.add_widget(qty_label)
        main_card.add_widget(qty_box)
        main_card.add_widget(create_row("هزینه هر نفر:", f"{price_per_person:,} ریال"))
        total_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(10))
        total_Value = MDLabel(
            text=self.fa(f"{total_price:,} ریال"), 
            font_name="Vazirmatn.ttf", 
            halign="center", 
            size_hint_x=None, 
            width=dp(200)
        )
        total_Value.font_size = "9sp"
        total_row.add_widget(total_Value)
        total_lbl = MDLabel(
            text=self.fa("جمع کل سفارش:"), 
            font_name="Vazirmatn.ttf", 
            halign="right", 
            size_hint_x=None, 
            width=dp(100)
        )
        total_lbl.font_size = "9sp"
        total_row.add_widget(total_lbl)
        main_card.add_widget(total_row)
        fee_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(10))
        fee_Value = MDLabel(
            text=self.fa(f"{app_fee:,} ریال"), 
            font_name="Vazirmatn.ttf", 
            halign="center", 
            size_hint_x=None, 
            width=dp(200)
        )
        fee_Value.font_size = "9sp"
        fee_row.add_widget(fee_Value)
        fee_lbl = MDLabel(
            text=self.fa("کارمزد اپلیکیشن:"), 
            font_name="Vazirmatn.ttf", 
            halign="right", 
            size_hint_x=None, 
            width=dp(100)
        )
        fee_lbl.font_size = "9sp"
        fee_row.add_widget(fee_lbl)
        main_card.add_widget(fee_row)
        final_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30), spacing=dp(10))
        final_Value = MDLabel(
            text=self.fa(f"{final_price:,} ریال"), 
            font_name="Vazirmatn.ttf", 
            halign="center", 
            size_hint_x=None, 
            width=dp(200), 
            bold=True
        )
        final_Value.font_size = "9sp"
        final_row.add_widget(final_Value)
        final_lbl = MDLabel(
            text=self.fa("کل پرداختی:"), 
            font_name="Vazirmatn.ttf", 
            halign="right", 
            size_hint_x=None, 
            width=dp(100), 
            bold=True
        )
        final_lbl.font_size = "9sp"
        final_row.add_widget(final_lbl)
        main_card.add_widget(final_row)
        def update_prices(instance, value):
            try:
                qty = int(value) if value else 1
            except:
                qty = 1
            new_total = price_per_person * qty
            new_fee = int(new_total * 0.10)
            new_final = new_total + new_fee
            total_Value.text = self.fa(f"{new_total:,} ریال")
            fee_Value.text = self.fa(f"{new_fee:,} ریال")
            final_Value.text = self.fa(f"{new_final:,} ریال")
        self.qty_field.bind(text=update_prices)
        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        def do_payment(instance):
            if self.selected_date == "--:--" or self.selected_time == "--:--":
                self.show_message("لطفا ابتدا تاریخ و ساعت رزرو را انتخاب کنید!")
                return
            import random
            try:
                restaurant_SelectDay = auth.get_restaurants_SelectDay(self.selected_date)
                restaurant_SelectDay = next((r for r in restaurant_SelectDay if r['name'] == restaurant_name), None)
            except Exception as e:
                self.show_message(f"خطا در دریافت ظرفیت: {e}")
                return
            if not restaurant_SelectDay:
                self.show_message("خطا در دریافت اطلاعات ظرفیت!")
                return
            capacity_SelectDay = int(restaurant_SelectDay.get('capacity', 0))
            reserved_SelectDay = int(restaurant_SelectDay.get('reserved_capacity', 0))
            remaining_capacity_SelectDay = capacity_SelectDay - reserved_SelectDay
            qty = int(self.qty_field.text) if self.qty_field.text.isdigit() else 1
            if qty > remaining_capacity_SelectDay:
                self.show_message(f"ظرفیت باقی‌مانده این مکان در تاریخ\n {self.selected_date} برابر {remaining_capacity_SelectDay} نفر است.\n لطفا تعداد کمتری انتخاب کنید.")
                return
            final_time = self.selected_time
            final_date = self.selected_date
            if not final_time:
                self.show_message("لطفا ساعت رزرو را وارد کنید!")
                return
            total_price = price_per_person * qty
            app_fee = int(total_price * 0.10)
            final_price_val = total_price + app_fee
            tracking_code = str(random.randint(100000, 999999))
            host_shaba = restaurant.get('shaba', '') 
            host_phone = restaurant.get('phone', '')
            host_username = restaurant.get('host_username', '')
            payment_successful = True 
            if payment_successful:
                success = auth.make_reservation(
                    restaurant_name=restaurant_name,
                    host_fullname=host_name,
                    services=food,
                    date=final_date,
                    time=final_time,
                    count=qty,
                    cost_person=price_per_person,
                    cost_total=total_price,
                    cost_app=app_fee,
                    final_cost=final_price_val,
                    guest_username=self.current_user,
                    category=restaurant.get('category', ''),
                    address=restaurant.get('address', ''),
                    host_phone=host_phone,
                    tracking_code=tracking_code,
                    host_username=host_username
                )
                if success:
                    self.show_message(
                        f"پرداخت با موفقیت انجام شد.\n"
                        f"مبلغ {final_price_val:,} ریال به حساب واسط واریز شد.\n\n"
                        f"کد رهگیری شما: {tracking_code}\n"
                        f"لطفاً این کد را هنگام حضور در محل به میزبان ارائه دهید تا مبلغ به حساب ایشان واریز شود."
                    )
                    view.dismiss()
                else:
                    self.show_message("خطا در ثبت اطلاعات رزرو!")
            else:
                self.show_message("پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.")
        btn_cancel = MDButton(style="text", on_release=lambda x: view.dismiss())
        btn_cancel.add_widget(MDButtonText(text=self.fa("انصراف"), font_name="Vazirmatn.ttf"))
        btn_pay = MDButton(style="filled", md_bg_color=(0.1, 0.6, 0.1, 1),theme_bg_color="Custom", on_release=do_payment)
        btn_pay.add_widget(MDButtonText(text=self.fa("پرداخت از طریق درگاه بانکی"), font_name="Vazirmatn.ttf"))
        btn_box.add_widget(btn_pay)
        btn_box.add_widget(btn_cancel)
        main_card.add_widget(btn_box)
        view.add_widget(main_card)
        view.open()
    def set_date(self, date_str):
        self.selected_date = date_str
        try:
            self.date_label_display.text = self.fa(date_str)
            self.date_menu.dismiss()
        except:
            pass
    def set_time(self, time_str):
        self.selected_time = time_str
        try:
            self.time_label_display.text = self.fa(time_str)
            self.time_menu.dismiss()
        except:
            pass
    def show_my_reservations(self):
        self.in_reservations_view = True
        try:
            reservations = auth.get_reservations_for_user(self.current_user)
        except Exception as e:
            self.show_message(f"خطای دیتابیس: {e}")
            return
        user_screen = self.root.get_screen('user_screen')
        user_screen.ids.restaurant_list.clear_widgets()
        try:
            user_screen.ids.user_screen_title.text = self.fa("رزروهای شما:")
        except:
            pass
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText
        from kivy.uix.image import Image
        from kivy.metrics import dp
        from bidi.algorithm import get_display
        import arabic_reshaper
        import os
        def fix_text(text):
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        if not reservations:
            empty_item = MDListItem() # اصلاح شد
            empty_text = MDListItemHeadlineText(text=fix_text("شما هیچ رزروی ندارید."), font_name="Vazirmatn.ttf")
            empty_item.add_widget(empty_text)
            user_screen.ids.restaurant_list.add_widget(empty_item)
            return
        categories = list(set([r.get('category', 'نامشخص') for r in reservations if r.get('category')]))
        for cat in categories:
            cat_reservations = [r for r in reservations if r.get('category') == cat]
            title = MDListItem() # اصلاح شد
            title_text = MDListItemHeadlineText(text=fix_text(f"{cat}‌ها"), font_name="Vazirmatn.ttf", theme_text_color="Custom", text_color=(0.2, 0.2, 0.8, 1))
            title.add_widget(title_text)
            user_screen.ids.restaurant_list.add_widget(title)
            for res in cat_reservations:
                card = MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(400),
                    radius=[10, 10, 10, 10],
                    elevation=1,
                    padding=dp(10),
                    spacing=dp(4),
                    md_bg_color=(1, 1, 1, 1),
                    theme_bg_color="Custom",
                )
                try:
                    all_rests = auth.get_restaurants()
                    host_rest = next((r for r in all_rests if r['name'] == res['restaurant']), None)
                    img_path = host_rest.get('image_path') if host_rest else None
                except:
                    img_path = None
                if img_path and os.path.exists(img_path):
                    img_container = MDBoxLayout(
                        orientation="vertical",
                        size_hint_y=None,
                        height=dp(70),
                        padding=[0, 0, 0, dp(5)]
                    )
                    img = Image(
                        source=img_path,
                        size_hint=(None, None),
                        size=(dp(60), dp(60)),
                        pos_hint={"center_x": .5}
                    )
                    img_container.add_widget(img)
                    card.add_widget(img_container)
                def create_res_row(title_text, value_text, bold=False):
                    row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(5))
                    Res_title = MDLabel(
                        text=fix_text(str(value_text)), 
                        font_name="Vazirmatn.ttf", 
                        halign="center", 
                        size_hint_x=.6, 
                        bold=bold
                    )
                    Res_title.font_size = "9sp"
                    row.add_widget(Res_title)
                    Res_value = MDLabel(
                        text=fix_text(title_text), 
                        font_name="Vazirmatn.ttf", 
                        halign="right", 
                        size_hint_x=.4, 
                        theme_text_color="Custom", 
                        text_color=(0.3,0.3,0.3,1), 
                    )
                    Res_value.font_size = "9sp"
                    row.add_widget(Res_value)
                    return row
                card.add_widget(create_res_row("برند میزبان:", res['restaurant'], True))
                card.add_widget(create_res_row("نام میزبان:", res['host_fullname']))
                card.add_widget(create_res_row("خدمات:", res['services']))
                card.add_widget(create_res_row("تاریخ رزرو:", res['date']))
                card.add_widget(create_res_row("ساعت رزرو:", res['time']))
                card.add_widget(create_res_row("تعداد رزرو:", f"{res['count']} نفر"))
                card.add_widget(create_res_row("کل پرداختی:", f"{int(res['final_cost']):,} ریال", True))
                card.add_widget(create_res_row("آدرس:", res['address']))
                card.add_widget(create_res_row("تلفن میزبان:", res['host_phone']))
                card.add_widget(create_res_row("کد رهگیری شما:", res['tracking_code'], True))
                card.add_widget(create_res_row("لوکیشن:", "مشاهده در نقشه"))
                if res.get('payment_status') == 'Settled':
                    status_text = "پذیرش انجام شد. (خوش آمدید.)"
                    status_color = (0.1, 0.6, 0.1, 1)
                else:
                    status_text = "پذیرش انجام نشد. (عودت موجودی!)"
                    status_color = (0.8, 0.1, 0.1, 1)
                status_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22), spacing=dp(5))
                status_value_lbl = MDLabel(
                    text=fix_text(status_text), 
                    font_name="Vazirmatn.ttf", 
                    halign="center", 
                    size_hint_x=.6, 
                    bold=True,
                    theme_text_color="Custom",
                    text_color=status_color
                )
                status_value_lbl.font_size = "9sp"
                status_title_lbl = MDLabel(
                    text=fix_text("وضعیت پذیرش:"), 
                    font_name="Vazirmatn.ttf", 
                    halign="right", 
                    size_hint_x=.4, 
                    theme_text_color="Custom", 
                    text_color=(0.3,0.3,0.3,1)
                )
                status_title_lbl.font_size = "9sp"
                status_row.add_widget(status_value_lbl)
                status_row.add_widget(status_title_lbl)
                card.add_widget(status_row)
                if res.get('payment_status') != 'Settled':
                    btn_refund = MDButton(
                        style="filled", 
                        size_hint=(None, None),
                        size=(dp(220), dp(35)),
                        pos_hint={"center_x": .5},
                        md_bg_color=(0.8, 0.1, 0.1, 1),
                        theme_bg_color="Custom",
                        on_release=lambda x, r=res: self.cancel_guest_reservation(r)
                    )
                    btn_refund.add_widget(MDButtonText(text=self.fa("درخواست عودت وجه و لغو رزرو"), font_name="Vazirmatn.ttf"))
                    card.add_widget(btn_refund)
                    card.height += dp(45)
                row_count = 12
                base_height = row_count * dp(22)
                img_height = dp(70) if img_path and os.path.exists(img_path) else 0
                padding_height = dp(20)
                extra_height = dp(45) if res.get('payment_status') != 'Settled' else 0
                card.height = base_height + img_height + padding_height + extra_height
                user_screen.ids.restaurant_list.add_widget(card)
                from kivy.uix.widget import Widget
                spacer = Widget(size_hint_y=None, height=dp(15))
                user_screen.ids.restaurant_list.add_widget(spacer)
    def cancel_guest_reservation(self, res):
        if res.get('payment_status') == 'Settled':
            self.show_message("این رزرو قبلاً پذیرش شده و قابل لغو نیست.")
            return
        try:
            conn = auth.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Reservations SET PaymentStatus = 'Cancelled' WHERE RandomServiceGuest = ?",
                (res['tracking_code'],)
            )
            conn.commit()
            conn.close()
            self.show_message("رزرو شما لغو شد و مبلغ به حساب شما عودت داده شد.")
            self.show_my_reservations()
        except Exception as e:
            self.show_message(f"خطا در لغو رزرو: {e}")
    def register_guest(self):
        screen = self.root.get_screen('guest_register_screen')
        fullname = screen.ids.guest_fullname.text.strip()
        phone    = screen.ids.guest_phone.text.strip()
        national = screen.ids.guest_national.text.strip()
        password = screen.ids.guest_pass.text.strip()
        if not (fullname and phone and national and password):
            self.show_message("همه فیلدها را پر کنید!")
            return
        if auth.register_user(
            fullname, phone, national, password, 
            role="user"
        ):
            self.show_message("ثبت نام مهمان با موفقیت انجام شد.")
            screen.ids.guest_fullname.text = ""
            screen.ids.guest_phone.text = ""
            screen.ids.guest_national.text = ""
            screen.ids.guest_pass.text = ""
            self.root.current = "login_screen"
        else:
            self.show_message("خطا در ثبت نام! (شماره ملی تکراری است؟)")
    def register_host(self):
        screen = self.root.get_screen('host_register_screen')
        fullname = screen.ids.host_fullname.text.strip()
        phone    = screen.ids.host_phone.text.strip()
        national = screen.ids.host_national.text.strip()
        password = screen.ids.host_pass.text.strip()
        shaba_number = screen.ids.IR_host_shaba.text.strip().replace("-", "")
        shaba = f"IR{shaba_number}" if shaba_number else ""
        if not (fullname and phone and national and password and shaba_number):
            self.show_message("همه فیلدها را پر کنید!")
            return
        if not screen.ids.host_contract_check.active:
            self.show_message("برای ثبت نام باید شرایط قرارداد را بپذیرید!")
            return
        if auth.register_user(
            fullname, phone, national, password, 
            role="admin", 
            shaba=shaba, 
            garadad=self.CONTRACT_HOST_TEXT
        ):
            self.show_message("ثبت نام میزبان با موفقیت انجام شد.")
            screen.ids.host_fullname.text = ""
            screen.ids.host_phone.text = ""
            screen.ids.host_national.text = ""
            screen.ids.host_pass.text = ""
            screen.ids.IR_host_shaba.text = ""
            screen.ids.host_contract_check.active = False
            self.root.current = "login_screen"
        else:
            self.show_message("خطا در ثبت نام! (شماره ملی تکراری است؟)")
    def go_admin_panel(self):
        self.root.current = "admin_screen"
    def go_guest_register(self):
        self.root.current = "guest_register_screen"
    def go_host_register(self):
        self.root.current = "host_register_screen"
    def go_login(self):
        self.root.current = "login_screen"
    def load_host_services(self):
        try:
            services = auth.get_services_by_host(self.current_user)
        except Exception as e:
            self.show_message(f"خطای دیتابیس: {e}")
            return
        screen = self.root.get_screen('host_services_screen')
        screen.ids.host_services_list.clear_widgets()
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText
        from kivy.metrics import dp
        from bidi.algorithm import get_display
        import arabic_reshaper
        def fix_text(text):
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        if not services:
            item = MDListItem() # اصلاح شد
            item_text = MDListItemHeadlineText(text=fix_text("هنوز خدمتی ثبت نکرده‌اید."), font_name="Vazirmatn.ttf")
            item.add_widget(item_text)
            screen.ids.host_services_list.add_widget(item)
            return
        for s in services:
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(140),
                radius=[10, 10, 10, 10],
                elevation=1,
                padding=dp(10),
                spacing=dp(5),
                md_bg_color=(1, 1, 1, 1),
                theme_bg_color="Custom",
            )
            name_lbl = MDLabel(
                text=fix_text(s['name']),
                font_name="Vazirmatn.ttf",
                bold=True,
                halign="right",
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1),
                size_hint_y=None,
                height=dp(25)
            )
            name_lbl.font_size = "12sp"
            card.add_widget(name_lbl)
            line1_text = f"گروه: {s['category']} | سرو خدمات: {s['food']} | ظرفیت: {s['capacity']} نفر"
            line1_lbl = MDLabel(
                text=fix_text(line1_text),
                font_name="Vazirmatn.ttf",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(20)
            )
            line1_lbl.font_size = "9sp"
            card.add_widget(line1_lbl)
            line2_text = f"تاریخ شروع: {s['date_start']} | تاریخ پایان: {s['date_finish']} | قیمت: {s['price']} ریال"
            line2_lbl = MDLabel(
                text=fix_text(line2_text),
                font_name="Vazirmatn.ttf",
                halign="right",
                theme_text_color="Custom",
                text_color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height=dp(20)
            )
            line2_lbl.font_size = "9sp"
            card.add_widget(line2_lbl)
            from kivy.uix.widget import Widget
            btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
            btn_row.add_widget(Widget(size_hint_x=.3))
            btn_edit = MDButton(
                style="filled",
                size_hint_x=.35,
                theme_bg_color="Custom",
                md_bg_color=(0.4, 0.8, 0.4, 1),  # ← سبز روشن
                on_release=lambda x, name=s['name']: self.edit_service_host_restaurant(name)
            )
            btn_edit.add_widget(MDButtonText(
                text=self.fa("ویرایش"), 
                font_name="Vazirmatn.ttf",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)  # متن سفید برای خوانایی بهتر روی سبز
            ))
            btn_delete = MDButton(
                style="filled",
                size_hint_x=.35,
                theme_bg_color="Custom",
                md_bg_color=(0.8, 0.1, 0.1, 1),  # ← قرمز با شفافیت ۴۰٪ (عدد آخر)
                on_release=lambda x, name=s['name']: self.delete_service_host_restaurant(name)
            )
            btn_delete.add_widget(MDButtonText(
                text=self.fa("حذف خدمت"), 
                font_name="Vazirmatn.ttf",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)  # متن سفید
            ))
            btn_row.add_widget(btn_delete)
            btn_row.add_widget(btn_edit)
            card.add_widget(btn_row)
            screen.ids.host_services_list.add_widget(card)
            from kivy.uix.widget import Widget
            spacer = Widget(size_hint_y=None, height=dp(10))
            screen.ids.host_services_list.add_widget(spacer)
    def edit_service_host_restaurant(self, service_name):
        try:
            all_services = auth.get_services_by_host(self.current_user)
            service = next((s for s in all_services if s['name'] == service_name), None)
        except Exception as e:
            self.show_message(f"خطا در دریافت اطلاعات: {e}")
            return
        if not service:
            self.show_message("خدمت یافت نشد!")
            return
        from kivy.uix.modalview import ModalView
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivy.uix.scrollview import ScrollView
        from kivy.metrics import dp
        from bidi.algorithm import get_display
        import arabic_reshaper
        def fix_text(text):
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        view = ModalView(size_hint=(0.95, 0.9), background_color=(0, 0, 0, 0.5))
        main_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
            radius=[15, 15, 15, 15],
            elevation=0,
            md_bg_color=(1, 1, 1, 1),
            theme_bg_color="Custom",
            ripple_behavior=True,
            hover_visible=True,
            state_layer_color=(1, 1, 1, 1),
            state_hover=0
        )
        title = MDLabel(
            text=self.fa(f"ویرایش خدمت: {service_name}"),
            font_name="Vazirmatn.ttf",
            font_size="14sp",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )
        main_card.add_widget(title)
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        form_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(650),
            spacing=dp(8),
            padding=dp(10)
        )
        def add_text_field(label_text, field_id, initial_value, input_filter=None):
            lbl = MDLabel(
                text=self.fa(label_text),
                font_name="Vazirmatn.ttf",
                halign="right",
                size_hint_y=None,
                height=dp(18)
            )
            lbl.font_size = "9sp"
            form_box.add_widget(lbl)
            field = PersianInput(
                text=str(initial_value) if initial_value and initial_value != "نامشخص" else "",
                font_name="Vazirmatn.ttf",
                multiline=False,
                halign="right",
                size_hint_y=None,
                height=dp(35),
                font_size="11sp",
                input_filter=input_filter
            )
            field.id = field_id
            form_box.add_widget(field)
            return field
        def add_dropdown_field(label_text, field_id, initial_value, is_time=False):
            lbl = MDLabel(
                text=self.fa(label_text),
                font_name="Vazirmatn.ttf",
                halign="right",
                size_hint_y=None,
                height=dp(18)
            )
            lbl.font_size = "9sp"
            form_box.add_widget(lbl)
            btn = MDButton(
                style="filled",
                size_hint=(1, None),
                height=dp(35),
                md_bg_color=(0.9, 0.9, 0.9, 1),
                theme_bg_color="Custom",
                on_release=lambda x: self.open_dropdown_for_edit(x, field_id, is_time)
            )
            btn.add_widget(MDButtonText(
                text=str(initial_value) if initial_value and initial_value != "نامشخص" else self.fa("انتخاب کنید"), 
                font_name="Vazirmatn.ttf",
                theme_text_color="Custom",      # ← این خط
                text_color=(0, 0, 0, 1)         # ← و این خط (رنگ مشکی)
            ))
            btn.id = field_id
            form_box.add_widget(btn)
            if field_id == "date_start":
                self.selected_edit_date_start = initial_value
            elif field_id == "date_finish":
                self.selected_edit_date_finish = initial_value
            elif field_id == "time_start":
                self.selected_edit_time_start = initial_value
            elif field_id == "time_finish":
                self.selected_edit_time_finish = initial_value
            return btn
        self.edit_food = add_text_field("سرو خدمات:", "food", service.get('food'))
        self.edit_cap = add_text_field("ظرفیت (نفر):", "cap", service.get('capacity'), input_filter="int")
        self.edit_price = add_text_field("مبلغ (ریال):", "price", service.get('price'), input_filter="int")
        self.edit_address = add_text_field("آدرس:", "address", service.get('address'))
        self.edit_phone = add_text_field("تلفن:", "phone", service.get('phone'), input_filter="int")
        self.edit_date_start_btn = add_dropdown_field("تاریخ شروع خدمت:", "date_start", service.get('date_start'), is_time=False)
        self.edit_date_finish_btn = add_dropdown_field("تاریخ پایان خدمت:", "date_finish", service.get('date_finish'), is_time=False)
        self.edit_time_start_btn = add_dropdown_field("ساعت شروع خدمت:", "time_start", service.get('time_start'), is_time=True)
        self.edit_time_finish_btn = add_dropdown_field("ساعت پایان خدمت:", "time_finish", service.get('time_finish'), is_time=True)
        scroll.add_widget(form_box)
        main_card.add_widget(scroll)
        btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_cancel = MDButton(style="text", on_release=lambda x: view.dismiss())
        btn_cancel.add_widget(MDButtonText(text=self.fa("انصراف"), font_name="Vazirmatn.ttf"))
        btn_save = MDButton(style="filled", md_bg_color=(0.1, 0.6, 0.1, 1),theme_bg_color="Custom", on_release=lambda x: self.save_service_changes(service_name, view))
        btn_save.add_widget(MDButtonText(text=self.fa("ثبت تغییرات"), font_name="Vazirmatn.ttf"))
        btn_box.add_widget(btn_save)
        btn_box.add_widget(btn_cancel)
        main_card.add_widget(btn_box)
        view.add_widget(main_card)
        view.open()
    def save_service_changes(self, service_name, view):
        food = getattr(self.edit_food, '_raw_text', self.edit_food.text).strip()
        cap = getattr(self.edit_cap, '_raw_text', self.edit_cap.text).strip()
        price = getattr(self.edit_price, '_raw_text', self.edit_price.text).strip()
        address = getattr(self.edit_address, '_raw_text', self.edit_address.text).strip()
        phone = getattr(self.edit_phone, '_raw_text', self.edit_phone.text).strip()
        date_start = getattr(self, 'selected_edit_date_start', None)
        date_finish = getattr(self, 'selected_edit_date_finish', None)
        time_start = getattr(self, 'selected_edit_time_start', None)
        time_finish = getattr(self, 'selected_edit_time_finish', None)
        if not food or not cap:
            self.show_message("فیلدهای خدمات و ظرفیت اجباری هستند!")
            return
        if auth.update_service(
            name=service_name,
            food=food,
            capacity=cap,
            price=price,
            address=address,
            phone=phone,
            date_start=date_start,
            date_finish=date_finish,
            time_start=time_start,
            time_finish=time_finish,
            host_username=self.current_user
        ):
            self.show_message("تغییرات با موفقیت ذخیره شد.")
            view.dismiss()
            self.load_host_services()
        else:
            self.show_message("خطا در ذخیره تغییرات!")
    def open_dropdown_for_edit(self, button, field_id, is_time=False):
        from kivymd.uix.menu import MDDropdownMenu
        from datetime import datetime, timedelta
        import jdatetime
        menu_items = []
        if is_time:
            for h in range(24):
                t = f"{h:02d}:00"
                menu_items.append({
                    "text": self.fa(t),
                    "font_size": "12sp",
                    "font_name": "Vazirmatn.ttf",
                    "on_release": lambda x=t, fid=field_id: self.set_dropdown_value(x, fid, button)
                })
        else:
            now = datetime.now()
            for i in range(30):
                future_gregorian = now + timedelta(days=i)
                future_jalali = jdatetime.date.fromgregorian(date=future_gregorian)
                date_str = future_jalali.strftime("%Y/%m/%d")
                date_with_day = future_jalali.strftime("%A %d %B %Y")
                menu_items.append({
                    "text": self.fa(date_with_day),
                    "font_size": "12sp",
                    "font_name": "Vazirmatn.ttf",
                    "on_release": lambda x=date_str, fid=field_id: self.set_dropdown_value(x, fid, button)
                })
        self.edit_dropdown_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
            max_height=dp(250)
        )
        self.edit_dropdown_menu.open()
    def set_dropdown_value(self, value, field_id, button):
        if hasattr(button, 'children') and len(button.children) > 0:
            for child in button.children:
                if hasattr(child, 'text'):
                    child.text = self.fa(value)
                    child.theme_text_color = "Custom"    # ← اضافه کنید
                    child.text_color = (0, 0, 0, 1)      # ← اضافه کنید (رنگ مشکی)
                    break
        if field_id == "date_start":
            self.selected_edit_date_start = value
        elif field_id == "date_finish":
            self.selected_edit_date_finish = value
        elif field_id == "time_start":
            self.selected_edit_time_start = value
        elif field_id == "time_finish":
            self.selected_edit_time_finish = value
        self.edit_dropdown_menu.dismiss()
    def delete_service_host_restaurant(self, service_name):
        try:
            conn = auth.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Restaurants WHERE Name = ? AND host_username = ?", (service_name, self.current_user))
            conn.commit()
            conn.close()
            self.show_message("خدمت با موفقیت حذف شد.")
            self.load_host_services()
        except Exception as e:
            self.show_message(f"خطا در حذف خدمت: {e}")
    def go_host_services(self):
        self.root.current = "host_services_screen"
        self.load_host_services()
    def show_host_orders(self):
        try:
            orders = auth.get_reservations_for_host(self.current_user)
        except Exception as e:
            self.show_message(f"خطای دیتابیس: {e}")
            return
        self.root.current = "host_demand_screen"
        screen = self.root.get_screen('host_demand_screen')
        screen.ids.host_demand_list.clear_widgets()
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.list import MDListItem, MDListItemHeadlineText
        from kivymd.uix.textfield import MDTextField
        from kivy.metrics import dp
        from bidi.algorithm import get_display
        import arabic_reshaper
        import jdatetime
        from datetime import timedelta
        def fix_text(text):
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        if not orders:
            empty_item = MDListItem() # اصلاح شد
            empty_text = MDListItemHeadlineText(text=fix_text("هنوز هیچ سفارشی ثبت نشده است."), font_name="Vazirmatn.ttf")
            empty_item.add_widget(empty_text)
            screen.ids.host_demand_list.add_widget(empty_item)
            return
        today = jdatetime.date.today()
        for order in orders:
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(410),
                radius=[10, 10, 10, 10],
                elevation=1,
                padding=dp(10),
                spacing=dp(4),
                md_bg_color=(1, 1, 1, 1),
                theme_bg_color="Custom"
            )
            def create_row(title, value, bold=False):
                row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28), spacing=dp(5))
                Host_Serv_title = MDLabel(text=fix_text(str(value)), font_name="Vazirmatn.ttf", halign="center", size_hint_x=.6, bold=bold)
                Host_Serv_title.font_size = "9sp"
                row.add_widget(Host_Serv_title)
                Host_Serv_value = MDLabel(text=fix_text(title), font_name="Vazirmatn.ttf", halign="right", size_hint_x=.4, theme_text_color="Custom", text_color=(0.3, 0.3, 0.3, 1))
                Host_Serv_value.font_size = "9sp"
                row.add_widget(Host_Serv_value)
                return row
            card.add_widget(create_row("نام مهمان:", order['guest_fullname'], True))
            card.add_widget(create_row("کد مهمان:", order.get('guest_username', 'نامشخص')))
            card.add_widget(create_row("برند تجاری خدمات:", order['restaurant'], True))
            card.add_widget(create_row("کد میزبان خدمت:", self.current_user))
            card.add_widget(create_row("نام میزبان خدمات:", order['host_fullname']))
            card.add_widget(create_row("سرو خدمات:", order['services']))
            card.add_widget(create_row("تاریخ رزرو:", order['date']))
            card.add_widget(create_row("ساعت رزرو:", order['time']))
            card.add_widget(create_row("تعداد رزرو:", f"{order['count']} نفر"))
            card.add_widget(create_row("مبلغ کل رزرو:", f"{int(order['final_cost']):,} ریال", True))
            tracking_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(75), spacing=dp(5))
            tracking_label = MDLabel(
                text=self.fa("کد رهگیری مهمان را وارد کنید:"),
                font_name="Vazirmatn.ttf",
                halign="right",
                size_hint_y=None,
                height=dp(18),
                theme_text_color="Custom",
                text_color=(0.4, 0.4, 0.4, 1)
            )
            tracking_label.font_size = "12sp"
            tracking_box.add_widget(tracking_label)
            input_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(5))
            local_tracking_input = MDTextField(
                font_name="Vazirmatn.ttf",
                halign="center",
                input_filter="int",
                size_hint_x=.4,
                height=dp(30)
            )
            local_tracking_input.font_size = "12sp"
            btn_settle = MDButton(
                style="filled",
                size_hint_x=.3,
                theme_bg_color="Custom",
                md_bg_color=(0.4, 0.8, 0.4, 1),  # ← سبز روشن
                on_release=lambda x, o=order, inp=local_tracking_input: self.settle_host_order(o, inp.text)
            )
            btn_settle.add_widget(MDButtonText(text=self.fa("تایید و تسویه"), font_name="Vazirmatn.ttf"))
            show_expire = False
            try:
                order_date = jdatetime.datetime.strptime(order['date'].strip(), "%Y/%m/%d").date()
                if (today - order_date).days > 1:
                    show_expire = True
            except Exception:
                show_expire = False
            if show_expire:
                btn_expire = MDButton(
                    style="filled",
                    size_hint_x=.3,
                    theme_bg_color="Custom",
                    md_bg_color=(0.8, 0.1, 0.1, 1),
                    on_release=lambda x, o=order: self.expire_host_order(o)
                )
                btn_expire.add_widget(MDButtonText(text=self.fa("منقضی شد"), font_name="Vazirmatn.ttf"))
                input_row.add_widget(btn_expire)
            else:
                from kivy.uix.widget import Widget
                input_row.add_widget(Widget(size_hint_x=.3))
            input_row.add_widget(btn_settle)
            input_row.add_widget(local_tracking_input)
            tracking_box.add_widget(input_row)
            card.add_widget(tracking_box)
            screen.ids.host_demand_list.add_widget(card)
            from kivy.uix.widget import Widget
            spacer = Widget(size_hint_y=None, height=dp(15))
            screen.ids.host_demand_list.add_widget(spacer)
    def expire_host_order(self, order):
        try:
            conn = auth.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Reservations SET PaymentStatus = 'Cancelled' WHERE RandomServiceGuest = ?",
                (order['tracking_code'],)
            )
            conn.commit()
            conn.close()
            self.show_message("سفارش با موفقیت منقضی شد و از لیست حذف گردید.")
            self.show_host_orders()
        except Exception as e:
            self.show_message(f"خطا در منقضی کردن سفارش: {e}")
    def on_start(self):
        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
        except (NotImplementedError, ModuleNotFoundError):
            print("GPS is not implemented on this platform")
        if platform == "android":
            self.request_android_permissions()
        import jdatetime
        self.current_date_display = self.fa(jdatetime.date.today().strftime("%Y/%m/%d"))
    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION])
    def get_location(self):
        try:
            gps.start(1000, 0)
        except (NotImplementedError, ModuleNotFoundError):
            self.show_message("دریافت موقعیت مکانی در این سیستم‌عامل (ویندوز) پشتیبانی نمی‌شود. لطفاً برنامه را روی گوشی اندروید اجرا کنید.")
        except Exception as e:
            self.show_message(f"خطا در دریافت موقعیت: {e}")
    def on_location(self, **kwargs):
        self.current_lat = kwargs.get('lat')
        self.current_lon = kwargs.get('lon')
        try:
            admin_screen = self.root.get_screen('admin_screen')
            admin_screen.ids.location_display.text = f"Lat: {self.current_lat}, Lon: {self.current_lon}"
        except:
            pass
        gps.stop()
    @mainthread
    def on_status(self, stype, status):
        if platform == "android":
            try:
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                self.request_android_permissions()
            except NotImplementedError:
                print("GPS is not implemented on this platform")
        else:
            print("GPS is only supported on Android in this app.")
    def select_image(self):
        path = os.path.expanduser("~")
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        self.file_manager.show(path)
    def exit_manager(self, *args):
        self.file_manager.close()
    def select_path(self, path):
        self.file_manager.close()
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            self.selected_image_path = path
            try:
                admin_screen = self.root.get_screen('admin_screen')
                admin_screen.ids.image_preview.source = path
                admin_screen.ids.image_preview.height = "120dp"
                admin_screen.ids.image_preview.opacity = 1
                admin_screen.ids.image_status.text = self.fa("عکس با موفقیت انتخاب شد")
                admin_screen.ids.image_status.theme_text_color = "Custom"
                admin_screen.ids.image_status.text_color = (0, 0.6, 0, 1)
            except Exception as e:
                self.show_message(f"خطا در نمایش عکس: {e}")
        else:
            self.show_message("لطفاً فقط فایل عکس (jpg, png) انتخاب کنید.") # اصلاح شد
            self.selected_image_path = None
    def settle_host_order(self, order, entered_code):
        if entered_code.strip() != str(order['tracking_code']):
            self.show_message("کد رهگیری وارد شده اشتباه است!")
            return
        try:
            conn = auth.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Reservations SET PaymentStatus = 'Settled' WHERE RandomServiceGuest = ?",
                (order['tracking_code'],)
            )
            conn.commit()
            conn.close()
            self.show_message("تسویه با موفقیت انجام شد و مبلغ به حساب شما واریز گردید.")
            self.show_host_orders()
        except Exception as e:
            self.show_message(f"خطا در تسویه: {e}")

RestaurantApp().run()
