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

    @staticmethod
    def bar_chart(data: Dict[str, float], width: int = 40, height: int = 8,
                  max_value: Optional[float] = None,
                  show_values: bool = False) -> str:
        """
        Create a vertical bar chart from data.

        Args:
            data: Dictionary of label -> value pairs
            width: Maximum width of chart in characters
            height: Height of chart in lines
            max_value: Maximum value for scaling (auto if None)
            show_values: Whether to show numeric values

        Returns:
            Formatted bar chart as string
        """
        if not data:
            return 'No data'

        # Unicode block elements for bars (8 levels)
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

        # Calculate max value if not provided
        if max_value is None:
            max_value = max(data.values()) if data.values() else 1

        if max_value == 0:
            max_value = 1

        # Calculate bar width per item
        num_items = len(data)
        bar_width = max(1, width // (num_items * 2))  # Leave space between bars

        lines = []

        # Draw from top to bottom
        for y in range(height - 1, -1, -1):
            line_parts = []
            threshold = (y + 1) / height * max_value

            for label, value in data.items():
                # Determine block level
                level = int((value / max_value) * height * 8) if max_value > 0 else 0
                level = max(0, min(8, level))

                # Draw bar
                if value >= threshold:
                    block = blocks[8]  # Full block
                elif value >= threshold - (max_value / height / 8):
                    block = blocks[level % 9]
                else:
                    block = blocks[0]  # Space

                # Build bar
                bar = block * bar_width
                line_parts.append(bar)

            lines.append(''.join(line_parts))

        # Add labels and values
        label_line = ''
        value_line = ''

        for label, value in data.items():
            label_short = label[:bar_width]
            label_line += label_short.ljust(bar_width)

            if show_values:
                value_str = f'{value:.1f}'[:bar_width]
                value_line += value_str.ljust(bar_width)

        result_lines = [*lines, label_line]
        if show_values:
            result_lines.append(value_line)

        return '\n'.join(result_lines)

    @staticmethod
    def horizontal_bar(values: List[float], labels: Optional[List[str]] = None,
                      width: int = 40, show_values: bool = True,
                      fill_char: str = '█', empty_char: str = '░') -> str:
        """
        Create horizontal bar chart from values.

        Args:
            values: List of numeric values
            labels: Optional list of labels (one per value)
            width: Maximum width of bars in characters
            show_values: Whether to show numeric values
            fill_char: Character to use for filled portion
            empty_char: Character to use for empty portion

        Returns:
            Formatted horizontal bar chart as string
        """
        if not values:
            return 'No data'

        max_value = max(abs(v) for v in values) if values else 1
        if max_value == 0:
            max_value = 1

        lines = []

        for i, value in enumerate(values):
            label = labels[i] if labels and i < len(labels) else f'Item {i+1}'

            # Calculate bar length
            bar_length = int((abs(value) / max_value) * width)
            bar_length = max(0, min(width, bar_length))

            # Build bar
            bar = fill_char * bar_length + empty_char * (width - bar_length)

            # Format line
            line = f'{label:15} │{bar}│ {value:.2f}' if show_values else f'{label:15} │{bar}│'

            lines.append(line)

        return '\n'.join(lines)

    @staticmethod
    def sparkline(values: List[float], width: int = 30,
                  height: int = 3, show_bounds: bool = False) -> str:
        """
        Create a sparkline (mini line chart) from values.

        Args:
            values: List of numeric values
            width: Width of sparkline in characters
            height: Height of sparkline in lines
            show_bounds: Whether to show min/max values

        Returns:
            Formatted sparkline as string
        """
        if not values:
            return 'No data'

        if len(values) < 2:
            return str(values[0]) if values else 'No data'

        # Unicode block elements for different heights
        blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

        # Normalize values to fit in width
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        if range_val == 0:
            range_val = 1

        # Sample values to fit width
        num_points = min(width, len(values))
        step = len(values) / num_points
        sampled = []

        for i in range(num_points):
            idx = int(i * step)
            if idx < len(values):
                sampled.append(values[idx])

        # Normalize to 0-8 range (8 block levels)
        normalized = [
            int(((v - min_val) / range_val) * (height * 8 - 1))
            for v in sampled
        ]

        # Create sparkline
        lines = []
        for y in range(height - 1, -1, -1):
            line = ''
            threshold_low = y * 8
            threshold_high = (y + 1) * 8

            for val in normalized:
                if val >= threshold_high:
                    block = blocks[8]  # Full block
                elif val >= threshold_low:
                    level = (val - threshold_low) % 9
                    block = blocks[level]
                else:
                    block = blocks[0]  # Space

                line += block

            lines.append(line)

        result = '\n'.join(lines)

        if show_bounds:
            result += f'\nMin: {min_val:.2f} Max: {max_val:.2f}'

        return result

    @staticmethod
    def histogram(values: List[float], bins: int = 10, width: int = 40,
                  fill_char: str = '█') -> str:
        """
        Create a histogram from values.

        Args:
            values: List of numeric values
            bins: Number of bins for histogram
            width: Maximum width of histogram bars
            fill_char: Character to use for bars

        Returns:
            Formatted histogram as string
        """
        if not values:
            return 'No data'

        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val

        if range_val == 0:
            # All values are the same
            bin_counts = [len(values)] + [0] * (bins - 1)
            bin_labels = [f'{min_val:.2f}']
        else:
            # Create bins
            bin_counts = [0] * bins
            bin_width = range_val / bins

            for value in values:
                bin_idx = min(int((value - min_val) / bin_width), bins - 1)
                bin_counts[bin_idx] += 1

            # Generate bin labels
            bin_labels = []
            for i in range(bins):
                bin_start = min_val + i * bin_width
                bin_end = min_val + (i + 1) * bin_width
                bin_labels.append(f'{bin_start:.1f}-{bin_end:.1f}')

        # Normalize counts for display
        max_count = max(bin_counts) if bin_counts else 1

        lines = []
        for i, count in enumerate(bin_counts):
            bar_length = int((count / max_count) * width)
            bar = fill_char * bar_length
            label = bin_labels[i] if i < len(bin_labels) else f'Bin {i+1}'
            lines.append(f'{label:15} │{bar}│ {count}')

        return '\n'.join(lines)

    @staticmethod
    def progress_bar(current: float, total: float, width: int = 30,
                    fill_char: str = '█', empty_char: str = '░',
                    show_percent: bool = True) -> str:
        """
        Create a progress bar.

        Args:
            current: Current value
            total: Total/maximum value
            width: Width of progress bar
            fill_char: Character for filled portion
            empty_char: Character for empty portion
            show_percent: Whether to show percentage

        Returns:
            Formatted progress bar as string
        """
        percent = 0.0 if total == 0 else min(100.0, max(0.0, current / total * 100.0))

        filled = int((percent / 100.0) * width)
        filled = max(0, min(width, filled))
        empty = width - filled

        bar = fill_char * filled + empty_char * empty

        if show_percent:
            return f'[{bar}] {percent:.1f}%'
        else:
            return f'[{bar}]'

    @staticmethod
    def candlestick(candles: List[Dict[str, float]], width: int = 60, height: int = 15,
                   labels: Optional[List[str]] = None,
                   bullish_char: str = '█', bearish_char: str = '█',
                   wick_char: str = '│') -> str:
        """
        Create a candlestick chart from OHLC data.

        Args:
            candles: List of dictionaries with 'open', 'high', 'low', 'close' keys
            width: Width of chart in characters
            height: Height of chart in lines
            labels: Optional list of labels for each candle
            bullish_char: Character for bullish (green/up) candles
            bearish_char: Character for bearish (red/down) candles
            wick_char: Character for wicks (high/low lines)

        Returns:
            Formatted candlestick chart as string
        """
        if not candles:
            return 'No data'

        # Extract OHLC values
        ohlc_data = []
        for candle in candles:
            ohlc = {
                'open': candle.get('open', 0),
                'high': candle.get('high', 0),
                'low': candle.get('low', 0),
                'close': candle.get('close', 0)
            }
            ohlc_data.append(ohlc)

        # Find min/max for scaling
        all_highs = [ohlc['high'] for ohlc in ohlc_data]
        all_lows = [ohlc['low'] for ohlc in ohlc_data]
        min_price = min(all_lows) if all_lows else 0
        max_price = max(all_highs) if all_highs else 1

        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1

        # Calculate candle width
        num_candles = len(ohlc_data)
        candle_width = max(1, width // num_candles - 1)  # Leave space between candles
        candle_width = min(candle_width, 5)  # Limit max width for readability

        # Create grid for plotting
        grid = [[' ' for _ in range(width)] for _ in range(height)]

        # Plot each candle
        for i, ohlc in enumerate(ohlc_data):
            open_price = ohlc['open']
            high_price = ohlc['high']
            low_price = ohlc['low']
            close_price = ohlc['close']

            # Determine if bullish (close > open) or bearish (close <= open)
            is_bullish = close_price >= open_price
            body_top = max(open_price, close_price)
            body_bottom = min(open_price, close_price)
            body_char = bullish_char if is_bullish else bearish_char

            # Calculate positions in grid (y is inverted - 0 is top, height-1 is bottom)
            def price_to_y(price: float) -> int:
                normalized = (price - min_price) / price_range
                y = int((1.0 - normalized) * (height - 1))
                return max(0, min(height - 1, y))

            high_y = price_to_y(high_price)
            low_y = price_to_y(low_price)
            body_top_y = price_to_y(body_top)
            body_bottom_y = price_to_y(body_bottom)

            # Calculate x position (centered in candle's space)
            x_start = i * (candle_width + 1)
            x_center = x_start + candle_width // 2

            # Draw wick (high-low line)
            for y in range(low_y, high_y + 1):
                if 0 <= x_center < width:
                    grid[y][x_center] = wick_char

            # Draw body (open-close rectangle)
            if body_top_y == body_bottom_y:
                # Single line body
                for x in range(x_start, min(x_start + candle_width, width)):
                    if 0 <= body_top_y < height:
                        grid[body_top_y][x] = body_char
            else:
                # Multi-line body
                for y in range(body_bottom_y, body_top_y + 1):
                    for x in range(x_start, min(x_start + candle_width, width)):
                        if 0 <= y < height and 0 <= x < width:
                            grid[y][x] = body_char

            # Overlay wick on body (ensure wick is visible)
            if 0 <= x_center < width:
                for y in range(low_y, high_y + 1):
                    grid[y][x_center] = wick_char

        # Convert grid to string lines
        lines = []
        for row in grid:
            lines.append(''.join(row))

        # Add price scale on the right
        scale_lines = []
        for i, line in enumerate(lines):
            y_ratio = i / (height - 1) if height > 1 else 0
            price = max_price - (price_range * y_ratio)
            scale_lines.append(f'{line} │ {price:.2f}')

        result = '\n'.join(scale_lines)

        # Add labels if provided
        if labels:
            label_line = ' ' * width + '│ '
            for i, label in enumerate(labels[:num_candles]):
                x_pos = i * (candle_width + 1) + candle_width // 2
                if x_pos < width:
                    label_short = label[:candle_width]
                    # Try to center label under candle
                    start_pos = max(0, x_pos - len(label_short) // 2)
                    label_line = label_line[:start_pos] + label_short + label_line[start_pos + len(label_short):]
                    label_line = label_line[:width] + '│ ' + label_line[width:]
            result += '\n' + label_line[:width + 20]  # Limit label line length

        return result

    @staticmethod
    def candlestick_simple(open_price: float, high_price: float, low_price: float,
                          close_price: float, width: int = 20) -> str:
        """
        Create a single simple candlestick representation.

        Args:
            open_price: Opening price
            high_price: High price
            low_price: Low price
            close_price: Closing price
            width: Width of display

        Returns:
            Simple candlestick string representation
        """
        is_bullish = close_price >= open_price

        # Determine price range
        price_range = high_price - low_price
        if price_range == 0:
            price_range = 1

        # Normalize positions (0-1 scale)
        open_pos = (open_price - low_price) / price_range
        close_pos = (close_price - low_price) / price_range

        body_top = max(open_pos, close_pos)
        body_bottom = min(open_pos, close_pos)

        # Create simple visualization
        height = 10
        chart = [' ' * width for _ in range(height)]

        # Draw wick
        wick_x = width // 2
        for y in range(height):
            chart[y] = chart[y][:wick_x] + '│' + chart[y][wick_x + 1:]

        # Draw body
        body_start = max(0, int(width * 0.3))
        body_end = min(width, int(width * 0.7))
        body_end - body_start

        body_top_y = int((1.0 - body_top) * (height - 1))
        body_bottom_y = int((1.0 - body_bottom) * (height - 1))

        body_char = '█' if is_bullish else '░'

        for y in range(body_bottom_y, body_top_y + 1):
            for x in range(body_start, body_end):
                if 0 <= x < width and 0 <= y < height:
                    chart[y] = chart[y][:x] + body_char + chart[y][x + 1:]

        # Build result
        lines = []
        for row in chart:
            lines.append(row)

        # Add price info
        price_info = f'O:{open_price:.2f} H:{high_price:.2f} L:{low_price:.2f} C:{close_price:.2f}'
        if is_bullish:
            price_info += ' ▲'
        else:
            price_info += ' ▼'

        lines.append(price_info)

        return '\n'.join(lines)

