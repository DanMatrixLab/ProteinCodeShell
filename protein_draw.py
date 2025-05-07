from Bio.PDB import PDBParser, Selection, NeighborSearch
from Bio.PDB.PDBExceptions import PDBConstructionWarning
import warnings
import numpy as np
from collections import defaultdict
from typing import Tuple, Optional

class ProteinDataLoader:
    def __init__(self, pdb_file: str):
        """
        升级版蛋白质数据加载器
        
        参数:
            pdb_file: PDB文件路径
        """
        self.pdb_file = pdb_file
        self.structure = None
        self._atom_cache = None
        
    def parse_pdb(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        解析PDB文件，返回原子位置、元素类型和键连关系
        
        返回:
            tuple: (原子坐标, 元素类型, 键连关系)
                  原子坐标: (N,3) numpy数组
                  元素类型: (N,) numpy数组
                  键连关系: (M,2) numpy数组
        """
        try:
            # 解析PDB文件
            self._parse_structure()
            
            # 获取所有原子
            atoms = self._get_atoms()
            
            # 提取原子坐标和元素类型
            atom_coords = np.array([atom.get_coord() for atom in atoms])
            elements = np.array([atom.element for atom in atoms])
            
            # 提取键连关系
            bonds = self._extract_bonds(atoms)
            
            return atom_coords, elements, bonds
            
        except Exception as e:
            print(f"Error parsing PDB file: {e}")
            return None, None, None
    
    def _parse_structure(self):
        """解析PDB结构"""
        warnings.simplefilter('ignore', PDBConstructionWarning)
        parser = PDBParser(QUIET=True)
        self.structure = parser.get_structure("protein", self.pdb_file)
        self._atom_cache = None  # 清除缓存
    
    def _get_atoms(self):
        """获取所有原子并缓存"""
        if self._atom_cache is None:
            self._atom_cache = list(Selection.unfold_entities(self.structure, 'A'))
        return self._atom_cache
    
    def _extract_bonds(self, atoms) -> np.ndarray:
        """
        提取键连关系，优先使用CONECT记录，否则自动检测
        
        参数:
            atoms: 原子列表
            
        返回:
            (M,2) numpy数组，表示原子间的键连
        """
        # 尝试从CONECT记录中获取
        conect_bonds = self._get_conect_bonds(atoms)
        if len(conect_bonds) > 0:
            return conect_bonds
            
        # 如果没有CONECT记录，使用距离自动检测
        return self._detect_bonds_by_distance(atoms)
    
    def _get_conect_bonds(self, atoms) -> np.ndarray:
        """从CONECT记录中提取键连关系"""
        atom_dict = {atom.get_serial_number(): idx for idx, atom in enumerate(atoms)}
        bonds = []
        
        for model in self.structure:
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        if hasattr(atom, 'xtra') and 'CONECT' in atom.xtra:
                            atom1 = atom.get_serial_number()
                            if atom1 in atom_dict:
                                for atom2 in atom.xtra['CONECT']:
                                    if atom2 in atom_dict and atom1 != atom2:
                                        bond = sorted([atom_dict[atom1], atom_dict[atom2]])
                                        if bond not in bonds:
                                            bonds.append(bond)
        
        return np.array(bonds) if bonds else np.empty((0, 2), dtype=int)
    
    def _detect_bonds_by_distance(self, atoms, max_bond_length=1.8) -> np.ndarray:
        """根据原子间距离自动检测键连关系，排除氢原子之间的键联"""
        coords = np.array([atom.get_coord() for atom in atoms])
        ns = NeighborSearch(atoms)
        bonds = set()
        
        for i, atom in enumerate(atoms):
            # 跳过氢原子作为键连起点的情况
            if atom.element == 'H':
                continue
                
            # 搜索半径内的邻近原子
            for neighbor in ns.search(atom.get_coord(), max_bond_length, level='A'):
                j = atoms.index(neighbor)
                
                # 排除氢原子之间的键联
                if i < j and not (atom.element == 'H' and neighbor.element == 'H'):
                    bonds.add((i, j))
        
        # 添加肽键 (C-N)
        self._add_peptide_bonds(atoms, bonds)
        
        return np.array(sorted(bonds), dtype=int) if bonds else np.empty((0, 2), dtype=int)

    
    def _add_peptide_bonds(self, atoms, bonds):
        """添加肽键连接"""
        residues = list(Selection.unfold_entities(self.structure, 'R'))
        
        for i in range(len(residues) - 1):
            try:
                # 当前残基的C原子
                c_atom = residues[i]['C']
                # 下一个残基的N原子
                n_atom = residues[i+1]['N']
                
                c_idx = atoms.index(c_atom)
                n_idx = atoms.index(n_atom)
                bonds.add((c_idx, n_idx))
            except KeyError:
                continue
    
    def get_secondary_structure(self):
        """获取二级结构信息"""
        # 实现二级结构解析逻辑
        pass
    
    def get_chain_info(self):
        """获取链信息"""
        # 实现链信息解析逻辑
        pass
