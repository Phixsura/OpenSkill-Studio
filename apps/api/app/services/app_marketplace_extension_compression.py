"""Compression Engine — multiple compression algorithms for data storage.

Implements:
- Run-Length Encoding (RLE) for repetitive data
- Dictionary compression for repeated strings
- Delta encoding for time-series integers
- Compression ratio calculation
- Auto-select best algorithm for data type
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CompressionResult:
    algorithm: str
    original_size: int
    compressed_size: int
    data: object  # compressed representation

    @property
    def ratio(self) -> float:
        return round(self.original_size / max(1, self.compressed_size), 2)

    @property
    def savings_pct(self) -> float:
        return round((1 - self.compressed_size / max(1, self.original_size)) * 100, 1)


class CompressionEngineService:
    def rle_encode(self, data: list) -> CompressionResult:
        """Run-Length Encoding: [a,a,a,b,b,c] → [(a,3),(b,2),(c,1)]."""
        if not data:
            return CompressionResult("rle", 0, 0, [])
        encoded = []
        current = data[0]
        count = 1
        for item in data[1:]:
            if item == current:
                count += 1
            else:
                encoded.append((current, count))
                current = item
                count = 1
        encoded.append((current, count))
        return CompressionResult("rle", len(data), len(encoded) * 2, encoded)

    def rle_decode(self, encoded: list[tuple]) -> list:
        result = []
        for value, count in encoded:
            result.extend([value] * count)
        return result

    def dict_encode(self, strings: list[str]) -> CompressionResult:
        """Dictionary compression: replace repeated strings with indices."""
        dictionary: dict[str, int] = {}
        encoded = []
        for s in strings:
            if s not in dictionary:
                dictionary[s] = len(dictionary)
            encoded.append(dictionary[s])

        orig_size = sum(len(s) for s in strings)
        dict_size = sum(len(s) for s in dictionary) + len(dictionary) * 4
        encoded_size = len(encoded) * 4 + dict_size

        return CompressionResult("dictionary", orig_size, encoded_size,
                                 {"dictionary": {v: k for k, v in dictionary.items()},
                                  "encoded": encoded})

    def dict_decode(self, compressed: dict) -> list[str]:
        dictionary = compressed["dictionary"]
        return [dictionary[idx] for idx in compressed["encoded"]]

    def delta_encode(self, values: list[int]) -> CompressionResult:
        """Delta encoding: store differences instead of absolute values.
        [100, 102, 105, 103] → [100, 2, 3, -2]."""
        if not values:
            return CompressionResult("delta", 0, 0, [])
        deltas = [values[0]]
        for i in range(1, len(values)):
            deltas.append(values[i] - values[i - 1])

        # Estimate size: deltas are typically smaller numbers
        orig_bits = sum(v.bit_length() + 1 for v in values)
        delta_bits = sum(abs(d).bit_length() + 1 for d in deltas)

        return CompressionResult("delta", orig_bits // 8 + len(values),
                                 delta_bits // 8 + len(deltas), deltas)

    def delta_decode(self, deltas: list[int]) -> list[int]:
        if not deltas:
            return []
        values = [deltas[0]]
        for d in deltas[1:]:
            values.append(values[-1] + d)
        return values

    def auto_select(self, data: list) -> CompressionResult:
        """Try all applicable algorithms, return best compression."""
        candidates = []

        # RLE works on any list
        candidates.append(self.rle_encode(data))

        # Delta for integer lists
        if data and all(isinstance(x, int) for x in data):
            candidates.append(self.delta_encode(data))

        # Dictionary for string lists
        if data and all(isinstance(x, str) for x in data):
            candidates.append(self.dict_encode(data))

        if not candidates:
            return CompressionResult("none", len(data), len(data), data)

        return min(candidates, key=lambda c: c.compressed_size)
