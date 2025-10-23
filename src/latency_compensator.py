"""
Sistema de Compensación de Latencia para Antarctic Autoclicker
Mide RTT al servidor del juego y ajusta timing de clics

CÓMO USAR:
1. Abre el juego BoomBang con DevTools habilitado
2. En Antarctic, ve a la sección "Latency Compensation"
3. Ingresa el puerto DevTools (por defecto 9222)
4. Click en "Connect"
5. Click en "Calibrate" para calibración automática (10 seg)
6. Activa el switch para habilitar compensación
7. Ajusta el multiplicador según necesites (0.0 - 2.0)

TEORÍA:
- RTT (Round Trip Time): Tiempo total de ida y vuelta al servidor
- Half-RTT: RTT/2, tiempo estimado que tarda en llegar al servidor
- Compensación: Resta half-RTT del delay para "predecir" llegada
- Calibración: Encuentra el offset óptimo basado en muestras reales
"""

import websocket
import threading
import time
import json
import base64
import statistics
from collections import deque
from typing import Optional, Callable
import subprocess
import re
import urllib.request


class LatencyCompensator:
    """Mide latencia y ajusta timing de clics"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.ws = None
        self.devtools_port = None
        self.game_ws_request_id = None
        self.running = False
        self.callback = callback
        
        # Mediciones de latencia
        self.ping_samples = deque(maxlen=100)  # Últimas 100 mediciones
        self.current_rtt_ms = 0.0
        self.half_rtt_ms = 0.0
        self.avg_rtt_ms = 0.0
        self.min_rtt_ms = 0.0
        self.max_rtt_ms = 0.0
        
        # Calibración automática
        self.calibration_mode = False
        self.calibration_samples = []
        self.optimal_offset_ms = 0.0
        
        # Compensación activa
        self.compensation_enabled = False
        self.compensation_multiplier = 1.0  # Ajuste fino
        
        # Ping monitoring basado en frames del juego
        self.ping_thread = None
        self.last_ping_time = 0
        self.ping_interval = 1.0
        self.last_sent_time = None  # Timestamp del último frame enviado

    def auto_detect_game(self, game_path: str = None) -> Optional[int]:
        """Lanza el juego y detecta el puerto DevTools automáticamente"""
        if game_path is None:
            game_path = r"C:\Users\Fran\AppData\Local\Programs\BoomBang-Launcher\BoomBangLauncher.exe"

        try:
            if self.callback:
                self.callback('status', 'Lanzando juego...')

            process = subprocess.Popen(
                [game_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if self.callback:
                self.callback('status', 'Esperando puerto DevTools...')

            # Lee stderr para capturar el puerto
            for line in process.stderr:
                match = re.search(r'DevTools listening on ws://127.0.0.1:(\d+)', line)
                if match:
                    port = int(match.group(1))
                    if self.callback:
                        self.callback('port_detected', port)
                    return port

            return None
        except Exception as e:
            if self.callback:
                self.callback('error', f"Error lanzando juego: {e}")
            return None

    def connect_to_game(self, devtools_port: int) -> bool:
        """Conecta al DevTools del juego"""
        try:
            self.devtools_port = devtools_port
            import urllib.request
            
            with urllib.request.urlopen(f'http://127.0.0.1:{devtools_port}/json') as response:
                targets = json.loads(response.read().decode())
            
            ws_url = targets[0]['webSocketDebuggerUrl']
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )
            
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
            return True
        except Exception as e:
            if self.callback:
                self.callback('error', f"Error conectando: {e}")
            return False
    
    def _on_open(self, ws):
        """Callback cuando se abre la conexión"""
        ws.send(json.dumps({"id": 1, "method": "Network.enable"}))
        self.running = True
        
        # Iniciar monitoreo de ping
        self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self.ping_thread.start()
        
        if self.callback:
            self.callback('connected', None)
    
    def _on_message(self, ws, message):
        """Procesa mensajes del DevTools"""
        try:
            data = json.loads(message)
            
            if 'method' not in data:
                return
            
            method = data['method']
            
            # Capturar WebSocket del juego
            if method == 'Network.webSocketCreated':
                self.game_ws_request_id = data['params']['requestId']
                if self.callback:
                    self.callback('game_ws_detected', self.game_ws_request_id)

            # Capturar frames ENVIADOS (cliente → servidor)
            elif method == 'Network.webSocketFrameSent':
                if 'params' in data and 'response' in data['params']:
                    # Guardar timestamp cuando el cliente envía algo
                    self.last_sent_time = time.time()

            # Capturar frames RECIBIDOS (servidor → cliente)
            elif method == 'Network.webSocketFrameReceived':
                if 'params' in data and 'response' in data['params']:
                    # Si hay un envío reciente, calcular RTT
                    if hasattr(self, 'last_sent_time') and self.last_sent_time:
                        rtt = (time.time() - self.last_sent_time) * 1000.0

                        # Registrar RTT si es razonable (10-500ms)
                        if 10 <= rtt <= 500:
                            self._record_ping(rtt)
                            self.last_sent_time = None  # Reset para próximo par
        
        except Exception as e:
            pass
    
    def _on_error(self, ws, error):
        """Callback de error"""
        if self.callback:
            self.callback('error', str(error))
    
    def _on_close(self, ws, close_msg, close_status_code):
        """Callback de cierre"""
        self.running = False
        if self.callback:
            self.callback('disconnected', None)
    
    def _ping_loop(self):
        """Loop que monitorea el estado de la conexión"""
        while self.running:
            try:
                # Solo verificar que tengamos datos recientes
                if len(self.ping_samples) == 0:
                    # No hay datos, esperar
                    pass

                # Esperar antes del siguiente check
                if False:  # Deshabilitado - ya no enviamos pings manuales
                    ping_id = 9000
                
                time.sleep(self.ping_interval)
            
            except Exception:
                break
    
    def _process_frame_timing(self, data):
        """Procesa timing de frames para estimar latencia"""
        try:
            # Timestamp del frame
            if 'params' in data and 'timestamp' in data['params']:
                timestamp = data['params']['timestamp']
                current_time = time.time()
                
                # Estimar RTT basado en diferencia de timestamps
                # (esto es aproximado, el ping manual es más preciso)
                estimated_rtt = abs(current_time - timestamp) * 1000.0
                
                if 10 < estimated_rtt < 500:  # Filtrar valores absurdos
                    self._record_ping(estimated_rtt)
        
        except Exception:
            pass
    
    def _record_ping(self, rtt_ms: float):
        """Registra una medición de ping"""
        self.ping_samples.append(rtt_ms)
        self.current_rtt_ms = rtt_ms
        self.half_rtt_ms = rtt_ms / 2.0
        
        if len(self.ping_samples) >= 5:
            self.avg_rtt_ms = statistics.mean(self.ping_samples)
            self.min_rtt_ms = min(self.ping_samples)
            self.max_rtt_ms = max(self.ping_samples)
        
        # Callback con stats actualizadas
        if self.callback:
            self.callback('ping_update', {
                'current': self.current_rtt_ms,
                'avg': self.avg_rtt_ms,
                'min': self.min_rtt_ms,
                'max': self.max_rtt_ms,
                'half': self.half_rtt_ms
            })
        
        # Si está en modo calibración, guardar muestra
        if self.calibration_mode:
            self.calibration_samples.append(rtt_ms)
    
    def start_calibration(self, duration_seconds: int = 10):
        """Inicia calibración automática"""
        self.calibration_mode = True
        self.calibration_samples = []
        
        if self.callback:
            self.callback('calibration_started', duration_seconds)
        
        def finish_calibration():
            time.sleep(duration_seconds)
            self.stop_calibration()
        
        threading.Thread(target=finish_calibration, daemon=True).start()
    
    def stop_calibration(self):
        """Detiene calibración y calcula offset óptimo"""
        self.calibration_mode = False

        if len(self.calibration_samples) >= 10:
            # Calcular offset óptimo (usar percentil 25 para ser conservador)
            sorted_samples = sorted(self.calibration_samples)
            percentile_25 = sorted_samples[len(sorted_samples) // 4]
            self.optimal_offset_ms = percentile_25 / 2.0

            if self.callback:
                self.callback('calibration_complete', {
                    'samples': len(self.calibration_samples),
                    'optimal_offset_ms': self.optimal_offset_ms,
                    'avg_rtt': statistics.mean(self.calibration_samples)
                })
                # Enviar actualización de stats para refrescar la UI
                self.callback('ping_update', self.get_stats())
        else:
            if self.callback:
                self.callback('calibration_failed', 'Muestras insuficientes')
    
    def get_compensated_delay(self, base_delay_ms: float) -> float:
        """Calcula delay compensado por latencia"""
        if not self.compensation_enabled:
            return base_delay_ms
        
        # Compensación: restar half-RTT para "predecir" cuando llegará al servidor
        compensation = self.half_rtt_ms * self.compensation_multiplier
        
        # Si hay offset óptimo de calibración, usarlo
        if self.optimal_offset_ms > 0:
            compensation = self.optimal_offset_ms * self.compensation_multiplier
        
        # Aplicar compensación
        compensated = base_delay_ms - compensation
        
        # No permitir delays negativos
        return max(0.1, compensated)
    
    def enable_compensation(self, enabled: bool = True):
        """Activa/desactiva compensación"""
        self.compensation_enabled = enabled
        
        if self.callback:
            self.callback('compensation_toggled', enabled)
    
    def set_compensation_multiplier(self, multiplier: float):
        """Ajusta el multiplicador de compensación (0.0 - 2.0)"""
        self.compensation_multiplier = max(0.0, min(2.0, multiplier))
    
    def get_stats(self) -> dict:
        """Retorna estadísticas actuales"""
        return {
            'connected': self.running,
            'current_rtt_ms': self.current_rtt_ms,
            'avg_rtt_ms': self.avg_rtt_ms,
            'min_rtt_ms': self.min_rtt_ms,
            'max_rtt_ms': self.max_rtt_ms,
            'half_rtt_ms': self.half_rtt_ms,
            'samples': len(self.ping_samples),
            'compensation_enabled': self.compensation_enabled,
            'optimal_offset_ms': self.optimal_offset_ms,
            'compensation_multiplier': self.compensation_multiplier
        }
    
    def disconnect(self):
        """Desconecta del juego"""
        self.running = False
        if self.ws:
            self.ws.close()

