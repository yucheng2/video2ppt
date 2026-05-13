# Video2PPT 帧提取优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 恢复顺序处理逻辑，在提帧时做快速像素差异预过滤，减少无效磁盘I/O和pHash计算

**Architecture:** 帧提取时先做像素级差异比较，大差异直接保存，疑似相似才走pHash精确比较

**Tech Stack:** OpenCV, numpy, imagehash

---

## 文件结构

- 修改: `main.py` — Video2PPT 类

---

### Task 1: 添加 pixel_threshold 参数

**Files:**
- Modify: `main.py:55-79` — `__init__` 方法

- [ ] **Step 1: 添加 pixel_threshold 属性**

在 `__init__` 方法中，在 `hash_threshold` 后添加：

```python
self.pixel_threshold = 30  # 像素差异阈值，>30直接保存，≤30走pHash
```

---

### Task 2: 重写 extract_frames 添加预过滤逻辑

**Files:**
- Modify: `main.py:90-131` — `extract_frames` 方法

- [ ] **Step 1: 重写 extract_frames**

用以下代码替换现有的 `extract_frames` 方法：

```python
def extract_frames(self) -> List[str]:
    """提帧阶段：快速预过滤 + 精确去重"""
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
    last_frame = None  # 上一帧的numpy数组

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_path = os.path.join(self.frames_dir, f"frame_{extracted_count:04d}.jpg")

            if last_frame is not None:
                # 快速像素差异比较
                diff = np.mean(np.abs(frame.astype(float) - last_frame.astype(float)))

                if diff > self.pixel_threshold:
                    # 差异大，直接保存
                    cv2.imwrite(frame_path, frame)
                    self.frames.append(frame_path)
                    self.last_hash = self._compute_frame_hash(frame_path)
                    extracted_count += 1
                    logger.debug(f"Frame {extracted_count}: diff={diff:.2f}, direct save")
                else:
                    # 疑似相似，pHash精确比较
                    current_hash = self._compute_frame_hash(frame_path)
                    if current_hash is not None:
                        if self.last_hash is None or \
                           abs(current_hash - self.last_hash) > self.hash_threshold:
                            cv2.imwrite(frame_path, frame)
                            self.frames.append(frame_path)
                            self.last_hash = current_hash
                            extracted_count += 1
                            logger.debug(f"Frame {extracted_count}: diff={diff:.2f}, pHash save")
                        else:
                            logger.debug(f"Frame skipped (similar): diff={diff:.2f}")
                            cv2.imwrite(frame_path, frame)  # 仍保存用于后续可能的处理
                            extracted_count += 1
                    else:
                        # pHash计算失败，保存帧
                        cv2.imwrite(frame_path, frame)
                        self.frames.append(frame_path)
                        self.last_hash = None
                        extracted_count += 1
            else:
                # 第一帧，直接保存
                cv2.imwrite(frame_path, frame)
                self.frames.append(frame_path)
                self.last_hash = self._compute_frame_hash(frame_path)
                extracted_count += 1

            last_frame = frame.copy()

            if extracted_count % 10 == 0:
                logger.info(f"Extracted {extracted_count} frames")

        frame_count += 1

    cap.release()
    logger.info(f"Frame extraction complete. Total frames extracted: {extracted_count}")
    return self.frames
```

---

### Task 3: 修改 convert 方法恢复顺序流程

**Files:**
- Modify: `main.py:196-227` — `convert` 方法

- [ ] **Step 1: 简化 convert 方法**

extract_frames 现在已经包含了去重逻辑，convert 方法只需要调用它并生成PPT：

```python
def convert(self) -> None:
    """完整转换流程：提帧(含去重) -> 生成PPT"""
    try:
        self.extract_frames()
        self.generate_ppt()
        logger.info("Conversion completed successfully!")
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        raise
    finally:
        self.cleanup()
```

---

### Task 4: 移除不需要的代码

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 移除 multiprocessing import**

删除第14行的 `import multiprocessing`

- [ ] **Step 2: 移除 compute_hashes 方法**

删除第133-145行的 `compute_hashes` 方法

- [ ] **Step 3: 移除 _compute_hash_for_file 函数**

删除第40-49行的 `_compute_hash_for_file` 函数

---

### Task 5: 测试验证

**Files:**
- 测试命令: `python main.py video.mp4 -o test_output.pptx`

- [ ] **Step 1: 运行转换**

Run: `cd /Users/yuchengfan/Downloads/video2ppt-main && python main.py video.mp4 -o test_output.pptx`

- [ ] **Step 2: 验证结果**

确认：
1. PPT 生成成功
2. 日志显示 "Extracted X frames"
3. 幻灯片数量合理（之前 ~31 张）
4. 处理时间明显减少

---

## 自检清单

- [ ] Spec 中每一项都有对应 task
- [ ] 无 placeholder (TBD/TODO)
- [ ] 方法名和属性名一致性检查
- [ ] 错误处理已包含
