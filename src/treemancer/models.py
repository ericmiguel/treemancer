"""Data models for tree structure representation."""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from typing import NotRequired
from typing import TypedDict
from typing import cast

import yaml


# TypedDict structures for serialized data
class FileNodeData(TypedDict):
    """Typed dictionary for file node serialized data."""

    name: str
    type: str  # Always "file"
    path: str
    depth: int
    content: NotRequired[str]
    size: NotRequired[int]


class DirectoryNodeData(TypedDict):
    """Typed dictionary for directory node serialized data."""

    name: str
    type: str  # Always "directory"
    path: str
    depth: int
    children: list[NodeData]


# Union type for any node data
NodeData = FileNodeData | DirectoryNodeData


class TreeData(TypedDict):
    """Typed dictionary for complete tree serialized data."""

    name: str
    type: str
    path: str
    depth: int
    children: NotRequired[list[NodeData]]


# Base node configuration dataclasses
@dataclass
class NodeConfig:
    """Base configuration for nodes."""

    name: str
    parent: DirectoryNode | None = None


@dataclass
class FileConfig(NodeConfig):
    """Configuration for file nodes."""

    content: str | None = None
    size: int | None = None


@dataclass
class DirectoryConfig(NodeConfig):
    """Configuration for directory nodes."""

    def __post_init__(self) -> None:
        """Initialize children list if not provided."""
        if not hasattr(self, "children"):
            self.children: list[FileSystemNode] = []


class FileSystemNode(ABC):
    """Abstract base class for file system nodes."""

    def __init__(self, name: str, parent: DirectoryNode | None = None) -> None:
        self.name = name
        self.parent = parent

    @abstractmethod
    def to_dict(self) -> NodeData:
        """Convert node to dictionary representation."""
        pass

    @abstractmethod
    def to_yaml(self) -> str:
        """Convert node to YAML string representation."""
        pass

    @abstractmethod
    def to_json(self) -> str:
        """Convert node to JSON string representation."""
        pass

    def get_path(self) -> str:
        """Get full path from root to this node."""
        if self.parent is None:
            return self.name
        return str(Path(self.parent.get_path()) / self.name)

    def get_depth(self) -> int:
        """Get depth level in the tree (root = 0)."""
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1

    def is_root(self) -> bool:
        """Check if this node is the root node."""
        return self.parent is None


@dataclass
class FileNode(FileSystemNode):
    """Represents a file in the tree structure."""

    content: str | None = None
    size: int | None = None

    def __init__(
        self,
        name: str,
        parent: DirectoryNode | None = None,
        content: str | None = None,
        size: int | None = None,
    ) -> None:
        super().__init__(name, parent)
        self.content = content
        self.size = size

    @classmethod
    def from_config(cls, config: FileConfig) -> FileNode:
        """Create FileNode from FileConfig."""
        return cls(config.name, config.parent, config.content, config.size)

    def to_dict(self) -> FileNodeData:
        """Convert file node to typed dictionary representation."""
        data: FileNodeData = {
            "name": self.name,
            "type": "file",
            "path": self.get_path(),
            "depth": self.get_depth(),
        }

        if self.content is not None:
            data["content"] = self.content
        if self.size is not None:
            data["size"] = self.size

        return data

    def to_yaml(self) -> str:
        """Convert file node to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)

    def to_json(self) -> str:
        """Convert file node to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self) -> str:
        """Create a string representation of the file node."""
        return f"FileNode(name='{self.name}', path='{self.get_path()}')"


