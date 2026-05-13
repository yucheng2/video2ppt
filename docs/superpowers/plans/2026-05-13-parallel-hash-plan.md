# Video2PPT 并发哈希计算实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将哈希计算从提取流程中分离，用多进程池并发计算，加速整体处理

**Architecture:** 两阶段并行：阶段1顺序提取帧，阶段2并发计算哈希，阶段3按序拼接去重

**Tech Stack:** multiprocessing.Pool, imagehash, cv2

---

## 文件结构

- 修改: `main.py` — Video2PPT 类

---

### Task 1: 添加 multiprocessing import

**Files:**
- Modify: `main.py:1-28` — import 区域

- [ ] **Step 1: 添加 multiprocessing import**

在文件头部添加：

```python
import multiprocessing
```

---

### Task 2: 新增 _compute_hash_for_file 独立函数

**Files:**
- Modify: `main.py` — Video2PPT 类外部定义

- [ ] **Step 1: 添加独立哈希计算函数**

在 `Video2PPT` 类定义之前（约第39行），添加：

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

---

### Task 3: 修改 extract_frames 只负责提帧

**Files:**
- Modify: `main.py:77-133` — `extract_frames` 方法

- [ ] **Step 1: 修改 extract_frames 不再计算哈希**

将 `extract_frames` 方法中第112-125行的哈希计算逻辑移除，改为只保存帧路径：

```python
def extract_frames(self) -> List[str]:
    """提帧阶段：只提取帧文件，返回帧路径列表"""
    logger.info("Starting frame extraction...")

    self.frames_dir = "temp_frames"
    os.makedirs(self.frames_dir, exist_ok=True)

    cap = cv2.VideoCapture(self.video_path)

    if not cap.isOpened():
        raise ValueError(f"Unable to open video file: {self.video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    logger.info(f"Video info - FPS: {fps:.2f}, Total frames: {total_frames}, Duration: {duration:.2f}s")

    frame_interval = int(fps * self.fps_interval)
    frame_count = 0
    extracted_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_path = os.path.join(self.frames_dir, f"frame_{extracted_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            self.frames.append(frame_path)
            extracted_count += 1

            if extracted_count % 10 == 0:
                logger.info(f"Extracted {extracted_count} frames")

        frame_count += 1

    cap.release()
    logger.info(f"Frame extraction complete. Total frames extracted: {extracted_count}")
    return self.frames
```

**注意：** 移除了哈希计算逻辑，保留 `return self.frames`。

---

### Task 4: 新增 compute_hashes 并发计算方法

**Files:**
- Modify: `main.py` — Video2PPT 类，在 `extract_frames` 之后添加

- [ ] **Step 1: 添加 compute_hashes 方法**

在 `extract_frames` 方法之后（约第134行），添加：

```python
def compute_hashes(self, frame_paths: List[str]) -> List[Tuple[int, imagehash.ImageHash, str]]:
    """并发计算所有帧的哈希"""
    logger.info(f"Computing hashes for {len(frame_paths)} frames using {multiprocessing.cpu_count()} workers...")

    pool = multiprocessing.Pool()
    args = [(i, fp) for i, fp in enumerate(frame_paths)]
    results = pool.map(_compute_hash_for_file, args)
    pool.close()
    pool.join()

    sorted_results = sorted(results, key=lambda x: x[0])  # 按 index 排序保证顺序
    logger.info("Hash computation complete.")
    return sorted_results
```

---

### Task 5: 修改 convert 方法整合三阶段

**Files:**
- Modify: `main.py:184-194` — `convert` 方法

- [ ] **Step 1: 重写 convert 方法**

替换原有 `convert` 方法：

```python
def convert(self) -> None:
    """完整转换流程：阶段1提帧 -> 阶段2并发哈希 -> 阶段3按序去重 -> 生成PPT"""
    try:
        # 阶段1: 提取帧
        frame_files = self.extract_frames()

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
        logger.info("Conversion completed successfully!")
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        raise
    finally:
        self.cleanup()
```

---

### Task 6: 测试验证

**Files:**
- 测试命令: `python main.py video.mp4 -o test_output.pptx`

- [ ] **Step 1: 运行转换**

Run: `cd /Users/yuchengfan/Downloads/video2ppt-main && python main.py video.mp4 -o test_output.pptx`

- [ ] **Step 2: 验证结果**

确认：
1. PPT 生成成功
2. 幻灯片顺序正确
3. 去重功能正常
4. 观察日志确认并发哈希计算执行

---

## 自检清单

- [ ] Spec 中每一项都有对应 task
- [ ] 无 placeholder (TBD/TODO)
- [ ] 方法名和属性名一致性检查
- [ ] 错误处理已包含
