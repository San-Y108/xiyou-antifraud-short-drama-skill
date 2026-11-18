#!/usr/bin/env python3
"""Optional portable media checks; uses only Python's standard library and ffmpeg/ffprobe."""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description='检查西游反诈短剧成片技术项；不能替代剧情、口型与中文可读性看片。')
    parser.add_argument('video', type=Path, help='待检查的正式MP4')
    parser.add_argument('--output', type=Path, help='报告路径；默认放在视频旁边')
    parser.add_argument('--max-seconds', type=float, default=55.0)
    args = parser.parse_args()
    if not args.video.is_file():
        parser.error('找不到输入视频文件。')
    missing = [name for name in ('ffprobe', 'ffmpeg') if not shutil.which(name)]
    if missing:
        parser.error('缺少本地工具：' + '、'.join(missing) + '。请先安装并确认可从命令行调用，或在剪辑软件中手动验收。')
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(args.video)], capture_output=True, text=True)
    if probe.returncode:
        parser.error('无法读取媒体：' + probe.stderr.strip())
    meta = json.loads(probe.stdout)
    videos = [s for s in meta.get('streams', []) if s.get('codec_type') == 'video']
    audios = [s for s in meta.get('streams', []) if s.get('codec_type') == 'audio']
    v = videos[0] if videos else {}
    a = audios[0] if audios else {}
    try:
        duration = float(meta.get('format', {}).get('duration', 'nan'))
    except (TypeError, ValueError):
        duration = float('nan')
    decode = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(args.video), '-f', 'null', '-'], capture_output=True, text=True)
    silence_log = []
    loudness = None
    analysis_error = None
    if audios:
        analysis = subprocess.run(['ffmpeg', '-i', str(args.video), '-af', 'silencedetect=noise=-40dB:d=0.7,loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
        silence_log = [line.strip() for line in analysis.stderr.splitlines() if 'silence_start:' in line or 'silence_end:' in line]
        match = re.search(r'\{\s*"input_i".*?\}', analysis.stderr, re.S)
        if match:
            measured = json.loads(match.group())
            loudness = {name: measured.get(name) for name in ('input_i', 'input_tp', 'input_lra')}
        if analysis.returncode:
            analysis_error = analysis.stderr[-2000:]
    checks = {
        '存在视频轨': bool(videos),
        '存在音轨': bool(audios),
        '时长在上限内': math.isfinite(duration) and 0 < duration <= args.max_seconds,
        '720乘1280竖屏': (v.get('width'), v.get('height')) == (720, 1280),
        'H264视频': v.get('codec_name') == 'h264',
        'AAC声音': a.get('codec_name') == 'aac',
        '完整解码无错误': decode.returncode == 0 and not decode.stderr.strip(),
        '声轨分析完成': bool(audios) and analysis_error is None,
        '无至少0点7秒的整轨低电平静音': bool(audios) and analysis_error is None and not silence_log,
    }
    report = {
        '文件名': args.video.name,
        '技术检查通过': all(checks.values()),
        '检查': checks,
        '实际时长秒': duration if math.isfinite(duration) else None,
        '尺寸': [v.get('width'), v.get('height')],
        '帧率': v.get('avg_frame_rate'),
        '像素宽高比': v.get('sample_aspect_ratio'),
        '视频编码': v.get('codec_name'),
        '声音编码': a.get('codec_name'),
        '原始声轨响度数据': loudness,
        '静音检测记录': silence_log,
        '解码错误': decode.stderr.strip(),
        '声轨分析错误': analysis_error,
        '仍需看片': ['真实案例与虚构边界', '前三秒钩子与剧情因果', '说话人、实际台词、字幕对齐', '反派顺序与道具状态', '中文可读性与遮挡', '有BGM但无剧情推进的空白', '音乐是否盖过人声', '判断按钮是否被误称为真交互'],
        '说明': '技术通过不等于整体成片通过；检测到静音也可能是有意的戏剧停顿，请按实际剧情复核。',
    }
    output = args.output or args.video.with_name(args.video.name + '.验收.json')
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['技术检查通过'] else 1


if __name__ == '__main__':
    sys.exit(main())
