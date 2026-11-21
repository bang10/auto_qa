import subprocess
import sys

def run_suite(platform_name, extra_args):
    print(f"\n{'='*60}")
    print(f"▶ [{platform_name.upper()}] 자동화 테스트 스위트 실행 시작")
    print(f"{'='*60}\n")

    cmd = [sys.executable, "-m", "pytest", f"--platform={platform_name}", *extra_args]
    result = subprocess.run(cmd)
    print(f"\n◀ [{platform_name.upper()}] 테스트 스위트 종료 (Exit Code: {result.returncode})\n")
    return result.returncode

if __name__ == "__main__":
    forwarded_args = sys.argv[1:]

    mobile_exit = run_suite("mobile", forwarded_args)
    pc_exit = run_suite("pc", forwarded_args)

    sys.exit(1 if (mobile_exit != 0 or pc_exit != 0) else 0)