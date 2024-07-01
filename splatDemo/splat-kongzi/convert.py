# 导入必要的库
from plyfile import PlyData  # 用于处理PLY文件的库
import numpy as np  # 用于数值计算的库
import argparse  # 用于处理命令行参数的库
from io import BytesIO  # 用于处理二进制数据的库

# 将PLY文件转换为SPLAT格式的函数
def process_ply_to_splat(ply_file_path):
    # 读取PLY文件
    plydata = PlyData.read(ply_file_path)
    # 提取顶点数据
    vert = plydata["vertex"]
    # 根据一定的计算对索引进行排序
    sorted_indices = np.argsort(
        -np.exp(vert["scale_0"] + vert["scale_1"] + vert["scale_2"])
        / (1 + np.exp(-vert["opacity"]))
    )
    # 创建缓冲区以存储转换后的数据
    buffer = BytesIO()
    # 遍历排序后的索引
    for idx in sorted_indices:
        # 获取顶点数据
        v = plydata["vertex"][idx]
        # 提取位置数据
        position = np.array([v["x"], v["y"], v["z"]], dtype=np.float32)
        # 提取缩放数据
        scales = np.exp(
            np.array(
                [v["scale_0"], v["scale_1"], v["scale_2"]],
                dtype=np.float32,
            )
        )
        # 提取旋转数据
        rot = np.array(
            [v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]],
            dtype=np.float32,
        )
        # 计算颜色数据
        SH_C0 = 0.28209479177387814
        color = np.array(
            [
                0.5 + SH_C0 * v["f_dc_0"],
                0.5 + SH_C0 * v["f_dc_1"],
                0.5 + SH_C0 * v["f_dc_2"],
                1 / (1 + np.exp(-v["opacity"])),
            ]
        )
        # 将数据写入缓冲区
        buffer.write(position.tobytes())
        buffer.write(scales.tobytes())
        buffer.write((color * 255).clip(0, 255).astype(np.uint8).tobytes())
        buffer.write(
            ((rot / np.linalg.norm(rot)) * 128 + 128)
            .clip(0, 255)
            .astype(np.uint8)
            .tobytes()
        )

    return buffer.getvalue()

# 将SPLAT数据保存到文件的函数
def save_splat_file(splat_data, output_path):
    with open(output_path, "wb") as f:
        f.write(splat_data)

# 主函数，处理命令行参数并处理文件
def main():
    # 参数解析器
    parser = argparse.ArgumentParser(description="将PLY文件转换为SPLAT格式.")
    # 输入PLY文件参数
    parser.add_argument(
        "input_files", nargs="+", help="要处理的输入PLY文件."
    )
    # 输出SPLAT文件参数
    parser.add_argument(
        "--output", "-o", default="output.splat", help="输出的SPLAT文件."
    )
    args = parser.parse_args()
    # 遍历输入文件
    for input_file in args.input_files:
        print(f"正在处理 {input_file}...")
        # 将PLY文件转换为SPLAT
        splat_data = process_ply_to_splat(input_file)
        # 确定输出文件名
        output_file = (
            args.output if len(args.input_files) == 1 else input_file + ".splat"
        )
        # 将SPLAT数据保存到文件
        save_splat_file(splat_data, output_file)
        print(f"已保存 {output_file}")

# 如果脚本直接运行，则执行主函数
if __name__ == "__main__":
    main()
