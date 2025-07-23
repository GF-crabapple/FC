import os
import hashlib
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from tkinter import font

VERSION = "2.3"
AUTHOR = "Crabapple"

def calculate_file_md5(file_path):
    """计算单个文件的MD5值"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def calculate_directory_md5(dir_path):
    """递归计算目录中所有文件的MD5值，返回组合后的MD5"""
    hasher = hashlib.md5()
    file_paths = sorted(Path(dir_path).rglob('*'))
    for file_path in file_paths:
        if file_path.is_file():
            rel_path = str(file_path.relative_to(dir_path))
            hasher.update(rel_path.encode('utf-8'))
            file_hash = calculate_file_md5(file_path)
            hasher.update(file_hash.encode('utf-8'))
    return hasher.hexdigest()

def calculate_md5(path):
    """根据路径类型计算文件或目录的MD5"""
    if os.path.isfile(path):
        return calculate_file_md5(path)
    elif os.path.isdir(path):
        return calculate_directory_md5(path)
    else:
        raise ValueError(f"路径不存在或不支持: {path}")

def save_to_temp_file(content):
    """将内容保存到临时文件并返回文件路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md5', dir=script_dir) as f:
        f.write(content)
        return f.name

def delete_temp_file(file_path):
    """删除临时文件"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"警告: 无法删除临时文件 {file_path}: {e}")

class MD5ComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MD5比较工具")
        self.root.geometry("750x500")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="SimHei", size=10)
        self.root.option_add("*Font", self.default_font)
        
        self.temp_files = []
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="MD5文件比较工具", 
            font=("SimHei", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(
            title_frame, 
            text=f"v{VERSION} | 作者: {AUTHOR}", 
            font=("SimHei", 10)
        )
        version_label.pack(side=tk.RIGHT, pady=5)
        
        # 比较类型选择
        type_frame = ttk.LabelFrame(main_frame, text="比较类型", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.compare_type = tk.IntVar(value=1)
        
        file_radio = ttk.Radiobutton(
            type_frame, 
            text="比较文件", 
            variable=self.compare_type, 
            value=1
        )
        file_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        folder_radio = ttk.Radiobutton(
            type_frame, 
            text="比较文件夹", 
            variable=self.compare_type, 
            value=2
        )
        folder_radio.pack(side=tk.LEFT)
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(main_frame, text="文件/文件夹路径", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 第一个路径
        path1_frame = ttk.Frame(path_frame)
        path1_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path1_frame, text="路径 1:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.path1_var = tk.StringVar()
        path1_entry = ttk.Entry(path1_frame, textvariable=self.path1_var, width=50)
        path1_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse1_btn = ttk.Button(
            path1_frame, 
            text="浏览...", 
            command=lambda: self.browse_path(self.path1_var)
        )
        browse1_btn.pack(side=tk.LEFT)
        
        # 第二个路径
        path2_frame = ttk.Frame(path_frame)
        path2_frame.pack(fill=tk.X)
        
        ttk.Label(path2_frame, text="路径 2:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.path2_var = tk.StringVar()
        path2_entry = ttk.Entry(path2_frame, textvariable=self.path2_var, width=50)
        path2_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse2_btn = ttk.Button(
            path2_frame, 
            text="浏览...", 
            command=lambda: self.browse_path(self.path2_var)
        )
        browse2_btn.pack(side=tk.LEFT)
        
        # 比较按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(0, 20))
        
        self.compare_btn = ttk.Button(
            btn_frame, 
            text="开始比较", 
            command=self.compare_md5,
            style="Accent.TButton"
        )
        self.compare_btn.pack(pady=10, padx=20, ipady=5, ipadx=20)
        
        # 结果区域
        result_frame = ttk.LabelFrame(main_frame, text="比较结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 设置主题样式
        self.setup_styles()
    
    def setup_styles(self):
        """设置自定义样式"""
        style = ttk.Style()
        
        # 尝试使用系统主题
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # 自定义样式
        style.configure('Accent.TButton', font=('SimHei', 10, 'bold'))
        style.configure('TLabelFrame.Label', font=('SimHei', 11, 'bold'))
    
    def browse_path(self, path_var):
        """打开文件/文件夹选择对话框"""
        try:
            if self.compare_type.get() == 1:
                path = filedialog.askopenfilename(
                    title="选择文件",
                    filetypes=[("所有文件", "*.*")]
                )
            else:
                path = filedialog.askdirectory(title="选择文件夹")
                
            if path:
                path_var.set(path)
                self.update_status("路径已选择")
        except Exception as e:
            messagebox.showerror("错误", f"选择路径时出错: {str(e)}")
    
    def update_result(self, message):
        """更新结果文本框"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def compare_md5(self):
        """比较两个路径的MD5值"""
        path1 = self.path1_var.get().strip()
        path2 = self.path2_var.get().strip()
        
        if not path1 or not path2:
            messagebox.showerror("错误", "请输入两个文件或文件夹路径")
            return
        
        # 清空结果区域
        self.result_text.delete(1.0, tk.END)
        self.update_result("开始比较...")
        self.update_result(f"1. {path1}")
        self.update_result(f"2. {path2}")
        self.update_result("------------------------")
        
        # 在新线程中执行MD5计算，避免界面卡顿
        threading.Thread(target=self._compare_md5_thread, daemon=True).start()
    
    def _compare_md5_thread(self):
        """在线程中执行MD5比较"""
        path1 = self.path1_var.get().strip()
        path2 = self.path2_var.get().strip()
        
        temp_file1 = None
        temp_file2 = None
        
        try:
            self.update_status("正在计算第一个MD5值...")
            self.update_result("正在计算第一个MD5值...")
            md5_1 = calculate_md5(path1)
            temp_file1 = save_to_temp_file(md5_1)
            self.temp_files.append(temp_file1)
            self.update_result(f"第一个MD5: {md5_1}")
            
            self.update_status("正在计算第二个MD5值...")
            self.update_result("正在计算第二个MD5值...")
            md5_2 = calculate_md5(path2)
            temp_file2 = save_to_temp_file(md5_2)
            self.temp_files.append(temp_file2)
            self.update_result(f"第二个MD5: {md5_2}")
            
            self.update_status("正在比较MD5值...")
            self.update_result("正在比较MD5值...")
            
            if md5_1 == md5_2:
                self.update_result("结果: 文件/文件夹内容相同")
                messagebox.showinfo("比较结果", "文件/文件夹内容相同")
            else:
                self.update_result("结果: 文件/文件夹内容不相同")
                messagebox.showinfo("比较结果", "文件/文件夹内容不相同")
            
            self.update_status("完成")
            
        except Exception as e:
            self.update_result(f"错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")
            self.update_status("操作失败")
        finally:
            # 确保临时文件被删除
            for temp_file in self.temp_files:
                delete_temp_file(temp_file)
            self.temp_files.clear()

def main():
    root = tk.Tk()
    app = MD5ComparerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()    
