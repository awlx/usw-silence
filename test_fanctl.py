import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent


class FanctlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        directory = Path(cls.temp.name)
        mock = directory / "mock.c"
        mock.write_text(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "int rpc_init_check(void) {\n"
            '  puts("INIT");\n'
            '  const char *s = getenv("INIT_RC");\n'
            "  return s ? atoi(s) : 0;\n"
            "}\n"
            "int rpcclt_usmDbBoxsFanOverrideSet(unsigned u, unsigned s,\n"
            "                                  unsigned op, int duty) {\n"
            '  printf("RPC %u %u %u %d\\n", u, s, op, duty);\n'
            '  const char *r = getenv("OVERRIDE_RC");\n'
            "  return r ? atoi(r) : 0;\n"
            "}\n"
        )
        cls.binary = directory / "fanctl"
        subprocess.run(
            ["cc", "-DFANCTL_TEST", "-Wall", "-Wextra", "-Werror",
             str(ROOT / "fanctl.c"), str(mock), "-o", str(cls.binary)],
            check=True,
        )

    def run_tool(self, *args, **env):
        environment = os.environ.copy()
        environment.pop("INIT_RC", None)
        environment.pop("OVERRIDE_RC", None)
        environment.update(env)
        return subprocess.run(
            [str(self.binary), *args], env=environment,
            text=True, capture_output=True, check=False,
        )

    def test_duty_range_and_touchscreen_source(self):
        for duty in range(101):
            with self.subTest(duty=duty):
                result = self.run_tool(str(duty))
                self.assertEqual(result.returncode, 0)
                self.assertIn(f"RPC 0 2 1 {duty}\n", result.stdout)

    def test_auto(self):
        result = self.run_tool("auto")
        self.assertEqual(result.returncode, 0)
        self.assertIn("RPC 0 2 1 -1\n", result.stdout)

    def test_check_does_not_change_fans(self):
        result = self.run_tool("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("INIT\n", result.stdout)
        self.assertNotIn("\nRPC ", result.stdout)

    def test_invalid_input_never_initializes_rpc(self):
        for args in ([], ["30", "40"], [""], ["101"], ["-1"], ["-30"],
                     ["+30"], ["30.0"], ["30x"], [" 30"], ["30 "],
                     ["999999999999999999999999999999"]):
            with self.subTest(args=args):
                result = self.run_tool(*args)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("INIT\n", result.stdout)
                self.assertNotIn("\nRPC ", result.stdout)

    def test_initialization_failure(self):
        result = self.run_tool("30", INIT_RC="7")
        self.assertEqual(result.returncode, 1)
        self.assertIn("initialization failed: 7", result.stdout)
        self.assertNotIn("\nRPC ", result.stdout)

    def test_override_failure(self):
        result = self.run_tool("30", OVERRIDE_RC="9")
        self.assertEqual(result.returncode, 1)
        self.assertIn("override failed: 9", result.stdout)
        self.assertNotIn("requested 30%", result.stdout)


if __name__ == "__main__":
    unittest.main()
