def evaluate_volume(volume_ratio):
    if volume_ratio >= 1.5:
        return True, f"Strong volume confirmation ({volume_ratio:.2f}x)"
    return False, f"Weak volume ({volume_ratio:.2f}x)"