class DirectoryNode(FileSystemNode):
    """Represents a directory in the tree structure."""

    def __init__(self, name: str, parent: DirectoryNode | None = None) -> None:
        super().__init__(name, parent)
        self.children: list[FileSystemNode] = []
        self._children_by_name: dict[str, FileSystemNode] = {}

    @classmethod
    def from_config(cls, config: DirectoryConfig) -> DirectoryNode:
        """Create DirectoryNode from DirectoryConfig."""
        node = cls(config.name, config.parent)
        for child in config.children:
            node.add_child(child)
        return node

    def add_child(self, child: FileSystemNode) -> None:
        """Add a child node to this directory."""
        if child.name in self._children_by_name:
            raise ValueError(f"Child with name '{child.name}' already exists")

        child.parent = self
        self.children.append(child)
        self._children_by_name[child.name] = child

    def remove_child(self, name: str) -> FileSystemNode | None:
        """Remove and return a child node by name."""
        if name not in self._children_by_name:
            return None

        child = self._children_by_name[name]
        self.children.remove(child)
        del self._children_by_name[name]
        child.parent = None
        return child

    def get_child(self, name: str) -> FileSystemNode | None:
        """Get a child node by name."""
        return self._children_by_name.get(name)

    def get_files(self) -> list[FileNode]:
        """Get all file children."""
        return [child for child in self.children if isinstance(child, FileNode)]

    def get_directories(self) -> list[DirectoryNode]:
        """Get all directory children."""
        return [child for child in self.children if isinstance(child, DirectoryNode)]

    def create_file(
        self, name: str, content: str | None = None, size: int | None = None
    ) -> FileNode:
        """Create and add a new file to this directory."""
        file_node = FileNode(name, self, content, size)
        self.add_child(file_node)
        return file_node

    def create_directory(self, name: str) -> DirectoryNode:
        """Create and add a new directory to this directory."""
        dir_node = DirectoryNode(name, self)
        self.add_child(dir_node)
        return dir_node

    def find_node(self, path: str) -> FileSystemNode | None:
        """Find a node by relative path from this directory."""
        if not path:
            return self

        parts = path.split("/")
        current = self

        for part in parts:
            if isinstance(current, DirectoryNode):
                current = current.get_child(part)
                if current is None:
                    return None
            else:
                return None

        return current

    def get_all_files(self) -> list[FileNode]:
        """Get all files recursively in this directory tree."""
        files: list[FileNode] = []
        for child in self.children:
            if isinstance(child, FileNode):
                files.append(child)
            elif isinstance(child, DirectoryNode):
                files.extend(child.get_all_files())
        return files

    def to_dict(self) -> DirectoryNodeData:
        """Convert directory node to dictionary representation."""
        return {
            "name": self.name,
            "type": "directory",
            "path": self.get_path(),
            "depth": self.get_depth(),
            "children": [child.to_dict() for child in self.children],
        }

    def to_yaml(self) -> str:
        """Convert directory node to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)

    def to_json(self) -> str:
        """Convert directory node to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def __repr__(self) -> str:
        """Create a string representation of the directory node."""
        return (
            f"DirectoryNode(name='{self.name}', "
            f"path='{self.get_path()}', "
            "children={len(self.children)})"
        )


