import argparse
import json
import sys
from gantt_chart import generate_gantt, generate_gantt_from_list


def demo():
    tasks = [
        {"name": "需求分析", "start": "2026-06-01", "end": "2026-06-07"},
        {"name": "系统设计", "start": "2026-06-05", "end": "2026-06-15", "dependencies": ["需求分析"]},
        {"name": "前端开发", "start": "2026-06-10", "end": "2026-06-25", "dependencies": ["系统设计"]},
        {"name": "后端开发", "start": "2026-06-12", "end": "2026-06-30", "dependencies": ["系统设计"]},
        {"name": "测试", "start": "2026-06-25", "end": "2026-07-05", "dependencies": ["前端开发", "后端开发"]},
        {"name": "上线部署", "start": "2026-07-03", "end": "2026-07-08", "dependencies": ["测试"]},
    ]
    
    output = generate_gantt(tasks, output_path="gantt_demo.png", title="项目开发甘特图")
    print(f"示例甘特图已生成: {output}")


def main():
    parser = argparse.ArgumentParser(description="甘特图生成服务")
    parser.add_argument("--demo", action="store_true", help="运行示例")
    parser.add_argument("--json", type=str, help="JSON 格式的任务数据文件路径")
    parser.add_argument("--output", type=str, default="gantt_chart.png", help="输出图片路径")
    parser.add_argument("--title", type=str, default="项目甘特图", help="甘特图标题")
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
        return
    
    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        output = generate_gantt(tasks, output_path=args.output, title=args.title)
        print(f"甘特图已生成: {output}")
        return
    
    print("请使用 --demo 运行示例，或使用 --json 指定任务数据文件。")
    print()
    print("JSON 文件格式示例:")
    print("""
[
    {"name": "任务1", "start": "2026-06-01", "end": "2026-06-05"},
    {"name": "任务2", "start": "2026-06-03", "end": "2026-06-10", "color": "#FF6B6B", "dependencies": ["任务1"]},
    {"name": "任务3", "start": "2026-06-10", "end": "2026-06-15", "dependencies": ["任务1", "任务2"]}
]
    """)


if __name__ == "__main__":
    main()
