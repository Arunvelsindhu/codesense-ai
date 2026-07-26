import os
from tree_sitter_language_pack import get_parser

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".rs": "rust",
    ".php": "php",
    ".cs": "csharp",
}

# Node types that represent a "chunkable" unit in each language.
# Names/values verified directly against the tree_sitter_language_pack
# grammars, since they vary a lot between languages (e.g. Go has no
# "class", Rust splits struct/impl/trait into separate node types).
CHUNK_NODE_TYPES = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "class_declaration", "method_definition"},
    "typescript": {"function_declaration", "class_declaration", "method_definition"},
    "java": {"method_declaration", "class_declaration", "interface_declaration"},
    "go": {"function_declaration", "method_declaration", "type_declaration"},
    "c": {"function_definition", "struct_specifier"},
    "cpp": {"function_definition", "class_specifier", "struct_specifier"},
    "ruby": {"method", "class", "module"},
    "rust": {"function_item", "struct_item", "impl_item", "trait_item"},
    "php": {"function_definition", "class_declaration", "method_declaration"},
    "csharp": {"method_declaration", "class_declaration", "interface_declaration"},
}


def get_language_from_file(file_path: str):
    ext = os.path.splitext(file_path)[1]
    return SUPPORTED_EXTENSIONS.get(ext)


def _decode(node, source_bytes: bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")


def extract_name(node, source_bytes: bytes):
    name_node = node.child_by_field_name("name")
    if name_node:
        return _decode(name_node, source_bytes)

    # C/C++ function_definition: the identifier is nested inside the
    # declarator subtree, which can itself be wrapped in pointer/array/
    # reference declarators (e.g. `int *add(...)` or `int (&add(...))`).
    if node.type == "function_definition":
        declarator = node.child_by_field_name("declarator")
        for _ in range(5):
            if declarator is None:
                break
            if declarator.type in ("identifier", "field_identifier"):
                return _decode(declarator, source_bytes)
            inner_name = declarator.child_by_field_name("name")
            if inner_name:
                return _decode(inner_name, source_bytes)
            declarator = declarator.child_by_field_name("declarator")

    # Rust impl blocks reference a type rather than having their own name.
    if node.type == "impl_item":
        type_node = node.child_by_field_name("type")
        if type_node:
            return f"impl {_decode(type_node, source_bytes)}"

    # Go type_declaration (used for both structs and other named types):
    # the actual name lives on a child type_spec node.
    if node.type == "type_declaration":
        for child in node.children:
            if child.type == "type_spec":
                spec_name = child.child_by_field_name("name")
                if spec_name:
                    return _decode(spec_name, source_bytes)

    return "anonymous"


def chunk_file(file_path: str):
    """
    Parses a single file and returns a list of chunks,
    each with code, type, name, and line range.
    """
    language = get_language_from_file(file_path)
    if not language:
        return []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source_code = f.read()

    source_bytes = source_code.encode("utf-8")

    parser = get_parser(language)
    tree = parser.parse(source_bytes)
    root_node = tree.root_node

    chunks = []
    target_types = CHUNK_NODE_TYPES.get(language, set())

    def walk(node):
        if node.type in target_types and node.child_count > 0:
            chunk_text = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")
            name = extract_name(node, source_bytes)
            chunks.append({
                "file": file_path,
                "type": node.type,
                "name": name,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "code": chunk_text,
            })
        for child in node.children:
            walk(child)

    walk(root_node)

    # Fallback: if no chunks found (e.g. procedural script with no functions/classes)
    if not chunks and source_code.strip():
        chunks.append({
            "file": file_path,
            "type": "module",
            "name": os.path.basename(file_path),
            "start_line": 1,
            "end_line": len(source_code.splitlines()),
            "code": source_code,
        })

    return chunks


def chunk_repo(repo_path: str):
    """
    Walks the whole repo, chunks every supported file,
    and returns a flat list of all chunks.
    """
    all_chunks = []
    ignore_dirs = {"node_modules", "venv", ".git", "__pycache__", "dist", "build"}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            if get_language_from_file(file_path):
                all_chunks.extend(chunk_file(file_path))

    return all_chunks