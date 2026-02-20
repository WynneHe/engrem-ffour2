from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.resources import resource_find
import pandas as pd
import random
import os
import difflib

# 注册系统字体以支持中文显示
try:
    # 尝试注册一些常见的中文字体
    font_paths = [
        'C:\Windows\Fonts\simsun.ttc',  # 宋体
        'C:\Windows\Fonts\simhei.ttf',  # 黑体
        'C:\Windows\Fonts\msyh.ttc',  # 微软雅黑
        'C:\Windows\Fonts\times.ttf',  # Times New Roman - 支持音标
        'C:\Windows\Fonts\arial.ttf',  # Arial - 支持音标
        'C:\Windows\Fonts\cour.ttf'  # Courier New - 支持音标
    ]

    for path in font_paths:
        if os.path.exists(path):
            font_name = os.path.splitext(os.path.basename(path))[0]
            LabelBase.register(name=font_name, fn_regular=path)
            print(f"已注册字体: {font_name} 路径: {path}")
            break
except Exception as e:
    print(f"注册字体时出错: {str(e)}")

# 设置窗口背景色为护眼色
Window.clearcolor = (0.93, 1, 0.93, 1)

# 重新定义颜色 - 调整为更浅的按钮颜色
COLORS = {
    'background': (0.93, 1, 0.93, 1),  # 护眼色
    'text': (0.2, 0.2, 0.2, 1),
    'primary': (0.42, 0.45, 0.5, 1),
    'secondary': (0.9, 0.9, 0.9, 0.6),  # 更浅的按钮背景
    'correct': (0.6, 0.9, 0.6, 1),  # 绿色表示正确
    'incorrect': (0.99, 0.65, 0.65, 1),  # 红色表示错误
    'vowel': (1, 0.27, 0, 1),  # 橙红色 - 元音，与EgTest.py中的ff4500对应
    'consonant': (0.39, 0.8, 0.93, 1),  # 蓝色 - 辅音，与EgTest.py中的6495ed对应
    'button': (0.96, 0.96, 0.96, 0.3),  # 更浅的按钮背景
    'button_text': (0.2, 0.2, 0.2, 1),  # 深色按钮文字，统一所有按钮的文字颜色
    'button_hover': (0.8, 0.8, 0.8, 0.2)  # 悬停效果
}
print(f"COLORS字典初始化完成 - button颜色: {COLORS['button']}")


# 彩色标签类 - 用于显示元音和辅音不同颜色
class ColoredLabel(BoxLayout):
    def __init__(self, text, **kwargs):
        # 移除kwargs中可能包含的不支持属性
        if 'halign' in kwargs:
            del kwargs['halign']
        if 'valign' in kwargs:
            del kwargs['valign']
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 0  # 设置为0以确保字符紧凑显示
        self.add_colored_chars(text)

    def add_colored_chars(self, text):
        vowels = set('aeiouAEIOU')
        self.char_labels = []

        # 创建一个水平布局来包裹所有字符标签，并使其居中
        chars_container = BoxLayout(orientation='horizontal', size_hint_x=1)

        # 计算字符总数
        total_chars = len(text)

        for char in text:
            # 检查是否为元音
            if char in vowels:
                color = COLORS['vowel']
            else:
                color = COLORS['consonant']

            char_label = Label(
                text=char,
                font_size='36sp',  # 增大字体
                color=color,  # 按照元音和辅音分色显示，而不是使用button_text颜色
                size_hint_x=1.0 / total_chars,  # 平均分配宽度
                halign='center',  # 水平居中
                valign='middle',  # 垂直居中
                text_size=(None, None),  # 让文本大小自适应
                font_name='simsun'  # 使用已注册的字体
            )
            chars_container.add_widget(char_label)
            self.char_labels.append(char_label)

        # 将容器添加到按钮
        self.add_widget(chars_container)


