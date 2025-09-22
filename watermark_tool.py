#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont, ExifTags
from datetime import datetime


def get_exif_date(image_path):
    """从图片中获取EXIF信息中的拍摄日期"""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data:
            # 查找日期时间标签
            date_time = None
            for tag, value in ExifTags.TAGS.items():
                if value == 'DateTimeOriginal':
                    if tag in exif_data:
                        date_time = exif_data[tag]
                        break
            
            if not date_time:
                # 如果没有DateTimeOriginal，尝试使用DateTime
                for tag, value in ExifTags.TAGS.items():
                    if value == 'DateTime':
                        if tag in exif_data:
                            date_time = exif_data[tag]
                            break
            
            if date_time:
                # 解析日期时间字符串
                try:
                    # EXIF日期格式通常是 "YYYY:MM:DD HH:MM:SS"
                    date_obj = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # 如果格式不匹配，尝试提取前10个字符
                    if len(date_time) >= 10:
                        return date_time[:10].replace(':', '-')
        
        # 如果没有EXIF信息或日期，返回None
        return None
    except Exception as e:
        print(f"Error reading EXIF from {image_path}: {e}")
        return None


def add_watermark(image_path, output_path, text, font_size, font_color, position):
    """向图片添加水印"""
    try:
        # 打开图片
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # 确保字体大小合理
        max_font_size = min(width, height) // 10
        if font_size > max_font_size:
            font_size = max_font_size
        
        # 尝试加载字体
        try:
            # Windows系统
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            try:
                # Linux系统
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except IOError:
                # 如果找不到字体，使用默认字体
                font = ImageFont.load_default()
        
        # 获取文本大小
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
        
        # 根据位置确定文本位置
        padding = 10  # 边距
        if position == 'top-left':
            x, y = padding, padding
        elif position == 'top-right':
            x, y = width - text_width - padding, padding
        elif position == 'bottom-left':
            x, y = padding, height - text_height - padding
        elif position == 'bottom-right':
            x, y = width - text_width - padding, height - text_height - padding
        elif position == 'center':
            x, y = (width - text_width) // 2, (height - text_height) // 2
        else:
            # 默认右下角
            x, y = width - text_width - padding, height - text_height - padding
        
        # 添加半透明背景
        bg_color = (*font_color[:3], 128)  # 50%透明度
        draw.rectangle([x-2, y-2, x+text_width+2, y+text_height+2], fill=bg_color)
        
        # 添加文本
        draw.text((x, y), text, font=font, fill=font_color)
        
        # 保存图片
        img.save(output_path)
        print(f"Watermark added to {output_path}")
        return True
    except Exception as e:
        print(f"Error adding watermark to {image_path}: {e}")
        return False


def process_images(input_path, font_size, font_color, position):
    """处理输入路径中的所有图片"""
    # 确定输入路径类型
    if os.path.isfile(input_path):
        # 单个文件
        process_file(input_path, font_size, font_color, position)
    elif os.path.isdir(input_path):
        # 目录
        # 创建输出目录
        parent_dir = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        output_dir = os.path.join(parent_dir, f"{base_name}_watermark")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 处理目录中的所有图片文件
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in supported_formats:
                    process_file(file_path, font_size, font_color, position, output_dir)
    else:
        print(f"Input path {input_path} does not exist.")


def process_file(file_path, font_size, font_color, position, output_dir=None):
    """处理单个图片文件"""
    # 获取日期水印文本
    date_text = get_exif_date(file_path)
    
    if not date_text:
        print(f"No valid date found in EXIF for {file_path}. Skipping.")
        return
    
    # 确定输出路径
    if output_dir:
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)
    else:
        # 对于单个文件，在原文件名基础上添加_watermark后缀
        base_name, ext = os.path.splitext(file_path)
        output_path = f"{base_name}_watermark{ext}"
    
    # 添加水印
    add_watermark(file_path, output_path, date_text, font_size, font_color, position)


def parse_color(color_str):
    """解析颜色字符串为RGBA元组"""
    # 支持格式: #RRGGBB, rgb(255,255,255), 255,255,255, or color name
    color_map = {
        'black': (0, 0, 0, 255),
        'white': (255, 255, 255, 255),
        'red': (255, 0, 0, 255),
        'green': (0, 255, 0, 255),
        'blue': (0, 0, 255, 255),
        'yellow': (255, 255, 0, 255),
        'cyan': (0, 255, 255, 255),
        'magenta': (255, 0, 255, 255),
        'gray': (128, 128, 128, 255),
        'grey': (128, 128, 128, 255)
    }
    
    if color_str.lower() in color_map:
        return color_map[color_str.lower()]
    
    # 尝试解析十六进制颜色
    if color_str.startswith('#'):
        try:
            color_str = color_str.lstrip('#')
            if len(color_str) == 6:
                r, g, b = int(color_str[0:2], 16), int(color_str[2:4], 16), int(color_str[4:6], 16)
                return (r, g, b, 255)
        except ValueError:
            pass
    
    # 尝试解析rgb格式
    if color_str.lower().startswith('rgb(') and color_str.endswith(')'):
        try:
            rgb_values = color_str[4:-1].split(',')
            r, g, b = int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2])
            return (r, g, b, 255)
        except (ValueError, IndexError):
            pass
    
    # 尝试解析逗号分隔的RGB值
    if ',' in color_str:
        try:
            rgb_values = color_str.split(',')
            if len(rgb_values) >= 3:
                r, g, b = int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2])
                a = 255
                if len(rgb_values) == 4:
                    a = int(rgb_values[3])
                return (r, g, b, a)
        except (ValueError, IndexError):
            pass
    
    # 默认返回白色
    print(f"Invalid color format: {color_str}. Using white instead.")
    return (255, 255, 255, 255)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Add date watermark from EXIF to images.')
    parser.add_argument('input_path', help='Input image file or directory path')
    parser.add_argument('--font-size', type=int, default=30, help='Font size of the watermark (default: 30)')
    parser.add_argument('--color', type=str, default='white', help='Font color (default: white)')
    parser.add_argument('--position', type=str, default='bottom-right', 
                        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                        help='Position of the watermark (default: bottom-right)')
    
    args = parser.parse_args()
    
    # 解析颜色
    font_color = parse_color(args.color)
    
    # 处理图片
    process_images(args.input_path, args.font_size, font_color, args.position)


if __name__ == '__main__':
    main()