# Video2PPT 帧去重设计

## 概述

在帧提取阶段增加感知哈希 (pHash) 比较，移除相似的连续帧，减少冗余输出。

## 依赖

新增 `imagehash` 库：
```
imagehash
```

## 修改点

### 1. Video2PPT 类

**新增方法：**
```python
def _compute_frame_hash(self, image_path: str) -> imagehash.ImageHash:
    """计算单帧的感知哈希"""
```

**修改方法：**
- `extract_frames()` — 在帧保留逻辑中增加哈希比较

### 2. 去重逻辑

在 `extract_frames()` 的帧保留循环中：

```python
# 伪代码
if frame_count % frame_interval == 0:
    frame_path = os.path.join(self.frames_dir, f"frame_{extracted_count:04d}.jpg")
    cv2.imwrite(frame_path, frame)

    # 新增：计算哈希并比较
    current_hash = self._compute_frame_hash(frame_path)
    if self.last_hash is None or \
       abs(current_hash - self.last_hash) > self.hash_threshold:
        self.frames.append(frame_path)
        self.last_hash = current_hash
        extracted_count += 1
```

### 3. 新增属性

`__init__` 中增加：
```python
self.last_hash = None
self.hash_threshold = 15  # 可通过参数配置
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `hash_threshold` | 15 | 哈希差异阈值，>15 保留，≤15 丢弃 |

## 流程对比

**修改前：**
```
提取帧 → 全部加入列表
```

**修改后：**
```
提取帧 → 计算pHash → 与上一保留帧比较差异 → 差异>15才保留
```

## 错误处理

- 图片读取失败：跳过该帧，记录日志
- 哈希计算失败：跳过该帧，记录日志

## 测试验证

1. 用视频运行，确认幻灯片数量减少
2. 验证关键帧（场景切换处）仍被保留
