"""Tests for new FileSystemNode models."""

from typing import Any
from typing import cast

from treemancer.models import DirectoryConfig
from treemancer.models import DirectoryNode
from treemancer.models import FileConfig
from treemancer.models import FileNode
from treemancer.models import FileSystemTree
from treemancer.models import NodeData
from treemancer.models import Tree
from treemancer.models import TreeData
from treemancer.models import create_node_from_data
from treemancer.models import create_tree_from_data
from treemancer.models import validate_directory_data
from treemancer.models import validate_file_data


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

    def test_get_depth(self) -> None:
        """Test getting depth of nodes."""
        root = DirectoryNode("root")
        assert root.get_depth() == 0
        assert root.is_root()

        level1 = DirectoryNode("level1")
        root.add_child(level1)
        assert level1.get_depth() == 1
        assert not level1.is_root()

        level2 = FileNode("level2.txt")
        level1.add_child(level2)
        assert level2.get_depth() == 2
        assert not level2.is_root()

    def test_remove_child(self) -> None:
        """Test removing children from directory."""
        parent = DirectoryNode("parent")
        child1 = FileNode("child1.txt")
        child2 = DirectoryNode("child2")

        # Add children
        parent.add_child(child1)
        parent.add_child(child2)
        assert len(parent.children) == 2

        # Remove existing child
        removed = parent.remove_child("child1.txt")
        assert removed == child1
        assert child1.parent is None
        assert len(parent.children) == 1
        assert child1 not in parent.children

        # Try to remove non-existent child
        not_removed = parent.remove_child("nonexistent")
        assert not_removed is None

    def test_get_child(self) -> None:
        """Test getting child by name."""
        parent = DirectoryNode("parent")
        child = FileNode("child.txt")
        parent.add_child(child)

        # Get existing child
        found = parent.get_child("child.txt")
        assert found == child

        # Get non-existent child
        not_found = parent.get_child("nonexistent")
        assert not_found is None

    def test_duplicate_child_error(self) -> None:
        """Test that adding duplicate child names raises error."""
        parent = DirectoryNode("parent")
        child1 = FileNode("same_name.txt")
        child2 = FileNode("same_name.txt")

        parent.add_child(child1)

        try:
            parent.add_child(child2)
            raise AssertionError("Should have raised ValueError for duplicate name")
        except ValueError as e:
            assert "already exists" in str(e)

    def test_serialization_methods(self) -> None:
        """Test to_yaml and to_json methods."""
        # Test FileNode serialization
        file_node = FileNode("test.py", content="print('test')")
        file_yaml = file_node.to_yaml()
        file_json = file_node.to_json()

        assert "test.py" in file_yaml
        assert "file" in file_yaml
        assert "test.py" in file_json
        assert "file" in file_json

        # Test DirectoryNode serialization
        dir_node = DirectoryNode("src")
        dir_node.add_child(file_node)

        dir_yaml = dir_node.to_yaml()
        dir_json = dir_node.to_json()

        assert "src" in dir_yaml
        assert "directory" in dir_yaml
        assert "src" in dir_json
        assert "directory" in dir_json

    def test_find_node_edge_cases(self) -> None:
        """Test find_node with various edge cases."""
        root = DirectoryNode("root")
        src = DirectoryNode("src")
        root.add_child(src)

        # Empty path should return the directory itself
        found = root.find_node("")
        assert found == root

        # Path through file should return None
        file_node = FileNode("test.py")
        src.add_child(file_node)

        # Try to find something beyond a file
        not_found = root.find_node("src/test.py/nonexistent")
        assert not_found is None

    def test_get_all_files_recursive(self) -> None:
        """Test getting all files recursively."""
        root = DirectoryNode("root")

        # Add files at root level
        root.create_file("root_file.txt")

        # Add nested structure
        src = root.create_directory("src")
        src.create_file("main.py")

        utils = src.create_directory("utils")
        utils.create_file("helper.py")

        # Get all files
        all_files = root.get_all_files()
        file_names = [f.name for f in all_files]

        assert len(all_files) == 3
        assert "root_file.txt" in file_names
        assert "main.py" in file_names
        assert "helper.py" in file_names

    def test_repr_methods(self) -> None:
        """Test string representations."""
        # Test FileNode repr
        file_node = FileNode("test.py")
        file_repr = repr(file_node)
        assert "FileNode" in file_repr
        assert "test.py" in file_repr

        # Test DirectoryNode repr
        dir_node = DirectoryNode("src")
        dir_node.add_child(file_node)
        dir_repr = repr(dir_node)
        assert "DirectoryNode" in dir_repr
        assert "src" in dir_repr
        assert "children=" in dir_repr


