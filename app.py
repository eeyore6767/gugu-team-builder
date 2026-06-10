import json
import os
from itertools import combinations
import streamlit as st


# =========================
# 基本設定
# =========================

GUGUS_FILE = "gugus.json"
STAGES_FILE = "stages.json"
SKILLS_FILE = "skills.json"

GUGU_IMAGE_DIR = "images/gugus"
SKILL_IMAGE_DIR = "images/skills"

os.makedirs(GUGU_IMAGE_DIR, exist_ok=True)
os.makedirs(SKILL_IMAGE_DIR, exist_ok=True)


# =========================
# 工具函式
# =========================

def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        save_json(file_path, default_data)
        return default_data

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_uploaded_image(uploaded_file, folder, name):
    if uploaded_file is None:
        return ""

    ext = uploaded_file.name.split(".")[-1].lower()

    if ext not in ["png", "jpg", "jpeg", "webp"]:
        st.error("圖片格式只支援 png、jpg、jpeg、webp")
        return ""

    safe_name = name.replace("/", "_").replace("\\", "_").strip()
    file_path = os.path.join(folder, f"{safe_name}.{ext}")

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


def get_skill_icon(skill_name):
    for skill in skills:
        if skill["name"] == skill_name:
            return skill.get("icon", "")
    return ""


def write_all_data():
    save_json(GUGUS_FILE, gugus)
    save_json(STAGES_FILE, stages)
    save_json(SKILLS_FILE, skills)


# =========================
# 讀取資料
# =========================

default_skills = [
    {"name": "運氣", "icon": ""},
    {"name": "碎岩", "icon": ""},
    {"name": "武士", "icon": ""},
    {"name": "白色", "icon": ""},
    {"name": "游泳", "icon": ""}
]

gugus = load_json(GUGUS_FILE, [])
stages = load_json(STAGES_FILE, [])
skills = load_json(SKILLS_FILE, default_skills)

skill_list = [skill["name"] for skill in skills]


# =========================
# 網站標題
# =========================

st.title("菇菇組隊模擬器")


# =========================
# 技能管理
# =========================

st.header("技能管理")

with st.form("add_skill_form"):
    new_skill_name = st.text_input("新增技能名稱")
    new_skill_icon = st.file_uploader(
        "技能圖示",
        type=["png", "jpg", "jpeg", "webp"],
        key="new_skill_icon"
    )

    add_skill_submit = st.form_submit_button("新增技能")

    if add_skill_submit:
        if not new_skill_name.strip():
            st.error("請輸入技能名稱")
        elif new_skill_name in skill_list:
            st.error("這個技能已經存在")
        else:
            icon_path = save_uploaded_image(
                new_skill_icon,
                SKILL_IMAGE_DIR,
                new_skill_name
            )

            skills.append({
                "name": new_skill_name.strip(),
                "icon": icon_path
            })

            save_json(SKILLS_FILE, skills)
            st.success("技能已新增")
            st.rerun()


st.subheader("技能總覽")

