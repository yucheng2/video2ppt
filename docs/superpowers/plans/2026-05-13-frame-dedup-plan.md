# Video2PPT 帧去重实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在帧提取阶段增加 pHash 相似度比较，移除相似帧减少冗余

**Architecture:** 在 `Video2PPT.extract_frames()` 中，提取帧后计算 pHash，与上一保留帧比较差异，差异>15 才加入列表

**Tech Stack:** imagehash, OpenCV, PIL

---

## 文件结构

- 修改: `main.py` — Video2PPT 类
- 修改: `requirements.txt` — 新增 imagehash 依赖

---

### Task 1: 添加 imagehash 依赖

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: 添加 imagehash 到 requirements.txt**

```
opencv-python
python-pptx
Pillow
numpy
imagehash
```

---

### Task 2: 添加 hash_threshold 参数和 last_hash 属性

**Files:**
- Modify: `main.py:41-63` — `__init__` 方法

- [ ] **Step 1: 添加 hash_threshold 参数和 last_hash 属性**

在 `__init__` 中，在现有属性后添加：

```python
self.hash_threshold = 15  # 哈希差异阈值，>15保留，≤15丢弃
self.last_hash = None      # 上一保留帧的哈希
```

---

### Task 3: 新增 _compute_frame_hash 方法

**Files:**
- Modify: `main.py` — Video2PPT 类

- [ ] **Step 1: 添加 _compute_frame_hash 方法**

在 `Video2PPT` 类中，在 `extract_frames` 方法之前添加：

```python
def _compute_frame_hash(self, image_path: str) -> imagehash.ImageHash:
    """计算单帧的感知哈希"""
    try:
        img = Image.open(image_path)
        return imagehash.phash(img)
    except Exception as e:
        logger.warning(f"Failed to compute hash for {image_path}: {e}")
        return None
```

---

### Task 4: 修改 extract_frames 方法增加去重逻辑

**Files:**
- Modify: `main.py:65-108` — `extract_frames` 方法

- [ ] **Step 1: 修改帧保留逻辑**

找到这段代码（约第96-100行）：

```python
if frame_count % frame_interval == 0:
    frame_path = os.path.join(self.frames_dir, f"frame_{extracted_count:04d}.jpg")
    cv2.imwrite(frame_path, frame)
    self.frames.append(frame_path)
    extracted_count += 1
```

替换为：

```python
if frame_count % frame_interval == 0:
    frame_path = os.path.join(self.frames_dir, f"frame_{extracted_count:04d}.jpg")
    cv2.imwrite(frame_path, frame)

    # 计算当前帧哈希并与上一保留帧比较
    current_hash = self._compute_frame_hash(frame_path)
    if current_hash is not None:
        if self.last_hash is None or abs(current_hash - self.last_hash) > self.hash_threshold:
            self.frames.append(frame_path)
            self.last_hash = current_hash
            extracted_count += 1
        else:
            logger.debug(f"Frame skipped (similar to previous): {frame_path}")
    else:
        # 哈希计算失败时保留帧
        self.frames.append(frame_path)
        self.last_hash = None
        extracted_count += 1
```

---

### Task 5: 添加 imagehash import

**Files:**
- Modify: `main.py:1-28` — 文件头部 import

- [ ] **Step 1: 添加 imagehash import**

在 import 区域添加：

```python
import imagehash
```

在 try 块中的 PIL import 之后添加：

```python
except ImportError as e:
    print(f"Error: Missing required library - {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# 尝试导入 imagehash
try:
    import imagehash
except ImportError:
    print("Error: Missing required library - imagehash")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)
```

---

### Task 6: 测试验证

**Files:**
- 测试命令: `python main.py video.mp4 -o test_output.pptx`

- [ ] **Step 1: 安装新依赖**

Run: `pip install imagehash`

- [ ] **Step 2: 运行转换**

Run: `python main.py video.mp4 -o test_output.pptx`

- [ ] **Step 3: 验证结果**

确认 PPT 生成成功，幻灯片数量比之前少

---

## 自检清单

- [ ] Spec 中每一项都有对应 task
- [ ] 无 placeholder (TBD/TODO)
- [ ] 方法名和属性名一致性检查
- [ ] 错误处理已包含
