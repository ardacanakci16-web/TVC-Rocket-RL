"""
TVC Rocket RL Results Plots Verifier & Generator
Verifies plots/sonuc_1, plots/sonuc_2, and plots/sonuc_3.
"""
import os

def check_plots():
    plots = [
        "plots/sonuc_1_hata_modlari_dagilimi.png",
        "plots/sonuc_2_telemetri_ve_hover.png",
        "plots/sonuc_3_handoff_ve_kalibrasyon.png"
    ]
    for p in plots:
        if os.path.exists(p):
            print(f"[OK] Grafik hazir: {p} ({os.path.getsize(p)/1024:.1f} KB)")
        else:
            print(f"[EKSIK] Grafik bulunamadi: {p}")

if __name__ == "__main__":
    check_plots()
