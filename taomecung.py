import random
from collections import deque

class MazeGenerator:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.maze = None  # Biến lưu cấu trúc mê cung dưới dạng ma trận 2D
    
    def _init_maze(self, default_cell='#'):
        """Khởi tạo mê cung với tất cả các ô là tường"""
        self.maze = [[default_cell for _ in range(self.width)] for _ in range(self.height)]
    
    def _is_valid(self, x, y):
        """Kiểm tra tọa độ có nằm trong mê cung không"""
        return 0 <= x < self.height and 0 <= y < self.width
    
    def _get_neighbors(self, x, y, distance=2):
        """Lấy các ô lân cận cách xa 2 đơn vị (cho thuật toán recursive backtracking)"""
        neighbors = []
        for dx, dy in [(-distance, 0), (distance, 0), (0, -distance), (0, distance)]:
            nx, ny = x + dx, y + dy  # Tính tọa độ mới
            if self._is_valid(nx, ny) and self.maze[nx][ny] == '#':
            # Nếu tọa độ mới hợp lệ và là tường ('#'), thì thêm vào danh sách
                neighbors.append((nx, ny, (x + dx//2, y + dy//2)))
                # Thêm nx, ny và tọa độ ô nằm giữa (x + dx//2, y + dy//2) – đây là ô tường nằm giữa, sẽ bị phá vỡ khi nối hai ô

        random.shuffle(neighbors)  # Trộn ngẫu nhiên danh sách ô lân cận – giúp sinh mê cung không có tính định hướng
        return neighbors
    
    def _get_adjacent_neighbors(self, x, y):
        """Lấy các ô lân cận kề nhau"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        # Lấy các ô liền kề 4 hướng xung quanh
            nx, ny = x + dx, y + dy
            if self._is_valid(nx, ny):  # Nếu hợp lệ thì thêm vào danh sách
                neighbors.append((nx, ny))
        return neighbors
    
    def create_perfect_maze(self):
        """Tạo mê cung hoàn hảo sử dụng thuật toán Recursive Backtracking"""
        self._init_maze()  # Gọi phương thức khởi tạo mê cung ban đầu: tất cả ô đều là '#' (tường)
        
        start_x, start_y = 1, 1  # Chọn điểm bắt đầu tại tọa độ (1, 1)
        self.maze[start_x][start_y] = '.'  # Đánh dấu ô bắt đầu là '.' (đường đi)
        
        stack = [(start_x, start_y)]  # Khởi tạo ngăn xếp (stack) với điểm bắt đầu
        while stack:
            current_x, current_y = stack[-1]  # Lấy đỉnh trên cùng của stack làm ô hiện tại
            
            neighbors = self._get_neighbors(current_x, current_y)
            # Lấy danh sách các ô lân cận hợp lệ cách 2 ô (nhảy qua 1 tường), chưa đi qua ('#')
            if not neighbors:
                stack.pop()
                continue
            # Nếu không còn ô lân cận nào chưa đi, backtrack: loại bỏ ô hiện tại ra khỏi stack và quay lại ô trước đó

            next_x, next_y, (wall_x, wall_y) = neighbors[0]
            # Chọn một ô lân cận (vì đã random.shuffle từ trước nên sẽ ngẫu nhiên)
            # wall_x, wall_y: tọa độ của bức tường ở giữa current và next
            self.maze[next_x][next_y] = '.'
            self.maze[wall_x][wall_y] = '.'
            # Đánh dấu cả ô kế tiếp và bức tường ở giữa là đường đi ('.')
            stack.append((next_x, next_y))  # Thêm ô kế tiếp vào stack để tiếp tục đi sâu (đệ quy sâu)
        
        self.maze[1][1] = 'S'
        self.maze[self.height-2][self.width-2] = 'E'
        # Đặt điểm bắt đầu và kết thúc
        
        return self.maze
    
    def create_no_solution_maze(self):
        """Tạo mê cung không có đường đi từ điểm bắt đầu đến điểm kết thúc"""
        
        self.create_perfect_maze()  # Đầu tiên tạo mê cung hoàn hảo
        
        # Tìm đường đi từ S đến E
        start_x, start_y = 1, 1
        end_x, end_y = self.height - 2, self.width - 2
        
        # Sử dụng BFS để tìm đường đi
        queue = deque([(start_x, start_y)])  # queue: hàng đợi các ô đang xét
        visited = set([(start_x, start_y)])  # visited: tập hợp các ô đã đi qua để tránh lặp lại
        parent = {(start_x, start_y): None}  # parent: từ điển dùng để truy vết đường đi từ E về S
        
        while queue:
            x, y = queue.popleft()  # Lặp qua các ô theo BFS
            
            if x == end_x and y == end_y:  # Nếu đã đến đích, dừng vòng lặp
                break
                
            for nx, ny in self._get_adjacent_neighbors(x, y):
                if (nx, ny) not in visited and self.maze[nx][ny] != '#':
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
            # Duyệt các ô liền kề (không phải tường), thêm vào hàng đợi
            # Lưu lại đường đi bằng parent
        
        # Tìm một điểm trên đường đi và chặn lại
        if (end_x, end_y) in parent:
        # Nếu tìm thấy đường từ S đến E
            current = (end_x, end_y)
            path = []
            
            while current != (start_x, start_y):
                path.append(current)
                current = parent[current]
            # Truy vết đường đi từ E về S và lưu vào danh sách path
            
            if path:
                block_point = path[len(path) // 6]
                self.maze[block_point[0]][block_point[1]] = '#'
            # Chọn một điểm trên đường đi để chặn
            
        self.maze[1][1] = 'S'
        self.maze[self.height-2][self.width-2] = 'E'
        # Đảm bảo điểm bắt đầu và kết thúc không bị thay đổi
        
        return self.maze
    
    def create_multiple_paths_maze(self):
        """Tạo mê cung với nhiều đường đi từ điểm bắt đầu đến điểm kết thúc"""
        
        self.create_perfect_maze()  # Đầu tiên tạo mê cung hoàn hảo
        
        # Sau đó mở thêm một số bức tường để tạo nhiều đường đi
        num_walls_to_remove = (self.height * self.width) // 10
        # Tính số lượng tường sẽ bị "mở ra", bằng khoảng 10% tổng số ô
        # Mục đích: tạo thêm các đường rẽ, vòng lặp, khiến mê cung có nhiều hướng đi hơn
        
        for _ in range(num_walls_to_remove):
            x = random.randint(1, self.height - 2)
            y = random.randint(1, self.width - 2)
        # Vòng lặp thực hiện việc chọn ngẫu nhiên các vị trí tường trong mê cung (loại bỏ biên)

            if self.maze[x][y] == '#':
                self.maze[x][y] = '.'
        # Vòng lặp thực hiện việc chọn ngẫu nhiên các vị trí tường trong mê cung (loại bỏ biên)
        # Nếu tại vị trí đó là tường ('#'), ta biến nó thành đường đi ('.')
        # Điều này sẽ tạo ra nhiều đường rẽ, nhánh phụ, hoặc vòng lặp
        
        self.maze[1][1] = 'S'
        self.maze[self.height-2][self.width-2] = 'E'
        # Đảm bảo điểm bắt đầu và kết thúc không bị thay đổi
        
        return self.maze
    
    def create_weighted_maze(self):
        """Tạo mê cung với trọng số (chi phí di chuyển khác nhau)"""
        
        self.create_multiple_paths_maze()  # Bắt đầu với mê cung có nhiều đường đi
        
        # Thay thế các ô đường đi bằng các số từ 1-9 thể hiện chi phí di chuyển
        weighted_maze = []
        for row in self.maze:
        # Duyệt qua toàn bộ mê cung
            new_row = []
            for cell in row:
                if cell == '.':
                    new_row.append(str(random.randint(1, 9)))
                # Nếu gặp ô đường đi ('.'), thì thay bằng một chữ số từ '1' đến '9' – đây là chi phí di chuyển tại ô đó
                else:
                    new_row.append(cell)
                # Nếu là tường ('#'), hoặc ký hiệu 'S'/'E', thì giữ nguyên
            weighted_maze.append(new_row)

        self.maze = weighted_maze  # Gán lại mê cung đã gán trọng số vào thuộc tính self.maze
        
        self.maze[1][1] = 'S'
        self.maze[self.height-2][self.width-2] = 'E'
        # Đảm bảo điểm bắt đầu và kết thúc không bị thay đổi
        
        return self.maze