# 彩色按钮类 - 用于选项按钮
class ColoredButton(ButtonBehavior, BoxLayout):
    def __init__(self, text, callback, **kwargs):
        # 移除kwargs中可能包含的不支持属性
        if 'halign' in kwargs:
            del kwargs['halign']
        if 'valign' in kwargs:
            del kwargs['valign']
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.text = text
        self.callback = callback
        self.padding = [10, 5]
        self.size_hint_y = None
        self.height = 100  # 增加按钮高度
        self.size_hint_x = 1  # 确保按钮占满整个网格单元

        print(f"ColoredButton初始化 - 使用button颜色: {COLORS['button']}")

        # 设置背景 - 使用更浅的背景色
        with self.canvas.before:
            self.bg_color = Color(*COLORS['button'])
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

        # 延迟添加字符，确保布局已初始化
        Clock.schedule_once(lambda dt: self.add_colored_chars(text), 0)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def add_colored_chars(self, text):
        vowels = set('aeiouAEIOU')
        # 创建一个水平布局来包裹文本标签
        chars_container = BoxLayout(orientation='horizontal', size_hint_x=1)
        chars_container.bind(size=self.update_text_label_size)

        # 构建带有颜色和加粗样式的文本
        colored_text = ''
        for char in text:
            # 检查是否为元音
            if char in vowels:
                color = 'ff4500'  # 橙红色 - 元音
            else:
                color = '6495ed'  # 蓝色 - 辅音

            # 添加加粗和颜色样式
            colored_text += f'[b][color={color}]{char}[/color][/b]'

        # 创建一个标签显示整个文本，使用markup=True支持富文本
        self.text_label = Label(
            text=colored_text,
            markup=True,  # 启用富文本标记
            font_size=40,  # 显著增大字体大小
            halign='center',  # 水平居中
            valign='middle',  # 垂直居中
            size_hint=(1, 1),  # 占满整个容器
            text_size=chars_container.size,  # 文本大小适应容器
            font_name='SimHei'  # 使用支持更好的字体
        )

        chars_container.add_widget(self.text_label)
        # 将容器添加到按钮
        self.add_widget(chars_container)

    def update_text_label_size(self, instance, value):
        # 确保文本标签在容器中居中显示
        if hasattr(self, 'text_label') and value[0] > 0 and value[1] > 0:
            # 更新文本标签的大小以适应容器
            self.text_label.text_size = (value[0], None)
            # 强制重新计算文本大小
            self.text_label.texture_update()

    def on_press(self):
        # 改变背景色表示按下
        self.bg_color.rgba = COLORS['button_hover']

    def on_release(self):
        # 恢复背景色
        self.bg_color.rgba = COLORS['button']
        # 调用回调函数
        self.callback(self.text)


