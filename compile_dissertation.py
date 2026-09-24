import os
import glob

dissertation_dir = r"D:\IMG_ANALYZE\docs\dissertation"
output_file = r"D:\IMG_ANALYZE\docs\DISSERTATION.md"

chapter_files = sorted([f for f in os.listdir(dissertation_dir) if f.endswith(".md")])
print("Found chapter files:")

total_words = 0
total_lines = 0

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in chapter_files:
        filepath = os.path.join(dissertation_dir, filename)
        with open(filepath, "r", encoding="utf-8") as infile:
            content = infile.read()
            words = len(content.split())
            lines = len(content.splitlines())
            total_words += words
            total_lines += lines
            print(f"  {filename}: {words:,} words, {lines:,} lines")
            outfile.write(content)
            outfile.write("\n\n<div style=\"page-break-after: always;\"></div>\n\n---\n\n")

file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

print("\n" + "="*60)
print(f"Master dissertation compiled to: {output_file}")
print(f"Total Chapters: {len(chapter_files)}")
print(f"Total Word Count: {total_words:,} words")
print(f"Total Line Count: {total_lines:,} lines")
print(f"Compiled File Size: {file_size_mb:.2f} MB")
print("="*60)
