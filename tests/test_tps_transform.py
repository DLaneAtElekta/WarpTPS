"""
Comprehensive unit tests for TPSTransform - Python version of C++ unit tests.

These tests correspond to the C++ unit tests in WarpTpsLib.UnitTests/WarpTpsLibTests.cpp
"""
import numpy as np
import pytest
import warptps


class TestTPSTransform:
    """Test class for TPS Transform - mirrors C++ TPSTransformUnitTest"""

    def test_add_landmark_identity(self):
        """
        Test adding landmarks with identity transform (source == dest).
        Corresponds to C++ TestAddLandmark
        """
        tps = warptps.TPSTransform()

        # Add landmarks where source and dest are the same
        landmarks = [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.25, 0.5, 0.0)
        ]

        for landmark in landmarks:
            tps.add_landmark_tuple(landmark, landmark)

        assert tps.get_landmark_count() == 4, "Should have 4 landmarks"

        # For identity transform, landmarks should remain unchanged
        # Note: Python bindings don't expose GetLandmark<N>, but we can test
        # by evaluating at those points
        for landmark in landmarks:
            offset = tps.eval(landmark, percent=1.0)
            transformed = tuple(landmark[i] + offset[i] for i in range(3))

            # Check that transformation is approximately identity
            for i in range(3):
                assert abs(transformed[i] - landmark[i]) < 1e-6, \
                    f"Identity transform failed at {landmark}: got {transformed}"

    def test_add_landmark_2d(self):
        """Test adding 2D landmarks (x, y only)"""
        tps = warptps.TPSTransform()

        # Add 2D landmarks
        landmarks_2d = [
            ((0.0, 0.0), (0.0, 0.0)),
            ((1.0, 0.0), (1.0, 0.0)),
            ((0.0, 1.0), (0.0, 1.0)),
            ((0.5, 0.5), (0.5, 0.5))
        ]

        for src, dst in landmarks_2d:
            tps.add_landmark_tuple(src, dst)

        assert tps.get_landmark_count() == 4

    def test_warp_at_landmarks(self):
        """
        Test that warping at landmark points gives exact destination.
        Corresponds to C++ TestWarpAtLandmarks
        """
        tps = warptps.TPSTransform()

        # Add landmarks with slight variations (corners of a square)
        landmarks = [
            ((-1.0, -1.0, 0.0), (-1.0, -1.0, 0.0)),  # identity at corner
            ((-1.0, 1.1, 0.0), (-1.0, 1.1, 0.0)),    # identity at corner
            ((1.1, 1.0, 0.0), (1.1, 1.0, 0.0)),      # identity at corner
            ((0.9, -1.0, 0.0), (0.9, -1.0, 0.0)),    # identity at corner
            ((0.0, 0.0, 0.0), (0.1, -0.2, 0.0))      # divergent landmark in center
        ]

        for src, dst in landmarks:
            tps.add_landmark_tuple(src, dst)

        assert tps.get_landmark_count() == 5

        # Test that each source landmark transforms to its destination
        for src, dst in landmarks:
            offset = tps.eval(src, percent=1.0)
            transformed = tuple(src[i] + offset[i] for i in range(3))

            # Check each coordinate
            for i in range(3):
                assert abs(transformed[i] - dst[i]) < 1e-6, \
                    f"Landmark transform failed: {src} -> {transformed}, expected {dst}"

    def test_warp_at_landmarks_2d(self):
        """Test warping at 2D landmarks"""
        tps = warptps.TPSTransform()

        # Add 2D landmarks with non-identity transform
        landmarks = [
            ((100.0, 100.0), (110.0, 110.0)),
            ((200.0, 100.0), (210.0, 105.0)),
            ((150.0, 200.0), (155.0, 210.0)),
            ((100.0, 200.0), (105.0, 205.0))
        ]

        for src, dst in landmarks:
            tps.add_landmark_tuple(src, dst)

        # Test that each source landmark transforms to its destination
        for src, dst in landmarks:
            offset = tps.eval(src, percent=1.0)
            transformed = (src[0] + offset[0], src[1] + offset[1])

            # Check each coordinate (2D only)
            for i in range(2):
                assert abs(transformed[i] - dst[i]) < 1e-4, \
                    f"2D landmark transform failed: {src} -> {transformed}, expected {dst}"

    def test_transform_points_at_landmarks(self):
        """Test transform_points method at landmark positions"""
        tps = warptps.TPSTransform()

        # Add landmarks
        source_landmarks = np.array([
            [100, 100],
            [200, 100],
            [150, 200],
            [100, 200]
        ], dtype=np.float64)

        dest_landmarks = np.array([
            [110, 110],
            [210, 105],
            [155, 210],
            [105, 205]
        ], dtype=np.float64)

        tps.add_landmarks(source_landmarks, dest_landmarks)

        # Transform the source landmarks
        transformed = tps.transform_points(source_landmarks, percent=1.0)

        # Check that they match the destination
        for i in range(len(source_landmarks)):
            for j in range(2):
                assert abs(transformed[i, j] - dest_landmarks[i, j]) < 1e-4, \
                    f"Point {i} coord {j}: {transformed[i, j]} != {dest_landmarks[i, j]}"

    def test_partial_morph(self):
        """Test partial morphing with percent < 1.0"""
        tps = warptps.TPSTransform()

        # Add a simple landmark pair
        src = (100.0, 100.0)
        dst = (120.0, 110.0)
        tps.add_landmark_tuple(src, dst)

        # Test at 0%, 50%, 100%
        for percent in [0.0, 0.5, 1.0]:
            offset = tps.eval(src, percent=percent)
            transformed = (src[0] + offset[0], src[1] + offset[1])

            # Expected values
            expected_x = src[0] + percent * (dst[0] - src[0])
            expected_y = src[1] + percent * (dst[1] - src[1])

            assert abs(transformed[0] - expected_x) < 1e-4, \
                f"At {percent*100}%: x={transformed[0]}, expected={expected_x}"
            assert abs(transformed[1] - expected_y) < 1e-4, \
                f"At {percent*100}%: y={transformed[1]}, expected={expected_y}"

    def test_inverse_warp_at_landmarks(self):
        """
        Test inverse warping by swapping source and destination.
        Corresponds to C++ TestInverseWarpAtLandmark (which was empty in C++)
        """
        # Create forward transform
        tps_forward = warptps.TPSTransform()

        source_landmarks = np.array([
            [100, 100],
            [200, 100],
            [150, 200]
        ], dtype=np.float64)

        dest_landmarks = np.array([
            [110, 110],
            [210, 105],
            [155, 210]
        ], dtype=np.float64)

        tps_forward.add_landmarks(source_landmarks, dest_landmarks)

        # Create inverse transform (swap source and dest)
        tps_inverse = warptps.TPSTransform()
        tps_inverse.add_landmarks(dest_landmarks, source_landmarks)

        # Test that inverse transform brings us back to source
        for i, src in enumerate(source_landmarks):
            # Forward transform
            offset_fwd = tps_forward.eval(tuple(src), percent=1.0)
            transformed = src + np.array(offset_fwd[:2])

            # Inverse transform
            offset_inv = tps_inverse.eval(tuple(transformed), percent=1.0)
            back_to_source = transformed + np.array(offset_inv[:2])

            # Should be close to original source
            for j in range(2):
                assert abs(back_to_source[j] - src[j]) < 1e-2, \
                    f"Inverse transform failed: {src} -> {transformed} -> {back_to_source}"

    def test_remove_all_landmarks(self):
        """Test removing all landmarks"""
        tps = warptps.TPSTransform()

        tps.add_landmark_tuple((100, 100), (110, 110))
        tps.add_landmark_tuple((200, 100), (210, 110))
        assert tps.get_landmark_count() == 2

        tps.remove_all_landmarks()
        assert tps.get_landmark_count() == 0

    def test_set_parameters(self):
        """Test setting r_exponent and k parameters"""
        tps = warptps.TPSTransform()

        # Test setting parameters (should not raise)
        tps.set_r_exponent(2.5)
        tps.set_k(0.5)

        # Add landmarks and verify transform still works
        tps.add_landmark_tuple((100, 100), (110, 110))
        tps.add_landmark_tuple((200, 100), (210, 110))

        offset = tps.eval((150, 100), percent=1.0)
        assert isinstance(offset, tuple)
        assert len(offset) == 3

    def test_image_warp_basic(self):
        """Test basic image warping functionality"""
        tps = warptps.TPSTransform()

        # Create a simple test image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[40:60, 40:60] = [255, 255, 255]  # White square

        # Add landmarks
        tps.add_landmark_tuple((50, 50), (55, 55))
        tps.add_landmark_tuple((25, 25), (25, 25))
        tps.add_landmark_tuple((75, 75), (75, 75))

        # Warp image
        warped = tps.warp(img, percent=1.0)

        assert warped.shape == img.shape
        assert warped.dtype == np.uint8
        # Image should have changed (not identical)
        assert not np.array_equal(warped, img)

    def test_image_warp_with_field(self):
        """Test image warping with presampled field"""
        tps = warptps.TPSTransform()

        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[40:60, 40:60] = 255

        tps.add_landmark_tuple((50, 50), (60, 60))
        tps.add_landmark_tuple((25, 25), (25, 25))
        tps.add_landmark_tuple((75, 75), (75, 75))

        # Warp with field (default)
        warped_with_field = tps.warp(img, percent=1.0, use_field=True)

        # Warp without field
        warped_no_field = tps.warp(img, percent=1.0, use_field=False)

        assert warped_with_field.shape == warped_no_field.shape
        # Results should be very similar (within tolerance due to interpolation)
        diff = np.abs(warped_with_field.astype(np.float32) - warped_no_field.astype(np.float32))
        mean_diff = np.mean(diff)
        assert mean_diff < 5.0, f"Field and non-field warping differ too much: {mean_diff}"


