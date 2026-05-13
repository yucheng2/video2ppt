# Video2PPT 并发哈希计算设计

## 概述

将帧提取和哈希计算分离，采用两阶段并行策略加速处理，同时保证帧顺序正确。

## 架构

```
阶段1: 帧提取 (单线程，顺序)
    cv2.VideoCapture.read() → 帧文件

阶段2: 并发哈希计算 (多线程)
    Pool.map(compute_hash, frame_files) → [(index, hash), ...]

阶段3: 按序拼接 (单线程)
    按 index 排序 → 去重 → frames list
```

## 依赖

无新增依赖，使用标准库 `multiprocessing`。

## 修改点

### 1. 新增 compute_hash 函数

```python
def _compute_hash_for_file(args) -> Tuple[int, imagehash.ImageHash, str]:
    """独立函数，用于多进程池调用"""
    idx, frame_path = args
    try:
        img = Image.open(frame_path)
        h = imagehash.phash(img)
        return (idx, h, frame_path)
    except Exception as e:
        logger.warning(f"Failed to compute hash for {frame_path}: {e}")
        return (idx, None, frame_path)
```

### 2. 修改 extract_frames()

只负责提帧，不计算哈希：

```python
def extract_frames(self) -> List[str]:
    """提帧阶段：只提取帧文件，返回帧路径列表（按提取顺序）"""
    # ... 现有提帧逻辑 ...
    # 不再调用 _compute_frame_hash
    # 直接保存帧文件路径到 self.frames
    return self.frames
```

### 3. 新增 compute_hashes()

```python
def compute_hashes(self, frame_paths: List[str]) -> List[Tuple[int, imagehash.ImageHash, str]]:
    """并发计算所有帧的哈希"""
    pool = multiprocessing.Pool()
    args = [(i, fp) for i, fp in enumerate(frame_paths)]
    results = pool.map(_compute_hash_for_file, args)
    pool.close()
    pool.join()
    return sorted(results, key=lambda x: x[0])  # 按 index 排序
```

### 4. 修改 convert()

```python
def convert(self) -> None:
    """完整转换流程"""
    try:
        # 阶段1: 提取帧
        frame_files = self.extract_frames()  # 返回 [(index, path), ...]

        # 阶段2: 并发计算哈希
        hash_results = self.compute_hashes(frame_files)

        # 阶段3: 按序拼接 + 去重
        self.frames = []
        self.last_hash = None
        for idx, current_hash, frame_path in hash_results:
            if current_hash is not None:
                if self.last_hash is None or \
                   abs(current_hash - self.last_hash) > self.hash_threshold:
                    self.frames.append(frame_path)
                    self.last_hash = current_hash
                else:
                    logger.debug(f"Frame skipped (similar): {frame_path}")
            else:
                self.frames.append(frame_path)
                self.last_hash = None

        # 生成PPT
        self.generate_ppt()
    finally:
        self.cleanup()
```

### 5. 修改 generate_ppt()

`self.frames` 现在已是有序列表，直接使用即可，无需修改。

## 错误处理

- 哈希计算失败：保留该帧（视为不相似）
- 进程池异常：向上传播

## 测试验证

1. 运行转换，确认输出 PPT 顺序正确
2. 对比并发前后的处理时间
3. 确认去重功能仍正常