# 分类选择页面 - 完整实现
class CategorySelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.build_ui()

    def set_app(self, app):
        self.app = app
        # 当应用引用设置后，加载分类
        self.load_categories()

    def build_ui(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # 设置整个背景颜色为护眼色
        with main_layout.canvas.before:
            Color(0.93, 1, 0.93, 1)  # 护眼色
            self.rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=self.update_rect, size=self.update_rect)

        # 标题标签
        title_label = Label(
            text='选择单词类别',
            font_size='48sp',
            color=COLORS['text'],
            size_hint_y=0.2,
            font_name='simsun'
        )
        main_layout.add_widget(title_label)

        # 分类按钮区域 - 使用滚动视图
        categories_scroll = ScrollView(size_hint_y=0.7)
        self.categories_layout = GridLayout(
            cols=5,  # 5列布局
            spacing=15,
            padding=10,
            size_hint_y=None
        )
        self.categories_layout.bind(minimum_height=self.categories_layout.setter('height'))
        categories_scroll.add_widget(self.categories_layout)

        main_layout.add_widget(categories_scroll)

        # 添加主布局到屏幕
        self.add_widget(main_layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def load_categories(self):
        if not self.app:
            return

        try:
            # 尝试加载Excel文件
            excel_file = 'data_four/words_four2.xlsx'
            # 使用resource_find查找文件路径
            actual_path = resource_find(excel_file)
            if not actual_path or not os.path.exists(actual_path):
                self.show_error(f'找不到Excel文件: {excel_file}')
                return

            # 读取Excel文件的所有工作表名称作为分类
            xl = pd.ExcelFile(actual_path)
            categories = xl.sheet_names

            # 清空现有按钮
            self.categories_layout.clear_widgets()

            # 为每个分类创建按钮 - 使用更浅的背景色和统一的文字颜色
            for category in categories:
                category_button = Button(
                    text=category,
                    font_size='20sp',  # 减小字体大小
                    background_color=COLORS['button'],  # 更浅的按钮背景
                    color=COLORS['button_text'],  # 统一的文字颜色
                    size_hint_y=None,
                    height=80,  # 减小按钮高度
                    font_name='simsun'  # 使用已注册的字体
                )

                # 绑定按钮事件
                category_button.bind(on_press=self.on_category_selected)

                # 添加到布局
                self.categories_layout.add_widget(category_button)

        except Exception as e:
            self.show_error(f'加载分类时出错: {str(e)}')

    def on_category_selected(self, instance):
        if not self.app:
            return

        try:
            # 获取选中的分类名称
            category = instance.text

            # 加载该分类的单词
            self.app.load_category_words(category)

            # 切换到单词学习页面
            self.manager.current = 'word_learning'

            # 让WordLearningScreen加载第一个单词
            word_screen = self.manager.get_screen('word_learning')
            word_screen.load_word()

        except Exception as e:
            self.show_error(f'选择分类时出错: {str(e)}')

    def show_error(self, message):
        # 创建错误弹窗
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_name='simsun', color=COLORS['text']))
        close_button = Button(
            text='确定',
            size_hint_y=None,
            height=40,
            font_name='simsun',
            background_color=COLORS['button'],  # 更浅的按钮背景
            color=COLORS['button_text']  # 统一的文字颜色
        )
        content.add_widget(close_button)

        popup = Popup(title='错误', content=content, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


# 单词学习页面 - 优化后的实现
class WordLearningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_sound = None
        self.has_sound = True  # 新增：控制是否播放音频
        self.hint_index = 0  # 新增：提示计数
        self.correct_count = 0  # 初始化正确计数
        self.build_ui()

    def set_app(self, app):
        self.app = app

    def build_ui(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        print(f"WordLearningScreen创建按钮 - 使用button颜色: {COLORS['button']}")
        # 设置整个背景颜色为护眼色
        with main_layout.canvas.before:
            Color(0.93, 1, 0.93, 1)  # 护眼色
            self.rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
            main_layout.bind(pos=self.update_rect, size=self.update_rect)

        # 顶部返回按钮和进度显示
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.05)
        # 进度标签 - 显示已答对/总题数
        self.progress_label = Label(
            text="已答对 0/0",
            font_size='18sp',
            color=COLORS['text'],
            size_hint_x=0.8,
            halign='right',
            valign='middle',
            font_name='simsun'
        )
        top_layout.add_widget(self.progress_label)

        back_button = Button(
            text="返回",
            font_size='18sp',  # 减小字体
            background_color=COLORS['button'],  # 更浅的按钮背景
            color=COLORS['button_text'],  # 统一的文字颜色
            size_hint_x=0.1,  # 减小宽度
            font_name='simsun'  # 使用已注册的字体
        )
        back_button.bind(on_press=self.go_back)
        top_layout.add_widget(back_button)
        # 右侧空白标签
        top_layout.add_widget(Label(size_hint_x=0.1))

        main_layout.add_widget(top_layout)
        # 汉字显示区域 - 居中显示在输入框上方，右侧放置喇叭按钮
        chinese_speaker_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)

        # 左侧空白空间，使汉字居中
        chinese_speaker_layout.add_widget(Label(size_hint_x=0.9))
        # 汉字标签
        self.chinese_label = Label(
            text="",  # 初始为空，稍后在load_word中设置
            font_size=100,  # 默认字体大小
            color=COLORS['text'],
            font_name='simsun',
            size_hint_x=0.5,
            halign='center',
            valign='middle'
        )
        chinese_speaker_layout.add_widget(self.chinese_label)

        # 发音按钮 - 喇叭图标，放置在汉字右侧
        self.speaker_button = Button(
            text="",
            on_press=self.play_pronunciation,
            background_color=COLORS['button'],
            size_hint=(0.2, 0.4),  # 调整宽度和高度
            pos_hint={'x': -1, 'center_y': 0.4},  # 调整位置
            background_normal='data/image/voice1.png',
            background_down='data/image/voice.png',
            valign='middle'
        )
        chinese_speaker_layout.add_widget(self.speaker_button)

        # 右侧空白空间
        chinese_speaker_layout.add_widget(Label(size_hint_x=0.8))

        main_layout.add_widget(chinese_speaker_layout)

        # 控制按钮部分 - 4个按钮大小、配色都一样
        self.control_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)

        # 音标显示按钮 - 样式与其他按钮保持一致，但优化音标显示
        self.pronunciation_button = Button(
            text="",  # 将在load_word中设置
            font_name='times',  # 使用Times New Roman字体显示音标
            font_size=40,  # 进一步增大字体大小以确保音标清晰显示
            size_hint_x=0.25,  # 与其他按钮相同的大小
            background_color=COLORS['button'],  # 更浅的按钮背景
            color=COLORS['text'],  # 使用深色文字以提高可读性
            halign='center',
            valign='middle'
        )

        self.hint_button = Button(
            text='提示',
            on_press=self.show_hint,
            font_name='simsun',
            background_color=COLORS['button'],  # 更浅的按钮背景
            font_size=24,  # 统一字体大小
            size_hint_x=0.25,  # 统一大小
            color=COLORS['button_text']  # 统一的文字颜色
        )

        self.clear_button = Button(
            text='清空',
            on_press=self.clear_selection,
            font_name='simsun',
            background_color=COLORS['button'],  # 更浅的按钮背景
            font_size=24,  # 统一字体大小
            size_hint_x=0.25,  # 统一大小
            color=COLORS['button_text']  # 统一的文字颜色
        )

        self.sound_toggle_button = Button(
            text='关闭发音' if self.has_sound else '开启发音',
            on_press=self.toggle_sound,
            font_name='simsun',
            background_color=COLORS['button'],  # 更浅的按钮背景
            font_size=24,  # 统一字体大小
            size_hint_x=0.25,  # 统一大小
            color=COLORS['button_text']  # 统一的文字颜色
        )

        self.control_layout.add_widget(self.pronunciation_button)  # 音标显示
        self.control_layout.add_widget(self.hint_button)  # 提示按钮
        self.control_layout.add_widget(self.clear_button)  # 清空按钮
        self.control_layout.add_widget(self.sound_toggle_button)  # 声音开关

        main_layout.add_widget(self.control_layout)

        # 答题部分
        self.answer_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.15), pos_hint={'center_y': 0.5})
        self.answer_input = TextInput(
            text='',
            multiline=False,
            font_size=90,
            halign='center',
            background_color=(1, 1, 1, 1),  # 白色背景
            font_name='simsun'
        )
        self.answer_layout.add_widget(self.answer_input)
        main_layout.add_widget(self.answer_layout)

        # 选项区域 - 使用滚动视图
        options_scroll = ScrollView(size_hint_y=0.35)
        self.options_layout = GridLayout(
            cols=5,  # 调整为5列布局
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        self.options_layout.bind(minimum_height=self.options_layout.setter('height'))
        options_scroll.add_widget(self.options_layout)

        main_layout.add_widget(options_scroll)

        # 将主布局添加到屏幕
        self.add_widget(main_layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _adjust_font_size_based_on_length(self, label):
        """根据文本长度动态调整字体大小"""
        if not label.text:  # 如果文本为空，不进行调整
            return

        text_length = len(label.text)
        # 根据字数设置字体大小
        if text_length <= 2:
            label.font_size = 100
        elif text_length <= 4:
            label.font_size = 80
        elif text_length <= 6:
            label.font_size = 60
        elif text_length <= 8:
            label.font_size = 50
        else:
            label.font_size = 40  # 对于更长的文本，使用最小字体大小

        # 强制标签重新布局以应用新的字体大小
        label.texture_update()

    def load_word(self):
        if not self.app or not hasattr(self.app, 'current_words') or not self.app.current_words:
            return
        # 清空输入和选项
        if hasattr(self.app, 'selected_pronunciations'):
            self.app.selected_pronunciations = []
        self.answer_input.text = ''
        self.options_layout.clear_widgets()
        self.hint_index = 0  # 重置提示计数

        # 获取当前单词
        try:
            current_word = self.app.current_words[self.app.current_word_index]
            print(f"加载单词: {current_word.get('chinese', '未知')}, 音频文件: {current_word.get('sound', '')}")

            # 更新标签
            self.chinese_label.text = str(current_word.get('chinese', ''))
            # 调整字体大小
            self._adjust_font_size_based_on_length(self.chinese_label)

            pronunciation_text = str(current_word.get('syllables', ''))
            self.pronunciation_button.text = pronunciation_text
            self.pronunciation_button.halign = 'center'
            self.pronunciation_button.valign = 'middle'

            # 加载选项
            self.load_options()

            # 更新进度显示
            if hasattr(self.app, 'current_words'):
                total_count = len(self.app.current_words)
                self.progress_label.text = f"已答对 {self.correct_count}/{total_count}"

            # 自动播放音频
            self.play_pronunciation(None)
        except Exception as e:
            print(f"加载单词信息时出错: {str(e)}")

    def load_options(self):
        try:
            # 获取当前单词的正确发音字节 - 从pronunciation字段获取音节
            current_word = self.app.current_words[self.app.current_word_index]
            pronunciation_str = str(current_word.get('pronunciation', '')).strip()
            current_syllables = pronunciation_str.split(',') if pronunciation_str else []

            # 排除当前单词的正确发音字节
            if hasattr(self.app, 'all_pronunciations'):
                other_syllables = [s for s in self.app.all_pronunciations if s not in current_syllables]
                random.shuffle(other_syllables)
            else:
                other_syllables = []

            # 复制当前单词的正确发音字节
            all_options = current_syllables.copy()

            # 补充干扰选项，直到达到8个选项
            while len(all_options) < 10 and other_syllables:
                all_options.append(other_syllables.pop(0))

            # 打乱选项顺序
            random.shuffle(all_options)

            # 创建按钮
            for syllable in all_options:
                # 使用ColoredButton而不是普通Button
                option_button = ColoredButton(
                    text=syllable,
                    callback=self.add_syllable
                )
                self.options_layout.add_widget(option_button)

        except Exception as e:
            print(f"加载选项时出错: {str(e)}")

    def add_syllable(self, syllable):
        # 添加选中的音节到输入框
        current_text = self.answer_input.text
        self.answer_input.text = current_text + syllable

        # 检查答案
        self.check_answer()

    def clear_selection(self, instance=None):
        # 清空输入框
        self.answer_input.text = ''

    def play_pronunciation(self, instance):
        if self.has_sound:
            # 播放当前单词的发音
            if not self.app or not hasattr(self.app, 'current_words') or not self.app.current_words:
                return

            try:
                current_word = self.app.current_words[self.app.current_word_index]
                self.pronounce_word(current_word)
            except Exception as e:
                print(f"播放当前单词发音时出错: {str(e)}")

    def pronounce_word(self, word):
        # 停止当前播放的声音
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None

        try:
            # 获取音频文件名
            sound_file = word.get('sound', '')
            if not sound_file:
                print("没有音频文件")
                return

            # 确保文件扩展名正确
            if not sound_file.endswith('.wav'):
                sound_file += '.wav'

            # 修复音频路径 - 直接使用Excel中指定的路径
            sound_path = sound_file

            # 如果sound_file不包含路径分隔符，添加默认路径
            if '\\' not in sound_file and '/' not in sound_file:
                sound_path = os.path.join("data", "sound", sound_file)

            print(f"尝试加载音频文件: {sound_path}")

            # 使用resource_find查找文件路径
            actual_path = resource_find(sound_path)
            if not actual_path:
                print(f"资源查找失败，尝试直接使用路径: {sound_path}")
                actual_path = sound_path

            # 直接尝试加载音频文件
            if os.path.exists(actual_path):
                try:
                    print(f"找到文件: {actual_path}")
                    self.current_sound = SoundLoader.load(actual_path)
                    if self.current_sound:
                        print(f"成功加载并播放音频: {actual_path}")
                        self.current_sound.play()
                    else:
                        print(f"无法加载音频文件: {actual_path} (SoundLoader返回None)")
                except Exception as e:
                    print(f"播放音频时出错: {str(e)}")
            else:
                print(f"音频文件不存在: {actual_path}")

        except Exception as e:
            print(f"播放音频时出错: {str(e)}")

    def show_hint(self, instance):
        try:
            if not self.app or not hasattr(self.app, 'current_words') or not self.app.current_words:
                return

            current_word = self.app.current_words[self.app.current_word_index]
            word = str(current_word.get('word', ''))

            # 获取所有音节 - 从pronunciation字段获取（实际存储的是音节）
            if 'pronunciation' in current_word and current_word['pronunciation']:
                pronunciation_str = str(current_word['pronunciation'])
                syllables = pronunciation_str.split(',')

                # 检查是否还有未提示的音节
                if self.hint_index < len(syllables):
                    # 显示当前index对应的音节
                    next_syllable = syllables[self.hint_index]
                    self.answer_input.text += next_syllable
                    # 增加提示索引，为下次提示做准备
                    self.hint_index += 1
                elif word:  # 如果所有音节都已提示但单词还不正确
                    # 显示整个单词作为最终提示
                    self.answer_input.text = word
            elif word:  # 如果没有pronunciation字段但有word字段
                # 显示整个单词作为提示
                self.answer_input.text = word

            # 检查答案
            self.check_answer()

        except Exception as e:
            print(f"显示提示时出错: {str(e)}")

    def toggle_sound(self, instance):
        self.has_sound = not self.has_sound
        instance.text = '关闭发音' if self.has_sound else '开启发音'

    def check_answer(self):
        try:
            if not self.app or not hasattr(self.app, 'current_words') or not self.app.current_words:
                return

            current_word = self.app.current_words[self.app.current_word_index]
            correct_word = str(current_word.get('word', '')).strip()
            user_answer = self.answer_input.text.strip()

            # 修正：将correct_answer改为correct_word
            if user_answer == correct_word:
                # 回答正确，答案框背景变绿色
                self.answer_input.background_color = COLORS['correct']
                self.correct_count += 1
                total_count = len(self.app.current_words)
                self.progress_label.text = f"已答对 {self.correct_count}/{total_count}"

                # 再读一遍正确音频
                self.pronounce_word(current_word)

                # 短暂延迟后进入下一题
                def next_word_func(dt):
                    self.next_word()

                Clock.schedule_once(next_word_func, 1)

        except Exception as e:
            print(f"检查答案时出错: {str(e)}")

    def next_word(self):
        try:
            if not self.app or not hasattr(self.app, 'current_words') or not self.app.current_words:
                return

            # 恢复答案框背景颜色
            self.answer_input.background_color = (1, 1, 1, 1)

            # 更新当前单词索引
            self.app.current_word_index += 1

            # 检查是否所有单词都学习完毕
            if self.app.current_word_index >= len(self.app.current_words):
                # 所有单词学习完毕，可以添加一些提示或返回到分类选择页面
                self.show_finish_message()
                return

            # 加载下一个单词
            self.load_word()

        except Exception as e:
            print(f"加载下一个单词时出错: {str(e)}")

    def show_finish_message(self):
        # 创建完成消息弹窗
        content = BoxLayout(orientation='vertical', padding=10, spacing=20)

        # 设置内容区域背景色
        with content.canvas.before:
            Color(1, 1, 1, 1)  # 白色背景
            self.content_rect = Rectangle(pos=content.pos, size=content.size)
            content.bind(pos=lambda instance, value: setattr(self.content_rect, 'pos', value),
                         size=lambda instance, value: setattr(self.content_rect, 'size', value))

        # 添加完成消息标签，使用更大的字体和深色文本
        finish_label = Label(
            text='恭喜！您已完成所有单词的学习。',
            font_name='simsun',
            color=(0, 0, 0, 1),  # 纯黑色文本确保清晰可见
            font_size='24sp',  # 增大字体大小
            halign='center',
            valign='middle'
        )
        finish_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
        content.add_widget(finish_label)

        # 返回按钮使用明显的颜色
        back_button = Button(
            text='返回分类选择',
            size_hint_y=None,
            height=60,  # 增大按钮高度
            font_name='simsun',
            font_size='18sp',  # 增大按钮文字
            background_color=(0.95, 0.95, 0.95, 0.3),  # 浅绿色背景
            color=(0, 0, 0, 1)  # 黑色文字确保清晰
        )
        content.add_widget(back_button)

        # 创建弹窗并设置背景色
        popup = Popup(
            title='学习完成',
            content=content,
            size_hint=(0.7, 0.4),
            background_color=(1, 1, 1, 1),  # 白色弹窗背景
            title_color=(0, 0, 0, 1)  # 黑色标题文字
        )

        # 绑定按钮事件
        back_button.bind(on_press=lambda instance: (popup.dismiss(), self.go_back(None)))
        popup.open()

    def go_back(self, instance):
        # 重置正确计数
        self.correct_count = 0
        # 切换到分类选择页面
        self.manager.current = 'category_selection'


# 单词拼写应用主类 - 完整实现
class WordSpellingApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_sound = None
        self.has_sound = True
        self.hint_index = 0
        self.correct_count = 0  # 新增：记录已答对的数量

    def build(self):
        # 创建屏幕管理器
        self.sm = ScreenManager()

        # 创建分类选择屏幕
        category_screen = CategorySelectionScreen(name='category_selection')
        category_screen.set_app(self)

        # 创建单词学习屏幕
        word_screen = WordLearningScreen(name='word_learning')
        word_screen.set_app(self)

        # 添加屏幕到管理器
        self.sm.add_widget(category_screen)
        self.sm.add_widget(word_screen)

        # 顶部返回按钮和进度显示
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=0.05)

        # 新增：答题进度显示标签
        self.progress_label = Label(
            text="已答对 0/0",
            font_size='20sp',
            color=COLORS['text'],
            size_hint_x=0.15,
            halign='right',
            font_name='simsun'
        )
        top_layout.add_widget(self.progress_label)

        # 调整左侧空白空间
        top_layout.add_widget(Label(size_hint_x=0.75))

        back_button = Button(
            text="返回",
            font_size='18sp',
            background_color=COLORS['button'],
            color=COLORS['button_text'],
            size_hint_x=0.1,
            font_name='simsun'
        )
        back_button.bind(on_press=self.go_back)
        top_layout.add_widget(back_button)

        # 设置初始屏幕
        self.sm.current = 'category_selection'

        return self.sm

    def go_back(self, instance=None):
        # 如果当前在单词学习页面，返回分类选择页面
        if hasattr(self, 'sm') and self.sm.current == 'word_learning':
            self.sm.current = 'category_selection'
            # 重置正确计数
            self.correct_count = 0
            # 更新进度显示
            if hasattr(self, 'progress_label'):
                self.progress_label.text = "已答对 0/0"

    def load_category_words(self, category):
        try:
            # 尝试加载Excel文件 - 统一使用words_four2.xlsx
            excel_file = 'data_four/words_four2.xlsx'
            # 使用resource_find查找文件路径
            actual_path = resource_find(excel_file)
            if not actual_path or not os.path.exists(actual_path):
                print(f'找不到Excel文件: {excel_file}')
                return

            # 读取指定分类（工作表）的数据
            try:
                df = pd.read_excel(actual_path, sheet_name=category)
            except ValueError as e:
                print(f'加载分类时出错: {str(e)}')
                return

            # 检查必要的列是否存在
            required_columns = ['chinese', 'word', 'pronunciation', 'syllables', 'sound']
            if not all(col in df.columns for col in required_columns):
                print(f'Excel文件缺少必要的列。需要的列: {required_columns}')
                return

            # 转换为字典列表
            self.current_words = []
            self.all_pronunciations = []

            for index, row in df.iterrows():
                # 将pronunciation字段的值分割成列表
                pronunciation_str = str(row.get('pronunciation', '')).strip()
                pronunciations = pronunciation_str.split(',') if pronunciation_str else []

                # 添加到所有发音列表中
                self.all_pronunciations.extend(pronunciations)

                # 创建单词信息字典
                word_info = {
                    'chinese': row.get('chinese', ''),
                    'word': row.get('word', ''),
                    'pronunciation': pronunciation_str,
                    'syllables': row.get('syllables', ''),  # 存储音标
                    'sound': row.get('sound', '')
                }

                self.current_words.append(word_info)

            # 新增：对单词列表进行随机打乱
            random.shuffle(self.current_words)

            # 初始化当前单词索引
            self.current_word_index = 0

            print(f'成功加载分类 "{category}" 的 {len(self.current_words)} 个单词')
        except Exception as e:
            print(f'加载单词时出错: {str(e)}')


# 应用入口
if __name__ == '__main__':
    WordSpellingApp().run()