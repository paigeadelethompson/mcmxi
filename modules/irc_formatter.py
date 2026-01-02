"""
IRC text formatting utilities.
"""
from typing import Dict, List, Optional


# Text formatting utility
class IRCFormatter:
    """IRC text formatting utilities (no colors)."""

    @staticmethod
    def bold(text: str) -> str:
        """Make text bold."""
        return f'\x02{text}\x02'

    @staticmethod
    def italic(text: str) -> str:
        """Make text italic."""
        return f'\x1d{text}\x1d'

    @staticmethod
    def underline(text: str) -> str:
        """Underline text."""
        return f'\x1f{text}\x1f'

    @staticmethod
    def strikethrough(text: str) -> str:
        """Strikethrough text."""
        return f'\x1e{text}\x1e'

    @staticmethod
    def monospace(text: str) -> str:
        """Monospace text."""
        return f'\x11{text}\x11'

    @staticmethod
    def reverse(text: str) -> str:
        """Reverse video (swap foreground/background)."""
        return f'\x16{text}\x16'

    @staticmethod
    def table(data: List[List[str]], headers: Optional[List[str]] = None,
              max_width: int = 400) -> str:
        """
        Format data as a table.
        Returns formatted string suitable for IRC.
        """
        if not data:
            return 'No data'

        # Include headers if provided
        rows = [headers, *data] if headers else data

        # Calculate column widths
        num_cols = len(rows[0])
        col_widths = [0] * num_cols

        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Limit column widths to prevent overflow
        total_width = sum(col_widths) + (num_cols - 1) * 3  # 3 for separators
        if total_width > max_width:
            scale = max_width / total_width
            col_widths = [int(w * scale) for w in col_widths]

        # Format rows
        lines = []
        for i, row in enumerate(rows):
            formatted_row = ' | '.join(
                str(cell)[:col_widths[j]].ljust(col_widths[j])
                for j, cell in enumerate(row)
            )
            lines.append(formatted_row)

            # Add separator after headers
            if headers and i == 0:
                lines.append('-+-'.join('-' * w for w in col_widths))

        return '\n'.join(lines)

    @staticmethod
    def truncate(text: str, max_len: int = 300, suffix: str = '...') -> str:
        """Truncate text to max length."""
        if len(text) <= max_len:
            return text
        return text[:max_len - len(suffix)] + suffix
