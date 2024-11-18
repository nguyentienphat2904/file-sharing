import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from dotenv import load_dotenv
import os
import threading

from CLIENT import main as sevice


WIN_WIDTH  = 720
WIN_HEIGHT = 500

load_dotenv()
BASE_URL = str(os.getenv('BASE_URL'))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Torrent App")
        self.root.geometry("{}x{}".format(WIN_WIDTH,WIN_HEIGHT))
        
        self.user_data = {}

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill="both")

        self.create_dashboard_page()
        # self.create_main_page()

    def create_main_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Welcome to the TORRENT", font=("Arial", 16)).pack(pady=20)
        
        login_button = tk.Button(self.main_frame, text="Đăng nhập", command=self.create_login_page, width=20)
        login_button.pack(pady=10)

        register_button = tk.Button(self.main_frame, text="Đăng ký", command=self.create_register_page, width=20)
        register_button.pack(pady=10)


#######
    def create_dashboard_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        print(BASE_URL)
        tk.Label(self.main_frame, text="Trang chủ", font=("Arial", 16)).pack(pady=20)

        server_thread = threading.Thread(target=sevice.start_peer_server, args=())
        server_thread.start()

        def publish_file(tracker_URL = BASE_URL):
            for item in table.get_children():
                table.delete(item)
            file_path = filedialog.askopenfilename(title="Chọn file", filetypes=[("Tất cả các file", "*.*")])
            signal = sevice.publish(file_path, tracker_URL)
            if signal == 0 :
                messagebox.showinfo("publish success")
            elif signal == 1 : 
                messagebox.showerror(f"Path {file_path} does not exist")
            else :
                messagebox.showerror(f"{file_path} is not a file")

        def fetch_info_file(service_url = BASE_URL, hash_info = None):
            response = sevice.fetch_file(BASE_URL,hash_info)

            if response and response.status_code == 200 and response.json() and response.json()['data']:
                for item in table.get_children():
                    table.delete(item)
                if(hash_info):
                    data = response.json()['data'][0]
                    peers = data.get('peers', [])
                    peers_str = ', '.join([f"{peer['address']}:{peer['port']}" for peer in peers])

                    if(peers):
                        value = (
                            data.get('hash_info'), 
                            data.get('name'), 
                            data.get('size'), 
                            peers_str
                        )
                        table.insert( parent="", index = 0, values=value)
                    else:
                        value = (
                            data.get('hash_info'), 
                            data.get('name'), 
                            data.get('size'), 
                            "No peers"
                        )
                        table.insert( parent="", index = tk.END, values=value)
                        
                else:
                    for item in response.json()['data']:
                        peer = item.get('peer', [])
                        
                        if peer :
                            value = (
                                item.get('hash_info'), 
                                item.get('name'), 
                                item.get('size'), 
                                f"{peer.get('address')}:{peer.get('port')}"
                            )
                            table.insert( parent="", index = tk.END, values=value)
                        else:
                            value = (
                                item.get('hash_info'), 
                                item.get('name'), 
                                item.get('size'), 
                                "No peers"
                            )
                            table.insert( parent="", index = tk.END, values=value)


        tk.Button(self.main_frame, text="Publish File", command=lambda:publish_file(), width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Fetch File", command=fetch_info_file, width=15).pack(pady=10)
        
        columns = (
            ('Info_Hash', WIN_WIDTH / 2),
            ('Name', WIN_WIDTH / 6), 
            ('Sizes (bytes)', WIN_WIDTH / 6),
            ('Peer', WIN_WIDTH / 6),
        )
        table = ttk.Treeview(self.main_frame, columns = [x[0] for x in columns], show = 'headings' )

        for col, width in columns :
            table.heading(col, text = col)
            table.column(col, width=int(width), anchor=tk.CENTER)
        table.pack()


        
        tk.Button(self.main_frame, text="Đăng xuất", command=self.create_main_page, width=15).pack(pady=5)

#######




    def create_register_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Đăng ký tài khoản", font=("Arial", 16)).pack(pady=20)

        tk.Label(self.main_frame, text="Tên đăng nhập:").pack()
        username_entry = tk.Entry(self.main_frame)
        username_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Mật khẩu:").pack()
        password_entry = tk.Entry(self.main_frame, show="*") 
        password_entry.pack(pady=5)

        def toggle_password():
            if password_entry.cget("show") == "*":
                password_entry.config(show="")
            else:
                password_entry.config(show="*")

        show_password_var = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(self.main_frame, text="Hiển thị mật khẩu", variable=show_password_var,
                                                command=toggle_password)
        show_password_checkbox.pack(pady=5)

        def handle_register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if username in self.user_data:
                messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác!")
            elif not username or not password:
                messagebox.showerror("Lỗi", "Tên đăng nhập và mật khẩu không được để trống!")
            else:
                self.user_data[username] = password
                messagebox.showinfo("Thành công", "Đăng ký thành công!")
                self.create_login_page()

        tk.Button(self.main_frame, text="Đăng ký", command=handle_register, width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Quay lại", command=self.create_main_page, width=15).pack(pady=5)

    def create_login_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Đăng nhập", font=("Arial", 16)).pack(pady=20)

        tk.Label(self.main_frame, text="Tên đăng nhập:").pack()
        username_entry = tk.Entry(self.main_frame)
        username_entry.pack(pady=5)

        tk.Label(self.main_frame, text="Mật khẩu:").pack()
        password_entry = tk.Entry(self.main_frame, show="*")  
        password_entry.pack(pady=5)

        def toggle_password():
            if password_entry.cget("show") == "*":
                password_entry.config(show="")
            else:
                password_entry.config(show="*")

        show_password_var = tk.BooleanVar()
        show_password_checkbox = tk.Checkbutton(self.main_frame, text="Hiển thị mật khẩu", variable=show_password_var,
                                                command=toggle_password)
        show_password_checkbox.pack(pady=5)

        def handle_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if username in self.user_data and self.user_data[username] == password:
                messagebox.showinfo("Thành công", "Đăng nhập thành công!")
                self.create_dashboard_page()
            else:
                messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

        tk.Button(self.main_frame, text="Đăng nhập", command=handle_login, width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Quay lại", command=self.create_main_page, width=15).pack(pady=5)

    
        
    


# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
