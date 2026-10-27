# Interface notes

## Control path

On the tested firmware, the `ubnt_diag_fan_control` library wrapper selects
override source 1 for ordinary clients and source 2 for the touchscreen client.
`swctrl fan set duty 30` uses source 1 and was rejected on the tested switch.

`fanctl` opens the native RPC connection with `rpc_init_check()`. It then calls
the exported function:

```c
rpcclt_usmDbBoxsFanOverrideSet(0, 2, 1, duty);
```

The arguments are unit 0, touchscreen override source 2, operation 1,
and duty. Duty `-1` requests automatic control.

This interface was identified through firmware analysis. Its ABI is not an
official compatibility guarantee. The tool has no hard-coded firmware offsets
and does not write to device registers directly.

## Build

The executable uses the switch's ARM/uClibc ABI and the dynamic loader
`/lib/ld-uClibc.so.0`. It loads these libraries from the device:

| Library | Purpose |
|---|---|
| `libubnt.so.1` | RPC initialization and fan override |
| `libc.so.0` | Process startup and output |
| `librpcclt.so` | Native switch RPC transport |
| `libz.so.1` | Dependency of the vendor runtime |

`fanctl-imports.S` contains original link-only stubs. The build gives each
import library the name used by the switch's runtime. The executable contains
dynamic symbol references, not copies of vendor code. At run time, the loader
resolves these symbols against the device's installed libraries.

**Never install the link-only import libraries on a switch.**
They do not implement these functions.

The small ARM startup routine calls the device's `__uClibc_main`. The build
does not need a vendor sysroot.

## Validation

Native tests use a mock RPC implementation. They cover all integer duties
from 0 to 100, automatic mode, connection checks, invalid input, and RPC errors.
These tests do not exercise physical fans.

Live checks on USW Enterprise 24 PoE firmware US.7.5.15 confirmed:

- A 30% request produces 29% reported duty for both fans.
- Manual duty remains active beyond the temporary diagnostic interval.
- `auto` restores the stock automatic duty.
- The stock touchscreen daemon and its startup entry remain unchanged.

Other devices and firmware versions are not verified. Sustained thermal safety
under maximum PoE and network load has not been established.
