"""String Similarity — multiple algorithms for fuzzy matching.

Implements:
- Levenshtein distance (edit distance)
- Jaro-Winkler similarity (good for names)
- Cosine similarity (token-based)
- Longest Common Subsequence (LCS)
- Normalized similarity scores (0.0-1.0)
- Best match from candidates
"""
from __future__ import annotations
from collections import Counter
import math


class StringSimilarityService:
    def levenshtein(self, a: str, b: str) -> int:
        """Minimum edit distance (insert, delete, substitute)."""
        m, n = len(a), len(b)
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            prev = dp[0]
            dp[0] = i
            for j in range(1, n + 1):
                temp = dp[j]
                if a[i-1] == b[j-1]:
                    dp[j] = prev
                else:
                    dp[j] = 1 + min(dp[j], dp[j-1], prev)
                prev = temp
        return dp[n]

    def levenshtein_similarity(self, a: str, b: str) -> float:
        """Normalized Levenshtein: 1.0 = identical, 0.0 = completely different."""
        if not a and not b:
            return 1.0
        dist = self.levenshtein(a, b)
        return round(1 - dist / max(len(a), len(b)), 4)

    def jaro(self, a: str, b: str) -> float:
        """Jaro similarity (0.0-1.0)."""
        if a == b:
            return 1.0
        if not a or not b:
            return 0.0

        match_dist = max(len(a), len(b)) // 2 - 1
        match_dist = max(0, match_dist)

        a_matches = [False] * len(a)
        b_matches = [False] * len(b)
        matches = 0
        transpositions = 0

        for i, ca in enumerate(a):
            start = max(0, i - match_dist)
            end = min(len(b), i + match_dist + 1)
            for j in range(start, end):
                if b_matches[j] or ca != b[j]:
                    continue
                a_matches[i] = True
                b_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len(a)):
            if not a_matches[i]:
                continue
            while not b_matches[k]:
                k += 1
            if a[i] != b[k]:
                transpositions += 1
            k += 1

        jaro = (matches / len(a) + matches / len(b) +
                (matches - transpositions / 2) / matches) / 3
        return round(jaro, 4)

    def jaro_winkler(self, a: str, b: str, prefix_weight: float = 0.1) -> float:
        """Jaro-Winkler: boosts score for common prefix (good for names)."""
        jaro_score = self.jaro(a, b)
        prefix_len = 0
        for i in range(min(4, min(len(a), len(b)))):
            if a[i] == b[i]:
                prefix_len += 1
            else:
                break
        return round(jaro_score + prefix_len * prefix_weight * (1 - jaro_score), 4)

    def cosine(self, a: str, b: str) -> float:
        """Cosine similarity on character bigrams."""
        if not a or not b:
            return 0.0 if a != b else 1.0
        bigrams_a = Counter(a[i:i+2] for i in range(len(a)-1))
        bigrams_b = Counter(b[i:i+2] for i in range(len(b)-1))
        if not bigrams_a or not bigrams_b:
            return 1.0 if a == b else 0.0
        intersection = sum((bigrams_a & bigrams_b).values())
        mag_a = math.sqrt(sum(v*v for v in bigrams_a.values()))
        mag_b = math.sqrt(sum(v*v for v in bigrams_b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return round(intersection / (mag_a * mag_b), 4)

    def lcs_length(self, a: str, b: str) -> int:
        """Length of Longest Common Subsequence."""
        m, n = len(a), len(b)
        dp = [0] * (n + 1)
        for i in range(1, m + 1):
            prev = 0
            for j in range(1, n + 1):
                temp = dp[j]
                if a[i-1] == b[j-1]:
                    dp[j] = prev + 1
                else:
                    dp[j] = max(dp[j], dp[j-1])
                prev = temp
        return dp[n]

    def lcs_similarity(self, a: str, b: str) -> float:
        if not a and not b:
            return 1.0
        lcs = self.lcs_length(a, b)
        return round(2 * lcs / (len(a) + len(b)), 4) if (len(a) + len(b)) > 0 else 1.0

    def best_match(self, query: str, candidates: list[str],
                   algorithm: str = "levenshtein") -> list[tuple[str, float]]:
        """Find best matches from candidates, sorted by similarity."""
        fn = {
            "levenshtein": self.levenshtein_similarity,
            "jaro_winkler": self.jaro_winkler,
            "cosine": self.cosine,
            "lcs": self.lcs_similarity,
        }.get(algorithm, self.levenshtein_similarity)

        scored = [(c, fn(query, c)) for c in candidates]
        scored.sort(key=lambda x: -x[1])
        return scored
