"""Logo placeholder — generate placeholder logos for apps without icons."""

import hashlib


GRADIENTS = [
    "from-blue-500 to-purple-600", "from-green-500 to-teal-600",
    "from-orange-500 to-red-600", "from-pink-500 to-rose-600",
    "from-cyan-500 to-blue-600", "from-violet-500 to-indigo-600",
    "from-amber-500 to-orange-600", "from-emerald-500 to-green-600",
]


def generate_placeholder(*, app_name: str, size: int = 64) -> dict:
    initials = "".join(w[0].upper() for w in app_name.split()[:2]) or "?"
    idx = int(hashlib.md5(app_name.encode()).hexdigest(), 16) % len(GRADIENTS)
    return {
        "initials": initials,
        "gradient": GRADIENTS[idx],
        "size": size,
        "font_size": size // 2,
        "shape": "rounded-xl" if size >= 48 else "rounded-lg",
    }
