#!/usr/bin/env python3
"""
mcs-skills: inspect and manage skills on Copilot Studio agents.

FORMAT (verified against real skills in a live environment, not guessed):

  botcomponent row
    componenttype = 9              <- NOT 13. Type 9 is a container for many kinds.
    data          = "kind: InlineAgentSkill\\ncontent: |\\n  <full SKILL.md, indented 2>"
    description   = routing text the orchestrator matches on
    schemaname    = <botschemaname>.skill.<skill-name>_<3 chars>, max 100 chars

The `content` block carries the ENTIRE SKILL.md including its front matter.

Type 9 also holds child agents (kind: AgentDialog) and tools (kind: McpTool,
kind: TaskDialog), so componenttype alone never identifies a skill. Always
discriminate on `kind`.

Usage:
  mcs_skills.py agents   --env-url URL
  mcs_skills.py assess   --env-url URL --bot-id GUID
  mcs_skills.py list     --env-url URL --bot-id GUID
  mcs_skills.py add      --env-url URL --bot-id GUID --path DIR [--dry-run]
  mcs_skills.py export   --env-url URL --bot-id GUID --out DIR
  mcs_skills.py remove   --env-url URL --bot-id GUID --name SKILL-NAME
  mcs_skills.py validate --path DIR
  mcs_skills.py package  --path DIR --out DIR

Auth: `az account get-access-token`, or set MCS_TOKEN. Optional MCS_TENANT_ID.
"""
import argparse, glob, json, os, random, re, string, subprocess, sys
import urllib.error, urllib.parse, urllib.request, zipfile

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install pyyaml")

SKILL_TYPE = 9
SKILL_KIND = "InlineAgentSkill"
MAX_SCHEMA = 100
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

KINDS = {
    "InlineAgentSkill": "skill", "AgentDialog": "child agent", "McpTool": "MCP tool",
    "TaskDialog": "tool / action", "WorkflowTool": "workflow tool",
    "KnowledgeSourceConfiguration": "knowledge", "DefaultFeedbackCollection": "settings",
    "AdaptiveDialog": "classic topic", "GptComponentMetadata": "classic agent",
}


# ------------------------------------------------------------------ auth / http

def get_token(env_url):
    tok = os.environ.get("MCS_TOKEN")
    if tok:
        return tok.strip()
    cmd = ["az", "account", "get-access-token", "--resource", env_url.rstrip("/"),
           "--query", "accessToken", "-o", "tsv"]
    tenant = os.environ.get("MCS_TENANT_ID")
    if tenant:
        cmd += ["--tenant", tenant]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if p.returncode != 0:
        sys.exit("could not get a token.\n  run:  az login\n"
                 "  or set MCS_TOKEN to a Dataverse access token.\n"
                 f"  az said: {p.stderr.strip()[:400]}")
    return p.stdout.strip()


def dv(method, env_url, path, token, body=None, extra=None):
    url = env_url.rstrip("/") + urllib.parse.quote(path, safe=":/?&=$,'()*+-_.~%@")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json",
               "OData-MaxVersion": "4.0", "OData-Version": "4.0",
               "Content-Type": "application/json; charset=utf-8"}
    if extra:
        headers.update(extra)
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body is not None else None,
        headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        try:
            txt = json.loads(txt)["error"]["message"]
        except Exception:
            pass
        return e.code, txt


def need(status, body, what):
    if status >= 400:
        sys.exit(f"{what} failed (HTTP {status}): {str(body)[:500]}")


# ------------------------------------------------------------------ skill data

def kind_of(row):
    d = (row.get("data") or "").replace("\r\n", "\n")
    for line in d.split("\n"):
        if line.startswith("kind:"):
            return line.split(":", 1)[1].strip()
    return ""


def skill_md_from_row(row):
    """Pull the SKILL.md back out of the `content: |` block."""
    d = (row.get("data") or "").replace("\r\n", "\n")
    lines = d.split("\n")
    for i, line in enumerate(lines):
        if re.match(r"^content:\s*\|-?\s*$", line):
            body = lines[i + 1:]
            out = []
            for ln in body:
                if ln.strip() == "":
                    out.append("")
                elif ln.startswith("  "):
                    out.append(ln[2:])
                else:
                    break
            return "\n".join(out).strip()
    return ""


