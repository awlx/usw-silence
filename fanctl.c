/* The prototypes below match the switch's ARM/uClibc ABI. No SDK is needed. */
extern int printf(const char *, ...);
extern int puts(const char *);
extern int rpc_init_check(void);
extern int rpcclt_usmDbBoxsFanOverrideSet(unsigned int, unsigned int,
                                       unsigned int, int);

enum {
    FAN_SOURCE_TOUCHSCREEN = 2,
    FAN_OPERATION_DUTY = 1
};

static int equal(const char *a, const char *b)
{
    while (*a && *a == *b) {
        ++a;
        ++b;
    }
    return *a == *b;
}

int main(int argc, char **argv)
{
    int duty = 0;
    int check = argc == 2 && equal(argv[1], "check");

    if (argc != 2) {
        puts("usage: fanctl check | auto | DUTY (0-100)");
        return 2;
    }
    if (equal(argv[1], "auto")) {
        duty = -1;
    } else if (!check) {
        const char *p = argv[1];
        if (!*p) {
            puts("error: duty must be an integer from 0 to 100");
            return 2;
        }
        for (; *p; ++p) {
            if (*p < '0' || *p > '9' || duty > 10) {
                puts("error: duty must be an integer from 0 to 100");
                return 2;
            }
            duty = duty * 10 + *p - '0';
        }
        if (duty > 100) {
            puts("error: duty must be an integer from 0 to 100");
            return 2;
        }
    }

    int rc = rpc_init_check();
    if (rc != 0) {
        printf("error: switch RPC initialization failed: %d\n", rc);
        return 1;
    }
    if (check) {
        puts("switch RPC connection ready; no fan setting changed");
        return 0;
    }

    rc = rpcclt_usmDbBoxsFanOverrideSet(0, FAN_SOURCE_TOUCHSCREEN,
                                     FAN_OPERATION_DUTY, duty);
    if (rc != 0) {
        printf("error: fan override failed: %d\n", rc);
        return 1;
    }
    if (duty == -1) {
        puts("automatic fan control requested; verify with swctrl env show");
    } else {
        printf("requested %d%% duty; verify with swctrl env show\n", duty);
    }
    return 0;
}

#if defined(__arm__) && !defined(FANCTL_TEST)
__asm__(
    ".text\n"
    ".arm\n"
    ".global _start\n"
    ".type _start, %function\n"
    "_start:\n"
    "mov fp, #0\n"
    "mov lr, #0\n"
    "pop {r1}\n"
    "mov r2, sp\n"
    "push {r2}\n"
    "push {r0}\n"
    "mov r3, #0\n"
    "push {r3}\n"
    "ldr r0, =main\n"
    "b __uClibc_main\n"
    ".size _start, .-_start\n"
    ".section .note.GNU-stack,\"\",%progbits\n"
);
#endif
