from functools import lru_cache

from matplotlib.font_manager import FontManager


@lru_cache
def get_monospace_fonts():
    font_manager = FontManager()
    monospace_fonts = {}

    for font in font_manager.ttflist:
        # This is an approximation - checking for names that typically indicate monospace fonts
        if any(
            mono_hint in font.name.lower()
            for mono_hint in ["mono", "console", "typewriter", "courier", "fixed"]
        ):
            monospace_fonts[font.name] = font.fname

    return monospace_fonts
