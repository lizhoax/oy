import streamlit as st
import numpy as np
import sqlite3


def init_bmi_db():
    conn = sqlite3.connect('bmi_records.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bmi_calculations (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        height REAL NOT NULL CHECK(height > 0),
        weight REAL NOT NULL CHECK(weight > 0),
        bmi_value REAL NOT NULL,
        bmi_category TEXT NOT NULL,
        record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('bmi_records.db')
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()


init_bmi_db()


def judge_BMI_standard(bmi_val):
    if bmi_val < 18.5:
        return "偏瘦"
    elif 18.5 <= bmi_val < 25:
        return "正常"
    elif 25 <= bmi_val < 28:
        return "超重"
    else:
        return "肥胖"


st.title("BMI指数管理系统")
tab1, tab2 = st.tabs(["BMI计算与保存", "历史记录管理"])

with tab1:
    st.subheader("💡 计算并保存BMI")
    height_input = st.text_input("请输入身高（m）", "")
    weight_input = st.text_input("请输入体重（kg）", "")

    if st.button("计算并保存"):
        try:
            height = np.float64(height_input)
            weight = np.float64(weight_input)

            if height <= 0 or weight <= 0:
                st.error("身高和体重必须为正数")
            else:
                bmi = round(weight / (height ** 2), 2)
                bmi_category = judge_BMI_standard(bmi)

                conn, cursor = get_db_connection()
                cursor.execute('''
                INSERT INTO bmi_calculations (height, weight, bmi_value, bmi_category)
                VALUES (?, ?, ?, ?)
                ''', (height, weight, bmi, bmi_category))
                conn.commit()
                conn.close()

                st.success("BMI记录已保存")
                st.metric("你的BMI指数", bmi)
                st.text(bmi_category)
                st.info(f"体重类别：{bmi_category}")

        except ValueError:
            st.error("请输入有效的数字")
        except Exception as e:
            st.error(f"保存失败：{str(e)}")

with tab2:
    st.subheader("历史记录管理")

    conn, cursor = get_db_connection()
    all_records = cursor.execute('''
    SELECT * FROM bmi_calculations ORDER BY record_time DESC
    ''').fetchall()
    conn.close()

    if not all_records:
        st.warning("暂无历史记录")
    else:
        record_options = [
            f"记录{idx + 1}（{record['record_time'][:16]} | BMI:{record['bmi_value']} | {record['bmi_category']}）"
            for idx, record in enumerate(all_records)
        ]
        selected_idx = st.selectbox("选择要操作的记录", range(len(record_options)),
                                    format_func=lambda x: record_options[x])
        selected_record = all_records[selected_idx]

        st.subheader("编辑记录")
        with st.form(f"edit_form_{selected_record['record_id']}"):
            new_height = st.text_input("修改身高（m）", str(selected_record["height"]))
            new_weight = st.text_input("修改体重（kg）", str(selected_record["weight"]))
            update_btn = st.form_submit_button("保存修改")

            if update_btn:
                try:
                    new_h = np.float64(new_height)
                    new_w = np.float64(new_weight)

                    if new_h <= 0 or new_w <= 0:
                        st.error("身高和体重必须为正数")
                    else:
                        new_bmi = round(new_w / (new_h ** 2), 2)
                        new_bmi_cat = judge_BMI_standard(new_bmi)

                        conn, cursor = get_db_connection()
                        cursor.execute('''
                        UPDATE bmi_calculations 
                        SET height = ?, weight = ?, bmi_value = ?, bmi_category = ?
                        WHERE record_id = ?
                        ''', (new_h, new_w, new_bmi, new_bmi_cat, selected_record["record_id"]))
                        conn.commit()
                        conn.close()

                        st.success("记录修改成功！刷新页面即可查看更新")
                except ValueError:
                    st.error("请输入有效的数字")

        st.subheader("🗑️ 删除记录")
        if st.button(f"删除选中的「{record_options[selected_idx]}」", type="primary", help="删除后无法恢复"):
            try:
                conn, cursor = get_db_connection()
                cursor.execute('''
                DELETE FROM bmi_calculations WHERE record_id = ?
                ''', (selected_record["record_id"],))
                conn.commit()
                conn.close()

                st.success("记录已删除！刷新页面即可更新列表")
                st.rerun()
            except Exception as e:
                st.error(f"删除失败：{str(e)}")