class FileSystemTree:
    """Represents a complete file system tree structure."""

    def __init__(self, root_name: str = "root"):
        self.root = DirectoryNode(root_name)

    def create_from_dict(self, data: dict[str, Any]) -> None:
        """Create tree structure from dictionary representation."""

        def _create_node(
            node_data: dict[str, Any], parent: DirectoryNode
        ) -> FileSystemNode:
            name = node_data["name"]
            node_type = node_data.get("type", "file")

            if node_type == "file":
                content = node_data.get("content")
                size = node_data.get("size")
                node = FileNode(name, parent, content, size)
                parent.add_child(node)
                return node
            else:  # directory
                node = DirectoryNode(name, parent)
                parent.add_child(node)

                for child_data in node_data.get("children", []):
                    _create_node(child_data, node)

                return node

        # Clear existing tree
        self.root = DirectoryNode(data.get("name", "root"))
        print(f"Created root directory: {self.root.name}")

        # Create children
        for child_data in data.get("children", []):
            _create_node(child_data, self.root)

            print(f"Created node: {child_data['name']}")

    def create_from_yaml(self, yaml_str: str) -> None:
        """Create tree structure from YAML string."""
        data = yaml.safe_load(yaml_str)
        self.create_from_dict(data)

    def create_from_json(self, json_str: str) -> None:
        """Create tree structure from JSON string."""
        data = json.loads(json_str)
        self.create_from_dict(data)

    def to_dict(self) -> TreeData:
        """Convert entire tree to dictionary representation."""
        root_data = self.root.to_dict()
        return TreeData(
            {
                "name": root_data["name"],
                "type": root_data["type"],
                "path": root_data["path"],
                "depth": root_data["depth"],
                "children": root_data.get("children", []),
            }
        )

    def to_yaml(self) -> str:
        """Convert entire tree to YAML string."""
        return self.root.to_yaml()

    def to_json(self) -> str:
        """Convert entire tree to JSON string."""
        return self.root.to_json()

    def find_node(self, path: str) -> FileSystemNode | None:
        """Find a node by absolute path from root."""
        if path.startswith("/"):
            path = path[1:]  # Remove leading slash
        return self.root.find_node(path)

    def get_all_files(self) -> list[FileNode]:
        """Get all files in the entire tree."""
        return self.root.get_all_files()

    def print_tree(
        self, node: FileSystemNode | None = None, prefix: str = "", is_last: bool = True
    ) -> None:
        """Print a visual representation of the tree."""
        if node is None:
            node = self.root

        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node.name}")

        if isinstance(node, DirectoryNode):
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension

            for i, child in enumerate(node.children):
                is_last_child = i == len(node.children) - 1
                self.print_tree(child, new_prefix, is_last_child)

    def __repr__(self) -> str:
        """Create a representation of the tree."""
        total_files = len(self.get_all_files())
        return f"FileSystemTree(root='{self.root.name}', total_files={total_files})"


# Factory functions for creating nodes from typed data
def create_node_from_data(
    node_data: NodeData, parent: DirectoryNode | None = None
) -> FileSystemNode:
    """Create a FileSystemNode from typed data."""
    if node_data["type"] == "file":
        file_data = cast(FileNodeData, node_data)
        config = FileConfig(
            name=file_data["name"],
            parent=parent,
            content=file_data.get("content"),
            size=file_data.get("size"),
        )
        return FileNode.from_config(config)

    elif node_data["type"] == "directory":
        dir_data = cast(DirectoryNodeData, node_data)
        config = DirectoryConfig(name=dir_data["name"], parent=parent)
        directory = DirectoryNode.from_config(config)

        # Add children recursively
        for child_data in dir_data.get("children", []):
            child = create_node_from_data(child_data, directory)
            directory.add_child(child)

        return directory

    else:
        raise ValueError(f"Unknown node type: {node_data['type']}")


def create_tree_from_data(tree_data: TreeData) -> FileSystemTree:
    """Create a FileSystemTree from typed data."""
    tree = FileSystemTree(tree_data["name"])

    # Add children to root if they exist
    for child_data in tree_data.get("children", []):
        child = create_node_from_data(child_data, tree.root)
        tree.root.add_child(child)

    return tree


# Utility functions for data validation
def validate_file_data(data: dict[str, Any]) -> FileNodeData:
    """Validate and return file node data."""
    required_fields = {"name", "type", "path", "depth"}
    if not required_fields.issubset(data.keys()):
        missing = required_fields - data.keys()
        raise ValueError(f"Missing required fields: {missing}")

    if data["type"] != "file":
        raise ValueError(f"Expected type 'file', got '{data['type']}'")

    return cast(FileNodeData, data)


def validate_directory_data(data: dict[str, Any]) -> DirectoryNodeData:
    """Validate and return directory node data."""
    required_fields = {"name", "type", "path", "depth", "children"}
    if not required_fields.issubset(data.keys()):
        missing = required_fields - data.keys()
        raise ValueError(f"Missing required fields: {missing}")

    if data["type"] != "directory":
        raise ValueError(f"Expected type 'directory', got '{data['type']}'")

    return cast(DirectoryNodeData, data)


Tree = FileSystemTree
