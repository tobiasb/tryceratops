import os
import sys

from tryceratops.analyzers import Runner
from tryceratops.settings import ERROR_LOG_FILENAME
from tryceratops.violations import Violation


class COLORS:
    DESCR = "\033[91m"
    CODE = "\033[93m"

    ENDC = "\033[0m"


def wrap_color(msg: str, color: str):
    return f"{color}{msg}{COLORS.ENDC}"


def present_violation(violation: Violation):
    codestr = wrap_color(violation.code, COLORS.CODE)
    descstr = wrap_color(violation.description, COLORS.DESCR)
    location = f"{violation.filename}:{violation.line}:{violation.col}"

    return f"[{codestr}] {descstr} - {location}"


class CliInterface:
    def __init__(self, runner: Runner):
        self.runner = runner

    def _present_violations(self):
        for violation in self.runner.violations:
            print(present_violation(violation))

    def _present_status(self):
        print("Done processing! 🦖✨")

        if self.runner.analyzed_files:
            print(f"Processed {self.runner.analyzed_files} files")
            print(f"Found {len(self.runner.violations)} violations")
        else:
            print("Nothing to check!")

        if self.runner.excluded_files:
            print(f"Skipped {self.runner.excluded_files} files")

        if self.runner.had_issues:
            print(
                f"Had {len(self.runner.runtime_errors)} unexpected issues "
                f"stored in {ERROR_LOG_FILENAME}"
            )

    def _exit(self):
        exit_code = 0

        if self.runner.had_issues:
            exit_code = 2
        elif self.runner.any_violation:
            exit_code = 1

        sys.exit(exit_code)

    def _delete_empty_logs(self):
        cwd = os.getcwd()
        log_file_path = f"{cwd}/{ERROR_LOG_FILENAME}"
        is_log_empty = os.path.getsize(log_file_path) == 0

        if is_log_empty:
            os.remove(log_file_path)

    def present_and_exit(self):
        self._present_violations()
        self._present_status()
        self._delete_empty_logs()
        self._exit()
