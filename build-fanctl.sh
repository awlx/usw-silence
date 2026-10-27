#!/bin/sh
set -eu
cd "$(dirname "$0")"

: "${CLANG:=clang}"
: "${LLD:=ld.lld}"
mkdir -p build/fanctl

# Stripped firmware libraries have no section headers. Build import-only
# libraries so the linker can name the symbols provided by the live firmware.
"$CLANG" --target=armv7-linux-gnueabi -marm -mfloat-abi=soft \
    -DFANCTL_LIBUBNT -c fanctl-imports.S -o build/fanctl/ubnt-imports.o
"$CLANG" --target=armv7-linux-gnueabi -marm -mfloat-abi=soft \
    -c fanctl-imports.S -o build/fanctl/libc-imports.o
"$CLANG" --target=armv7-linux-gnueabi -marm -mfloat-abi=soft \
    -DFANCTL_DEPENDENCY -c fanctl-imports.S -o build/fanctl/dependency.o
"$LLD" -flavor gnu -m armelf_linux_eabi -shared -soname libubnt.so.1 \
    -o build/fanctl/libubnt-imports.so build/fanctl/ubnt-imports.o
"$LLD" -flavor gnu -m armelf_linux_eabi -shared -soname libc.so.0 \
    -o build/fanctl/libc-imports.so build/fanctl/libc-imports.o
"$LLD" -flavor gnu -m armelf_linux_eabi -shared -soname librpcclt.so \
    -o build/fanctl/rpc-imports.so build/fanctl/dependency.o
"$LLD" -flavor gnu -m armelf_linux_eabi -shared -soname libz.so.1 \
    -o build/fanctl/z-imports.so build/fanctl/dependency.o
"$CLANG" --target=armv7-linux-gnueabi -marm -mfloat-abi=soft \
    -O2 -Wall -Wextra -Werror -ffreestanding -fno-stack-protector -fno-pie \
    -c fanctl.c -o build/fanctl/fanctl.o
"$LLD" -flavor gnu -m armelf_linux_eabi \
    --dynamic-linker /lib/ld-uClibc.so.0 -e _start \
    -o fanctl build/fanctl/fanctl.o \
    build/fanctl/libubnt-imports.so build/fanctl/libc-imports.so \
    build/fanctl/rpc-imports.so build/fanctl/z-imports.so
