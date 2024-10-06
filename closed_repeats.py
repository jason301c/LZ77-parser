"""
Rightmost LZ77 Parsing Using Right Closed Repeats
Here, we compute right-closed repeats of a string (i.e. repeats that cannot be extended to the right), and
use them to compute the rightmost LZ77 parsing of any substring of the string.
"""

from typing import List, Tuple, Dict

__author__ = "Jason Alexander Sutiono"
__version__ = "1.0"

class RightClosedRepeats:
    """
    Preprocess a string to enable efficient computation of the rightmost LZ77 parsing
    of its substrings.

    Attributes:
        text (str): The input string to preprocess.
        length (int): The length of the input string.
        suffix_array (List[int]): The suffix array of the input string.
        lcp_array (List[int]): The longest common prefix (LCP) array of the input string.
        repeats_at_position (Dict[int, List[Tuple[int, int]]]): A mapping from positions to lists
            of right closed repeats that have their next occurrence starting at that position.
    """

    def __init__(self, text: str):
        """
        Initialize the RightClosedRepeats object and preprocess the input string.

        Args:
            text (str): The input string to preprocess.
        """
        self.text: str = text
        self.length: int = len(text)
        self.suffix_array: List[int] = []
        self.lcp_array: List[int] = []
        self.repeats_at_position: Dict[int, List[Tuple[int, int]]] = self._build_right_closed_repeats()

    def _build_suffix_array(self) -> List[int]:
        """
        Construct the suffix array of the input string using a doubling algorithm.

        Here we use a suffix array instead of a suffix tree to simplify the implementation.
        Implementing a complexer suffix tree is in progress
        Returns:
            List[int]: The suffix array of the input string.
        """
        n: int = self.length
        k: int = 1
        rank: List[int] = [ord(c) for c in self.text]
        temp_rank: List[int] = [0] * n
        suffix_array: List[int] = list(range(n))

        while True:
            # Sort based on current rank and rank at position k steps ahead
            suffix_array.sort(key=lambda x: (rank[x], rank[x + k] if x + k < n else -1))

            temp_rank[suffix_array[0]] = 0
            for i in range(1, n):
                prev, curr = suffix_array[i - 1], suffix_array[i]
                temp_rank[curr] = temp_rank[prev] + (
                    (rank[curr], rank[curr + k] if curr + k < n else -1) !=
                    (rank[prev], rank[prev + k] if prev + k < n else -1)
                )

            rank, temp_rank = temp_rank, rank
            if rank[suffix_array[-1]] == n - 1:
                break
            k <<= 1  # Double the comparison length

        return suffix_array

    def _build_lcp_array(self) -> List[int]:
        """
        Construct the LCP (Longest Common Prefix) array using the suffix array.

        Returns:
            List[int]: The LCP array of the input string.
        """
        n: int = self.length
        rank: List[int] = [0] * n
        for i in range(n):
            rank[self.suffix_array[i]] = i

        lcp_array: List[int] = [0] * (n - 1)
        h: int = 0
        for i in range(n):
            if rank[i] > 0:
                j: int = self.suffix_array[rank[i] - 1]
                while i + h < n and j + h < n and self.text[i + h] == self.text[j + h]:
                    h += 1
                lcp_array[rank[i] - 1] = h
                if h > 0:
                    h -= 1
            else:
                h = 0  # Reset h because rank[i] == 0

        return lcp_array

    def _build_right_closed_repeats(self) -> Dict[int, List[Tuple[int, int]]]:
        """
        Identify and build a data structure of right closed repeats in the input string.

        Returns:
            Dict[int, List[Tuple[int, int]]]: A dictionary mapping positions to lists of
            right closed repeats whose next occurrence is at those positions.
        """
        self.suffix_array = self._build_suffix_array()
        self.lcp_array = self._build_lcp_array()

        repeats_at_position: Dict[int, List[Tuple[int, int]]] = {}

        for i in range(len(self.lcp_array)):
            lcp_length: int = self.lcp_array[i]
            if lcp_length == 0:
                continue  # No repeat of length > 0 at this position

            pos1: int = self.suffix_array[i]
            pos2: int = self.suffix_array[i + 1]

            # Ensure pos1 < pos2 for consistency
            if pos1 > pos2:
                pos1, pos2 = pos2, pos1

            end1: int = pos1 + lcp_length
            end2: int = pos2 + lcp_length

            # Check right closure condition
            if (end1 < self.length and end2 < self.length and self.text[end1] != self.text[end2]) or end1 == self.length or end2 == self.length:
                # Add the right closed repeat to repeats_at_position
                repeats_at_position.setdefault(pos2, []).append((pos1, lcp_length))

        # Sort repeats at each position for efficient predecessor queries
        for p in repeats_at_position:
            # Sort by decreasing q_x (previous occurrence position) and increasing t_x (repeat length)
            repeats_at_position[p].sort(key=lambda x: (-x[0], x[1]))

        return repeats_at_position


