import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="个人信息管理系统", page_icon="", layout="wide")

BASE_DIR = Path().parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "records.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)
COLUMNS = ["id", "title", "category", "date_obtained", "importance", "tags", "notes", "created_at"]


def load_data() -> pd.DataFrame:
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    return df


def save_data(df: pd.DataFrame):
    try:
        # 确保 tags 字段为字符串格式（逗号分隔）
        df["tags"] = df["tags"].apply(lambda x: ",".join(x) if isinstance(x, list) else x)
        df.to_csv(CSV_PATH, index=False)
    except Exception as e:
        st.error(f"保存失败：{str(e)}")


def input_form(df: pd.DataFrame) -> pd.DataFrame:
    with st.form("add_form", clear_on_submit=True):
        new = {}
        new["id"] = (0 if df.empty else int(df["id"].max()) + 1)
        new["title"] = st.text_input("标题 *", placeholder="")
        CATEGORIES = ["荣誉", "教育经历", "竞赛", "证书", "账号", "其他"]
        new["category"] = st.selectbox("类别", CATEGORIES, index=0)
        new["date_obtained"] = st.date_input("获取日期", value=pd.Timestamp.now())
        new["importance"] = st.slider("重要性", 1, 5, 3)
        new["tags"] = st.multiselect("标签", ["家庭", "校园", "职场", "个人", "公开", "私密"])
        new["notes"] = st.text_area("备注（可选）", placeholder="关键信息、链接或行动项…", height=100)
        submitted = st.form_submit_button("保存", type="primary", use_container_width=True)

    if submitted:
        new["created_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        # 将多选标签转换为逗号分隔的字符串
        new["tags"] = ",".join(new["tags"])  # 核心修复：列表转字符串
        df_new = pd.DataFrame(new, index=[0])
        df = pd.concat([df, df_new], ignore_index=True)
        save_data(df)
        st.success("已保存 ")
    return df


# 主流程
df = load_data()
st.title("个人信息管理系统")
st.write("记录重要个人信息，支持分类、查询与导出")

st.subheader("添加新记录")
df = input_form(df)

st.subheader("当前数据（简化输出）")
st.write(df)

st.subheader("数据总览")
if df.empty:
    st.info("暂无数据，请添加")
else:
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "导出数据",
        data=csv,
        file_name="personal_records.csv",
        mime="text/csv",
        use_container_width=True
    )
