# iwevent monitor
**Requirement**: `iwevent` from the `wireless_tools` linux package

Enables event driven code based on occurrences from wireless network interfaces

## Usage
1. Create a `IweventMonitor` object - this will spawn a separate monitor thread based on `iwevent`
1. Link methods to supported events using predefined decorators or manually
    * `association_new_event()` - triggers whenever a WiFi connection is established
    * `association_lost_event()` - triggers whenever a WiFi connection is lost
    * `register_method_for_event(event, method)` - manually register a method

Linked methods will automatically be executed whenever their corresponding wireless interface event is detected.
Currently supported events: connection established, connection lost

IweventMonitor contains two parameters which decide how linked methods are executed:
* `use_threading` (default `True`) - Uses threads to call each method; specifying this as `False` will execute all linked methods consecutively in order of linking
* `daemonized_threads` (default `False`) - Spawns threads as daemons

## Example
See `example.py`.