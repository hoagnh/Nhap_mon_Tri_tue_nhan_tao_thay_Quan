import tkinter as tk  
from tkinter import ttk, messagebox
from taomecung import MazeGenerator
import threading  # threading dùng để chạy giải thuật DFS trong luồng riêng (tránh treo giao diện)
import time  # time để sử dụng sleep, tạo hiệu ứng từng bước khi duyệt mê cung
import random

CELL_SIZE = 40  # Kích thước ô mặc định ban đầu

class MazeApp:
    def __init__(self, root):
    # Đây là class chính tạo và điều khiển ứng dụng GUI. root là cửa sổ Tkinter gốc (được truyền từ bên ngoài)
        self.root = root
        self.root.title("Mô phỏng các loại mê cung")

        config_frame = tk.Frame(root)  # Tạo khung chứa combobox, nút, ô nhập liệu
        config_frame.pack(pady=10)

        # Combobox chọn loại mê cung
        self.combo = ttk.Combobox(config_frame, values=[
            "Mê cung hoàn hảo", 
            "Mê cung không có đường đi", 
            "Mê cung có nhiều đường đi", 
            "Mê cung có trọng số"
        ], width=25)
        self.combo.current(0)  # Chọn mặc định là "Mê cung hoàn hảo"
        self.combo.grid(row=0, column=0, padx=5)

        # Nút tạo mê cung
        self.generate_btn = tk.Button(config_frame, text="Tạo mê cung", command=self.draw_maze)
        self.generate_btn.grid(row=0, column=1, padx=5)

        # Nút tìm đường đi (DFS)
        self.solve_btn = tk.Button(config_frame, text="Tìm đường đi (DFS)", command=self.start_solving_thread)
        self.solve_btn.grid(row=0, column=2, padx=5)

        # Chiều cao
        tk.Label(config_frame, text="Chiều cao:").grid(row=0, column=3, padx=2)
        self.height_entry = tk.Entry(config_frame, width=4)
        self.height_entry.insert(0, "15")
        self.height_entry.grid(row=0, column=4, padx=2)

        # Chiều rộng
        tk.Label(config_frame, text="Chiều rộng:").grid(row=0, column=5, padx=2)
        self.width_entry = tk.Entry(config_frame, width=4)
        self.width_entry.insert(0, "15")
        self.width_entry.grid(row=0, column=6, padx=2)

        # Nút cập nhật kích thước
        tk.Button(config_frame, text="Cập nhật", command=self.update_size).grid(row=0, column=7, padx=5)

        # Kích thước ô
        tk.Label(config_frame, text="Kích thước ô:").grid(row=0, column=8, padx=2)
        self.cellsize_entry = tk.Entry(config_frame, width=4)
        self.cellsize_entry.insert(0, str(CELL_SIZE))
        self.cellsize_entry.grid(row=0, column=9, padx=2)

        # Nút cập nhật kích thước ô
        tk.Button(config_frame, text="Cập nhật", command=self.update_cell_size).grid(row=0, column=10, padx=5)

        # Tốc độ đi
        tk.Label(config_frame, text="Tốc độ đi (s):").grid(row=0, column=11, padx=2)
        self.speed_go_entry = tk.Entry(config_frame, width=4)
        self.speed_go_entry.insert(0, "0.05")
        self.speed_go_entry.grid(row=0, column=12, padx=2)

        # Tốc độ quay lui
        tk.Label(config_frame, text="Tốc độ quay lui (s):").grid(row=0, column=13, padx=2)
        self.speed_back_entry = tk.Entry(config_frame, width=4)
        self.speed_back_entry.insert(0, "0.03")
        self.speed_back_entry.grid(row=0, column=14, padx=2)

        # Nút cập nhật tốc độ
        tk.Button(config_frame, text="Cập nhật", command=self.update_speed).grid(row=0, column=15, padx=5)

        # Nền để hiển thị mê cung
        self.canvas = tk.Canvas(root, width=1500, height=800, bg='white')
        self.canvas.pack(pady=10)

        # Kích thước mê cung mặc định ban đầu
        self.height = 15
        self.width = 15

        self.maze = []
        self.path = []
        self.visited = set()

        # Tốc độ hiệu ứng mặc định ban đầu
        self.speed_go = 0.05
        self.speed_back = 0.03

        # Lưu id của mỗi ô trên canvas để thay đổi màu
        self.cell_rects = {}

    def update_size(self):
    # Hàm cập nhật kích thước mê cung
        try:
            h = int(self.height_entry.get())
            w = int(self.width_entry.get())
            if h > 0 and w > 0:
                self.height = h
                self.width = w
            else:
                messagebox.showerror("Lỗi", "Kích thước phải lớn hơn 0.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên.")

    def update_cell_size(self):
    # Hàm cập nhật kích thước ô
        global CELL_SIZE
        try:
            size = int(self.cellsize_entry.get())
            if size >= 5:
                CELL_SIZE = size
            else:
                messagebox.showerror("Lỗi", "Cell size phải >= 5.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên.")

    def update_speed(self):
    # Hàm cập nhật tốc độ
        try:
            go = float(self.speed_go_entry.get())
            back = float(self.speed_back_entry.get())
            if go >= 0 and back >= 0:
                self.speed_go = go
                self.speed_back = back
            else:
                messagebox.showerror("Lỗi", "Tốc độ không được âm.")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số thực hợp lệ.")

    def draw_maze(self):
    # Tạo và hiển thị mê cung
        self.canvas.delete("all")  # Xóa toàn bộ các hình ảnh đang có trên Canvas
        generator = MazeGenerator(self.height, self.width)
        choice = self.combo.get()

        if choice == "Mê cung hoàn hảo":
            maze = generator.create_perfect_maze()
        elif choice == "Mê cung không có đường đi":
            maze = generator.create_no_solution_maze()
        elif choice == "Mê cung có nhiều đường đi":
            maze = generator.create_multiple_paths_maze()
        elif choice == "Mê cung có trọng số":
            maze = generator.create_weighted_maze()
        else:
            return

        self.maze = maze
        self.path = []
        self.visited = set()
        # Lưu mê cung vào biến của đối tượng, đồng thời xóa đường đi và tập đã duyệt
        self.visualize_maze()
        # Gọi hàm để vẽ mê cung lên Canvas

    def start_solving_thread(self):
    # Bắt đầu giải mê cung trong luồng riêng
        if not self.maze:
            messagebox.showerror("Lỗi", "Chưa tạo mê cung.")
            return
        # Nếu chưa có mê cung, hiện thông báo lỗi

        self.reset_canvas_colors()
        # Reset màu trước khi chạy DFS

        self.root.after(100, lambda: threading.Thread(target=self.dfs_with_effect).start())
        # Khởi tạo luồng mới để chạy dfs_with_effect() nhằm không làm treo GUI khi chạy DFS chậm từng bước

    def dfs_with_effect(self):
    # Giải mê cung bằng DFS có hiệu ứng từng bước
        maze = self.maze
        start = end = None
        # Lấy mê cung đang dùng, và khởi tạo start, end
        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == 'S':
                    start = (i, j)
                elif maze[i][j] == 'E':
                    end = (i, j)
        # Duyệt toàn bộ mê cung để tìm tọa độ điểm S (Start) và E (End)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # Thứ tự ưu tiên các hướng đi: lên, xuống, trái, phải
        visited = set()
        path = {}
        # Tập đã duyệt và dictionary để lưu dấu vết đường đi

        def dfs(current):
        # Hàm DFS đệ quy bên trong
            x, y = current
            if current == end:
                return True
            # Nếu đến điểm kết thúc, trả về True

            visited.add(current)
            if maze[x][y] != 'S':
                self.highlight_cell(x, y, "lightblue")
            time.sleep(self.speed_go)
            # Đánh dấu ô đang thăm bằng màu xanh nhạt, dừng một chút để tạo hiệu ứng

            shuffled_dirs = directions[:]  # Tạo bản sao của directions
            random.shuffle(shuffled_dirs)  # Xáo trộn bản sao
            
            for dx, dy in shuffled_dirs:
                nx, ny = x + dx, y + dy
                if (0 <= nx < len(maze) and 0 <= ny < len(maze[0]) and
                        maze[nx][ny] != '#' and (nx, ny) not in visited):
                    path[(nx, ny)] = current
                    if dfs((nx, ny)):
                        return True
            # Thử đi theo các hướng nếu ô đó không phải tường và chưa được thăm

            self.highlight_cell(x, y, "gray")
            time.sleep(self.speed_back)
            # Nếu không tìm được đường, tô màu xám
            return False

        if not dfs(start):
            messagebox.showinfo("Kết quả", "Không tìm thấy đường đi.")
            return

        current = end
        path_cells = []
        while current != start:
            path_cells.append(current)
            current = path[current]
        path_cells.append(start)
        path_cells.reverse()
        # Truy vết từ end ngược về start để lấy đường đi

        for x, y in path_cells:
            if maze[x][y] not in ['S', 'E']:
                self.highlight_cell(x, y, "yellow")
            # Tô màu vàng các ô thuộc đường đi. Giữ nguyên màu của S và E
            time.sleep(0.03)

        step=-1
        total_cost = 0
        for x, y in path_cells:
            step+=1
            cell_value = self.maze[x][y]
            if cell_value.isdigit():
                total_cost += int(cell_value)
        # Tính số bước đi và tổng chi phí đường đi

        if self.combo.get() in {"Mê cung hoàn hảo", "Mê cung có nhiều đường đi"}:
            messagebox.showinfo("Số bước đi", f"Số bước đi: {step}")
        # Hiển thị số bước đi

        if self.combo.get() == "Mê cung có trọng số":
            messagebox.showinfo("Tổng chi phí", f"Tổng chi phí đường đi: {total_cost}")
        # Hiển thị chi phí đường đi nếu là mê cung có trọng số

    def highlight_cell(self, i, j, color):
    # Hàm tô màu ô trong quá trình tìm đường đi
        rect_id = self.cell_rects.get((i, j))
        # Lấy rect_id của ô (i, j) đã được lưu trước đó trong self.cell_rects
        if rect_id:
            self.canvas.itemconfig(rect_id, fill=color)
        # Nếu tồn tại rect_id, dùng itemconfig để thay đổi màu (fill) của hình chữ nhật đó

        x1 = j * CELL_SIZE
        y1 = i * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        # Tính tọa độ góc trên trái và góc dưới phải của ô, dựa trên vị trí (i, j) và kích thước ô (CELL_SIZE)

        cell = self.maze[i][j]
        if cell.isdigit():
            text_id = self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=cell, fill="black")
            self.canvas.tag_raise(text_id, rect_id)
        # Nếu ô đó là số (trọng số), hiển thị số ở giữa ô

        self.root.update_idletasks()
        # Cập nhật giao diện ngay lập tức (nếu không sẽ bị delay)

    def reset_canvas_colors(self):
    # Hàm tô lại màu ô khi tìm đường đi mới
        for (i, j), rect_id in self.cell_rects.items():
        # Duyệt qua toàn bộ các ô đã được lưu ID trong self.cell_rects

            if i==1 and j==1:
                self.canvas.itemconfig(rect_id, fill="green")
            # Trường hợp mê cung không có đường đi thì tô lại màu điểm bắt đầu

            fill = self.canvas.itemcget(rect_id, "fill")
            # Lấy màu hiện tại của ô đó từ canvas
            if fill in ("yellow", "gray", "lightblue"):
                self.canvas.itemconfig(rect_id, fill="white")
        
        self.root.update_idletasks()
        # Cập nhật ngay thay đổi giao diện

    def visualize_maze(self):
    # Vẽ toàn bộ mê cung ban đầu
        self.canvas.delete("all")  # Xóa canvas để vẽ mới
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                x0, y0 = j * CELL_SIZE, i * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
        # Duyệt từng ô, tính tọa độ để vẽ

                if cell == '#':
                    color = "black"
                elif cell == 'S':
                    color = "green"
                elif cell == 'E':
                    color = "red"
                else:
                    color = "white"

                rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")
                # Tạo một hình chữ nhật trên Canvas, trả về rect_id – ID duy nhất của hình chữ nhật được tạo ra
                self.cell_rects[(i, j)] = rect_id  # Lưu lại id hình chữ nhật vào mảng
                
                if cell.isdigit():
                    self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=cell, fill="black")
                # Vẽ ô và số (nếu có trọng số)

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
