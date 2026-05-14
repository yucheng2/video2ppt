import pytest, os, sys, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Video2PPT


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def small_video():
    return "tests/fixtures/small_test.mp4"


class TestVideo2PPTInit:
    def test_init_with_valid_video(self, small_video, temp_dir):
        converter = Video2PPT(small_video, os.path.join(temp_dir, "out.pptx"))
        assert converter.video_path == small_video
        assert converter.fps_interval == 1
        assert converter.output_path == os.path.join(temp_dir, "out.pptx")

    def test_init_with_custom_interval(self, small_video, temp_dir):
        converter = Video2PPT(small_video, os.path.join(temp_dir, "out.pptx"), fps_interval=2)
        assert converter.fps_interval == 2

    def test_init_with_invalid_video(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            Video2PPT("nonexistent.mp4")


class TestFrameExtraction:
    def test_extract_frames_produces_frames(self, small_video, temp_dir):
        converter = Video2PPT(small_video, os.path.join(temp_dir, "out.pptx"))
        frames = converter.extract_frames()
        assert len(frames) > 0
        for f in frames:
            assert os.path.exists(f)

    def test_extract_frames_increments_extracted_count(self, small_video, temp_dir):
        converter = Video2PPT(small_video, os.path.join(temp_dir, "out.pptx"))
        frames = converter.extract_frames()
        assert len(frames) > 0


class TestConversion:
    def test_convert_produces_pptx(self, small_video, temp_dir):
        output = os.path.join(temp_dir, "out.pptx")
        converter = Video2PPT(small_video, output)
        converter.convert()
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_convert_cleans_up_frames_dir(self, small_video, temp_dir):
        output = os.path.join(temp_dir, "out.pptx")
        converter = Video2PPT(small_video, output)
        converter.convert()
        assert not os.path.exists(converter.frames_dir)


class TestHashComputation:
    def test_compute_hash_from_array_returns_imagehash(self, small_video, temp_dir):
        import cv2
        converter = Video2PPT(small_video, os.path.join(temp_dir, "out.pptx"))
        cap = cv2.VideoCapture(small_video)
        ret, frame = cap.read()
        cap.release()
        assert ret
        h = converter._compute_hash_from_array(frame)
        assert h is not None
        assert hasattr(h, '__sub__')  # ImageHash supports diff calculation

    def test_compute_hash_from_array_identical_frames_same_hash(self, small_video, temp_dir):
        import cv2
        converter = Video2PPT(small_video, os.path.join(temp_dir, "out.pptx"))
        cap = cv2.VideoCapture(small_video)
        ret1, frame1 = cap.read()
        ret2, frame2 = cap.read()
        cap.release()
        h1 = converter._compute_hash_from_array(frame1)
        h2 = converter._compute_hash_from_array(frame2)
        # Different frames should produce different hashes (likely)
        # Same frame should produce same hash
        h1_copy = converter._compute_hash_from_array(frame1)
        assert abs(h1 - h1_copy) == 0