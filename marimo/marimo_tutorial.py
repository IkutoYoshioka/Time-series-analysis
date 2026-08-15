# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy",
#     "pandas",
#     "matplotlib",
#     "duckdb==1.5.5",
#     "sqlglot==30.17.0",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md("""
    # marimo 機能ツアー

    このノートブックは marimo の主要機能を一通り体験するための
    サンプルです。各セクションが独立した機能を示します。

    1. Reactivity（依存関係の自動再実行）
    2. UI要素（スライダー・ドロップダウン・テキスト入力）
    3. データフレーム表示とインタラクティブテーブル
    4. 条件分岐によるレイアウト制御
    5. レイアウト（タブ・アコーディオン・カラム）
    6. SQL統合
    7. 状態管理（mo.state）
    """)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    return mo, np, pd, plt


@app.cell
def _(mo):
    mo.md("""
    ## 1. Reactivity: 依存関係の自動再実行
    """)
    return


@app.cell
def _(mo):
    x_input = mo.ui.number(start=0, stop=100, value=10, label="x の値")
    x_input
    return (x_input,)


@app.cell
def _(x_input):
    # x_input を変えると、このセルも自動で再実行される
    y_value = x_input.value ** 2
    y_value
    return (y_value,)


@app.cell
def _(mo, y_value):
    # y_value に依存するセルもさらに連鎖して再実行される
    mo.md(f"x^2 = **{y_value}** （x_input を上で動かすとここも自動更新されます）")
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. 主なUI要素
    """)
    return


@app.cell
def _(mo):
    slider = mo.ui.slider(0, 100, value=50, label="スライダー")
    dropdown = mo.ui.dropdown(
        options=["linear", "log", "quadratic"], value="linear", label="the way of the conversion"
    )
    text = mo.ui.text(value="研究テーマ", label="テキスト入力")
    checkbox = mo.ui.checkbox(value=True, label="グリッド表示")
    date = mo.ui.date(label="基準日")

    # mo.hstack / mo.vstack でレイアウトを組める
    mo.vstack([
        mo.hstack([slider, dropdown]),
        mo.hstack([text, checkbox, date]),
    ])
    return checkbox, date, dropdown, slider, text


@app.cell
def _(checkbox, date, dropdown, mo, slider, text):
    # すべてのUI要素の現在値を .value で参照するだけで反応的に使える
    mo.md(
        f"""
        **現在の値**：slider={slider.value}, dropdown={dropdown.value},
        text="{text.value}", checkbox={checkbox.value}, date={date.value}
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. データフレーム表示（mo.ui.table でソート・フィルタ可能）
    """)
    return


@app.cell
def _(np, pd):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "id": range(1, 21),
        "category": rng.choice(["A", "B", "C"], size=20),
        "value": rng.normal(100, 15, size=20).round(2),
    })
    return (df,)


@app.cell
def _(df, mo):
    # mo.ui.table はソート・フィルタ・行選択ができるインタラクティブ表
    table = mo.ui.table(df, page_size=8, label="サンプルデータ")
    table
    return (table,)


@app.cell
def _(mo, table):
    # table.value でユーザーが選択した行だけを取得できる
    mo.md(
        f"選択された行数: **{len(table.value)}** "
        f"（テーブルの行をクリックして選択してみてください）"
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. UI値に応じたプロットの動的切り替え
    """)
    return


@app.cell
def _(dropdown, np, plt, slider):
    xs = np.linspace(0.1, 10, 200)
    if dropdown.value == "linear":
        ys = xs * (slider.value / 50)
    elif dropdown.value == "log":
        ys = np.log(xs) * (slider.value / 10)
    else:  # 二次
        ys = (xs ** 2) * (slider.value / 500)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(xs, ys)
    ax.set_title(f"conversion: {dropdown.value} (slider={slider.value})")
    fig
    return


@app.cell
def _(mo):
    mo.md("""
    ## 5. レイアウト: タブ / アコーディオン
    """)
    return


@app.cell
def _(df, mo):
    tabs = mo.ui.tabs({
        "概要": mo.md(f"データ件数: {len(df)}件"),
        "統計量": df.describe(),
        "先頭5行": df.head(),
    })
    tabs
    return


@app.cell
def _(mo):
    accordion = mo.accordion({
        "このノートブックについて": mo.md(
            "marimoの機能ツアー用サンプル。研究ノートブックの雛形として複製して使えます。"
        ),
        "次に試すこと": mo.md(
            "- SQLセルの利用\n- mo.state による永続的なUI状態管理\n- 重いセルの stale 化設定"
        ),
    })
    accordion
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. SQL統合

    marimoはPython変数を参照するSQLクエリをセル内に直接書け、
    結果はPythonのデータフレームとして返ります（`--` で始まる
    特殊コメント、または `mo.sql()` 呼び出しの形をとります）。
    下は `mo.sql()` を明示的に使う例です。
    """)
    return


@app.cell
def _(mo):
    # df を直接テーブルのように参照できる。SQL単独ファイルを持つ必要がない。
    result = mo.sql(
        f"""
        SELECT category, COUNT(*) AS n, AVG(value) AS avg_value
        FROM df
        GROUP BY category
        ORDER BY avg_value DESC
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7. mo.state: セル間で共有する明示的な状態

    通常UIの値はreactivityで自動伝播しますが、
    「ボタンを押した時だけ更新したい」ようなケースでは
    `mo.state` と `mo.ui.button` を組み合わせます。
    """)
    return


@app.cell
def _(mo):
    get_count, set_count = mo.state(0)
    increment = mo.ui.button(
        label="カウントを増やす", on_click=lambda _: set_count(get_count() + 1)
    )
    increment
    return (get_count,)


@app.cell
def _(get_count, mo):
    mo.md(f"""
    現在のカウント: **{get_count()}**（ボタンを押すごとに増加）
    """)
    return


if __name__ == "__main__":
    app.run()
