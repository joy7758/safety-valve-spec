#!/usr/bin/env python3
import subprocess

def git_diff_names(base="origin/main...HEAD"):
  out=subprocess.check_output(["git","diff","--name-only",base], text=True)
  return [x.strip() for x in out.splitlines() if x.strip()]

def main():
  # Works in PR context; fallback to HEAD~1 if origin/main not available
  bases=["origin/main...HEAD","HEAD~1...HEAD"]
  files=[]
  selected_base = None
  for b in bases:
    try:
      files=git_diff_names(b)
      selected_base = b
      break
    except Exception:
      continue

  if selected_base is None:
    print("FAIL: unable to determine git diff base")
    return 1

  touched_spec = any(f.startswith("spec/") or f.startswith("schemas/") for f in files)
  if not touched_spec:
    print("OK: no spec/schema changes detected")
    return 0

  # RFC file created?
  rfc_new = subprocess.check_output(["git","diff","--name-status",selected_base], text=True, errors="ignore")
  created = [line.split("\t",1)[1].strip() for line in rfc_new.splitlines() if line.startswith("A\tRFC/")]
  created = [c for c in created if not c.endswith("0000-template.md") and not c.endswith("README.md")]

  if created:
    print("OK: RFC present for spec/schema change:", created)
    return 0

  print("FAIL: spec/ or schemas/ changed but no new RFC added in RFC/")
  print("Hint: create RFC/000X-<title>.md based on RFC/0000-template.md")
  return 1

if __name__ == "__main__":
  raise SystemExit(main())
