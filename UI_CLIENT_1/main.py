import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from dotenv import load_dotenv
import os
import threading
import time


from CLIENT import main as service
from ui_helper import main as auth


WIN_WIDTH  = 720
WIN_HEIGHT = 500

load_dotenv()
BASE_URL = str(os.getenv('BASE_URL'))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Torrent App")
        self.root.geometry("{}x{}".format(WIN_WIDTH,WIN_HEIGHT))

        self.selected_item = None
        
        self.main_frame = tk.Frame(root, background="#F8E6CB")
        self.main_frame.pack(expand=True, fill="both")

        self.root.protocol("WM_DELETE_WINDOW", lambda: self.quit_app())


        self.start_app()
        # self.create_main_page()
        self.create_dashboard_page()




    def start_app(self):
        try:
            server_thread = threading.Thread(target=service.start_peer_server, args=(service.HOST, service.PORT))
            server_thread.start()
            time.sleep(1)
        except KeyboardInterrupt:
            print('\nMessenger stopped by user')
        finally:
            print("Cleanup done.")

    def quit_app(self):
            if messagebox.askokcancel("Thoát ứng dụng", "Bạn có chắc chắn muốn thoát ứng dụng?"):
                service.stop_peer_server()
                self.root.destroy()  

    def create_main_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Welcome to the TORRENT", font=("Arial", 16)).pack(pady=20)

        

        
        login_button = tk.Button(self.main_frame, text="Đăng nhập", command=self.create_login_page, width=20)
        login_button.pack(pady=10)

        register_button = tk.Button(self.main_frame, text="Đăng ký", command=self.create_register_page, width=20)
        register_button.pack(pady=10)

               

#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #



    def create_dashboard_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Trang chủ", font=("Arial", 16)).pack(pady=10)
        
        

        def publish_file(tracker_URL = BASE_URL):
            for item in table.get_children():
                table.delete(item)
            file_path = filedialog.askopenfilename(title="Chọn file", filetypes=[("Tất cả các file", "*.*")])
            signal = service.publish(file_path, tracker_URL)
            if signal == 0 :
                messagebox.showinfo("pulish","publish success")
            elif signal == 1 : 
                messagebox.showerror("error",f"Path {file_path} does not exist")
            else :
                messagebox.showerror("error",f"{file_path} is not a file")

        def fetch_info_file(service_url = BASE_URL, hash_info = None):
            response = service.fetch_file(BASE_URL,hash_info)

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

        # UI for FETCH
        fetch_frame = tk.Frame(self.main_frame)
        fetch_frame.pack(pady=10)

        fetch_hash_info_entry = tk.Entry(fetch_frame, width=50)
        fetch_hash_info_entry.pack(side=tk.LEFT, padx=5)  # Đặt Entry ở bên trái

        fetch_button = tk.Button(fetch_frame, text="Fetch File", command=lambda: fetch_info_file(hash_info=fetch_hash_info_entry.get()), width=15)
        fetch_button.pack(side=tk.LEFT)

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
        table.pack(pady=10)


        


        # UI for DOWNLOAD

        download_button = tk.Button(self.main_frame, text="Download File", command=lambda: download_file() ,width=15)
        download_button.pack(pady=10)

        def on_item_select(event):
            selected = table.selection()
            if selected:
                self.selected_item = table.item(selected[0])["values"]
            else:
                self.selected_item = None

        table.bind("<<TreeviewSelect>>", on_item_select)

        def download_file():
            if self.selected_item:
                print (self.selected_item[0])
                service.download(self.selected_item[0], BASE_URL)
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hàng trước khi nhấn Print!")

        def logout ():
            self.create_main_page()
        
        tk.Button(self.main_frame, text="Đăng xuất", command=logout, width=15).pack(pady=5)

        
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #




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

            response = auth.resigter_peer(BASE_URL, username, password, service.HOST, service.PORT)
            if not username or not password :
                messagebox.showerror("Error", " chưa điền đầy đủ thông tin")
            if response and response.json() :
                if response.status_code==500:
                    messagebox.showerror("error", response.json()["message"]) 
                elif response.status_code==400:
                    messagebox.showerror("error", response.json()["message"])
                else:
                    messagebox.showinfo("Suscess", response.json()["message"])
                    self.create_dashboard_page()
            else:
                messagebox.showerror("error", "Internal server error")

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
            
            response = auth.login_peer(BASE_URL, username, password)
            if response and response.json() :
                if response.status_code==500:
                    messagebox.showerror("error", response.json()["message"]) 
                elif response.status_code==400 and response.json()["isSuscess"] != "0":
                    messagebox.showerror("error", response.json()["message"])
                else:
                    messagebox.showinfo("Suscess", response.json()["message"])
                    self.create_dashboard_page()
            else:
                messagebox.showerror("error", "Internal server error")
                

        tk.Button(self.main_frame, text="Đăng nhập", command=handle_login, width=15).pack(pady=10)
        tk.Button(self.main_frame, text="Quay lại", command=self.create_main_page, width=15).pack(pady=5)

    
        
    


# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
