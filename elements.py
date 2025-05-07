import numpy as np
from vispy import scene
from vispy.scene import visuals
from vispy.color import Color

class WireframeCube:
    def __init__(self, parent=None, size=1.0, position=(0, 0, 0), color='#808080'):
        """
        创建一个线框立方体
        
        参数:
            parent: 父级视图
            size: 立方体大小
            position: 立方体位置 (x, y, z)
            color: 线框颜色
        """
        self.parent = parent
        self.size = size
        self.position = position
        self.color = color
        self.lines = None
        
        self._setup_wireframe()
        
        if parent:
            self.add_to_view(parent)
    
    def _setup_wireframe(self):
        """初始化线框立方体"""
        half_size = self.size / 2
        vertices = np.array([
            [-half_size, -half_size, -half_size],  # 0
            [half_size, -half_size, -half_size],   # 1
            [half_size, half_size, -half_size],    # 2
            [-half_size, half_size, -half_size],   # 3
            [-half_size, -half_size, half_size],   # 4
            [half_size, -half_size, half_size],    # 5
            [half_size, half_size, half_size],     # 6
            [-half_size, half_size, half_size]     # 7
        ], dtype=np.float32)
        
        # 调整位置
        vertices += np.array(self.position, dtype=np.float32)
        
        # 定义12条边
        edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],  # 底面
            [4, 5], [5, 6], [6, 7], [7, 4],  # 顶面
            [0, 4], [1, 5], [2, 6], [3, 7]   # 侧面连接线
        ], dtype=np.uint32)
        
        self.lines = visuals.Line(
            pos=vertices,
            connect=edges,
            color=self.color,
            width=2,
            method='gl'
        )
    
    def add_to_view(self, view):
        """将线框立方体添加到视图"""
        view.add(self.lines)
        self.parent = view
    
    def set_position(self, x, y, z):
        """设置立方体位置"""
        self.position = (x, y, z)
        self._update_positions()
    
    def _update_positions(self):
        """更新顶点位置"""
        half_size = self.size / 2
        base_vertices = np.array([
            [-half_size, -half_size, -half_size],
            [half_size, -half_size, -half_size],
            [half_size, half_size, -half_size],
            [-half_size, half_size, -half_size],
            [-half_size, -half_size, half_size],
            [half_size, -half_size, half_size],
            [half_size, half_size, half_size],
            [-half_size, half_size, half_size]
        ], dtype=np.float32)
        
        vertices = base_vertices + np.array(self.position, dtype=np.float32)
        self.lines.set_data(pos=vertices)
    
    def set_color(self, color):
        """设置线框颜色"""
        self.color = color
        self.lines.set_data(color=self.color)
