"""JSON Patch Engine — RFC 6902 compliant JSON Patch operations.

Supports: add, remove, replace, move, copy, test
With path parsing using JSON Pointer (RFC 6901)
"""
from __future__ import annotations
from copy import deepcopy


class JsonPatchError(Exception):
    pass


class JsonPatchEngineService:
    def apply(self, document: dict | list, operations: list[dict]) -> dict | list:
        """Apply a list of JSON Patch operations to a document."""
        result = deepcopy(document)
        for i, op in enumerate(operations):
            try:
                result = self._apply_op(result, op)
            except (KeyError, IndexError, TypeError) as e:
                raise JsonPatchError(f"Operation {i} ({op.get('op')}) failed: {e}")
        return result

    def _apply_op(self, doc, op: dict):
        operation = op.get("op")
        path = op.get("path", "")

        if operation == "add":
            return self._op_add(doc, path, op["value"])
        elif operation == "remove":
            return self._op_remove(doc, path)
        elif operation == "replace":
            return self._op_replace(doc, path, op["value"])
        elif operation == "move":
            return self._op_move(doc, path, op["from"])
        elif operation == "copy":
            return self._op_copy(doc, path, op["from"])
        elif operation == "test":
            return self._op_test(doc, path, op["value"])
        else:
            raise JsonPatchError(f"Unknown operation: {operation}")

    def _parse_path(self, path: str) -> list[str]:
        """Parse JSON Pointer (RFC 6901)."""
        if not path:
            return []
        if not path.startswith("/"):
            raise JsonPatchError(f"Invalid path: {path}")
        parts = path[1:].split("/")
        return [p.replace("~1", "/").replace("~0", "~") for p in parts]

    def _get(self, doc, path: str):
        """Get value at path."""
        parts = self._parse_path(path)
        current = doc
        for part in parts:
            if isinstance(current, list):
                current = current[int(part)]
            elif isinstance(current, dict):
                current = current[part]
            else:
                raise JsonPatchError(f"Cannot traverse {type(current)}")
        return current

    def _set(self, doc, path: str, value):
        """Set value at path."""
        parts = self._parse_path(path)
        if not parts:
            return value  # replace entire document

        current = doc
        for part in parts[:-1]:
            if isinstance(current, list):
                current = current[int(part)]
            else:
                current = current[part]

        last = parts[-1]
        if isinstance(current, list):
            idx = int(last) if last != "-" else len(current)
            if last == "-" or idx == len(current):
                current.append(value)
            else:
                current.insert(idx, value)
        else:
            current[last] = value
        return doc

    def _delete(self, doc, path: str):
        parts = self._parse_path(path)
        current = doc
        for part in parts[:-1]:
            if isinstance(current, list):
                current = current[int(part)]
            else:
                current = current[part]

        last = parts[-1]
        if isinstance(current, list):
            current.pop(int(last))
        else:
            del current[last]
        return doc

    def _op_add(self, doc, path, value):
        return self._set(doc, path, value)

    def _op_remove(self, doc, path):
        return self._delete(doc, path)

    def _op_replace(self, doc, path, value):
        self._get(doc, path)  # verify exists
        parts = self._parse_path(path)
        current = doc
        for part in parts[:-1]:
            current = current[int(part)] if isinstance(current, list) else current[part]
        last = parts[-1]
        if isinstance(current, list):
            current[int(last)] = value
        else:
            current[last] = value
        return doc

    def _op_move(self, doc, path, from_path):
        value = self._get(doc, from_path)
        doc = self._delete(doc, from_path)
        doc = self._set(doc, path, value)
        return doc

    def _op_copy(self, doc, path, from_path):
        value = deepcopy(self._get(doc, from_path))
        return self._set(doc, path, value)

    def _op_test(self, doc, path, value):
        actual = self._get(doc, path)
        if actual != value:
            raise JsonPatchError(f"Test failed: {actual} != {value}")
        return doc

    def diff(self, old: dict, new: dict, prefix: str = "") -> list[dict]:
        """Generate patch operations to transform old into new."""
        ops = []
        all_keys = set(old.keys()) | set(new.keys())
        for key in sorted(all_keys):
            path = f"{prefix}/{key}"
            if key not in old:
                ops.append({"op": "add", "path": path, "value": new[key]})
            elif key not in new:
                ops.append({"op": "remove", "path": path})
            elif old[key] != new[key]:
                if isinstance(old[key], dict) and isinstance(new[key], dict):
                    ops.extend(self.diff(old[key], new[key], path))
                else:
                    ops.append({"op": "replace", "path": path, "value": new[key]})
        return ops
