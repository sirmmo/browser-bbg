"""
Async Tick Service
Runs game ticks continuously in the background using asyncio
"""
import asyncio
import logging
from datetime import datetime
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class TickService:
    """Async service that processes game ticks at regular intervals"""

    def __init__(self, interval_seconds=60):
        """
        Initialize the tick service

        Args:
            interval_seconds: Time between ticks in seconds (default: 60)
        """
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.task = None
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """Start the tick service"""
        if self.is_running:
            logger.warning("Tick service is already running")
            return

        self.is_running = True
        logger.info(f"Starting tick service with {self.interval_seconds}s interval")

        try:
            await self._run_loop()
        except asyncio.CancelledError:
            logger.info("Tick service cancelled")
        except Exception as e:
            logger.error(f"Tick service error: {e}", exc_info=True)
        finally:
            self.is_running = False
            logger.info("Tick service stopped")

    async def _run_loop(self):
        """Main async loop that processes ticks"""
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Process a tick
                await self._process_tick()

                # Wait for next interval or shutdown signal
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self.interval_seconds
                    )
                    # If we get here, shutdown was requested
                    break
                except asyncio.TimeoutError:
                    # Timeout is normal - continue to next tick
                    pass

            except Exception as e:
                logger.error(f"Error processing tick: {e}", exc_info=True)
                # Continue running even if one tick fails
                await asyncio.sleep(5)  # Brief pause before retrying

    async def _process_tick(self):
        """Process a single game tick asynchronously"""
        start_time = timezone.now()

        try:
            # Import here to avoid circular imports
            from game.models import GameTick

            # Create tick (sync operation wrapped in async)
            tick = await sync_to_async(GameTick.create_tick)()
            tick_number = tick.tick_number

            logger.info(f"Processing tick #{tick_number}")

            # Process tick (sync operation wrapped in async)
            stats = await sync_to_async(tick.process_tick)()

            # Calculate processing time
            duration = (timezone.now() - start_time).total_seconds()

            logger.info(
                f"Tick #{tick_number} completed in {duration:.2f}s - "
                f"Players: {stats['players_processed']}, "
                f"Buildings: {stats['buildings_completed']}, "
                f"Researches: {stats['researches_completed']}"
            )

        except Exception as e:
            logger.error(f"Failed to process tick: {e}", exc_info=True)
            raise

    async def stop(self):
        """Stop the tick service gracefully"""
        if not self.is_running:
            logger.warning("Tick service is not running")
            return

        logger.info("Stopping tick service...")
        self.is_running = False
        self._shutdown_event.set()

        # Wait for current tick to complete (max 30 seconds)
        if self.task:
            try:
                await asyncio.wait_for(self.task, timeout=30)
            except asyncio.TimeoutError:
                logger.warning("Tick service did not stop gracefully, forcing cancellation")
                self.task.cancel()

    def run_in_background(self):
        """
        Run the tick service in the background
        Returns the asyncio Task
        """
        if self.task and not self.task.done():
            logger.warning("Tick service task already exists")
            return self.task

        self.task = asyncio.create_task(self.start())
        return self.task


# Global instance
_tick_service = None


def get_tick_service(interval_seconds=60):
    """Get or create the global tick service instance"""
    global _tick_service
    if _tick_service is None:
        _tick_service = TickService(interval_seconds=interval_seconds)
    return _tick_service


async def start_tick_service(interval_seconds=60):
    """Start the global tick service"""
    service = get_tick_service(interval_seconds)
    await service.start()


async def stop_tick_service():
    """Stop the global tick service"""
    global _tick_service
    if _tick_service:
        await _tick_service.stop()
        _tick_service = None
