import asyncio
import signal
import sys
from django.core.management.base import BaseCommand
from game.models import GameTick
from game.services.tick_service import TickService


class Command(BaseCommand):
    help = 'Process game ticks (time-based progression)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            dest='async_mode',
            help='Run async tick service in continuous loop',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval between ticks in seconds (default: 60)',
        )

    def handle(self, *args, **options):
        if options.get('async_mode'):
            self._run_async_service(options['interval'])
        else:
            self._process_single_tick()

    def _process_single_tick(self):
        """Process a single game tick (synchronous)"""
        self.stdout.write('Processing game tick...')

        # Create and process new tick
        tick = GameTick.create_tick()
        stats = tick.process_tick()

        self.stdout.write(self.style.SUCCESS(f'Tick #{tick.tick_number} processed successfully!'))
        self.stdout.write(f'  Players processed: {stats["players_processed"]}')
        self.stdout.write(f'  Buildings completed: {stats["buildings_completed"]}')
        self.stdout.write(f'  Researches completed: {stats["researches_completed"]}')
        self.stdout.write(f'  Resources collected: {stats["resources_collected"]}')

    def _run_async_service(self, interval):
        """Run the async tick service continuously"""
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting async tick service (interval: {interval}s)\n'
                f'Press Ctrl+C to stop gracefully...'
            )
        )

        # Create tick service
        service = TickService(interval_seconds=interval)

        # Set up signal handlers for graceful shutdown
        shutdown_event = asyncio.Event()

        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('\nShutdown signal received...'))
            shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run the async service
        try:
            asyncio.run(self._async_main(service, shutdown_event))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Interrupted by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Service error: {e}'))
            sys.exit(1)
        finally:
            self.stdout.write(self.style.SUCCESS('Tick service stopped'))

    async def _async_main(self, service, shutdown_event):
        """Main async entry point"""
        # Start the service in background
        service_task = asyncio.create_task(service.start())

        # Wait for shutdown signal
        await shutdown_event.wait()

        # Stop the service gracefully
        await service.stop()

        # Wait for service task to complete
        try:
            await asyncio.wait_for(service_task, timeout=5)
        except asyncio.TimeoutError:
            service_task.cancel()
