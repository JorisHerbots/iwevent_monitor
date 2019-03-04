from iwevent_monitor.monitor import Iwevents, IweventMonitor
import sys
import time

print("Starting iwevent monitor!")
# Monitor object
monitor = IweventMonitor()


# Methods linked to wireless connect and disconnect events
@monitor.association_new_event()
def new():
    print("NEW ASSOCIATION FOUND")


@monitor.association_lost_event()
def lost():
    print("ASSOCIATION LOST")


try:
    # Example processing
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nInterrupt requested, cleaning up IweventMonitor object.")
    monitor.stop()
    sys.exit(0)