class TestConvenienceFunctions:
    """Test convenience functions warp_image and morph_images"""

    def test_warp_image_function(self):
        """Test the warp_image convenience function"""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[40:60, 40:60] = 255

        source_landmarks = np.array([[50, 50], [25, 25], [75, 75]], dtype=np.float64)
        dest_landmarks = np.array([[55, 55], [25, 25], [75, 75]], dtype=np.float64)

        warped = warptps.warp_image(
            img, source_landmarks, dest_landmarks,
            percent=1.0, r_exponent=2.0, k=1.0
        )

        assert warped.shape == img.shape
        assert warped.dtype == np.uint8

    def test_morph_images_function(self):
        """Test the morph_images convenience function"""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img1[40:60, 40:60] = [255, 0, 0]  # Red

        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2[40:60, 40:60] = [0, 0, 255]  # Blue

        landmarks1 = np.array([[50, 50], [40, 40], [60, 60]], dtype=np.float64)
        landmarks2 = np.array([[50, 50], [45, 40], [55, 60]], dtype=np.float64)

        frames = warptps.morph_images(img1, img2, landmarks1, landmarks2, num_frames=4)

        assert len(frames) == 5  # num_frames + 1
        assert all(frame.shape == img1.shape for frame in frames)
        assert all(frame.dtype == np.uint8 for frame in frames)

        # First frame should be close to img1
        assert np.mean(np.abs(frames[0].astype(float) - img1.astype(float))) < 50
        # Last frame should be close to img2
        assert np.mean(np.abs(frames[-1].astype(float) - img2.astype(float))) < 50


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_no_landmarks_eval(self):
        """Test evaluating with no landmarks"""
        tps = warptps.TPSTransform()

        # Should return zero offset
        offset = tps.eval((100, 100), percent=1.0)
        assert abs(offset[0]) < 1e-10
        assert abs(offset[1]) < 1e-10

    def test_single_landmark(self):
        """Test with just one landmark"""
        tps = warptps.TPSTransform()
        tps.add_landmark_tuple((100, 100), (110, 110))

        # Should still work
        offset = tps.eval((100, 100), percent=1.0)
        assert isinstance(offset, tuple)

    def test_grayscale_image(self):
        """Test warping grayscale image"""
        tps = warptps.TPSTransform()

        img_gray = np.zeros((100, 100), dtype=np.uint8)
        img_gray[40:60, 40:60] = 255

        tps.add_landmark_tuple((50, 50), (55, 55))
        tps.add_landmark_tuple((25, 25), (25, 25))

        warped = tps.warp(img_gray, percent=1.0)

        # Should handle grayscale
        assert warped.shape == img_gray.shape or warped.shape == (100, 100, 1)
        assert warped.dtype == np.uint8

    def test_invalid_image_dtype(self):
        """Test that non-uint8 images raise error"""
        tps = warptps.TPSTransform()
        tps.add_landmark_tuple((50, 50), (55, 55))

        img_float = np.zeros((100, 100, 3), dtype=np.float32)

        with pytest.raises(ValueError, match="uint8"):
            tps.warp(img_float, percent=1.0)

    def test_mismatched_landmark_shapes(self):
        """Test that mismatched landmark arrays raise error"""
        tps = warptps.TPSTransform()

        source = np.array([[100, 100], [200, 100]])
        dest = np.array([[110, 110]])  # Different size

        with pytest.raises(ValueError, match="same shape"):
            tps.add_landmarks(source, dest)

    def test_invalid_point_dimensions(self):
        """Test that invalid point dimensions raise error"""
        tps = warptps.TPSTransform()

        # 1D points should fail
        with pytest.raises(ValueError):
            tps.add_landmarks(np.array([[100]]), np.array([[110]]))

        # 4D points should fail
        with pytest.raises(ValueError):
            tps.add_landmarks(
                np.array([[100, 100, 0, 0]]),
                np.array([[110, 110, 0, 0]])
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
