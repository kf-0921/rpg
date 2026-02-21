import os
import re
import json
import csv


# ------------ 通用：解析單一物品（非 basic.txt 用）------------

def parse_item(lines, file_name, category):
    item = {
        "file": os.path.basename(file_name),
        "category": category,
        "name": lines[0].strip(),
        "id": "",
        "level_required": 0,
        "stats": {},
        "buff": "",
        "job_required": "",
        "resources": []
    }

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        if line.startswith("物品代號:"):
            item["id"] = line.split(":", 1)[1].strip()
            continue

        if line.startswith("等級需求:"):
            try:
                item["level_required"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
            continue

        if "套裝效果:" in line:
            item["buff"] = line.split("套裝效果:", 1)[1].strip()
            continue

        if "符文共鳴:" in line:
            item["buff"] = line.split("符文共鳴:", 1)[1].strip()
            continue

        if line.startswith("職業需求:"):
            item["job_required"] = line.split(":", 1)[1].strip()
            continue

        if "~" in line and (":" in line or "：" in line):
            m = re.search(r"([^:：]+)[:：](\d+)~(\d+)", line)
            if m:
                stat_name = m.group(1).strip()
                item["stats"][f"{stat_name}_min"] = int(m.group(2))
                item["stats"][f"{stat_name}_max"] = int(m.group(3))
            continue

        if "x" in line:
            m = re.match(r"(.+?)x(\d+)", line)
            if m:
                item["resources"].append({
                    "name": m.group(1).strip(),
                    "amount": int(m.group(2))
                })
            continue

    return item


# ------------ basic.txt 專用：4 段品質值解析 ------------

def parse_four_vals(raw_str):
    """
    把 "4,6,8,10" 解析成 [4,6,8,10]。
    處理漏逗號的情況，例如 "20,26,3136" -> [20,26,31,36]
    """
    parts = [p.strip() for p in raw_str.split(",")]
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            pass

    # 修復：只有 3 個值且最後一個是 4 位數，代表兩個數字被合併了
    if len(nums) == 3 and nums[-1] >= 1000:
        s = str(nums[-1])
        mid = len(s) // 2
        try:
            nums[-1] = int(s[:mid])
            nums.append(int(s[mid:]))
        except (ValueError, IndexError):
            pass

    # 補齊到 4 個
    while len(nums) < 4:
        nums.append(nums[-1] if nums else 0)
    return nums[:4]


def parse_basic_item(lines, file_name, category):
    """
    basic.txt 專用 parser。
    攻擊力 / 血量 / 防禦力 存成 _vals 陣列，對應品質：
    index 0=稀有  1=史詩  2=神話  3=傳奇
    例：攻擊力:4,6,8,10 → stats["攻擊力_vals"] = [4, 6, 8, 10]
    """
    item = {
        "file": os.path.basename(file_name),
        "category": category,
        "name": lines[0].strip(),
        "id": "",
        "level_required": 0,
        "stats": {},
        "buff": "",
        "job_required": "",
        "resources": []
    }

    STAT_KEYWORDS = {"攻擊力", "血量", "防禦力"}

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        if line.startswith("物品代號:"):
            item["id"] = line.split(":", 1)[1].strip()
            continue

        if line.startswith("等級需求:"):
            try:
                item["level_required"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
            continue

        # 4 段品質數值行：攻擊力:4,6,8,10
        if ":" in line:
            colon_idx = line.index(":")
            stat_name = line[:colon_idx].strip()
            raw_vals = line[colon_idx + 1:].strip()
            if stat_name in STAT_KEYWORDS:
                item["stats"][f"{stat_name}_vals"] = parse_four_vals(raw_vals)
                continue

        # 素材：原木x20
        m = re.match(r"(.+?)x(\d+)\s*$", line)
        if m:
            item["resources"].append({
                "name": m.group(1).strip(),
                "amount": int(m.group(2))
            })

    return item


# ------------ basic.txt 主解析 ------------

def parse_basic_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    results = []
    section_re = re.compile(r"^#(主武器|副武器|頭盔|上衣|下裝|鞋子)\s*$", re.M)
    parts = section_re.split(content)
    item_split_re = re.compile(r"(?=^[^\n]+?\n物品代號:)", re.M)

    for i in range(1, len(parts), 2):
        cat_name = parts[i].strip()
        cat_block = parts[i + 1]

        raw_items = item_split_re.split(cat_block)
        for raw in raw_items:
            raw = raw.strip()
            if not raw:
                continue
            lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            if len(lines) < 2:
                continue
            # ★ 改用 basic 專用 parser
            item = parse_basic_item(lines, path, cat_name)
            results.append(item)

    return results


# ------------ 其他 txt ------------

def get_category_from_content(path, content):
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            continue
        return line
    return os.path.basename(path).replace(".txt", "")


def parse_generic_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    category = get_category_from_content(path, content)
    results = []
    item_split_re = re.compile(r"(?=^[^\n]+?\n物品代號:)", re.M)
    raw_items = item_split_re.split(content)

    for raw in raw_items:
        raw = raw.strip()
        if not raw:
            continue
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        item = parse_item(lines, path, category)
        results.append(item)

    return results


# ------------ 主流程 ------------

def parse_all_txt_in_folder(folder="."):
    all_items = []
    txt_files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    print(f"發現 txt 檔案：{txt_files}")

    for filename in txt_files:
        path = os.path.join(folder, filename)
        if filename == "basic.txt":
            print("解析 basic.txt（4 段品質模式）...")
            items = parse_basic_file(path)
        else:
            print(f"解析 {filename}...")
            items = parse_generic_file(path)
        all_items.extend(items)

    return all_items


def main():
    equipment = parse_all_txt_in_folder(".")

    with open("complete_equipment.json", "w", encoding="utf-8") as f:
        json.dump(equipment, f, ensure_ascii=False, indent=2)

    with open("complete_equipment.csv", "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["來源檔案", "分類", "物品名稱", "物品ID",
                      "等級需求", "套裝效果", "職業需求", "屬性", "素材"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in equipment:
            row = {
                "來源檔案": item["file"],
                "分類": item["category"],
                "物品名稱": item["name"],
                "物品ID": item["id"],
                "等級需求": item["level_required"],
                "套裝效果": item["buff"],
                "職業需求": item["job_required"],
                "屬性": json.dumps(item["stats"], ensure_ascii=False),
                "素材": "; ".join(f"{r['name']}x{r['amount']}" for r in item["resources"]),
            }
            writer.writerow(row)

    print(
        f"完成！共解析 {len(equipment)} 個物品，已輸出 complete_equipment.json / complete_equipment.csv")


if __name__ == "__main__":
    main()