def compute_rightmost_lz77(processor: RightClosedRepeats, start_index: int, substring_length: int
                           ) -> List[Tuple[int, int]]:
    """
    Compute the rightmost LZ77 parsing of the specified substring.

    Args:
        processor (RightClosedRepeats): An instance of RightClosedRepeats containing preprocessed data.
        start_index (int): The starting index of the substring (0-based).
        substring_length (int): The length of the substring.

    Returns:
        List[Tuple[int, int]]: A list of phrases representing the LZ77 parsing.
            Each phrase is either (0, c) for a literal character c,
            or (distance, match_length) for a copy operation.
    """
    text: str = processor.text
    repeats_at_position: Dict[int, List[Tuple[int, int]]] = processor.repeats_at_position
    end_index: int = start_index + substring_length
    position: int = start_index
    phrases: List[Tuple[int, int]] = []

    while position < end_index:
        # Check if current character has occurred before in the substring
        previous_occurrences: List[int] = [
            idx for idx in range(start_index, position) if text[idx] == text[position]
        ]

        if not previous_occurrences:
            # Literal character
            phrases.append((0, text[position]))
            position += 1
        else:
            # Attempt to find the longest match using right closed repeats
            repeats: List[Tuple[int, int]] = repeats_at_position.get(position, [])
            match_found: bool = False

            for q_x, t_x in repeats:
                if start_index <= q_x < position:
                    remaining_length: int = end_index - position
                    match_length: int = min(t_x, remaining_length)
                    phrases.append((position - q_x, match_length))
                    position += match_length
                    match_found = True
                    break  # Found the rightmost occurrence with the longest match

            if not match_found:
                # No suitable right closed repeat found; find the longest match manually
                q: int = max(previous_occurrences)
                max_match_length: int = end_index - position
                match_length: int = 0
                while match_length < max_match_length and text[position + match_length] == text[q + match_length]:
                    match_length += 1

                phrases.append((position - q, match_length))
                position += match_length

    return phrases


def main():
    text: str = input("Enter the string: ")
    processor = RightClosedRepeats(text)

    print("Enter the query substring indices (i and length ell):")
    start_pos: int = int(input("i = ")) - 1  # Convert to 0-based
    substring_length: int = int(input("ell = "))

    if start_pos < 0 or start_pos + substring_length > len(text):
        print("Invalid indices")
        return

    phrases: List[Tuple[int, int]] = compute_rightmost_lz77(processor, start_pos, substring_length)
    print("Rightmost LZ77 parsing:")
    for phrase in phrases:
        if phrase[0] == 0:
            # Literal character
            print(f"Literal: '{phrase[1]}'")
        else:
            # Reference to previous substring
            distance, match_length = phrase
            print(f"Copy: distance={distance}, length={match_length}")


if __name__ == "__main__":
    main()
