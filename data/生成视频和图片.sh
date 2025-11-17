#!/bin/bash
# 删除之前生成的所有mp4和png文件
 echo "清理旧文件..."
rm -f ./*.mp4 ./*.png

# 获取当前日期
current_date=$(date +"%Y_%m%d_%H%M")
# 定义生成数量


for i in {1..100}
do
    # 生成带索引的文件名
    index_date="${i}_${current_date}"
    echo "\n=== 生成第 $i 组文件 ($index_date) ==="
    
    # 生成3MB随机图片
    echo "正在生成随机图片..."
    ffmpeg -y -f lavfi -i "nullsrc=size=1000x1000,geq=random(1)*255:random(2)*255:random(3)*255" -frames:v 1 -c:v png -compression_level 0 "${index_date}.png"
    
done


# 检查music目录是否存在
if [ ! -d "./music" ]; then
    echo "错误: ./music 目录不存在"
    exit 1
fi

# 获取music目录下所有的音频文件
audio_files=($(find ./music -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.aac" -o -name "*.flac" -o -name "*.m4a" \)))

# 检查是否有音频文件
if [ ${#audio_files[@]} -eq 0 ]; then
    echo "错误: ./music 目录中没有找到音频文件"
    exit 1
fi

echo "找到 ${#audio_files[@]} 个音频文件"

for i in {1..100}
do
    # 生成带索引的文件名
    index_date="${i}_${current_date}"
    echo -e "\n=== 生成第 $i 组文件 ($index_date) ==="
    
    # 生成25MB视频文件
    echo "正在生成视频文件..."
    seed_value=$((100 + i))
    ffmpeg -y -f lavfi -i "gradients=c0=red:c1=blue:c2=green:n=3:duration=20000:size=3840x2160:rate=24:type=circular:seed=${seed_value},format=rgb0" -c:v libx264 -preset ultrafast -fs 25M -pix_fmt yuv420p "${index_date}.mp4"
    
    # 随机选择一个音频文件
    random_index=$((RANDOM % ${#audio_files[@]}))
    selected_audio="${audio_files[$random_index]}"
    echo "随机选择的音频文件: $(basename "$selected_audio")"
    
    # 获取视频和音频的时长
    video_duration=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "${index_date}.mp4")
    audio_duration=$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$selected_audio")
    
    echo "视频时长: ${video_duration:-未知} 秒"
    echo "音频时长: ${audio_duration:-未知} 秒"
    
    # 处理音频文件（如果音频比视频长，则截取；如果短则循环）
    temp_audio="temp_audio_${i}.aac"
    
    if [ -n "$audio_duration" ] && [ -n "$video_duration" ]; then
        if (( $(echo "$audio_duration > $video_duration" | bc -l) )); then
            # 音频比视频长，截取音频
            echo "音频比视频长，截取音频..."
            ffmpeg -y -i "$selected_audio" -t "$video_duration" -c:a aac "$temp_audio"
        else
            # 音频比视频短，循环音频
            echo "音频比视频短，循环音频..."
            # 计算需要循环的次数
            loops=$(echo "scale=0; $video_duration / $audio_duration + 1" | bc)
            ffmpeg -y -stream_loop $loops -i "$selected_audio" -t "$video_duration" -c:a aac "$temp_audio"
        fi
    else
        # 如果无法获取时长，直接使用原始音频
        echo "无法获取时长信息，直接转换音频格式..."
        ffmpeg -y -i "$selected_audio" -c:a aac "$temp_audio"
    fi
    
    # 合并视频和音频
    echo "正在合并视频和音频..."
    output_file="${index_date}_with_audio.mp4"
    ffmpeg -y -i "${index_date}.mp4" -i "$temp_audio" -c:v copy -c:a aac -shortest "$output_file"
    
    # 清理临时文件
    rm -f "$temp_audio"
    
    echo "完成: $output_file"
    
    # 可选：删除原始无音频视频文件
    rm -f "${index_date}.mp4"
done

# 检查文件大小
echo "\n=== 生成完成！所有文件大小：==="
ls -lh *.png *.mp4
echo -e "\n=== 所有处理完成 ==="