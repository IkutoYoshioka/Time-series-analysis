# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy",
#     "pandas",
#     "matplotlib",
#     "statsmodels",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

    return ARIMA, acorr_ljungbox, het_arch, mo, np, plot_acf, plot_pacf, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # marimo入門：ARMA残差診断ウィジェット

    AR(1)過程を模したデータをシミュレーションし、フィットしたARMAモデルの
    残差診断（ACF/PACF、Ljung-Box、ARCH-LM）をスライダーで対話的に確認します。
    """)
    return


@app.cell
def _(np):
    # --- データ生成: AR(1) + 意図的な非線形性（ARCH的なボラティリティクラスタ）---
    rng = np.random.default_rng(42)
    n = 500
    phi = 0.6

    y = np.zeros(n)
    sigma = np.ones(n)
    for t in range(1, n):
        # ボラティリティが過去の誤差の大きさに依存（ARCH的な生成）
        sigma[t] = np.sqrt(0.05 + 0.85 * (y[t - 1] - phi * y[t - 2 if t > 1 else 0]) ** 2) if t > 1 else 1.0
        eps = rng.normal(0, sigma[t])
        y[t] = phi * y[t - 1] + eps
    return (y,)


@app.cell
def _(mo):
    # --- UI: 次数選択スライダー(ここを動かすと下流セルが自動再実行される) ---
    p_slider = mo.ui.slider(0, 5, value=1, label="AR次数 p")
    q_slider = mo.ui.slider(0, 5, value=0, label="MA次数 q")
    lag_slider = mo.ui.slider(5, 30, value=11, label="ACF/PACF・検定用ラグ数")

    mo.hstack([p_slider, q_slider, lag_slider])
    return lag_slider, p_slider, q_slider


@app.cell
def _(ARIMA, p_slider, q_slider, y):
    # --- モデル推定: スライダー値に依存するため、動かすたびに自動再実行される ---
    model = ARIMA(y, order=(p_slider.value, 0, q_slider.value))
    fit = model.fit()
    resid = fit.resid
    return fit, resid


@app.cell
def _(fit, mo, p_slider, q_slider):
    mo.md(f"""
    ## 推定結果: ARMA({p_slider.value}, {q_slider.value})

    - AIC: **{fit.aic:.2f}**
    - BIC: **{fit.bic:.2f}**
    - 対数尤度: **{fit.llf:.2f}**
    """)
    return


@app.cell(hide_code=True)
def _(lag_slider, plot_acf, plot_pacf, plt, resid):
    # --- 残差のACF/PACF: lag_sliderの値に連動 ---
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    plot_acf(resid, lags=lag_slider.value, ax=axes[0])
    axes[0].set_title("residual ACF")
    plot_pacf(resid, lags=lag_slider.value, ax=axes[1])
    axes[1].set_title("residual PACF")
    plt.tight_layout()
    fig
    return


@app.cell(hide_code=True)
def _(acorr_ljungbox, het_arch, lag_slider, mo, resid):
    # --- 診断検定: Ljung-Box(線形自己相関) と ARCH-LM(条件付き分散の自己相関) ---
    lb = acorr_ljungbox(resid, lags=[lag_slider.value], return_df=True)
    lb_pvalue = lb["lb_pvalue"].iloc[0]

    arch_stat, arch_pvalue, _, _ = het_arch(resid, nlags=lag_slider.value)

    mo.md(
        f"""
        ## 診断検定（ラグ数 = {lag_slider.value}）

        | 検定 | 帰無仮説 | p値 | 判定 |
        |---|---|---|---|
        | Ljung-Box | 残差に系列相関なし | {lb_pvalue:.4f} | {"❌ 棄却（自己相関あり）" if lb_pvalue < 0.05 else "✅ 棄却できず"} |
        | ARCH-LM | 条件付き分散に系列相関なし（ARCH効果なし） | {arch_pvalue:.4f} | {"❌ 棄却（ARCH効果あり → GARCH検討）" if arch_pvalue < 0.05 else "✅ 棄却できず"} |
        """
    )
    return


if __name__ == "__main__":
    app.run()
