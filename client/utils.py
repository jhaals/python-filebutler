from datetime import datetime, timedelta

class ProgressMeter(object):
    '''
    Prints some data about the upload process.

    It currently updates once per second with filename, the progress expressed
    in percents, and the average transfer speed.
    '''

    def __init__(self):
        self.started = None
        self.previous_update = None
        self.previous_output = ''

    def __call__(self, param, current, total):
        now = datetime.now()

        # Is this the first time we're getting called?
        if self.previous_update is None:
            self.started = now
            self.previous_update = self.started

        # Update once per second
        if now - self.previous_update > timedelta(seconds=1):
            delta = now - self.started

            output = '{filename} {percent:.1%} {speed:.0f} KiB/s'.format(
                filename = param.name,
                percent = current / float(total),
                speed = current / float(delta.seconds) / 1024.0
            )

            sys.stdout.write('\r' + output)

            # If the previous output was longer than our current, we must "pad"
            # our output with spaces to prevent characters from the old output
            # to show up.
            output_delta = len(self.previous_output) - len(output)
            if output_delta > 0:
                sys.stdout.write(' ' * output_delta)

            sys.stdout.flush()

            self.previous_update = now

