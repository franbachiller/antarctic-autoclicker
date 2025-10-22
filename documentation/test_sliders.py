"""
Script de prueba para verificar que los sliders funcionan correctamente
Ejecuta esto para ver cómo cada configuración afecta el timing
"""

import time
import random

class TestConfig:
    def __init__(self):
        self.clicks = 24
        self.interval = 10
        self.duration = 0.30
        self.auto_burst_delay = 0.0
        self.humanize_enabled = False
        self.ultra_mode = False
        self.advanced_timing_enabled = False
        self.advanced_profile: MockProfile | None = None
        self.timing_profile = 'precise'
        self.time_jitter_ms = 2.0

class MockProfile:
    def __init__(self):
        self.jitter_range = (0.0001, 0.0003)
        self.burst_pattern = [1, 1, 2, 1, 1, 3]

def get_timing_delay(config):
    """Copia de la función get_timing_delay para testing"""
    # Ultra mode: no delay
    if config.ultra_mode:
        return 0
    
    # Start with the interval slider value (in milliseconds, convert to seconds)
    base_delay = config.interval / 1000.0
    
    # Apply humanization if enabled
    if config.humanize_enabled:
        if config.timing_profile == 'human_slow':
            # Add random delay on top of base
            base_delay += random.uniform(0.010, 0.025)
        elif config.timing_profile == 'human_fast':
            # Add smaller random delay
            base_delay += random.uniform(0.002, 0.008)
        elif config.timing_profile == 'random':
            # Random multiplier
            base_delay *= random.uniform(0.5, 2.0)
        
        # Apply time jitter if configured
        if config.time_jitter_ms > 0:
            jitter = random.uniform(-config.time_jitter_ms, config.time_jitter_ms) / 1000.0
            base_delay += jitter
    
    # Apply advanced timing modifications if enabled
    if config.advanced_timing_enabled and config.advanced_profile:
        profile = config.advanced_profile
        
        # Apply micro-jitter for race conditions (additive)
        if profile.jitter_range:
            jitter = random.uniform(profile.jitter_range[0], profile.jitter_range[1])
            base_delay += jitter
    
    # Ensure minimum delay
    return max(0.001, base_delay)

def test_configuration(name, config):
    """Prueba una configuración específica"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Configuracion:")
    print(f"  Clicks/Batch: {config.clicks}")
    print(f"  Interval: {config.interval}ms")
    print(f"  Duration: {config.duration}s")
    print(f"  Humanization: {'SI' if config.humanize_enabled else 'NO'}")
    print(f"  Burst Variations: {'SI' if config.advanced_timing_enabled else 'NO'}")
    print(f"  ULTRA MODE: {'SI' if config.ultra_mode else 'NO'}")
    
    # Simular 10 delays
    print(f"\nTimings generados (primeros 10 clics):")
    delays = []
    for i in range(10):
        delay = get_timing_delay(config)
        delays.append(delay)
        print(f"  Clic {i+1}: {delay*1000:.3f}ms")
    
    # Estadísticas
    avg_delay = sum(delays) / len(delays) * 1000
    min_delay = min(delays) * 1000
    max_delay = max(delays) * 1000
    
    print(f"\nEstadísticas:")
    print(f"  Promedio: {avg_delay:.3f}ms")
    print(f"  Mínimo: {min_delay:.3f}ms")
    print(f"  Máximo: {max_delay:.3f}ms")
    
    # Calcular clics esperados
    if avg_delay > 0:
        expected_clicks = int(config.duration / (avg_delay / 1000))
        cps = expected_clicks / config.duration
        print(f"\nResultado esperado:")
        print(f"  Clics por rafaga (~{config.duration}s): {expected_clicks}")
        print(f"  CPS (clics por segundo): {cps:.1f}")
    else:
        print(f"\nResultado esperado:")
        print(f"  ULTRA MODE: Clics ilimitados (sin delay)")
        print(f"  CPS: MAXIMO (limitado solo por CPU/ventana)")

def main():
    print("="*60)
    print(" TEST DE SLIDERS - ANTARCTIC AUTOCLICKER")
    print("="*60)
    
    # Test 1: Configuración Normal
    config1 = TestConfig()
    config1.clicks = 24
    config1.interval = 10
    config1.duration = 0.30
    test_configuration("Configuración Normal (Sin mods)", config1)
    
    # Test 2: Con Humanization
    config2 = TestConfig()
    config2.clicks = 24
    config2.interval = 10
    config2.duration = 0.30
    config2.humanize_enabled = True
    config2.timing_profile = 'human_fast'
    test_configuration("Con Humanization", config2)
    
    # Test 3: Con Burst Variations
    config3 = TestConfig()
    config3.clicks = 24
    config3.interval = 10
    config3.duration = 0.30
    config3.advanced_timing_enabled = True
    config3.advanced_profile = MockProfile()
    test_configuration("Con Burst Variations", config3)
    
    # Test 4: ULTRA MODE
    config4 = TestConfig()
    config4.clicks = 24
    config4.interval = 10  # Ignorado en ultra mode
    config4.duration = 0.30
    config4.ultra_mode = True
    test_configuration("ULTRA MODE", config4)
    
    # Test 5: Interval Alto
    config5 = TestConfig()
    config5.clicks = 24
    config5.interval = 50  # Más lento
    config5.duration = 0.50
    test_configuration("Interval Alto (50ms)", config5)
    
    # Test 6: Interval Bajo
    config6 = TestConfig()
    config6.clicks = 24
    config6.interval = 2  # Muy rápido
    config6.duration = 0.20
    test_configuration("Interval Bajo (2ms)", config6)
    
    print(f"\n{'='*60}")
    print("PRUEBAS COMPLETADAS")
    print("="*60)
    print("\nCONCLUSIONES:")
    print("  - El slider Interval SIEMPRE afecta el timing base")
    print("  - Humanization SUMA variacion aleatoria")
    print("  - Burst Variations SUMA micro-jitter")
    print("  - ULTRA MODE ignora todo (delay = 0)")
    print("\nRECOMENDACIONES:")
    print("  - Interval 10-20ms: Seguro y efectivo")
    print("  - Interval 5ms: Rapido pero detectado")
    print("  - Interval < 3ms: Solo con Humanization")
    print("  - ULTRA MODE: Solo para testing\n")

if __name__ == "__main__":
    main()
