# Mac development guide

The FreeRTOS GCC_POSIX port targets Linux, not native macOS. Use an Ubuntu VM or Linux container on the Mac.

## Ubuntu commands

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build git python3
git clone https://github.com/sunnatbek06/FreeRTOSproject.git
cd FreeRTOSproject
git checkout feature/spacecraft-simulator
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j2
python3 -m unittest discover -s tests -v
mkdir -p results
./build/spacecraft_sim --duration 9 --run-id firstreal > results/firstreal.csv 2> results/firstreal.txt
python3 scripts/analyze.py results/firstreal.csv results/firstreal_summary.csv
```

Default CMake downloads pinned FreeRTOS-Kernel V11.1.0. Initial configuration needs network. To build offline, provide an existing kernel checkout using -DFREERTOS_KERNEL_PATH=/absolute/path.

Results are valid for the host simulator only. Verify the complete CSV, final COUNTS stderr output and zero unprocessed messages before making comparisons.
