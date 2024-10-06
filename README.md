# Rightmost LZ77 Parsing Using Right Closed Repeats

This Python script computes the **rightmost LZ77 parsing** of any substring of a given string using **right closed repeats**. 

I did not come up with this on my own; it's based on concepts and algorithms from this paper that I found: [_"Closed Repeats"_](https://arxiv.org/abs/2410.00209).

## Overview

The script preprocesses the input string to identify right closed repeats, which helps in efficiently computing the LZ77 parsing with a focus on the rightmost occurrences.

### What are Right Closed Repeats?

A **right closed repeat** is a substring that appears more than once in the string and cannot be extended to the right to match further. This concept is defined in the paper shown above.

### LZ77 Parsing

LZ77 (Lempel-Ziv) parsing is a way to compress a string by replacing repeating occurences with a "reference" to an occurence before it.
The _rightmost_ part basically means that the reference will use the most recently occured repetition (the right-most repetition)

### What did the paper outline?

It showed that their algorithm can compute the **rightmost** LZ77 compression in $O(n\log n)$ space and $O(z\log\log\ell)$ time, where n is the length of the string, z is the number of phrases in the parsing, and $\ell$ is how many characters is being queried (i.e. the length of the substring that you want to parse).

This is slightly cheaper in time compared to current methods, but with a tradeoff in space complexity.

## How It Works

1. **Preprocessing**:
   - Builds the **suffix array** and **Longest Common Prefix (LCP) array** of the input string.
   - Identifies all right closed repeats and stores them for quick access.

2. **Computing the Parsing**:
   - Uses the preprocessed data to find the longest matches when parsing a substring.
   - Ensures that matches are chosen based on their rightmost occurrences.

## Limitations
Note that although the paper outlines the use of a suffix tree and a Van Emde Boas tree to achieve said complexity, this is a **simplified** version, which aims to eventually implement the algorithm shown on the paper.

Therefore, this script does not mirror the complexity given in the paper, although that is the eventual goal.

## Usage
Download the script and then run it with Python 3.9+.

### Sample Usage
After running the file, when prompted, enter the string:
```
Enter the string: abracadabra
```
Now, enter the indices of the substring to query:
```
Enter the query substring indices (i and length ell):
i = 1
ell = 11
```
It will now output the rightmost LZ77 parsing:
```
Rightmost LZ77 parsing:
Literal: 'a'
Literal: 'b'
Literal: 'r'
Copy: distance=3, length=1
Literal: 'c'
Copy: distance=2, length=1
Literal: 'd'
Copy: distance=7, length=4
```
