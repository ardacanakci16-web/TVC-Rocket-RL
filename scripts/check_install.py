"""
TVC Rocket RL Environment Installation Check
"""
import sys
import os

def check():
    print("=" * 60)
    print("TVC ROCKET REINFORCEMENT LEARNING KURULUM KONTROLU")
    print("=" * 60)
    print(f"Python Surumu: {sys.version.split()[0]} ({sys.executable})")

    packages = [
        ("numpy", "NumPy Matris ve Vektor Islemleri"),
        ("scipy", "SciPy Dinamik ve Numerik Cozucu"),
        ("matplotlib", "Matplotlib Grafik Cizimi"),
        ("PIL", "Pillow Gorsel Isleme"),
    ]

    all_ok = True
    for pkg, desc in packages:
        try:
            __import__(pkg)
            print(f"[OK] {pkg:<15} - {desc}")
        except ImportError:
            print(f"[EKSIK] {pkg:<15} - {desc}")
            all_ok = False

    # Check local modules
    sys.path.insert(0, os.path.abspath("."))
    try:
        from src.tvc_env import TVCRocketDynamics, TVCRewardShaper, HandoffGateEvaluator
        print(f"[OK] src.tvc_env     - TVC Dinamik ve Odul Sekillendirme Motoru")
    except Exception as e:
        print(f"[EKSIK] src.tvc_env     - {e}")
        all_ok = False

    print("=" * 60)
    if all_ok:
        print("TEBRIKLER: Tum TVC Rocket RL bagimliliklari eksiksiz!")
        print("Simulasyonu calistirmak icin: python scripts/run_simulation.py")
    else:
        print("Lutfen eksik paketleri 'pip install -r requirements.txt' ile yukleyin.")
    print("=" * 60)

if __name__ == "__main__":
    check()