def to_data(skill_md):
    """Build the `data` column: kind + the whole SKILL.md indented under content."""
    indented = "\n".join(("  " + ln if ln.strip() else "") for ln in skill_md.strip().split("\n"))
    return f"kind: {SKILL_KIND}\ncontent: |\n{indented}\n"


def parse_skill_md(path_or_text, is_text=False):
    text = path_or_text if is_text else open(path_or_text, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        raise ValueError("missing YAML front matter delimited by --- lines")
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"front matter is not valid YAML: {e}")
    if not isinstance(fm, dict):
        raise ValueError("front matter must be a mapping")
    name = str(fm.get("name", "")).strip()
    desc = " ".join(str(fm.get("description", "")).split())
    body = m.group(2).strip()
    if not name:
        raise ValueError("front matter is missing 'name'")
    if not desc:
        raise ValueError("front matter is missing 'description'")
    if not NAME_RE.match(name):
        raise ValueError(f"name '{name}' must be lowercase letters, numbers and single hyphens")
    if not body:
        raise ValueError("no instruction body below the front matter")
    return name, desc, body


def find_skills(path):
    if os.path.isfile(path):
        return [path]
    hits = sorted(glob.glob(os.path.join(path, "**", "SKILL.md"), recursive=True))
    return [h for h in hits if "/_" not in h]


def suffix():
    return "".join(random.choice(string.ascii_letters) for _ in range(3))


def get_bot(env_url, bot_id, token):
    st, b = dv("GET", env_url, f"/api/data/v9.2/bots({bot_id})"
               "?$select=name,schemaname,configuration,publishedon", token)
    need(st, b, "reading the agent")
    return b


def get_components(env_url, bot_id, token):
    st, b = dv("GET", env_url, "/api/data/v9.2/botcomponents?$select=name,schemaname,"
               f"componenttype,description,data&$filter=_parentbotid_value eq {bot_id}", token)
    need(st, b, "listing components")
    return b.get("value", [])


def get_skills(env_url, bot_id, token):
    return [c for c in get_components(env_url, bot_id, token)
            if c["componenttype"] == SKILL_TYPE and kind_of(c) == SKILL_KIND]


def detect_shape(bot):
    cfg = bot.get("configuration") or ""
    try:
        cfg = json.loads(cfg) if isinstance(cfg, str) else cfg
    except Exception:
        cfg = {}
    rec = ((cfg.get("recognizer") or {}).get("$kind") or "")
    if rec == "CLICopilotRecognizer":
        return 2, rec, "modern, GitHub Copilot harness"
    if rec:
        return 1, rec, "classic, Standard harness"
    return 0, rec or "(none)", "unknown"


# ------------------------------------------------------------------ commands

def cmd_agents(a):
    token = get_token(a.env_url)
    st, b = dv("GET", a.env_url,
               "/api/data/v9.2/bots?$select=name,botid&$filter=statecode eq 0", token)
    need(st, b, "listing agents")
    rows = sorted(b.get("value", []), key=lambda r: (r.get("name") or "").lower())
    print(f"{len(rows)} agent(s) in {a.env_url}\n")
    for r in rows:
        print(f"  {r['botid']}  {r.get('name')}")
    return 0


def cmd_assess(a):
    token = get_token(a.env_url)
    bot = get_bot(a.env_url, a.bot_id, token)
    comps = get_components(a.env_url, a.bot_id, token)
    shape, rec, label = detect_shape(bot)

    tally = {}
    for c in comps:
        k = kind_of(c) or "(none)"
        tally[k] = tally.get(k, 0) + 1

    print(f"agent      {bot.get('name')}")
    print(f"schema     {bot.get('schemaname')}")
    print(f"published  {bot.get('publishedon') or '(never)'}")
    print(f"recognizer {rec}")
    print(f"shape      {shape}  ({label})")
    print(f"\ncomponents ({len(comps)}), by kind")
    for k in sorted(tally):
        print(f"  {k:<30} {tally[k]:>3}   {KINDS.get(k, '')}")

    skills = tally.get(SKILL_KIND, 0)
    print("\nverdict")
    if shape == 2:
        print("  Modern agent. Skills are supported.")
        print(f"  {skills} skill(s)." if skills else "  No skills yet.")
        ca = tally.get("AgentDialog", 0)
        if ca and skills:
            print(f"  {ca} child agent(s) alongside {skills} skill(s). Check for overlap:")
            print("  child agents are specialist domains, skills are situational procedures.")
    elif shape == 1:
        print("  Classic agent on the Standard harness. Skills are not available here.")
        print("  Upgrade with the official plugin, then verify:")
        print("    /plugin marketplace add microsoft/copilot-studio-plugin")
        print("    /plugin install mcs-assistant@copilot-studio-plugin")
        print("    /mcs-assistant:migrate Upgrade this agent to the GitHub Copilot harness: <url>")
    else:
        print("  Shape undetermined. Inspect the agent manually.")
    return 0


