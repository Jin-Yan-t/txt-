import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import webbrowser

# 设置 Tcl/Tk 库路径 - 解决 "Can't find a usable init.tcl" 错误
if sys.platform.startswith('win'):
    python_dir = os.path.dirname(sys.executable)
    tcl_dir = os.path.join(python_dir, 'tcl', 'tcl8.6')
    tk_dir = os.path.join(python_dir, 'tcl', 'tk8.6')

    if os.path.exists(tcl_dir):
        os.environ['TCL_LIBRARY'] = tcl_dir
    if os.path.exists(tk_dir):
        os.environ['TK_LIBRARY'] = tk_dir


class SettingsWindow:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("设置")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        # 尝试设置图标
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass

        # 创建笔记本式选项卡
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 主题设置选项卡
        self.theme_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.theme_frame, text="主题设置")

        # 免责声明选项卡
        self.disclaimer_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.disclaimer_frame, text="免责声明")

        # 关于选项卡
        self.about_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.about_frame, text="关于")

        # 构建各选项卡内容
        self.create_theme_tab()
        self.create_disclaimer_tab()
        self.create_about_tab()

    def create_theme_tab(self):
        # 主题选择
        ttk.Label(self.theme_frame, text="选择主题:").grid(row=0, column=0, sticky=tk.W, pady=5)

        self.theme_var = tk.StringVar(value=self.app.current_theme)
        themes = ["明亮模式", "暗黑模式", "护眼模式"]

        for i, theme in enumerate(themes):
            rb = ttk.Radiobutton(
                self.theme_frame,
                text=theme,
                variable=self.theme_var,
                value=theme,
                command=self.apply_theme
            )
            rb.grid(row=i + 1, column=0, sticky=tk.W, padx=20, pady=2)

        # 字体设置
        ttk.Label(self.theme_frame, text="字体大小:").grid(row=len(themes) + 1, column=1, sticky=tk.W, pady=10)
        self.font_size_var = tk.StringVar(value="12")
        font_spin = ttk.Spinbox(
            self.theme_frame,
            from_=8,
            to=24,
            textvariable=self.font_size_var,
            width=5,
            command=self.apply_font
        )
        font_spin.grid(row=len(themes) + 1, column=0, sticky=tk.W, padx=20)

    def create_disclaimer_tab(self):
        disclaimer_text = (
            "免责声明\n\n"
            "1. 本软件仅用于阅读文本文件，不收集任何用户数据。\n"
            "2. 使用本软件打开的文件内容由用户自行负责。\n"
            "3. 开发者不对软件使用造成的任何损失负责。\n"
            "4. 请勿使用本软件打开敏感或受版权保护的内容。"
        )

        text = tk.Text(self.disclaimer_frame, wrap=tk.WORD, height=10, padx=10, pady=10)
        text.insert(tk.END, disclaimer_text)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_about_tab(self):
        about_text = (
            "大型TXT文件阅读器 v1.0\n\n"
            "功能特点:\n"
            "- 高效加载大型文本文件\n"
            "- 分页阅读，支持快速翻页\n"
            "- 书签功能，记录阅读位置\n"
            "- 自定义显示设置\n\n"
            "开发者: Jin-Yan-t\n"
            "GitHub: https://github.com/Jin-Yan-t/txt-"
        )

        text = tk.Text(self.about_frame, wrap=tk.WORD, height=12, padx=10, pady=10)
        text.insert(tk.END, about_text)
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加GitHub链接按钮
        github_btn = ttk.Button(
            self.about_frame,
            text="访问GitHub项目",
            command=lambda: webbrowser.open("https://github.com/Jin-Yan-t/txt-")
        )
        github_btn.pack(pady=10)

    def apply_theme(self):
        theme = self.theme_var.get()
        self.app.apply_theme(theme)

    def apply_font(self):
        try:
            size = int(self.font_size_var.get())
            self.app.apply_font(size)
        except ValueError:
            pass


class TextReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("大型TXT文件阅读器")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # 初始化变量
        self.file_path = ""
        self.file_size = 0
        self.file_encoding = "utf-8"
        self.total_pages = 0
        self.current_page = 0
        self.lines_per_page = 100
        self.bookmarks = {}
        self.current_theme = "明亮模式"
        self.text_font = ("微软雅黑", 12)

        # 创建UI
        self.create_widgets()

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg="#e0e0e0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status("就绪 - 请打开一个TXT文件")

    def create_widgets(self):
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg="#e0e0e0", bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)

        # 按钮
        open_btn = tk.Button(toolbar, text="打开文件", command=self.open_file,
                             bg="#4CAF50", fg="white", padx=10, pady=5)
        open_btn.pack(side=tk.LEFT, padx=5, pady=2)

        prev_btn = tk.Button(toolbar, text="上一页", command=self.prev_page,
                             bg="#2196F3", fg="white", padx=10, pady=5)
        prev_btn.pack(side=tk.LEFT, padx=5, pady=2)

        next_btn = tk.Button(toolbar, text="下一页", command=self.next_page,
                             bg="#2196F3", fg="white", padx=10, pady=5)
        next_btn.pack(side=tk.LEFT, padx=5, pady=2)

        bookmark_btn = tk.Button(toolbar, text="添加书签", command=self.add_bookmark,
                                 bg="#FF9800", fg="white", padx=10, pady=5)
        bookmark_btn.pack(side=tk.LEFT, padx=5, pady=2)

        goto_btn = tk.Button(toolbar, text="转到页面", command=self.goto_page,
                             bg="#9C27B0", fg="white", padx=10, pady=5)
        goto_btn.pack(side=tk.LEFT, padx=5, pady=2)

        # 设置按钮
        settings_btn = tk.Button(toolbar, text="设置", command=self.open_settings,
                                 bg="#607D8B", fg="white", padx=10, pady=5)
        settings_btn.pack(side=tk.RIGHT, padx=5, pady=2)

        # 页面控制
        page_frame = tk.Frame(toolbar, bg="#e0e0e0")
        page_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(page_frame, text="页面:", bg="#e0e0e0").pack(side=tk.LEFT)
        self.page_entry = tk.Entry(page_frame, width=6)
        self.page_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(page_frame, text="/", bg="#e0e0e0").pack(side=tk.LEFT)
        self.total_pages_label = tk.Label(page_frame, text="0", bg="#e0e0e0")
        self.total_pages_label.pack(side=tk.LEFT)

        # 显示设置
        settings_frame = tk.Frame(toolbar, bg="#e0e0e0")
        settings_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(settings_frame, text="每页行数:", bg="#e0e0e0").pack(side=tk.LEFT)
        self.lines_var = tk.StringVar(value="100")
        lines_spin = tk.Spinbox(settings_frame, from_=50, to=500, increment=10,
                                textvariable=self.lines_var, width=5, command=self.update_lines_per_page)
        lines_spin.pack(side=tk.LEFT, padx=5)

        # 文本显示区域
        text_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加滚动条
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 文本显示控件
        self.text_area = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                 font=self.text_font, bg="white", padx=10, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        # 配置滚动条
        scrollbar.config(command=self.text_area.yview)

        # 书签面板
        self.bookmark_frame = tk.Frame(self.root, width=200, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)
        self.bookmark_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        self.bookmark_frame.pack_propagate(False)

        tk.Label(self.bookmark_frame, text="书签", font=("微软雅黑", 12, "bold"),
                 bg="#f0f0f0", pady=5).pack(fill=tk.X)

        self.bookmark_listbox = tk.Listbox(self.bookmark_frame, bg="white", font=("微软雅黑", 10))
        self.bookmark_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.bookmark_listbox.bind("<<ListboxSelect>>", self.goto_bookmark)

        # 初始隐藏书签面板
        self.bookmark_frame.pack_forget()

    def open_settings(self):
        SettingsWindow(self.root, self)

    def apply_theme(self, theme):
        self.current_theme = theme
        if theme == "明亮模式":
            self.text_area.config(bg="white", fg="black")
            self.root.configure(bg="#f0f0f0")
            self.status_bar.configure(bg="#e0e0e0")
        elif theme == "暗黑模式":
            self.text_area.config(bg="#2d2d2d", fg="#e0e0e0")
            self.root.configure(bg="#1e1e1e")
            self.status_bar.configure(bg="#333333")
        elif theme == "护眼模式":
            self.text_area.config(bg="#C7EDCC", fg="black")
            self.root.configure(bg="#e0f0e0")
            self.status_bar.configure(bg="#d0e0d0")

    def apply_font(self, size):
        self.text_font = (self.text_font[0], size)
        self.text_area.config(font=self.text_font)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if file_path:
            self.file_path = file_path
            try:
                # 获取文件大小
                self.file_size = os.path.getsize(file_path)

                # 重置状态
                self.current_page = 0
                self.bookmarks = {}
                self.bookmark_listbox.delete(0, tk.END)
                self.bookmark_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

                # 更新状态栏
                size_mb = self.file_size / (1024 * 1024)
                self.update_status(f"正在打开文件: {os.path.basename(file_path)} ({size_mb:.2f} MB)...")
                self.root.update()

                # 计算总页数
                start_time = time.time()
                self.total_pages = self.calculate_total_pages()
                end_time = time.time()

                self.total_pages_label.config(text=str(self.total_pages))
                self.update_status(
                    f"文件加载完成! 总页数: {self.total_pages}, 计算耗时: {end_time - start_time:.2f}秒")

                # 显示第一页
                self.show_page(0)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件: {str(e)}")

    def calculate_total_pages(self):
        """计算文件总页数"""
        line_count = 0
        try:
            with open(self.file_path, "r", encoding=self.file_encoding, errors="ignore") as file:
                for _ in file:
                    line_count += 1
            return max(1, (line_count + self.lines_per_page - 1) // self.lines_per_page)
        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错: {str(e)}")
            return 0

    def show_page(self, page_num):
        if not self.file_path:
            return

        if page_num < 0:
            page_num = 0
        if page_num >= self.total_pages:
            page_num = self.total_pages - 1

        self.current_page = page_num
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(page_num + 1))

        # 更新状态栏
        self.update_status(f"正在加载第 {page_num + 1}/{self.total_pages} 页...")
        self.root.update()

        try:
            # 清空文本区域
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete(1.0, tk.END)

            # 读取指定页的内容
            start_line = page_num * self.lines_per_page
            content = []
            with open(self.file_path, "r", encoding=self.file_encoding, errors="ignore") as file:
                # 跳过前面的行
                for _ in range(start_line):
                    try:
                        next(file)
                    except StopIteration:
                        break

                # 读取当前页的行
                for i in range(self.lines_per_page):
                    line = file.readline()
                    if not line:
                        break
                    content.append(line)

            # 显示内容
            self.text_area.insert(tk.END, ''.join(content))
            self.text_area.config(state=tk.DISABLED)

            # 滚动到顶部
            self.text_area.yview_moveto(0)

            # 更新状态
            self.update_status(
                f"第 {page_num + 1}/{self.total_pages} 页 | 文件: {os.path.basename(self.file_path)}")

            # 高亮显示书签
            self.highlight_bookmarks()

        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错: {str(e)}")

    def prev_page(self):
        if self.total_pages > 0:
            self.show_page(self.current_page - 1)

    def next_page(self):
        if self.total_pages > 0:
            self.show_page(self.current_page + 1)

    def goto_page(self):
        if not self.total_pages:
            return

        try:
            page_num = int(self.page_entry.get()) - 1
            self.show_page(page_num)
        except ValueError:
            messagebox.showwarning("输入错误", "请输入有效的页码")

    def add_bookmark(self):
        if not self.file_path:
            return

        bookmark_name = f"书签 {len(self.bookmarks) + 1} (第 {self.current_page + 1} 页)"
        self.bookmarks[bookmark_name] = self.current_page
        self.bookmark_listbox.insert(tk.END, bookmark_name)
        self.highlight_bookmarks()

    def goto_bookmark(self, event):
        if not self.bookmark_listbox.curselection():
            return

        selected = self.bookmark_listbox.get(self.bookmark_listbox.curselection())
        if selected in self.bookmarks:
            self.show_page(self.bookmarks[selected])

    def highlight_bookmarks(self):
        # 移除所有现有标记
        self.text_area.tag_remove("bookmark", "1.0", tk.END)

        # 添加当前页的书签标记
        if self.current_page in self.bookmarks.values():
            self.text_area.tag_config("bookmark", background="#FFFF99")
            self.text_area.tag_add("bookmark", "1.0", "1.0 lineend")

    def update_lines_per_page(self):
        try:
            new_lines = int(self.lines_var.get())
            if 50 <= new_lines <= 500:
                self.lines_per_page = new_lines
                if self.file_path:
                    self.total_pages = self.calculate_total_pages()
                    self.total_pages_label.config(text=str(self.total_pages))
                    self.show_page(min(self.current_page, self.total_pages - 1))
        except ValueError:
            pass

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextReaderApp(root)
    root.mainloop()
