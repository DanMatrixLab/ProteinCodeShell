from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QFrame, QSplitter, 
                            QToolBar, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from vispy import scene
from protein_visualizer import ProteinVisualizer


class ProteinViewWindow(QWidget):
    """单个蛋白质视图窗口"""
    def __init__(self, window_id: int, parent=None):
        super().__init__(parent)
        self.window_id = window_id
        self.setup_ui()
        self.setup_visualizer()
        self.add_labels()
    
    def setup_ui(self):
        """初始化UI界面"""
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # 带边框的画布容器
        self.canvas_frame = QFrame()
        self.canvas_frame.setFrameShape(QFrame.Shape.Box)
        self.canvas_frame.setLineWidth(2)
        self.canvas_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #C0C0C0;
                background-color: black;
            }
        """)
        layout.addWidget(self.canvas_frame)
        
        # 画布布局
        canvas_layout = QVBoxLayout(self.canvas_frame)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        # VisPy画布
        self.canvas = scene.SceneCanvas(
            keys='interactive',
            bgcolor='black',
            parent=self.canvas_frame
        )
        canvas_layout.addWidget(self.canvas.native)
        
        # 3D视图设置
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.TurntableCamera(
            fov=45,
            distance=30,
            elevation=20,
            azimuth=30 * self.window_id  # 每个窗口不同初始角度
        )
    
    def setup_visualizer(self):
        """设置蛋白质可视化器"""
        self.visualizer = ProteinVisualizer(self.view)
    
    def load_protein(self, pdb_path: str) -> bool:
        """加载PDB文件"""
        success = self.visualizer.load_protein(pdb_path)
        if success:
            self.status_label.setText(f"已加载: {pdb_path.split('/')[-1]}")
        else:
            self.status_label.setText("加载失败")
        return success
    
    def add_labels(self):
        """添加信息标签"""
        # 右下角状态标签
        self.status_label = QLabel("就绪", self.canvas_frame)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                background-color: rgba(0, 0, 0, 0.5);
                padding: 3px;
                border-radius: 3px;
            }
        """)
        self.status_label.adjustSize()
        self.update_label_position()
        self.status_label.raise_()
        
        # 左上角win标签
        self.win_label = QLabel(f"win{self.window_id}", self.canvas_frame)
        self.win_label.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 16px;
                background-color: #C0C0C0;
                padding: 3px;
                border: 2px solid #C0C0C0;
                border-bottom-right-radius: 5px;
            }
        """)
        self.win_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.win_label.adjustSize()
        self.win_label.move(0, 0)
        self.win_label.raise_()
    
    def update_label_position(self):
        """更新标签位置"""
        if hasattr(self, 'status_label'):
            margin = 5
            frame_size = self.canvas_frame.size()
            self.status_label.move(
                frame_size.width() - self.status_label.width() - margin,
                frame_size.height() - self.status_label.height() - margin
            )
    
    def resizeEvent(self, event):
        """窗口大小改变时更新标签位置"""
        super().resizeEvent(event)
        self.update_label_position()

class MultiViewWindow(QWidget):
    """包含4个视图和切换功能的主窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "quad"  # 初始为四窗格模式
        self.active_single_view = None
        self.setup_ui()
        self.setup_views()
        self.setup_toolbar()
    
    def setup_ui(self):
        self.setWindowTitle("蛋白质多视图可视化")
        self.setMinimumSize(1000, 800)
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 设置主窗口背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #C0C0C0;
            }
            QToolBar {
                background-color: #E0E0E0;
                border-top: 1px solid #A0A0A0;
                padding: 2px;
            }
        """)
        
        # 视图容器
        self.view_container = QWidget()
        self.view_container_layout = QVBoxLayout(self.view_container)
        self.view_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建四个视图
        self.view1 = ProteinViewWindow(1)
        self.view2 = ProteinViewWindow(2)
        self.view3 = ProteinViewWindow(3)
        self.view4 = ProteinViewWindow(4)
        
        # 初始四视图布局
        self.setup_quad_view()
        
        self.main_layout.addWidget(self.view_container)
    
    def setup_quad_view(self):
        """设置四视图布局"""
        # 清除当前布局
        while self.view_container_layout.count():
            item = self.view_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
        
        # 创建新的分割器
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.h_splitter1 = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter2 = QSplitter(Qt.Orientation.Horizontal)
        
        # 添加视图到分割器
        self.h_splitter1.addWidget(self.view1)
        self.h_splitter1.addWidget(self.view2)
        self.h_splitter2.addWidget(self.view3)
        self.h_splitter2.addWidget(self.view4)
        
        # 设置分割比例 (1:1)
        self.h_splitter1.setSizes([1, 1])
        self.h_splitter2.setSizes([1, 1])
        
        self.splitter.addWidget(self.h_splitter1)
        self.splitter.addWidget(self.h_splitter2)
        
        # 设置垂直分割比例 (1:1)
        self.splitter.setSizes([1, 1])
        
        self.view_container_layout.addWidget(self.splitter)
        
        # 显示所有视图
        for view in [self.view1, self.view2, self.view3, self.view4]:
            view.show()
    
    def setup_toolbar(self):
        """设置底部工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        
        # 添加模式切换按钮
        self.quad_view_btn = QAction("四视图模式", self)
        self.quad_view_btn.triggered.connect(self.switch_to_quad_view)
        
        self.single_view1_btn = QAction("视图1", self)
        self.single_view1_btn.triggered.connect(lambda: self.switch_to_single_view(1))
        
        self.single_view2_btn = QAction("视图2", self)
        self.single_view2_btn.triggered.connect(lambda: self.switch_to_single_view(2))
        
        self.single_view3_btn = QAction("视图3", self)
        self.single_view3_btn.triggered.connect(lambda: self.switch_to_single_view(3))
        
        self.single_view4_btn = QAction("视图4", self)
        self.single_view4_btn.triggered.connect(lambda: self.switch_to_single_view(4))
        
        self.toolbar.addAction(self.quad_view_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.single_view1_btn)
        self.toolbar.addAction(self.single_view2_btn)
        self.toolbar.addAction(self.single_view3_btn)
        self.toolbar.addAction(self.single_view4_btn)
        
        self.main_layout.addWidget(self.toolbar)
    
    def switch_to_quad_view(self):
        """切换到四视图模式"""
        if self.current_mode == "quad":
            return
        
        self.current_mode = "quad"
        self.setup_quad_view()
    
    def switch_to_single_view(self, view_num):
        """切换到单视图模式"""
        if self.current_mode == view_num:
            return
        
        self.current_mode = view_num
        
        # 隐藏所有视图
        for view in [self.view1, self.view2, self.view3, self.view4]:
            view.hide()
        
        # 清除当前布局
        while self.view_container_layout.count():
            item = self.view_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
        
        # 显示选定的视图
        view_map = {
            1: self.view1,
            2: self.view2,
            3: self.view3,
            4: self.view4
        }
        self.active_single_view = view_map[view_num]
        self.view_container_layout.addWidget(self.active_single_view)
        self.active_single_view.show()
    
    def setup_views(self):
        """设置每个视图的初始相机位置"""
        # 视图1: 默认视角
        self.view1.view.camera.azimuth = 30
        self.view1.view.camera.elevation = 20
        
        # 视图2: 旋转90度
        self.view2.view.camera.azimuth = 120
        self.view2.view.camera.elevation = 20
        
        # 视图3: 俯视角度
        self.view3.view.camera.azimuth = 30
        self.view3.view.camera.elevation = 70
        
        # 视图4: 侧视角度
        self.view4.view.camera.azimuth = -60
        self.view4.view.camera.elevation = 0
    
    def load_protein(self, pdb_path: str):
        """在所有视图中加载蛋白质"""
        for view in [self.view1, self.view2, self.view3, self.view4]:
            view.load_protein(pdb_path)

        """设置每个视图的初始相机位置"""
        # 视图1: 默认视角
        self.view1.view.camera.azimuth = 30
        self.view1.view.camera.elevation = 20
        
        # 视图2: 旋转90度
        self.view2.view.camera.azimuth = 120
        self.view2.view.camera.elevation = 20
        
        # 视图3: 俯视角度
        self.view3.view.camera.azimuth = 30
        self.view3.view.camera.elevation = 70
        
        # 视图4: 侧视角度
        self.view4.view.camera.azimuth = -60
        self.view4.view.camera.elevation = 0
    
    def load_protein(self, pdb_path: str):
        """在所有视图中加载蛋白质"""
        for view in [self.view1, self.view2, self.view3, self.view4]:
            view.load_protein(pdb_path)
