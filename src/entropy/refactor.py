import os
import shutil
import json
import ast
from typing import Dict, Any, List

class RefactorManager:
    def delete_file(self, filepath: str) -> bool:
        try:
            os.remove(filepath)
            return True
        except OSError as e:
            print(f"Error deleting {filepath}: {e}")
            return False

    def quarantine_file(self, filepath: str) -> bool:
        quarantine_dir = "tests/quarantine"
        if not os.path.exists(quarantine_dir):
            os.makedirs(quarantine_dir)

        filename = os.path.basename(filepath)
        dest = os.path.join(quarantine_dir, filename)

        try:
            shutil.move(filepath, dest)
            return True
        except OSError as e:
            print(f"Error quarantining {filepath}: {e}")
            return False

    def externalize_snapshots(self, filepath: str, large_literals: List[Dict[str, Any]]) -> bool:
        """
        Extracts large literals to JSON files.
        """
        if not large_literals:
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # We need to process replacements carefully.
            # It's best to process from bottom to top to avoid offset shifts?
            # Or just use ast.get_source_segment and string replacement if unique enough.
            # But get_source_segment relies on the AST node.
            # The nodes passed in large_literals were created from a previous parse.
            # We should probably re-parse here to ensure valid nodes for the current content
            # if we do multiple replacements, but for now let's assume one pass or re-parse loop.

            # To be safe: Sort literals by start position descending (bottom-up).
            # But the nodes from scanner might not have full position info attached if not handled carefully.
            # Scanner uses `ast.parse(content)`.

            # Let's re-parse to get fresh nodes and segments.
            tree = ast.parse(content)

            # We need to find the *same* nodes. This is hard without ID.
            # But we can just find *all* large literals again and process them.

            # Re-implement finding logic here briefly or trust the scanner provided locations?
            # Scanner provided `lineno`.

            # Let's refine the approach:
            # 1. Identify large literals in current content.
            # 2. For each, extract and replace.
            # 3. Save file.

            replacements = []

            class LiteralVisitor(ast.NodeVisitor):
                def visit_Dict(self, node):
                    self._check(node)
                    self.generic_visit(node)
                def visit_List(self, node):
                    self._check(node)
                    self.generic_visit(node)
                def _check(self, node):
                    segment = ast.get_source_segment(content, node)
                    if segment and len(segment) > 1000: # Threshold matching scanner
                        replacements.append((node, segment))

            LiteralVisitor().visit(tree)

            # Sort by start offset descending
            replacements.sort(key=lambda x: x[0].lineno, reverse=True) # Approximate sort by line
            # Better: sort by node.col_offset + (node.lineno * 100000)

            # But wait, we need exact offsets.
            # node.end_lineno and node.end_col_offset exist in 3.12.

            replacements.sort(key=lambda x: (x[0].lineno, x[0].col_offset), reverse=True)

            modified_content = content
            snapshots_dir = "tests/snapshots"
            if not os.path.exists(snapshots_dir):
                os.makedirs(snapshots_dir)

            import_added = False

            for i, (node, segment) in enumerate(replacements):
                # Generate snapshot filename
                base_name = os.path.basename(filepath).replace('.py', '')
                snapshot_name = f"{base_name}_snapshot_{i}.json"
                snapshot_path = os.path.join(snapshots_dir, snapshot_name)

                # Parse the segment to get the object (safely)
                try:
                    obj = ast.literal_eval(segment)
                except:
                    continue # Skip if can't eval

                # Write JSON
                with open(snapshot_path, 'w') as f:
                    json.dump(obj, f, indent=2)

                # Replacement string
                replacement_code = f"json.load(open('{snapshot_path}'))"

                # We need to replace the segment in modified_content.
                # Since we sort reverse, we can use string slicing if we have offsets.
                # get_source_segment returns the string. finding it in content is risky if duplicates exist.
                # We should use node positions.

                start_line = node.lineno
                start_col = node.col_offset
                end_line = node.end_lineno
                end_col = node.end_col_offset

                # Map to string indices?
                # This is tedious.
                # Alternative: Use `redbaron` or similar? No, only stdlib.

                # Simple approach: Search for the segment string. Verify it matches context?
                # No, that's brittle.

                # Let's rely on the fact that we process reverse order.
                # But we need to map (line, col) to string index.
                pass

            # Since implementing robust AST transformation is complex and error-prone in a script without specialized libs,
            # I will implement a simplified version:
            # ONLY replace if the file contains EXACTLY ONE large literal matching the scanner's finding.
            # Or use a placeholder comment and manual fix?
            # The prompt says "Action: Externalize Snapshots".

            # I'll try to use line-based replacement if it spans lines.

            # Let's try a different strategy for `refactor.py`.
            # We will use `ast.get_source_segment` and string replacement, but we need to calculate offsets.

            # Calculate offsets
            lines = content.splitlines(keepends=True)
            # Offset map
            line_offsets = [0]
            for line in lines:
                line_offsets.append(line_offsets[-1] + len(line))

            # Now we can convert (lineno, col) to index.
            # lineno is 1-based.

            new_content_segments = []
            last_idx = len(content)

            for node, segment in replacements:
                start_idx = line_offsets[node.lineno - 1] + node.col_offset
                end_idx = line_offsets[node.end_lineno - 1] + node.end_col_offset

                # Verify segment matches
                if content[start_idx:end_idx] != segment:
                    # Fallback or mismatch
                    # Maybe encoding issue or something.
                    # Try to trust the segment?
                    pass

                # We are going backwards.
                # content = content[:start_idx] + replacement + content[end_idx:]
                # But we have multiple.

                # Wait, if I replace in `content`, the offsets for subsequent (earlier) nodes remain valid?
                # Yes, if I process reverse.

                pass

            # Let's do it.
            for i, (node, segment) in enumerate(replacements):
                start_idx = line_offsets[node.lineno - 1] + node.col_offset
                end_idx = line_offsets[node.end_lineno - 1] + node.end_col_offset

                base_name = os.path.basename(filepath).replace('.py', '')
                snapshot_name = f"{base_name}_snapshot_{node.lineno}.json"
                snapshot_path = os.path.join(snapshots_dir, snapshot_name)

                try:
                    obj = ast.literal_eval(segment)
                    with open(snapshot_path, 'w') as f:
                        json.dump(obj, f, indent=2)

                    snapshot_path_str = snapshot_path.replace(os.sep, '/')
                    replacement = f"json.load(open('{snapshot_path_str}'))"

                    content = content[:start_idx] + replacement + content[end_idx:]
                    import_added = True

                except Exception as e:
                    print(f"Failed to externalize snapshot: {e}")
                    continue

            if import_added:
                # Add import json if needed
                if "import json" not in content:
                    lines = content.splitlines()
                    insert_idx = 0

                    # Skip shebang and encoding lines at the very top
                    for i, line in enumerate(lines):
                        if line.startswith("#!") or line.startswith("# -*-") or line.startswith("# coding="):
                            insert_idx = i + 1
                        elif not line.strip():
                            pass # Skip empty lines
                        else:
                            break

                    # Try to find existing imports to group with
                    last_import_idx = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith("import ") or line.strip().startswith("from "):
                            last_import_idx = i

                    if last_import_idx != -1:
                        insert_idx = last_import_idx + 1

                    # Insert the import
                    lines.insert(insert_idx, "import json")
                    content = "\n".join(lines) + "\n" # Ensure trailing newline

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except Exception as e:
            print(f"Error externalizing snapshots for {filepath}: {e}")
            return False
