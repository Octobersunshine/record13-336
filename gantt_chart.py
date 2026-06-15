import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
from datetime import datetime
import os
import platform


def _setup_chinese_font():
    system = platform.system()
    if system == "Windows":
        font_names = ["Microsoft YaHei", "SimHei", "SimSun"]
    elif system == "Darwin":
        font_names = ["PingFang SC", "Heiti SC", "STHeiti"]
    else:
        font_names = ["WenQuanYi Micro Hei", "Noto Sans CJK SC", "Source Han Sans CN"]
    
    available_fonts = {f.name for f in font_manager.fontManager.ttflist}
    
    for font_name in font_names:
        if font_name in available_fonts:
            plt.rcParams["font.sans-serif"] = [font_name]
            plt.rcParams["axes.unicode_minus"] = False
            return
    
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


_setup_chinese_font()


def generate_gantt(tasks, output_path="gantt_chart.png", title="项目甘特图", 
                   figsize=(12, 8), bar_height=0.5, show_grid=True):
    if not tasks:
        raise ValueError("任务列表不能为空")

    parsed_tasks = []
    for task in tasks:
        name = task["name"]
        start = task["start"]
        end = task["end"]
        
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        
        if end <= start:
            raise ValueError(f"任务 '{name}' 的结束时间必须晚于开始时间")
        
        parsed_tasks.append({
            "name": name,
            "start": start,
            "end": end,
            "color": task.get("color", None)
        })

    parsed_tasks.sort(key=lambda x: x["start"])

    fig, ax = plt.subplots(figsize=figsize)
    
    colors = plt.cm.tab20.colors
    
    for i, task in enumerate(parsed_tasks):
        color = task["color"] if task["color"] else colors[i % len(colors)]
        start_num = mdates.date2num(task["start"])
        end_num = mdates.date2num(task["end"])
        duration = end_num - start_num
        
        ax.barh(i, duration, left=start_num, height=bar_height, 
                color=color, align="center", edgecolor="black", linewidth=0.5)
        
        mid_point = start_num + duration / 2
        duration_days = duration
        duration_text = f"{duration_days:.1f} 天" if duration_days >= 1 else f"{duration_days * 24:.1f} 小时"
        ax.text(mid_point, i, f"{task['name']}\n{duration_text}", 
                ha="center", va="center", fontsize=9, color="black")

    ax.set_yticks(range(len(parsed_tasks)))
    ax.set_yticklabels([task["name"] for task in parsed_tasks])
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.xticks(rotation=45, ha="right")
    
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("时间", fontsize=12)
    ax.set_ylabel("任务", fontsize=12)
    
    if show_grid:
        ax.grid(True, axis="x", linestyle="--", alpha=0.7)
    
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    
    return os.path.abspath(output_path)


def generate_gantt_from_list(task_list, output_path="gantt_chart.png", **kwargs):
    tasks = []
    for item in task_list:
        if len(item) == 3:
            name, start, end = item
            color = None
        elif len(item) == 4:
            name, start, end, color = item
        else:
            raise ValueError("每个任务必须包含3或4个元素：名称、开始时间、结束时间、[颜色]")
        
        task_dict = {"name": name, "start": start, "end": end}
        if color:
            task_dict["color"] = color
        tasks.append(task_dict)
    
    return generate_gantt(tasks, output_path, **kwargs)
