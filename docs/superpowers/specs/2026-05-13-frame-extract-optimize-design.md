# Video2PPT 帧提取优化设计

## 问题分析

**现状：**
- 帧提取阶段：每帧都写入磁盘，然后才做去重
- 大量相似帧也写入磁盘 → 无效 I/O
- pHash 计算本身较慢

**根本原因：** 相似帧在哈希计算前就被写入磁盘

## 优化方案

**快速预过滤 + 精确去重：**

```
帧提取时:
1. 读取帧 → 计算快速差异（像素级）
2. 差异大(>阈值) → 直接保存，差异小 → 计算pHash精确比较
3. pHash差异大 → 保存，小 → 跳过
```

### 两级过滤

**第一级：快速像素差异**
- 对比相邻帧的像素均值差异
- 计算快，但不能处理色调变化

**第二级：pHash 精确比较**
- 只对可能相似的帧计算
- 大幅减少 pHash 调用次数

### 数据结构

```python
def extract_frames(self) -> List[str]:
    """提帧阶段：快速预过滤 + 精确去重"""
    last_frame = None  # 上一帧的 numpy 数组

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            if last_frame is not None:
                # 快速像素差异
                diff = np.mean(np.abs(frame.astype(float) - last_frame.astype(float)))

                if diff > self.pixel_threshold:
                    # 差异大，直接保存
                    self.frames.append(frame_path)
                    self.last_hash = self._compute_frame_hash(frame_path)  # 同步计算
                else:
                    # 可能相似，精确pHash比较
                    current_hash = self._compute_frame_hash(frame_path)
                    if self.last_hash is None or abs(current_hash - self.last_hash) > self.hash_threshold:
                        self.frames.append(frame_path)
                        self.last_hash = current_hash
                    # else: 跳过

            last_frame = frame.copy()

    return self.frames
```

### 新增参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `pixel_threshold` | 30 | 像素差异阈值，>30直接保存，≤30走pHash |

## 优点

1. 大部分帧用像素差异快速判断，不走pHash
2. 减少磁盘I/O（相似帧不写入）
3. 保持原有逻辑顺序
4. 不需要并发（因为计算本身变少了）

## 移除的代码

- `multiprocessing` import（不再需要）
- `compute_hashes()` 方法
- `convert()` 中的并发逻辑
