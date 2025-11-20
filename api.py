# ======================== 必要库导入 ========================
import sklearn as sk  # 核心修复：定义sk别名（解决NameError）
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn import datasets  # 加载数据集
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from openai import OpenAI
import json
from lightgbm import LGBMClassifier

# ======================== 1. 初始化配置 ========================
# [大语言模型](https://open.toutiao.com/article/url/?param=UY8vg8rg8Uwb93zX1mar8DK1NMK6S16bQ1wzHCF5jSJKQ6qDeTZtUMupNVnQHuysjzi2C9yhjwqXttFpZP9hAPwfFfS8JR4kHCScKfohFpvxcMnvLaA3377xHSmcCJCyhJs7xC5Z32cudjZXGFk3hYiXtFfbrCyciCBHxA8E2n8tCAG9HoxYm6W126dr6Vz4nVZVGZpyxrT9HstZxyVkhssKNvYRaHTs74LFEgHBRVzVe9xGT9hAjCGBZEW8eDd&partner=agent_bot_7520145467502544393_default_content&version=3)配置（请替换为实际API信息）
API_KEY = "sk-your-api-key"  # 替换为真实API Key
API_BASE = "https://api.openai.com/v1"  # 或模型服务地址
MODEL_ID = "gpt-3.5-turbo"  # 替换为实际模型ID

# 初始化OpenAI客户端
client = OpenAI(api_key=API_KEY, base_url=API_BASE)


# ======================== 2. 大语言模型调用模块 ========================
def ask_ai(messages, json_type=True, model_id=MODEL_ID):
    """调用大语言模型，支持JSON结构化输出"""
    json_messages = [{"role": "user", "content": messages}]
    extra_body = {"response_format": {"type": "json_object"}} if json_type else {}

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=json_messages,
            **extra_body
        )
        return json.loads(response.choices[0].message.content) if json_type else response.choices[0].message.content
    except Exception as e:
        return {"error": f"API调用失败: {str(e)}"}


# ======================== 3. 数据加载与预处理 ========================
def load_data(dataset_name):
    """加载内置数据集（修复sk.datasets调用）"""
    if dataset_name == "鸢尾花数据集":
        data = sk.datasets.load_iris()  # 使用sk别名访问datasets
    elif dataset_name == "乳腺癌数据集":
        data = sk.datasets.load_breast_cancer()  # 使用sk别名访问datasets
    else:
        raise ValueError(f"不支持的数据集: {dataset_name}")

    X, y = data.data, data.target
    return X, y, data.feature_names, data.target_names


# ======================== 4. 模型训练与评估 ========================
def train_model(X, y, method="决策树", test_size=0.3):
    """训练分类模型（修复sk.tree调用）"""
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=test_size, random_state=0)

    # 根据方法选择模型（使用sk别名）
    if method == "决策树":
        model = sk.tree.DecisionTreeClassifier(random_state=0)  # sk别名调用tree
    elif method == "LightGBM":
        model = LGBMClassifier(random_state=0, n_estimators=100)
    else:
        raise ValueError(f"不支持的模型: {method}")

    model.fit(X_tr, y_tr)
    y_pred = model.predict(X_te)
    acc = accuracy_score(y_te, y_pred)
    cm = confusion_matrix(y_te, y_pred)

    # 混淆矩阵可视化
    cm_df = pd.DataFrame(cm, index=[f"真实:{t}" for t in np.unique(y)], columns=[f"预测:{t}" for t in np.unique(y)])
    heatmap = alt.Chart(cm_df.reset_index().melt("index")).mark_rect().encode(
        x=alt.X("variable:N", title="预测类别"),
        y=alt.Y("index:N", title="真实类别"),
        color=alt.Color("value:Q", scale=alt.Scale(scheme="blues")),
        tooltip=["index", "variable", "value"]
    ).properties(title=f"混淆矩阵 (准确率: {acc:.3f})")

    return model, acc, cm, heatmap


# ======================== 5. 主界面与交互 ========================
def main():
    st.set_page_config(page_title="决策支持系统", layout="wide")
    st.title("AI驱动的决策支持系统")

    # 侧边栏配置
    with st.sidebar:
        st.header("参数配置")
        dataset = st.selectbox("选择数据集", ["鸢尾花数据集", "乳腺癌数据集"])
        model_method = st.selectbox("选择模型", ["决策树", "LightGBM"])
        test_size = st.slider("测试集比例", 0.2, 0.5, 0.3)
        run_analysis = st.button("开始分析")

    # 执行分析
    if run_analysis:
        try:
            # 1. 加载数据
            with st.expander("1. 数据概览", expanded=True):
                X, y, feature_names, target_names = load_data(dataset)
                st.write(f"特征名称: {', '.join(feature_names[:5])}...")
                st.write(f"类别标签: {', '.join(target_names)}")
                st.write(f"数据规模: {X.shape[0]}样本, {X.shape[1]}特征")

            # 2. 模型训练
            with st.expander("2. 模型结果", expanded=True):
                model, acc, cm, heatmap = train_model(X, y, method=model_method, test_size=test_size)
                st.altair_chart(heatmap, use_container_width=True)
                st.success(f"模型准确率: **{acc:.3f}**")

            # 3. AI建议（需API密钥）
            with st.expander("3. AI决策建议", expanded=True):
                highlights = f"准确率={acc:.3f}，模型={model_method}"
                advice = ask_ai(f"基于{highlights}，给出3条业务建议", json_type=False)
                st.write(advice)

        except Exception as e:
            st.error(f"执行失败: {str(e)}")


if __name__ == "__main__":
    main()
