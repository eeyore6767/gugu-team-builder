from itertools import combinations

# =========================
# 菇菇資料
# =========================

import json
from itertools import combinations


# 讀取菇菇資料
with open("gugus.json", "r", encoding="utf-8") as f:
    gugus = json.load(f)


# 讀取關卡資料
with open("stages.json", "r", encoding="utf-8") as f:
    stages = json.load(f)


# 目前先使用第一關
current_stage = stages[0]

tasks = current_stage["tasks"]

# =========================
# 計算實際數值
# =========================

def get_stat(gugu, stat_name):

    value = gugu["stats"][stat_name]

    # 運氣技能：力量 +30
    if stat_name == "力量":
        if "運氣" in gugu["skills"]:
            value += 30

    return value


# =========================
# 任務判定
# =========================

def check_task(team, task):

    # 單體數值
    if task["type"] == "single_stat":

        for gugu in team:

            if get_stat(gugu, task["stat"]) >= task["value"]:
                return True

        return False

    # 指定數量符合條件
    elif task["type"] == "count_stat":

        count = 0

        for gugu in team:

            if get_stat(gugu, task["stat"]) >= task["value"]:
                count += 1

        return count >= task["count"]

    # 全隊總和
    elif task["type"] == "team_stat":

        total = 0

        for gugu in team:
            total += get_stat(gugu, task["stat"])

        return total >= task["value"]

    return False


# =========================
# 計算隊伍分數
# =========================

def calc_score(team):

    score = 0

    for task in tasks:

        if check_task(team, task):
            score += 1

    return score


# =========================
# 搜尋最佳隊伍
# =========================

best_team = None
best_score = -1

all_teams = []

for size in range(1, 4):
    all_teams.extend(combinations(gugus, size))

for team in all_teams:

    score = calc_score(team)

    print("========")
    print("隊伍：")

    for gugu in team:
        print(gugu["name"])

    print("完成任務數：", score)

    if score > best_score:
        best_score = score
        best_team = team


# =========================
# 顯示最佳隊伍
# =========================

print("\n====================")
print("最佳隊伍")
print("====================")

for gugu in best_team:
    print(gugu["name"])

print("完成任務數：", best_score)