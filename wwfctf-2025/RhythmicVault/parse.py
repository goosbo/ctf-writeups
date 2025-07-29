import json

RDLEVEL_PATH = "task.rdlevel"
OUTPUT_PATH = "parsed_level.txt"

def get_conditional_mapping(conditionals):
    mapping = {}
    for idx, cond in enumerate(conditionals):
        code = f"{idx}d0"
        expr = cond.get("expression", "[unknown]")
        mapping[code] = expr
    return mapping

def parse_rdlevel(path, output_path):
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # Acquire events and conditionals, depending on structure
    if isinstance(data, dict):
        events = data.get("events", data)
        conditionals = data.get("conditionals", [])
    else:
        # If your data is just a JSON list, you need to load conditionals separately
        events = data
        conditionals = []
        # You can load another file here if needed

    cond_map = get_conditional_mapping(conditionals)
    tags = {}
    lines = []
    lines.append(f"Loaded {len(events)} events.\n")

    for event in events:
        tag = event.get("tag")
        if tag is not None:
            tags.setdefault(str(tag), []).append(event)

    for tag, evlist in tags.items():
        lines.append(f"\n=== Tag {tag} ({len(evlist)} events) ===\n")
        for event in evlist:
            descrip = f'@ Bar {event.get("bar")}, Beat {event.get("beat")}, Type: {event.get("type")}'
            if event.get("type") == "TagAction":
                action = event.get("Action")
                target = event.get("Tag")
                cond = event.get("if")
                cond_str = ""
                if cond:
                    # Remove trailing quotes/handle str(int) etc.
                    cond_key = str(cond)
                    expr = cond_map.get(cond_key, f"[unknown cond: {cond_key}]")
                    cond_str = f" (if {expr})"
                lines.append(f"{descrip}: {action} tag {target}{cond_str}\n")
            elif event.get("type") == "FloatingText":
                text = event.get("text", "[no text]")
                lines.append(f"{descrip}: FloatingText: '{text}'\n")
            elif event.get("type") == "CallCustomMethod":
                method = event.get("methodName")
                lines.append(f"{descrip}: CallCustomMethod: {method}\n")
            else:
                lines.append(descrip + "\n")

    lines.append("\n=== Tag dependency map (TagA -> TagB if TagA runs TagB) ===\n")
    for ev in events:
        if ev.get("type") == "TagAction" and ev.get("Action") == "Run":
            src, dst = ev.get("tag"), ev.get("Tag")
            cond = ev.get("if")
            cond_str = ""
            if cond:
                cond_key = str(cond)
                expr = cond_map.get(cond_key, f"[unknown cond: {cond_key}]")
                cond_str = f" [if {expr}]"
            lines.append(f"{src} -> {dst}{cond_str}\n")

    with open(output_path, "w", encoding="utf-8") as outf:
        outf.writelines(lines)

if __name__ == "__main__":
    parse_rdlevel(RDLEVEL_PATH, OUTPUT_PATH)
    print(f"Done! Output saved to {OUTPUT_PATH}")
