# macOS development setup

Use macOS for editing, reviewing documents and Python analysis. Run the simulator in Ubuntu 22.04 through a Linux VM/container or GitHub Actions. No Linux runtime was installed on the development Mac during this review, so native/local simulator execution is not claimed.

The repository deliberately rejects native Apple builds in CMake. Upstream V11.1.0 POSIX code contains Apple-specific branches, but this project has not validated them. The Linux-only project configuration should not be interpreted as blanket upstream macOS incompatibility.

Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for exact Linux build, smoke-test, full matrix and contention commands. The current branch is `feature/spacecraft-simulator`; check it before building. The first CMake configuration downloads the pinned FreeRTOS tag, or accepts a local kernel tree through `FREERTOS_KERNEL_PATH`.

You can run `python3 -m unittest discover -s tests -v` and `python3 tools/review_results.py` on the Mac. The latter audits preserved Linux traces and does not execute or imitate the scheduler.