class TestTreeSerialization:
    """Test cases for tree serialization methods."""

    def test_create_from_yaml(self) -> None:
        """Test creating tree from YAML string."""
        yaml_content = """
name: project
type: directory
children:
  - name: README.md
    type: file
    content: "# Project"
  - name: src
    type: directory
    children:
      - name: main.py
        type: file
        content: "print('Hello')"
"""

        tree = FileSystemTree("temp")
        tree.create_from_yaml(yaml_content)

        assert tree.root.name == "project"
        assert len(tree.root.children) == 2

        readme = tree.root.get_child("README.md")
        assert isinstance(readme, FileNode)
        assert readme.content == "# Project"

    def test_create_from_json(self) -> None:
        """Test creating tree from JSON string."""
        json_content = """{
  "name": "project",
  "type": "directory",
  "children": [
    {
      "name": "README.md",
      "type": "file",
      "content": "# Project"
    },
    {
      "name": "src",
      "type": "directory",
      "children": [
        {
          "name": "main.py",
          "type": "file",
          "content": "print('Hello')"
        }
      ]
    }
  ]
}"""

        tree = FileSystemTree("temp")
        tree.create_from_json(json_content)

        assert tree.root.name == "project"
        assert len(tree.root.children) == 2

    def test_tree_to_yaml_json(self) -> None:
        """Test converting tree to YAML and JSON."""
        tree = FileSystemTree("project")
        tree.root.create_file("README.md", "# Test")

        yaml_output = tree.to_yaml()
        json_output = tree.to_json()

        assert "project" in yaml_output
        assert "README.md" in yaml_output

        assert "project" in json_output
        assert "README.md" in json_output

    def test_find_node_with_leading_slash(self) -> None:
        """Test finding node with leading slash in path."""
        tree = FileSystemTree("project")
        src = tree.root.create_directory("src")
        main_file = src.create_file("main.py")

        # Test with leading slash
        found = tree.find_node("/src/main.py")
        assert found == main_file

    def test_print_tree(self) -> None:
        """Test print_tree method."""
        tree = FileSystemTree("project")
        src = tree.root.create_directory("src")
        src.create_file("main.py")
        tree.root.create_file("README.md")

        # This should not raise any errors
        tree.print_tree()

    def test_tree_repr(self) -> None:
        """Test FileSystemTree repr."""
        tree = FileSystemTree("project")
        tree.root.create_file("test1.py")
        tree.root.create_file("test2.py")

        tree_repr = repr(tree)
        assert "FileSystemTree" in tree_repr
        assert "project" in tree_repr
        assert "total_files=2" in tree_repr


