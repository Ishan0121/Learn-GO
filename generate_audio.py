import os
import re
import subprocess
import html

work_dir = "/home/phantom/Documents/Codes/Aetheris/go/Learn/"

readme_path = os.path.join(work_dir, "ByPract/WebServer/06-FRAMEWORKS-VS-STDLIB.md")
audio_dir = os.path.join(work_dir, "ByPract/WebServer/audio")
os.makedirs(audio_dir, exist_ok=True)
audio_output = os.path.join(audio_dir, "06-FRAMEWORKS-VS-STDLIB.wav")

with open(readme_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove fenced code blocks
text = re.sub(r'```.*?```', '\n[    ]\n', text, flags=re.DOTALL)

# 2. Remove HTML tags
text = re.sub(r'<[^>]+>', '', text)

# 3. Decode HTML entities
text = html.unescape(text)

# 4. Remove URLs
text = re.sub(r'https?://[^\s<>"\']+', '', text)

# 5. BEFORE stripping headings, surround ALL headings (H1-H3) with ellipses for pauses, and add a period.
text = re.sub(r'(?:^|\n)(#{1,3})\s+([^\n]+)', r'\n [] [] \n\2.\n [] []\n', text)

# 6. Remove remaining markdown headings (H1), horizontal rules, bold, italic, blockquotes
text = re.sub(r'(^|\n)\s*---+', '.', text)
text = re.sub(r'#+\s+', '', text)
text = re.sub(r'[*_]{1,2}', '', text)
text = re.sub(r'^\s*>\s+', '', text, flags=re.MULTILINE)

# 6b. Remove any stray HTML inner text that survived tag stripping
text = re.sub(r'Listen to the audio version above!?', '', text)

# 7. Remove inline backtick code  (`code` -> code)
text = re.sub(r'`([^`]*)`', r'\1', text)

# 8. Remove markdown link syntax ([text](url) -> text)
text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)

# 9. Filter remaining non-ASCII (emojis, special unicode)
text = re.sub(r'[^\x00-\x7F]+', ' ', text)

# 10. Collapse only horizontal whitespace (spaces/tabs), preserve newlines
text = re.sub(r'[ \t]+', ' ', text)

# 11. Split into sentences — put each sentence on its own line.
#     We split after '.', '!', or '?' followed by a space or newline.
sentences = re.split(r'(?<=[.!?])\s+', text)
text = '\n'.join(s.strip() for s in sentences if s.strip())

# 12. Normalise excessive blank lines (max 2 in a row)
text = re.sub(r'\n{3,}', '\n\n', text)

sanitized_path = os.path.join(work_dir, "sanitized_for_audio.txt") 
with open(sanitized_path, "w", encoding="utf-8") as f:
    f.write(text.strip())

print(f"Sanitized text written to: {sanitized_path}")

say_env = "/home/phantom/Documents/Codes/Aetheris/AI/modules/kokoro_tts/.venv/bin/python3"
kokoro_path = "/home/phantom/Documents/Codes/Aetheris/AI/modules/kokoro_tts"
say_script = "say.py"

print("Running TTS over the sanitized text...")
res = subprocess.run([
    say_env, say_script,
    "-f", sanitized_path,
    "-o", audio_output
], cwd=kokoro_path)

if res.returncode == 0:
    print(f"Audio successfully generated at {audio_output}")
else:
    print("Error generating audio.")
