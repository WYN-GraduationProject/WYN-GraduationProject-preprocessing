import time


class FPSCalculator:
    """
    计算FPS的类
    """
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()

    async def update(self):
        """
        更新FPS
        :return: FPS
        """
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed > 0:
            fps = self.frame_count / elapsed
        else:
            fps = 0
        return fps
