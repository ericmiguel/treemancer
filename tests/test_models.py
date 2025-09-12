"""Tests for new FileSystemNode models."""

from typing import Any

from treemancer.models import DirectoryNode
from treemancer.models import FileNode
from treemancer.models import FileSystemTree


class TestFileSystemNodes:
    """Test cases for FileSystemNode models."""

    def test_create_file_node(self) -> None:
        """Test creating a file node."""
        node = FileNode("test.py")

        assert node.name == "test.py"
        assert isinstance(node, FileNode)
        assert node.parent is None

    def test_create_directory_node(self) -> None:
        """Test creating a directory node."""
        node = DirectoryNode("src")

        assert node.name == "src"
        assert isinstance(node, DirectoryNode)
        assert node.children == []
        assert node.parent is None

    def test_add_child(self) -> None:
        """Test adding child nodes."""
        parent = DirectoryNode("parent")
        child1 = FileNode("child1.py")
        child2 = DirectoryNode("child2")

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2
        assert parent.children[0] == child1
        assert parent.children[1] == child2

        # Check parent references
        assert child1.parent == parent
        assert child2.parent == parent

    def test_get_path_root(self) -> None:
        """Test getting path for root node."""
        root = DirectoryNode("root")
        assert root.get_path() == "root"

    def test_get_path_nested(self) -> None:
        """Test getting path for nested nodes."""
        root = DirectoryNode("project")
        src = DirectoryNode("src")
        utils = DirectoryNode("utils")
        helper = FileNode("helper.py")

        root.add_child(src)
        src.add_child(utils)
        utils.add_child(helper)

        assert root.get_path() == "project"
        assert src.get_path() == "project/src"
        assert utils.get_path() == "project/src/utils"
        assert helper.get_path() == "project/src/utils/helper.py"

    def test_file_with_content(self) -> None:
        """Test file node with content."""
        content = "print('Hello, World!')"
        file_node = FileNode("main.py", content=content)

        assert file_node.name == "main.py"
        assert file_node.content == content

    def test_file_with_size(self) -> None:
        """Test file node with size."""
        file_node = FileNode("data.txt", size=1024)

        assert file_node.name == "data.txt"
        assert file_node.size == 1024

    def test_directory_operations(self) -> None:
        """Test directory-specific operations."""
        root = DirectoryNode("project")

        # Test create_file method
        readme = root.create_file("README.md", "# Project")
        assert isinstance(readme, FileNode)
        assert readme.name == "README.md"
        assert readme.content == "# Project"
        assert readme in root.children

        # Test create_directory method
        src_dir = root.create_directory("src")
        assert isinstance(src_dir, DirectoryNode)
        assert src_dir.name == "src"
        assert src_dir in root.children

        # Test get_files method
        files = root.get_files()
        assert len(files) == 1
        assert readme in files

        # Test get_directories method
        directories = root.get_directories()
        assert len(directories) == 1
        assert src_dir in directories

    def test_to_dict_file(self) -> None:
        """Test converting file node to dictionary."""
        node = FileNode("test.py", content="print('test')", size=50)
        result = node.to_dict()

        assert result["name"] == "test.py"
        assert result["type"] == "file"
        assert result.get("content") == "print('test')"
        assert result.get("size") == 50
        assert "path" in result
        assert "depth" in result

    def test_to_dict_directory(self) -> None:
        """Test converting directory node to dictionary."""
        parent = DirectoryNode("src")
        child = FileNode("main.py")
        parent.add_child(child)

        result = parent.to_dict()

        assert result["name"] == "src"
        assert result["type"] == "directory"
        assert len(result["children"]) == 1
        assert result["children"][0]["name"] == "main.py"


class TestFileSystemTree:
    """Test cases for FileSystemTree."""

    def test_create_empty_tree(self) -> None:
        """Test creating an empty tree."""
        tree = FileSystemTree("project")

        assert tree.root.name == "project"
        assert isinstance(tree.root, DirectoryNode)
        assert len(tree.root.children) == 0

    def test_tree_operations(self) -> None:
        """Test tree-level operations."""
        tree = FileSystemTree("project")

        # Add some structure
        tree.root.create_file("README.md")
        src_dir = tree.root.create_directory("src")
        src_dir.create_file("main.py")

        # Test get_all_files
        all_files = tree.get_all_files()
        assert len(all_files) == 2
        file_names = [f.name for f in all_files]
        assert "README.md" in file_names
        assert "main.py" in file_names

    def test_find_node(self) -> None:
        """Test finding nodes by path."""
        tree = FileSystemTree("project")

        # Create structure
        src_dir = tree.root.create_directory("src")
        main_file = src_dir.create_file("main.py")

        # Test finding nodes
        found_src = tree.find_node("src")
        assert found_src == src_dir

        found_main = tree.find_node("src/main.py")
        assert found_main == main_file

        # Test non-existent path
        not_found = tree.find_node("nonexistent")
        assert not_found is None

    def test_to_dict_tree(self) -> None:
        """Test converting entire tree to dictionary."""
        tree = FileSystemTree("project")
        tree.root.create_file("README.md")

        result = tree.to_dict()

        assert result["name"] == "project"
        assert result["type"] == "directory"
        assert len(result.get("children", [])) == 1
        children = result.get("children", [])
        assert len(children) == 1
        assert children[0]["name"] == "README.md"

    def test_create_from_dict(self) -> None:
        """Test creating tree from dictionary."""
        data: dict[str, Any] = {
            "name": "test_project",
            "type": "directory",
            "children": [
                {"name": "README.md", "type": "file", "content": "# Test Project"},
                {
                    "name": "src",
                    "type": "directory",
                    "children": [
                        {"name": "main.py", "type": "file", "content": "print('Hello')"}
                    ],
                },
            ],
        }

        tree = FileSystemTree("temp")
        tree.create_from_dict(data)

        assert tree.root.name == "test_project"
        assert len(tree.root.children) == 2

        # Check README
        readme = tree.root.get_child("README.md")
        assert isinstance(readme, FileNode)
        assert readme.content == "# Test Project"

        # Check src directory
        src = tree.root.get_child("src")
        assert isinstance(src, DirectoryNode)
        assert len(src.children) == 1

        # Check main.py
        main_py = src.get_child("main.py")
        assert isinstance(main_py, FileNode)
        assert main_py.content == "print('Hello')"