def cmd_list(a):
    token = get_token(a.env_url)
    skills = get_skills(a.env_url, a.bot_id, token)
    if not skills:
        print("no skills on this agent")
        return 0
    print(f"{len(skills)} skill(s)\n")
    for s in sorted(skills, key=lambda r: r["name"] or ""):
        md = skill_md_from_row(s)
        print(f"  {s['name']}   ({len(md)} chars)")
        print(f"      {(s.get('description') or '')[:105]}")
    return 0


def cmd_add(a):
    files = find_skills(a.path)
    if not files:
        sys.exit(f"no SKILL.md found under {a.path}")
    parsed, bad = [], 0
    for f in files:
        try:
            name, desc, _ = parse_skill_md(f)
            parsed.append((f, name, desc, open(f, encoding="utf-8").read().strip()))
        except ValueError as e:
            print(f"  INVALID  {f}\n           {e}")
            bad += 1
    if bad:
        sys.exit(f"\n{bad} file(s) invalid. Nothing was sent.")

    if a.dry_run:
        print(f"{len(parsed)} skill(s) would be written:\n")
        for _, n, _, md in parsed:
            print(f"  {n:<44} {len(md):>6} chars")
        return 0

    token = get_token(a.env_url)
    bot = get_bot(a.env_url, a.bot_id, token)
    shape, _, _ = detect_shape(bot)
    if shape == 1:
        sys.exit("this is a classic Standard-harness agent. Skills are not supported.\n"
                 "Upgrade it first, see docs/02-conversion-playbook.md.")
    botschema = bot["schemaname"]
    existing = {c["name"]: c for c in get_skills(a.env_url, a.bot_id, token)}

    print(f"agent {bot.get('name')}\n")
    for _, name, desc, md in parsed:
        data = to_data(md)
        if name in existing:
            cid = existing[name]["botcomponentid"]
            st, b = dv("PATCH", a.env_url, f"/api/data/v9.2/botcomponents({cid})", token,
                       {"name": name, "description": desc, "data": data}, {"If-Match": "*"})
            ok = st in (200, 204)
            print(f"  {'updated' if ok else 'FAILED':<8} {name:<44}{'' if ok else str(b)[:180]}")
        else:
            schema = f"{botschema}.skill.{name}_{suffix()}"
            if len(schema) > MAX_SCHEMA:
                print(f"  SKIPPED  {name:<44}schemaname would be {len(schema)} chars, "
                      f"max {MAX_SCHEMA}. Shorten the skill name.")
                continue
            st, b = dv("POST", a.env_url, "/api/data/v9.2/botcomponents", token, {
                "name": name, "schemaname": schema, "componenttype": SKILL_TYPE,
                "description": desc, "data": data,
                "parentbotid@odata.bind": f"/bots({a.bot_id})",
            }, {"Prefer": "return=representation"})
            ok = st in (200, 201)
            print(f"  {'created' if ok else 'FAILED':<8} {name:<44}{'' if ok else str(b)[:180]}")

    print("\nConfirm from the server, do not trust the line above:")
    print(f"  python3 {os.path.basename(__file__)} list --env-url {a.env_url} --bot-id {a.bot_id}")
    return 0


