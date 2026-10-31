# apply_patch.py
# Usage: python apply_patch.py /path/to/Launcher.exe patch.json [--recoded]
#
#   --recoded   also apply the Kingdom Hearts Recoded patches
#               (leave off if you don't have a Recoded executable)

import sys, os, json, shutil, hashlib

args = sys.argv[1:]
include_recoded = "--recoded" in args
args = [a for a in args if a != "--recoded"]

if len(args) != 2:
    sys.exit("Usage: python apply_patch.py <path to Launcher.exe> <patch.json> [--recoded]")

launcher_path, patch_path = args
backup_path = launcher_path + ".backup"

sha = lambda b: hashlib.sha256(b).hexdigest()

if not os.path.isfile(launcher_path):
    sys.exit(f"Launcher not found: {launcher_path}")
if not os.path.isfile(patch_path):
    sys.exit(f"Patch file not found: {patch_path}")

data = json.load(open(patch_path))
orig = open(launcher_path, "rb").read()

if len(orig) != data["original_size"] or sha(orig) != data["original_sha256"]:
    msg = "This is not the expected original launcher (size/hash mismatch). Nothing was changed."
    if os.path.exists(backup_path):
        msg += (f"\nIf it was already patched, a backup exists at {backup_path}. "
                "Restore it over the launcher and run this again.")
    sys.exit(msg)

buf = bytearray(orig)
applied = skipped = 0
for p in data["patches"]:
    if p.get("group") == "recoded" and not include_recoded:
        skipped += 1
        continue
    off, length = p["offset"], p["length"]
    if sha(bytes(buf[off:off + length])) != p["old_sha256"]:
        sys.exit(f"Unexpected bytes at 0x{off:X}. Nothing was changed.")
    buf[off:off + length] = bytes.fromhex(p["new"])
    applied += 1
buf += bytes.fromhex(data["append"])

if os.path.exists(backup_path):
    if sha(open(backup_path, "rb").read()) != data["original_sha256"]:
        sys.exit(f"{backup_path} already exists and is not the original launcher. "
                 "Move or rename it and run again. Nothing was changed.")
else:
    shutil.copy2(launcher_path, backup_path)

tmp_path = launcher_path + ".tmp"
with open(tmp_path, "wb") as f:
    f.write(buf)
os.replace(tmp_path, launcher_path)

print(f"Patched: {launcher_path} ({len(buf)} bytes)")
print(f"Applied {applied} patches; Recoded {'included' if include_recoded else 'NOT included'}"
      f" ({skipped} skipped).")
print(f"Backup:  {backup_path}")
print()
print("=" * 60)
print(f"IMPORTANT: Do NOT delete {os.path.basename(backup_path)}!")
print("It is your original launcher and is needed to restore it.")
print("=" * 60)