for skill_index, skill in enumerate(skills):
    with st.expander(skill["name"]):
        edit_skill_name = st.text_input(
            "技能名稱",
            value=skill["name"],
            key=f"edit_skill_name_{skill_index}"
        )

        if skill.get("icon") and os.path.exists(skill["icon"]):
            st.image(skill["icon"], width=64)

        uploaded_skill_icon = st.file_uploader(
            "更換技能圖示",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"replace_skill_icon_{skill_index}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("儲存技能", key=f"save_skill_{skill_index}"):
                old_name = skill["name"]

                icon_path = skill.get("icon", "")

                if uploaded_skill_icon is not None:
                    icon_path = save_uploaded_image(
                        uploaded_skill_icon,
                        SKILL_IMAGE_DIR,
                        edit_skill_name
                    )

                skills[skill_index] = {
                    "name": edit_skill_name.strip(),
                    "icon": icon_path
                }

                # 同步更新菇菇身上的技能名稱
                for gugu in gugus:
                    gugu["skills"] = [
                        edit_skill_name.strip() if s == old_name else s
                        for s in gugu["skills"]
                    ]

                # 同步更新任務技能名稱
                for stage in stages:
                    for task in stage["tasks"]:
                        if task.get("type") == "single_skill" and task.get("skill") == old_name:
                            task["skill"] = edit_skill_name.strip()

                write_all_data()
                st.success("技能已儲存")
                st.rerun()

        with col2:
            if st.button("刪除技能", key=f"delete_skill_{skill_index}"):
                deleted_name = skill["name"]
                skills.pop(skill_index)

                for gugu in gugus:
                    gugu["skills"] = [
                        s for s in gugu["skills"]
                        if s != deleted_name
                    ]

                write_all_data()
                st.warning("技能已刪除")
                st.rerun()


# 重新整理技能列表
skill_list = [skill["name"] for skill in skills]


# =========================
# 新增菇菇
# =========================

st.header("新增菇菇")

with st.form("add_gugu_form"):
    name = st.text_input("名稱")

    power = st.number_input("力量", min_value=0, value=50)
    wisdom = st.number_input("智慧", min_value=0, value=50)
    speed = st.number_input("速度", min_value=0, value=50)

    selected_skills = st.multiselect(
        "技能",
        skill_list
    )

    gugu_image = st.file_uploader(
        "菇菇圖片",
        type=["png", "jpg", "jpeg", "webp"],
        key="new_gugu_image"
    )

    submitted = st.form_submit_button("新增菇菇")

    if submitted:
        if not name.strip():
            st.error("請輸入菇菇名稱")
        else:
            image_path = save_uploaded_image(
                gugu_image,
                GUGU_IMAGE_DIR,
                name
            )

            new_gugu = {
                "name": name.strip(),
                "stats": {
                    "力量": power,
                    "智慧": wisdom,
                    "速度": speed
                },
                "skills": selected_skills,
                "image": image_path
            }

            gugus.append(new_gugu)
            save_json(GUGUS_FILE, gugus)

            st.success(f"{name} 已新增")
            st.rerun()


# =========================
# 菇菇總覽
# =========================

st.header("菇菇總覽")

for index, gugu in enumerate(gugus):
    with st.expander(gugu["name"]):
        if gugu.get("image") and os.path.exists(gugu["image"]):
            st.image(gugu["image"], width=120)

        edit_name = st.text_input(
            "名稱",
            value=gugu["name"],
            key=f"name_{index}"
        )

        edit_power = st.number_input(
            "力量",
            min_value=0,
            value=gugu["stats"]["力量"],
            key=f"power_{index}"
        )

        edit_wisdom = st.number_input(
            "智慧",
            min_value=0,
            value=gugu["stats"]["智慧"],
            key=f"wisdom_{index}"
        )

        edit_speed = st.number_input(
            "速度",
            min_value=0,
            value=gugu["stats"]["速度"],
            key=f"speed_{index}"
        )

        edit_skills = st.multiselect(
            "技能",
            skill_list,
            default=[
                s for s in gugu["skills"]
                if s in skill_list
            ],
            key=f"skills_{index}"
        )

        st.write("技能圖示")
        if edit_skills:
            cols = st.columns(5)
            for i, skill_name in enumerate(edit_skills):
                with cols[i % 5]:
                    icon_path = get_skill_icon(skill_name)

                    if icon_path and os.path.exists(icon_path):
                        st.image(icon_path, width=48)

                    st.caption(skill_name)

        uploaded_gugu_image = st.file_uploader(
            "更換菇菇圖片",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"replace_gugu_image_{index}"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("儲存", key=f"save_{index}"):
                image_path = gugu.get("image", "")

                if uploaded_gugu_image is not None:
                    image_path = save_uploaded_image(
                        uploaded_gugu_image,
                        GUGU_IMAGE_DIR,
                        edit_name
                    )

                gugus[index] = {
                    "name": edit_name.strip(),
                    "stats": {
                        "力量": edit_power,
                        "智慧": edit_wisdom,
                        "速度": edit_speed
                    },
                    "skills": edit_skills,
                    "image": image_path
                }

                save_json(GUGUS_FILE, gugus)

                st.success("已儲存")
                st.rerun()

        with col2:
            if st.button("刪除", key=f"delete_{index}"):
                gugus.pop(index)
                save_json(GUGUS_FILE, gugus)

                st.warning("已刪除")
                st.rerun()


# =========================
# 新增關卡
# =========================

st.header("新增關卡")

with st.form("add_stage_form"):
    new_stage_name = st.text_input("關卡名稱")
    stage_submit = st.form_submit_button("新增關卡")

    if stage_submit:
        if not new_stage_name.strip():
            st.error("請輸入關卡名稱")
        else:
            new_stage = {
                "name": new_stage_name.strip(),
                "tasks": []
            }

            stages.append(new_stage)
            save_json(STAGES_FILE, stages)

            st.success(f"{new_stage_name} 已新增")
            st.rerun()


# =========================
# 關卡任務管理
# =========================

st.header("關卡任務管理")

task_types = [
    "single_stat",
    "count_stat",
    "team_stat",
    "single_skill"
]

stats = ["力量", "智慧", "速度"]

for stage_index, stage in enumerate(stages):
    with st.expander(stage["name"]):
        st.subheader("目前任務")

        for task_index, task in enumerate(stage["tasks"]):
            st.markdown(f"### 任務 {task_index + 1}")

            edit_task_name = st.text_input(
                "任務名稱",
                value=task["name"],
                key=f"task_name_{stage_index}_{task_index}"
            )

            edit_task_type = st.selectbox(
                "任務類型",
                task_types,
                index=task_types.index(task["type"]),
                key=f"type_{stage_index}_{task_index}"
            )

            edit_stat = "力量"

            if edit_task_type != "single_skill":
                edit_stat = st.selectbox(
                    "數值",
                    stats,
                    index=stats.index(task.get("stat", "力量")),
                    key=f"stat_{stage_index}_{task_index}"
                )

            edit_skill = ""

            if edit_task_type == "single_skill":
                edit_skill = st.selectbox(
                    "技能",
                    skill_list,
                    index=skill_list.index(
                        task.get("skill", skill_list[0])
                    ) if skill_list and task.get("skill") in skill_list else 0,
                    key=f"skill_{stage_index}_{task_index}"
                )

            edit_value = 0

            if edit_task_type != "single_skill":
                edit_value = st.number_input(
                    "需求數值",
                    min_value=0,
                    value=task.get("value", 50),
                    key=f"value_{stage_index}_{task_index}"
                )

            edit_count = 1

            if edit_task_type == "count_stat":
                edit_count = st.number_input(
                    "需求人數",
                    min_value=1,
                    value=task.get("count", 2),
                    key=f"count_{stage_index}_{task_index}"
                )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "儲存任務",
                    key=f"save_task_{stage_index}_{task_index}"
                ):
                    updated_task = {
                        "name": edit_task_name.strip(),
                        "type": edit_task_type
                    }

                    if edit_task_type != "single_skill":
                        updated_task["stat"] = edit_stat
                        updated_task["value"] = edit_value

                    if edit_task_type == "count_stat":
                        updated_task["count"] = edit_count

                    if edit_task_type == "single_skill":
                        updated_task["skill"] = edit_skill

                    stages[stage_index]["tasks"][task_index] = updated_task
                    save_json(STAGES_FILE, stages)

                    st.success("任務已儲存")
                    st.rerun()

            with col2:
                if st.button(
                    "刪除任務",
                    key=f"delete_task_{stage_index}_{task_index}"
                ):
                    stages[stage_index]["tasks"].pop(task_index)
                    save_json(STAGES_FILE, stages)

                    st.warning("任務已刪除")
                    st.rerun()

            st.divider()

        st.subheader("新增任務")

        with st.form(f"add_task_form_{stage_index}"):
            new_task_name = st.text_input("任務名稱")

            new_task_type = st.selectbox(
                "任務類型",
                task_types
            )

            new_task_stat = "力量"

            if new_task_type != "single_skill":
                new_task_stat = st.selectbox(
                    "數值",
                    stats
                )

            new_task_skill = ""

            if new_task_type == "single_skill":
                if skill_list:
                    new_task_skill = st.selectbox(
                        "技能",
                        skill_list
                    )
                else:
                    st.warning("請先新增技能")

            new_task_value = 0

            if new_task_type != "single_skill":
                new_task_value = st.number_input(
                    "需求數值",
                    min_value=0,
                    value=50
                )

            new_task_count = 2

            if new_task_type == "count_stat":
                new_task_count = st.number_input(
                    "需求人數",
                    min_value=1,
                    value=2
                )

            add_task_submit = st.form_submit_button("新增任務")

            if add_task_submit:
                new_task = {
                    "name": new_task_name.strip(),
                    "type": new_task_type
                }

                if new_task_type != "single_skill":
                    new_task["stat"] = new_task_stat
                    new_task["value"] = new_task_value

                if new_task_type == "count_stat":
                    new_task["count"] = new_task_count

                if new_task_type == "single_skill":
                    new_task["skill"] = new_task_skill

                stages[stage_index]["tasks"].append(new_task)
                save_json(STAGES_FILE, stages)

                st.success("任務已新增")
                st.rerun()


# =========================
# 最佳隊伍計算
# =========================

st.header("最佳隊伍計算")

if not stages:
    st.warning("目前沒有關卡，請先新增關卡")
else:
    stage_names = [stage["name"] for stage in stages]

    selected_stage_name = st.selectbox(
        "選擇關卡",
        stage_names
    )

    current_stage = next(
        stage for stage in stages
        if stage["name"] == selected_stage_name
    )

    tasks = current_stage["tasks"]


    def get_stat(gugu, stat_name):
        value = gugu["stats"][stat_name]

        if stat_name == "力量":
            if "運氣" in gugu["skills"]:
                value += 30

        return value


    def check_task(team, task):
        if task["type"] == "single_stat":
            for gugu in team:
                if get_stat(gugu, task["stat"]) >= task["value"]:
                    return True
            return False

        elif task["type"] == "count_stat":
            count = 0
            for gugu in team:
                if get_stat(gugu, task["stat"]) >= task["value"]:
                    count += 1
            return count >= task["count"]

        elif task["type"] == "team_stat":
            total = 0
            for gugu in team:
                total += get_stat(gugu, task["stat"])
            return total >= task["value"]

        elif task["type"] == "single_skill":
            for gugu in team:
                if task["skill"] in gugu["skills"]:
                    return True
            return False

        return False


    def calc_score(team):
        score = 0
        success_tasks = []

        for task in tasks:
            if check_task(team, task):
                score += 1
                success_tasks.append(task["name"])

        return score, success_tasks


    best_team = None
    best_score = -1
    best_success_tasks = []

    all_teams = []

    for size in range(1, 4):
        all_teams.extend(combinations(gugus, size))

    for team in all_teams:
        score, success_tasks = calc_score(team)

        if score > best_score:
            best_score = score
            best_team = team
            best_success_tasks = success_tasks

    st.header("最佳隊伍")

    if best_team:
        cols = st.columns(len(best_team))

        for i, gugu in enumerate(best_team):
            with cols[i]:
                if gugu.get("image") and os.path.exists(gugu["image"]):
                    st.image(gugu["image"], width=120)

                st.write(gugu["name"])

                for skill_name in gugu["skills"]:
                    icon_path = get_skill_icon(skill_name)

                    if icon_path and os.path.exists(icon_path):
                        st.image(icon_path, width=32)

                    st.caption(skill_name)

        st.write(f"完成任務數：{best_score} / {len(tasks)}")

        st.subheader("完成的任務")

        for task_name in best_success_tasks:
            st.write(f"✅ {task_name}")
    else:
        st.warning("目前沒有菇菇可計算")