def cmd_export(a):
    token = get_token(a.env_url)
    skills = get_skills(a.env_url, a.bot_id, token)
    if not skills:
        print("no skills to export")
        return 0
    os.makedirs(a.out, exist_ok=True)
    for s in skills:
        md = skill_md_from_row(s)
        if not md:
            print(f"  SKIPPED {s['name']}: could not read the content block")
            continue
        d = os.path.join(a.out, s["name"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(md + "\n")
        print(f"  wrote {s['name']}/SKILL.md  ({len(md)} chars)")
    print(f"\n{len(skills)} skill(s) exported to {a.out}")
    return 0


def cmd_remove(a):
    token = get_token(a.env_url)
    hit = [s for s in get_skills(a.env_url, a.bot_id, token) if s["name"] == a.name]
    if not hit:
        sys.exit(f"no skill named '{a.name}'")
    st, b = dv("DELETE", a.env_url,
               f"/api/data/v9.2/botcomponents({hit[0]['botcomponentid']})", token)
    need(st, b, "deleting the skill")
    print(f"deleted {a.name}")
    return 0


def cmd_validate(a):
    files = find_skills(a.path)
    if not files:
        sys.exit(f"no SKILL.md found under {a.path}")
    bad = 0
    for f in files:
        try:
            n, d, body = parse_skill_md(f)
            notes = []
            if len(d) < 60:
                notes.append("description is short, the orchestrator routes on it")
            if len(f"{'x'*40}.skill.{n}_abc") > MAX_SCHEMA:
                notes.append("name may overflow the 100 char schemaname limit")
            print(f"  ok       {n:<42} body {len(body):>6}  desc {len(d):>4}"
                  + ("  WARN " + "; ".join(notes) if notes else ""))
        except ValueError as e:
            print(f"  INVALID  {f}\n           {e}")
            bad += 1
    print(f"\n{len(files)-bad}/{len(files)} valid")
    return 1 if bad else 0


def cmd_package(a):
    files = find_skills(a.path)
    if not files:
        sys.exit(f"no SKILL.md found under {a.path}")
    os.makedirs(a.out, exist_ok=True)
    for f in files:
        try:
            name, _, _ = parse_skill_md(f)
        except ValueError as e:
            sys.exit(f"refusing to package invalid skill {f}: {e}")
        folder = os.path.dirname(os.path.abspath(f))
        z = os.path.join(a.out, f"{name}.zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, fns in os.walk(folder):
                for fn in fns:
                    full = os.path.join(root, fn)
                    zf.write(full, os.path.relpath(full, folder))
        with zipfile.ZipFile(z) as zf:
            assert "SKILL.md" in zf.namelist(), f"{z}: SKILL.md must be at the archive root"
            n = len(zf.namelist())
        print(f"  {name:<42} {os.path.getsize(z):>8} bytes  {n} entries")
    print(f"\n{len(files)} zip(s) in {a.out}")
    return 0


def main():
    p = argparse.ArgumentParser(description="Inspect and manage Copilot Studio agent skills.",
                                epilog="Auth: az login, or set MCS_TOKEN.")
    sub = p.add_subparsers(dest="cmd", required=True)

    def env(sp, bot=True):
        sp.add_argument("--env-url", required=True)
        if bot:
            sp.add_argument("--bot-id", required=True)

    env(sub.add_parser("agents", help="list agents in an environment"), bot=False)
    env(sub.add_parser("assess", help="report shape and components by kind"))
    env(sub.add_parser("list", help="list skills"))
    sp = sub.add_parser("add", help="create or update skills from SKILL.md files"); env(sp)
    sp.add_argument("--path", required=True); sp.add_argument("--dry-run", action="store_true")
    sp = sub.add_parser("export", help="download skills as SKILL.md"); env(sp)
    sp.add_argument("--out", required=True)
    sp = sub.add_parser("remove", help="delete a skill"); env(sp)
    sp.add_argument("--name", required=True)
    sp = sub.add_parser("validate", help="check SKILL.md files offline")
    sp.add_argument("--path", required=True)
    sp = sub.add_parser("package", help="build one zip per skill")
    sp.add_argument("--path", required=True); sp.add_argument("--out", required=True)

    a = p.parse_args()
    return {"agents": cmd_agents, "assess": cmd_assess, "list": cmd_list, "add": cmd_add,
            "export": cmd_export, "remove": cmd_remove, "validate": cmd_validate,
            "package": cmd_package}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
