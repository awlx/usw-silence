# USW Silence

A small, unofficial command-line tool to set the fan duty on a UniFi switch.
It uses libraries already installed on the switch. It does not patch firmware,
replace the touchscreen daemon, or change startup files.

**Verified hardware:** USW Enterprise 24 PoE, firmware **US.7.5.15**.
Other models and firmware versions are not verified.

## Safety

**Manual duty is fixed. It does not increase with temperature.**
Low duty can cause overheating, especially under high PoE or network load.
Monitor temperatures and fan speeds. Use `fanctl auto` to restore automatic
control. Do not select a duty that stops a fan.

This tool uses an undocumented interface. Firmware updates can break it.
Use it at your own risk. This project is not affiliated with Ubiquiti.

## Build

You need Clang with ARM support, LLD, Python 3, and a native C compiler.
No vendor SDK, firmware image, or extracted library is needed.

```sh
git clone https://github.com/awlx/usw-silence.git
cd usw-silence
sh build-fanctl.sh
python3 -m unittest -v test_fanctl.py
```

Set `CLANG` and `LLD` if the tools are not on your path:

```sh
CLANG=/path/to/clang LLD=/path/to/ld.lld sh build-fanctl.sh
```

The Rust toolchain's `rust-lld` also works as `LLD`.
The output is `fanctl`, a 32-bit ARM executable for the tested switch.

## Install

Copy **only `fanctl`**. Never copy the import libraries from `build/`.

```sh
scp -O ./fanctl USER@SWITCH:/tmp/fanctl.new
```

Compare its SHA-256 on your computer and the switch before installation:

```sh
# Computer: use sha256sum, or shasum -a 256 on macOS.
sha256sum fanctl

# Switch:
sha256sum /tmp/fanctl.new
chmod 755 /tmp/fanctl.new
mv /tmp/fanctl.new /tmp/fanctl
/tmp/fanctl check
```

`check` opens the RPC connection but does not change the fan setting.
It does not prove that the hardware supports manual control.

## Use

Run these commands on the switch:

```sh
/tmp/fanctl 30     # Request 30% duty for both fans.
/tmp/fanctl auto   # Restore automatic control.
swctrl env show   # Read temperature, duty, and fan speed.
```

The accepted duty range is 0 to 100. On the tested switch, a 30% request
reports approximately 29%. This is an example, not a safe setting for all loads.
Automatic duty can take a control cycle to update after `auto`.

The tool exits with status 0 when the request succeeds, 1 for an RPC error,
or 2 for invalid input. Always check the actual duty with `swctrl env show`.

The executable in `/tmp` is lost on reboot. No boot hook is installed.
Before removing the tool, run `/tmp/fanctl auto` and confirm automatic control.

See [the interface notes](docs/interface.md) for the control path and build details.

## License

[MIT](LICENSE). No vendor firmware or libraries are included.
