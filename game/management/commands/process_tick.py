from django.core.management.base import BaseCommand
from game.models import GameTick


class Command(BaseCommand):
    help = 'Process a game tick (time-based progression)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously (for use with cron or scheduled tasks)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Processing game tick...')

        # Create and process new tick
        tick = GameTick.create_tick()
        stats = tick.process_tick()

        self.stdout.write(self.style.SUCCESS(f'Tick #{tick.tick_number} processed successfully!'))
        self.stdout.write(f'  Players processed: {stats["players_processed"]}')
        self.stdout.write(f'  Buildings completed: {stats["buildings_completed"]}')
        self.stdout.write(f'  Researches completed: {stats["researches_completed"]}')
        self.stdout.write(f'  Resources collected: {stats["resources_collected"]}')

        if options.get('continuous'):
            self.stdout.write('Continuous mode - tick processed. Schedule next tick via cron.')
