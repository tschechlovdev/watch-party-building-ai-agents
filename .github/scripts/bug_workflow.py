#!/usr/bin/env python3
"""Helpers for bug-workflows/issue-<n>-workflow.md, used by the Bob GitHub Actions.

Standard library only, so it runs on a bare GitHub runner.

Commands:
  init <issue.json> <doc>            create the doc from templates/bugfix-workflow.md
  get <doc> <key>                    print one front matter value
  set <doc> <key> <value>            set one front matter value
  section <doc> <heading>            print the body of a "## heading" section
  triage-comment <doc> <trusted>     print the issue comment for the triage result
  pr-body <doc> <issue> <gate.log> [eng.md] [rev.md]  print the PR body
"""

import json
import re
import sys
from pathlib import Path

TEMPLATE = Path("templates/bugfix-workflow.md")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def front_matter(text):
    m = FM_RE.match(text)
    if not m:
        raise SystemExit("workflow doc has no front matter")
    return m


def get(text, key):
    lines = front_matter(text).group(1).splitlines()
    for i, line in enumerate(lines):
        k, sep, v = line.partition(":")
        if sep and k.strip() == key:
            v = v.strip()
            if not v:  # YAML block list: "key:\n  - a\n  - b"
                items = []
                for nxt in lines[i + 1:]:
                    if not nxt.lstrip().startswith("- "):
                        break
                    items.append(nxt.lstrip()[2:].strip().strip('"').strip("'"))
                return "[" + ", ".join(items) + "]" if items else ""
            if v.startswith('"'):
                try:
                    return json.loads(v)
                except ValueError:
                    pass
            v = v.split(" #", 1)[0].strip()
            return v.strip('"').strip("'")
    return ""


def set_value(text, key, value):
    m = front_matter(text)
    lines = m.group(1).splitlines()
    rendered = f"{key}: {value}"
    for i, line in enumerate(lines):
        if line.partition(":")[0].strip() == key:
            lines[i] = rendered
            break
    else:
        lines.append(rendered)
    return "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]


def section(text, heading):
    """Body of '## heading' up to the next '## ' heading or '---' separator."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower().startswith(heading.lower())
            continue
        if inside and line.strip() == "---":
            break
        if inside:
            out.append(line)
    body = "\n".join(out)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)  # drop template hints
    body = re.sub(r"^_Filled in by .*_$", "", body, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def quote(s):
    return json.dumps(s, ensure_ascii=False)


def cmd_init(issue_json, doc):
    issue = json.loads(Path(issue_json).read_text())
    number, title = issue["number"], issue.get("title") or ""
    body = issue.get("body") or "(no description)"
    labels = ", ".join(lbl["name"] for lbl in issue.get("labels", []))

    text = TEMPLATE.read_text()
    text = set_value(text, "issue", str(number))
    text = set_value(text, "title", quote(title))
    text = text.replace("{{title}}", f"#{number}")

    # Blockquote every line so nothing in the body can open a new section or
    # close the marker comment.
    quoted = "\n".join("> " + line.replace("-->", "-- >") for line in
                       [f"**Title:** {title}", f"**Labels:** {labels}", ""] +
                       body.splitlines())
    text = text.replace("<!-- ISSUE-START -->\n<!-- ISSUE-END -->",
                        f"<!-- ISSUE-START -->\n{quoted}\n<!-- ISSUE-END -->")
    Path(doc).parent.mkdir(parents=True, exist_ok=True)
    Path(doc).write_text(text)


def cmd_triage_comment(doc, trusted):
    text = Path(doc).read_text()
    f = {k: get(text, k) for k in
         ("confidence", "criticality", "complexity", "needs-info",
          "autofix-eligible", "files")}
    if f["needs-info"] == "true":
        nxt = ("**Next step:** Bob needs more information. Please answer the "
               "questions under *Questions for the Reporter* above.")
    elif f["autofix-eligible"] == "true" and trusted == "true":
        nxt = ("**Next step:** this looks like a small, clear fix. Bob is starting "
               "the Engineer -> Reviewer pipeline now and will open a PR.")
    elif f["autofix-eligible"] == "true":
        nxt = ("**Next step:** this looks like a small, clear fix. A maintainer can "
               "add the `bob-fix` label to let Bob open a PR.")
    else:
        nxt = ("**Next step:** this needs a human decision. Add the `bob-fix` label "
               "to let Bob attempt the recommended fix, or fix it manually.")

    print(f"""## 🤖 Bob bug triage

| Criticality | Complexity | Confidence | Auto-fix eligible | Files |
|---|---|---|---|---|
| {f['criticality']} | {f['complexity']} | {f['confidence']} | {f['autofix-eligible']} | `{f['files']}` |

{section(text, 'Triage')}

---
{nxt}

<sub>Generated by Bob (`bug-triage-agent`) in GitHub Actions. Analysis only, no code was changed.</sub>""")


def bob_message(path):
    """Bob's final message for a phase, without the completion marker line."""
    if not path or not Path(path).is_file():
        return ""
    lines = [ln for ln in Path(path).read_text().splitlines()
             if not re.fullmatch(r"\s*[A-Z_]+_COMPLETE\s*", ln)]
    return "\n".join(lines).strip()


def malformed(text):
    """Top-level sections that appear more than once (a broken agent edit)."""
    heads = re.findall(r"^## (.+)$", text, flags=re.M)
    return sorted({h for h in heads if heads.count(h) > 1})


def cmd_pr_body(doc, issue, gate_log, eng_msg="", rev_msg=""):
    text = Path(doc).read_text()
    triage = section(text, "Triage")
    # Prefer Bob's own final messages: they are always complete, even when an
    # agent's in-place edit of the workflow document went wrong.
    impl = bob_message(eng_msg) or section(text, "Implementation Notes")
    review = bob_message(rev_msg) or section(text, "Review Feedback")
    log = Path(gate_log).read_text()[-6000:] if Path(gate_log).exists() else "n/a"
    dup = malformed(text)
    note = (f"\n> ⚠️ The trace document has duplicated sections ({', '.join(dup)}). "
            "The summaries above come from Bob's final messages.\n" if dup else "")
    print(f"""Fixes #{issue}

Automated bugfix by the Bob SDLC team: **Triage -> Engineer -> Reviewer**, then an
independent CI gate (no new test failures, lint, build).

<details><summary>🔍 Triage</summary>

{triage}

</details>

## 🛠️ Engineer

{impl}

## ✅ Reviewer

{review}

<details><summary>🧪 CI gate output</summary>

```
{log}
```

</details>

Full trace: `{doc}`
{note}
🤖 Generated with Bob in GitHub Actions""")


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    cmd, args = argv[1], argv[2:]
    if cmd == "init":
        cmd_init(*args)
    elif cmd == "get":
        print(get(Path(args[0]).read_text(), args[1]))
    elif cmd == "set":
        p = Path(args[0])
        p.write_text(set_value(p.read_text(), args[1], args[2]))
    elif cmd == "section":
        print(section(Path(args[0]).read_text(), args[1]))
    elif cmd == "triage-comment":
        cmd_triage_comment(*args)
    elif cmd == "pr-body":
        cmd_pr_body(*args)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
