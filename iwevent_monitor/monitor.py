import subprocess
import threading
import enum


class IweventNotInstalledException(Exception):
    """Exception thrown when iwevent is not installed on the host OS"""
    pass


class UnsupportedEvent(Exception):
    """Exception thrown when trying to register a method to an unsupported iwevent"""
    pass


class UncleanShutdownException(Exception):
    """Raised when the IweventMonitor.stop() method cannot cleanly halt the monitor thread"""
    pass


class Iwevents(enum.Enum):
    """Currently supported list of events from iwevent"""
    ASSOCIATION_NEW = enum.auto()
    ASSOCIATION_LOST = enum.auto()

    @classmethod
    def check_value_existence(cls, enum_value):
        values = [item.value for item in cls]
        print(values)
        if enum_value not in values:
            raise ValueError("Unknown value [{}]".format(enum_value))


class IweventMonitor:
    """iwevent monitor tool
    Enables event driven code based on occurrences from wireless network interfaces

    Upon creating the monitoring process starts automatically in a seperate thread.
    Methods are (dynamically) added to the monitor tool through the supported dectorators/method:
        connect_event()
        disconnect_event()
        register_method_for_event(Iwevents value, method)

    IweventMonitor object needs to be cleaned up with its builtin stop() method.
    """
    def __init__(self):

        self.__check_iwevent_presence()
        self.monitor_thread = threading.Thread(target=self.__iwevent_parser)
        self.monitor_thread.start()
        self.iwevent_process = None

        self.connected_methods = {}
        for event in list(Iwevents):
            self.connected_methods[event.value] = []

    def __check_iwevent_presence(self):
        process = subprocess.run(['which', 'iwevent'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        if process.returncode is not 0:
            raise IweventNotInstalledException()

    def __process_single_event(self, data):
        data = data.lower()
        if "new access point/cell" not in data:
            return

        if len(self.connected_methods[Iwevents.ASSOCIATION_NEW.value]) > 0 and "not-associated" not in data:
            for method in self.connected_methods[Iwevents.ASSOCIATION_NEW.value]:
                method()

        if len(self.connected_methods[Iwevents.ASSOCIATION_LOST.value]) > 0 and "not-associated" in data:
            for method in self.connected_methods[Iwevents.ASSOCIATION_LOST.value]:
                method()

    def __iwevent_parser(self):
        self.iwevent_process = subprocess.Popen(['iwevent'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = self.iwevent_process.stdout.readline()
            if line.decode("utf-8") == "" or self.iwevent_process.poll():
                break
            self.__process_single_event(line.decode("utf-8"))
        self.iwevent_process.wait()

    def stop(self):
        """Stop the monitor
        :raises: UncleanShutdownException when the monitor thread cannot be killed.
        """
        if self.iwevent_process:
            self.iwevent_process.kill()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            if self.monitor_thread.is_alive(): # 5sec timeout
                raise UncleanShutdownException("Could not stop iwevent monitor thread.")

    def association_new_event(self):
        """Decorator for new association events"""
        def decorator(f):
            self.register_method_for_event(Iwevents.ASSOCIATION_NEW, f)
            return f
        return decorator

    def association_lost_event(self):
        """Decorator for lost association events"""
        def decorator(f):
            self.register_method_for_event(Iwevents.ASSOCIATION_LOST, f)
            return f
        return decorator

    def register_method_for_event(self, event, method):
        """Register a method for a given event
        IweventMonitor will execute all linked methods upon receiving the corresponding event
        :param event: Iwevents enum value (it is advised to use Iwevents directly
        :param method: Method to call
        :raises: UnsupportedEvent whenever a wrong event type is given
        """
        if isinstance(event, int) and not Iwevents.check_value_existence(event):
            raise UnsupportedEvent("Event [{}] unknown.".format(event))
        else:
            try:
                event = event.value
            except ValueError:
                raise UnsupportedEvent("Event [{}] unknown.".format(event))
        self.connected_methods[event].append(method)
