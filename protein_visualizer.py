import numpy as np
from vispy import scene, visuals
from protein_draw import ProteinDataLoader
from typing import Optional, Tuple

class ProteinVisualizer:
    def __init__(self, view: scene.ViewBox):
        """
        独立的蛋白质3D可视化器(无坐标轴)
        
        参数:
            view: vispy的ViewBox对象
        """
        self.view = view
        self._setup_visuals()
        
    def _setup_visuals(self):
        """初始化可视化元素"""
        # 元素颜色映射 (CPK配色)
        self.element_colors = {
            'H': (0.9, 0.9, 0.9, 1),    # 浅灰色
            'C': (0.4, 0.4, 0.4, 1),    # 深灰色
            'N': (0.2, 0.2, 1.0, 1),    # 蓝色
            'O': (1.0, 0.2, 0.2, 1),    # 红色
            'S': (0.9, 0.8, 0.2, 1),    # 黄色
            'P': (1.0, 0.6, 0.1, 1),    # 橙色
            'OTHERS': (0.8, 0.2, 0.8, 1) # 紫色
        }
        
        # 可视化对象
        self.atoms_visual = None
        self.bonds_visual = None
        self.bounding_box = None
    
    def load_protein(self, pdb_file: str) -> bool:
        """
        加载并可视化蛋白质
        
        参数:
            pdb_file: PDB文件路径
            
        返回:
            bool: 是否加载成功
        """
        self._clear_visuals()
        
        loader = ProteinDataLoader(pdb_file)
        coords, elements, bonds = loader.parse_pdb()
        
        if coords is None:
            return False
        
        self._create_atoms(coords, elements)
        self._create_bonds(coords, bonds)
        self._create_bounding_box(coords)
        self._auto_zoom(coords)
        
        return True
    
    def _clear_visuals(self):
        """清除现有的可视化对象"""
        for visual in [self.atoms_visual, self.bonds_visual, self.bounding_box]:
            if visual is not None:
                self.view.remove(visual)
    
    def _create_atoms(self, coords: np.ndarray, elements: np.ndarray):
        """创建原子球体可视化"""
        colors = []
        sizes = []
        for elem in elements:
            elem_str = str(elem).strip().upper()
            colors.append(self.element_colors.get(elem_str, self.element_colors['OTHERS']))
            sizes.append(5 if elem_str == 'H' else 8)
        
        self.atoms_visual = scene.visuals.Markers(
            pos=coords,
            size=np.array(sizes),
            face_color=colors,
            edge_color=(0, 0, 0, 0.5),
            edge_width=0.3,
            spherical=True,
            antialias=1,
            parent=self.view.scene
        )
    
    def _create_bonds(self, coords: np.ndarray, bonds: np.ndarray):
        """创建键连圆柱体可视化"""
        if len(bonds) == 0:
            return
            
        bond_pos = np.array([(coords[b[0]], coords[b[1]]) for b in bonds]).reshape(-1, 3)
        
        self.bonds_visual = scene.visuals.Line(
            pos=bond_pos,
            color=(0.7, 0.7, 0.7, 1),
            width=2.5,
            connect='segments',
            method='gl',
            antialias=True,
            parent=self.view.scene
        )
    
    def _create_bounding_box(self, coords: np.ndarray):
        """创建蛋白质边界线框"""
        if len(coords) == 0:
            return
            
        min_coords = np.min(coords, axis=0)
        max_coords = np.max(coords, axis=0)
        center = (min_coords + max_coords) / 2
        size = max_coords - min_coords
        
        half_size = size / 2
        vertices = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # 底面
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # 顶面
        ], dtype=np.float32)
        
        vertices = vertices * half_size + center
        
        edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],  # 底面
            [4, 5], [5, 6], [6, 7], [7, 4],  # 顶面
            [0, 4], [1, 5], [2, 6], [3, 7]   # 侧面
        ], dtype=np.uint32)
        
        self.bounding_box = scene.visuals.Line(
            pos=vertices,
            connect=edges,
            color=(0.5, 0.5, 0.5, 0.8),
            width=1.5,
            method='gl',
            parent=self.view.scene
        )
    
    def _auto_zoom(self, coords: np.ndarray):
        """自动调整视角"""
        if len(coords) == 0:
            return
            
        center = np.mean(coords, axis=0)
        max_dist = np.max(np.linalg.norm(coords - center, axis=1))
        
        self.view.camera.center = center
        self.view.camera.scale_factor = max_dist * 2.2
        self.view.camera.distance = max_dist * 3