class TestFactoryFunctions:
    """Test cases for factory functions and configurations."""

    def test_file_config(self) -> None:
        """Test FileConfig and FileNode.from_config."""
        config = FileConfig(name="test.py", content="print('test')", size=100)
        file_node = FileNode.from_config(config)

        assert file_node.name == "test.py"
        assert file_node.content == "print('test')"
        assert file_node.size == 100

    def test_directory_config(self) -> None:
        """Test DirectoryConfig and DirectoryNode.from_config."""
        config = DirectoryConfig(name="src")
        # Test post_init
        assert hasattr(config, "children")
        assert config.children == []

        dir_node = DirectoryNode.from_config(config)
        assert dir_node.name == "src"
        assert len(dir_node.children) == 0

    def test_directory_config_with_children(self) -> None:
        """Test DirectoryConfig with pre-existing children."""
        # Create children first
        file1 = FileNode("test1.py")
        file2 = FileNode("test2.py")

        config = DirectoryConfig(name="src")
        config.children = [file1, file2]

        dir_node = DirectoryNode.from_config(config)
        assert dir_node.name == "src"
        assert len(dir_node.children) == 2
        assert file1.parent == dir_node
        assert file2.parent == dir_node

    def test_create_node_from_data_file(self) -> None:
        """Test creating FileNode from typed data."""
        file_data = {
            "name": "test.py",
            "type": "file",
            "path": "test.py",
            "depth": 0,
            "content": "print('test')",
            "size": 50,
        }

        node = create_node_from_data(cast(NodeData, file_data))
        assert isinstance(node, FileNode)
        assert node.name == "test.py"
        assert node.content == "print('test')"
        assert node.size == 50

    def test_create_node_from_data_directory(self) -> None:
        """Test creating DirectoryNode from typed data."""
        dir_data = {
            "name": "src",
            "type": "directory",
            "path": "src",
            "depth": 0,
            "children": [
                {"name": "main.py", "type": "file", "path": "src/main.py", "depth": 1}
            ],
        }

        node = create_node_from_data(cast(NodeData, dir_data))
        assert isinstance(node, DirectoryNode)
        assert node.name == "src"
        assert len(node.children) == 1
        assert isinstance(node.children[0], FileNode)

    def test_create_node_invalid_type(self) -> None:
        """Test creating node with invalid type."""
        invalid_data = {"name": "test", "type": "invalid", "path": "test", "depth": 0}

        try:
            create_node_from_data(cast(NodeData, invalid_data))
            raise AssertionError("Should have raised ValueError for invalid type")
        except ValueError as e:
            assert "Unknown node type" in str(e)

    def test_create_tree_from_data(self) -> None:
        """Test creating FileSystemTree from typed data."""
        tree_data = {
            "name": "project",
            "type": "directory",
            "path": "project",
            "depth": 0,
            "children": [
                {
                    "name": "README.md",
                    "type": "file",
                    "path": "project/README.md",
                    "depth": 1,
                    "content": "# Project",
                }
            ],
        }

        tree = create_tree_from_data(cast(TreeData, tree_data))
        assert tree.root.name == "project"
        assert len(tree.root.children) == 1

        readme = tree.root.get_child("README.md")
        assert isinstance(readme, FileNode)
        assert readme.content == "# Project"

    def test_validate_file_data_valid(self) -> None:
        """Test validating valid file data."""
        valid_data = {
            "name": "test.py",
            "type": "file",
            "path": "test.py",
            "depth": 0,
            "content": "print('test')",
        }

        result = validate_file_data(valid_data)
        assert result["name"] == "test.py"
        assert result["type"] == "file"

    def test_validate_file_data_invalid(self) -> None:
        """Test validating invalid file data."""
        # Missing required fields
        invalid_data = {"name": "test.py"}

        try:
            validate_file_data(invalid_data)
            raise AssertionError("Should have raised ValueError for missing fields")
        except ValueError as e:
            assert "Missing required fields" in str(e)

        # Wrong type
        wrong_type_data = {
            "name": "test.py",
            "type": "directory",  # Wrong type
            "path": "test.py",
            "depth": 0,
        }

        try:
            validate_file_data(wrong_type_data)
            raise AssertionError("Should have raised ValueError for wrong type")
        except ValueError as e:
            assert "Expected type 'file'" in str(e)

    def test_validate_directory_data_valid(self) -> None:
        """Test validating valid directory data."""
        valid_data: dict[str, Any] = {
            "name": "src",
            "type": "directory",
            "path": "src",
            "depth": 0,
            "children": [],
        }

        result = validate_directory_data(valid_data)
        assert result["name"] == "src"
        assert result["type"] == "directory"

    def test_validate_directory_data_invalid(self) -> None:
        """Test validating invalid directory data."""
        # Missing required fields
        invalid_data = {"name": "src", "type": "directory"}

        try:
            validate_directory_data(invalid_data)
            raise AssertionError("Should have raised ValueError for missing fields")
        except ValueError as e:
            assert "Missing required fields" in str(e)

        # Wrong type
        wrong_type_data: dict[str, Any] = {
            "name": "src",
            "type": "file",  # Wrong type
            "path": "src",
            "depth": 0,
            "children": [],
        }

        try:
            validate_directory_data(wrong_type_data)
            raise AssertionError("Should have raised ValueError for wrong type")
        except ValueError as e:
            assert "Expected type 'directory'" in str(e)

    def test_tree_alias(self) -> None:
        """Test Tree alias for FileSystemTree."""
        tree = Tree("project")
        assert isinstance(tree, FileSystemTree)
        assert tree.root.name == "project"
