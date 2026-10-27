/* Link-only import libraries. Never copy these libraries to a switch. */
.text
.arm

.macro import_symbol name
.global \name
.type \name, %function
\name:
    bx lr
.size \name, .-\name
.endm

#ifdef FANCTL_LIBUBNT
import_symbol rpc_init_check
import_symbol rpcclt_usmDbBoxsFanOverrideSet
#elif !defined(FANCTL_DEPENDENCY)
import_symbol __uClibc_main
import_symbol printf
import_symbol puts
#endif

.section .note.GNU-stack,"",%progbits
