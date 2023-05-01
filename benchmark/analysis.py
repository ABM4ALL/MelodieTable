import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def autolabel(ax,rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(round(height, 3)),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

def draw_table(df: pd.DataFrame, size: int):
    df["timePerKQuery"] = df["time"]/df["queries"]*1000

    df_size_100k = df[df["size"] == size][[
        "type", "queries", "timePerKQuery"]]
    # print(df_size_100k)
    cpython_res = df_size_100k[df_size_100k["type"]
                               == "cpython"].to_dict(orient="records")
    pypy_res = df_size_100k[df_size_100k["type"]
                            == "pypy"].to_dict(orient="records")
    assert len(cpython_res) == len(pypy_res)
    x = np.arange(len(cpython_res))
    width = 0.35
    plt.figure()
    fig, ax = plt.subplots()
    labels = [v["queries"] for v in cpython_res]
    rects1 = ax.bar(x - width/2, [v["timePerKQuery"]
                    for v in cpython_res], width, label='CPython-Pandas')
    rects2 = ax.bar(x + width/2, [v["timePerKQuery"]
                    for v in pypy_res], width, label='PyPy-MelodieTable')
    autolabel(ax, rects1)
    autolabel(ax, rects2)
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Time Per 1000 Queries/s')
    ax.set_xlabel('Query Times')
    ax.set_title(
        f'Querying Performance Comparison for Table with {size} Rows')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.savefig(f"../output/querying_performance_{size}_rows.png")
    # plt.show()
    


df = pd.read_csv("find.csv")
for size in [100, 1000, 10_000, 100_000]:
    draw_table(df, size)
