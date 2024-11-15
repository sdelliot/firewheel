from enum import Enum, auto


class ScheduleEventType(Enum):
    """
    The possible types of allowed schedule events.
    """

    EXPERIMENT_START_TIME_SET = 0
    EMPTY_SCHEDULE = 1
    NEW_ITEM = auto()
    TRANSFER = auto()
    EXIT = auto()
    PAUSE = auto()
    RESUME = auto()
    UNKNOWN = auto()


class ScheduleEvent:
    """
    These objects get added to the event queue and
    processed by the VM Resource Handler launcher.
    """

    def __init__(self, event_type, data):
        """
        Create an event.

        Args:
            event_type (ScheduleEventType): Type of event
            data (object) : Event data to be processed
        """
        self.event_type = event_type
        self.data = data

    def __lt__(self, other):
        """
        Comparison function. If two events have the same start time
        then the ScheduleEvents will be compared on insert into the
        priority queue. If both event have the same start time then
        it doesn't matter which one gets put first in the queue, they
        will all be processed at the same time regardless. Therefore,
        just return True every time to create an arbitrary order of
        the ScheduleEvents in the priority queue.

        Args:
            other (int): A value for comparison. This argument is ignored.

        Returns:
            bool: True
        """
        return True

    def get_type(self):
        """
        Get the type of event.

        Returns:
            enum: Event type
        """
        return self.event_type

    def get_data(self):
        """
        Get the event's data

        Returns:
            object: The event data.
        """
        return self.data
