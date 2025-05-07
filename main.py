import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from multi_view_window import MultiViewWindow

# 在主程序中使用
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("proteincode.tech")
        
        # 创建多视图窗口
        self.multi_view = MultiViewWindow()
        self.setCentralWidget(self.multi_view)
        
        # 加载PDB文件
        self.multi_view.load_protein("1ake.pdb")  # 替换为您的PDB文件

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


