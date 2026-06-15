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


def _assign_tracks(tasks):
    sorted_tasks = sorted(enumerate(tasks), key=lambda x: x[1]["start"])
    original_indices = []
    sorted_only = []
    for idx, task in sorted_tasks:
        original_indices.append(idx)
        sorted_only.append(task)
    
    track_ends = []
    track_assignments = []
    
    for task in sorted_only:
        assigned = False
        best_track = -1
        best_gap = None
        
        for t_idx, track_end in enumerate(track_ends):
            if track_end <= task["start"]:
                gap = task["start"] - track_end
                if best_gap is None or gap < best_gap:
                    best_gap = gap
                    best_track = t_idx
        
        if best_track != -1:
            track_assignments.append(best_track)
            track_ends[best_track] = task["end"]
        else:
            new_track = len(track_ends)
            track_assignments.append(new_track)
            track_ends.append(task["end"])
    
    num_tracks = len(track_ends)
    
    result = [None] * len(tasks)
    for orig_idx, track_idx, task in zip(original_indices, track_assignments, sorted_only):
        result[orig_idx] = (track_idx, task)
    
    return result, num_tracks


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
        
        deps = task.get("dependencies", [])
        if deps is None:
            deps = []
        if not isinstance(deps, list):
            deps = [deps]
        
        parsed_tasks.append({
            "name": name,
            "start": start,
            "end": end,
            "color": task.get("color", None),
            "dependencies": deps
        })

    assigned, num_tracks = _assign_tracks(parsed_tasks)

    fig_height = max(figsize[1], 2 + num_tracks * 0.6)
    fig, ax = plt.subplots(figsize=(figsize[0], fig_height))
    
    colors = plt.cm.tab20.colors
    
    name_to_info = {}
    track_task_names = {}
    for task_idx, (track_idx, task) in enumerate(assigned):
        color = task["color"] if task["color"] else colors[task_idx % len(colors)]
        start_num = mdates.date2num(task["start"])
        end_num = mdates.date2num(task["end"])
        duration = end_num - start_num
        
        ax.barh(track_idx, duration, left=start_num, height=bar_height, 
                color=color, align="center", edgecolor="black", linewidth=0.5)
        
        mid_point = start_num + duration / 2
        duration_days = duration
        duration_text = f"{duration_days:.1f} 天" if duration_days >= 1 else f"{duration_days * 24:.1f} 小时"
        ax.text(mid_point, track_idx, f"{task['name']}\n{duration_text}", 
                ha="center", va="center", fontsize=9, color="black")
        
        if track_idx not in track_task_names:
            track_task_names[track_idx] = []
        track_task_names[track_idx].append(task["name"])
        
        name_to_info[task["name"]] = (track_idx, start_num, end_num, task)
    
    for task_idx, (track_idx, task) in enumerate(assigned):
        for dep_name in task["dependencies"]:
            if dep_name not in name_to_info:
                import warnings
                warnings.warn(f"任务 '{task['name']}' 的依赖 '{dep_name}' 不存在，已忽略")
                continue
            
            dep_track, dep_start, dep_end, dep_task = name_to_info[dep_name]
            curr_start = mdates.date2num(task["start"])
            
            x_from = dep_end
            y_from = dep_track
            x_to = curr_start
            y_to = track_idx
            
            bar_half = bar_height / 2
            
            if y_from == y_to:
                x_mid = (x_from + x_to) / 2
                y_peak = y_from - bar_half - 0.15
                ax.annotate("",
                    xy=(x_to, y_to),
                    xytext=(x_from, y_from),
                    arrowprops=dict(
                        arrowstyle="->",
                        color="#555555",
                        lw=1.2,
                        connectionstyle=f"arc3,rad=-0.3"
                    )
                )
            else:
                direction = 1 if y_to > y_from else -1
                x_mid = (x_from + x_to) / 2
                ax.annotate("",
                    xy=(x_to, y_to),
                    xytext=(x_from, y_from),
                    arrowprops=dict(
                        arrowstyle="->",
                        color="#555555",
                        lw=1.2,
                        connectionstyle=f"arc3,rad={direction * 0.2}"
                    )
                )

    y_labels = []
    for t in range(num_tracks):
        names = track_task_names.get(t, [])
        if len(names) == 1:
            y_labels.append(names[0])
        else:
            y_labels.append(f"轨道 {t+1} ({len(names)}个任务)")
    
    ax.set_yticks(range(num_tracks))
    ax.set_yticklabels(y_labels)
    
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
