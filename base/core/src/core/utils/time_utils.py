import asyncio
import time

from core.context.context import Context, ContextHolder


class MusicTimer:
    def __init__(self, tick_ms=10):
        self.context : Context | None = None
        self.duration_ms = 0
        self.on_finished = None

        self._start_ts = 0.0
        self._elapsed_ms = 0.0
        self._running = False

        # worker
        self._stop_flag = False
        self._tick = tick_ms / 1000.0  # 转换为秒

    # ----------------------------------------------------
    # 对象生命周期：创建内部线程
    # ----------------------------------------------------
    def _ensure_worker(self):
        self._stop_flag = False
        asyncio.create_task(self._worker_loop())

    # ----------------------------------------------------
    # 供外部调用
    # ----------------------------------------------------
    def load(self, context: Context, duration_ms, on_finished=None):
        self.context = context
        self.duration_ms = int(duration_ms)
        self.on_finished = on_finished
        self._elapsed_ms = 0.0
        self._running = False
        self._start_ts = 0.0

        self._ensure_worker()

    def play(self):
        if self._running:
            return
        self._running = True
        self._start_ts = time.perf_counter()
        self._stop_flag = False

    def pause(self):
        if not self._running:
            return
        now = time.perf_counter()
        self._elapsed_ms += (now - self._start_ts) * 1000.0
        self._running = False

    def stop(self):
        """停止计时器，同时回收线程"""
        self._running = False
        self._stop_flag = True
        self._elapsed_ms = 0.0
        self._start_ts = 0.0
        self.duration_ms = 0

    def get_position_ms(self):
        if self._running:
            now = time.perf_counter()
            pos = self._elapsed_ms + (now - self._start_ts) * 1000.0
        else:
            pos = self._elapsed_ms
        return int(min(pos, self.duration_ms))

    # ----------------------------------------------------
    # 内部线程逻辑
    # ----------------------------------------------------
    async def _worker_loop(self):
        ContextHolder.set(self.context)
        while not self._stop_flag:
            await self.update()
            await asyncio.sleep(self._tick)

    async def update(self):
        """计时更新逻辑；由 worker 线程调用"""
        if not self._running:
            return

        pos = self.get_position_ms()
        if pos >= self.duration_ms > 0:
            # 到底，触发回调
            self._running = False
            self._elapsed_ms = float(self.duration_ms)
            if self.on_finished:
                await self.on_finished()

    # ----------------------------------------------------
    # 对象被回收时自动退出线程（可选）
    # ----------------------------------------------------
    def __del__(self):
        self.stop()