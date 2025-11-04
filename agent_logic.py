import time
import json
from dataclasses import dataclass, field
from typing import Dict, Any

# --- DEFINICIONES DE ESTRUCTURA DE DATOS (REUTILIZANDO PASO 1) ---

# Mock de las estructuras de datos (simplificado para el ejemplo)
@dataclass
class DatosEticos:
    modo_falla_red: str = "REINTENTO_EXPONENCIAL"
    modo_falla_verificacion: str = "PAUSAR_Y_NOTIFICAR"

@dataclass
class SolicitudPEPSPay:
    contratoID: str
    url_metadatos_acceso: str
    datos_eticos: DatosEticos

# --- UTILIDADES Y MOCKS ---

def notificarUsuario(mensaje: str):
    """Simula el envío de una notificación al usuario."""
    print(f"[💬 NOTIFICACIÓN AL USUARIO] {mensaje}")

def realizarLlamadaHTTP_mock(url_oraculo: str, simulacion_falla=False) -> Dict[str, Any]:
    """
    PASO 3A: SIMULACIÓN de la consulta HTTP al Oráculo RWA.
    
    En un entorno real, se usaría 'requests.get(url_oraculo)'.
    """
    print(f"   [🌐 ORÁCULO] Consultando URL de verificación: {url_oraculo}...")
    
    if simulacion_falla:
        # Simula una falla de comunicación (timeout)
        raise ConnectionError("Fallo al conectar con el servidor del Oráculo.")

    # Simulación de respuesta exitosa del Oráculo
    if "status/12345_OK" in url_oraculo:
        return {"status": "COMPLETADO", "pagoAprobado": True, "verificadoEn": int(time.time())}
    elif "status/12345_PENDIENTE" in url_oraculo:
        return {"status": "PENDIENTE", "pagoAprobado": False, "razon": "Faltan metadatos GPS"}
    else:
        # Respuesta por defecto para simulación de falla de verificación
        return {"status": "NO_ENCONTRADO", "pagoAprobado": False, "razon": "ID de servicio inválido"}

class ContratoPEPSPay_Mock:
    """
    PASO 4: MOCK de la interacción con el Smart Contract (web3.py).
    
    En un entorno real, se usaría web3.eth.contract(address, abi).
    """
    def __init__(self, simulacion_falla_red=False):
        self.simulacion_falla_red = simulacion_falla_red
        print("   [⛓️ ARC] Interfaz de contrato PEPSPayEscrow inicializada.")

    def releasePayment(self, contratoID: str):
        """Simula la llamada on-chain a releasePayment."""
        print(f"   [⛓️ ARC] Enviando transacción 'releasePayment' para Contrato ID: {contratoID}...")
        
        if self.simulacion_falla_red:
            # Simula una falla de red (Ej. low gas, nodo caído)
            raise RuntimeError("Fallo en la transacción: NODE_ERROR_GAS_LIMIT.")
        
        # Simulación de transacción exitosa
        class TransaccionMock:
            def esperarConfirmacion(self):
                time.sleep(1) # Simula el tiempo de espera del bloque
                print("   [⛓️ ARC] Transacción confirmada en la cadena ARC.")
            hash = f"0xARC{contratoID}_{int(time.time())}"
        
        return TransaccionMock()

def reintentarConRetrocesoExponencial(funcion_a_reintentar, max_intentos: int, *args, **kwargs):
    """Implementa el mecanismo ético de REINTENTO_EXPONENCIAL."""
    for intento in range(max_intentos):
        espera = 2 ** intento  # 1s, 2s, 4s, etc.
        print(f"   [🔁 FALLA RED] Esperando {espera} segundos para reintento #{intento + 1}...")
        time.sleep(espera)
        try:
            funcion_a_reintentar(*args, **kwargs)
            return True # Éxito en el reintento
        except RuntimeError as e:
            if intento == max_intentos - 1:
                print(f"   [❌ FALLO FINAL] Se agotaron los {max_intentos} intentos. Pago fallido.")
                notificarUsuario(f"El pago falló permanentemente debido a errores de red: {e}")
                return False
    return False

# --- FUNCIÓN PRINCIPAL DEL AGENTE (PASOS 3, 4, 5) ---

def ejecutarVerificacionYPago(
    solicitud: SolicitudPEPSPay, 
    contrato_mock: ContratoPEPSPay_Mock
):
    """
    Función principal del Agente. Activada tras la detección del evento 'EscrowCreado'.
    """
    contratoID = solicitud.contratoID
    urlOraculo = solicitud.url_metadatos_acceso
    datosEticos = solicitud.datos_eticos

    print(f"\n--- 🚀 INICIANDO PROCESO PARA CONTRATO: {contratoID} ---")
    
    # --------------------------------------------------------------------------------
    # PASO 3: LLAMADA OFF-CHAIN AL ORÁCULO (Verificación del Mundo Real)
    # --------------------------------------------------------------------------------
    try:
        respuesta = realizarLlamadaHTTP_mock(urlOraculo) 
        
        # Lógica de Verificación
        if respuesta.get('status') == 'COMPLETADO' and respuesta.get('pagoAprobado') is True:
            
            print(f"✅ VERIFICACIÓN EXITOSA para el Contrato {contratoID}")
            
            # --------------------------------------------------------------------------------
            # PASO 4: EJECUCIÓN DEL PAGO ON-CHAIN
            # --------------------------------------------------------------------------------
            try:
                # Llamada al mock del Contrato Inteligente
                transaccion = contrato_mock.releasePayment(contratoID)

                # Esperar a que la transacción se confirme en la red Arc
                transaccion.esperarConfirmacion()

                # --------------------------------------------------------------------------------
                # PASO 5: CONFIRMACIÓN Y NOTIFICACIÓN
                # --------------------------------------------------------------------------------
                print(f"🎉 PAGO LIBERADO. Hash: {transaccion.hash}")
                notificarUsuario(f"Pago por servicio {contratoID} liberado exitosamente. Hash de Transacción: {transaccion.hash}")
            
            except RuntimeError as errorDeRed:
                # Fallo por Red (Lógica Ética: REINTENTO_EXPONENCIAL)
                if datosEticos.modo_falla_red == 'REINTENTO_EXPONENCIAL':
                    print(f"⚠️ Fallo de Red: {errorDeRed}. Implementando reintento exponencial...")
                    # Reintentar llamando a sí misma (o a una versión que pueda ser retried)
                    # Para simplificar, reintentaremos la llamada completa
                    reintentarConRetrocesoExponencial(ejecutarVerificacionYPago, 3, solicitud, ContratoPEPSPay_Mock(simulacion_falla_red=False))
                
        else:
            # Fallo por Verificación (Lógica Ética: PAUSAR_Y_NOTIFICAR)
            if datosEticos.modo_falla_verificacion == 'PAUSAR_Y_NOTIFICAR':
                print(f"🛑 VERIFICACIÓN FALLIDA. Oráculo devuelve: {respuesta.get('status', 'N/A')}.")
                notificarUsuario(f"Alerta: Pago {contratoID} PAUSADO. El servicio no fue verificado. Razón: {respuesta.get('razon', 'Desconocida')}.")
                # El Agente NO llama a releasePayment.

    except ConnectionError as errorDeComunicacion:
        # Fallo al contactar al servidor del Oráculo
        print(f"❌ Error de comunicación con el Oráculo: {errorDeComunicacion}.")
        notificarUsuario("Alerta: El sistema de verificación RWA está inactivo o inalcanzable. Contactar a soporte.")

# --- ESCENARIOS DE PRUEBA (Para validar la lógica) ---

# 1. Escenario Exitoso: Verificación OK y Red OK
solicitud_exitosa = SolicitudPEPSPay(
    contratoID="BODEGA_C_INV_001", 
    url_metadatos_acceso="https://api.verificacion-mock.com/status/12345_OK", 
    datos_eticos=DatosEticos()
)
contrato_ok = ContratoPEPSPay_Mock(simulacion_falla_red=False)
ejecutarVerificacionYPago(solicitud_exitosa, contrato_ok)

# 2. Escenario Falla de Verificación: Se PAUSA
solicitud_pausada = SolicitudPEPSPay(
    contratoID="BODEGA_C_INV_002", 
    url_metadatos_acceso="https://api.verificacion-mock.com/status/12345_PENDIENTE", 
    datos_eticos=DatosEticos()
)
contrato_ok = ContratoPEPSPay_Mock(simulacion_falla_red=False)
ejecutarVerificacionYPago(solicitud_pausada, contrato_ok)

# 3. Escenario Falla de Red: Se REINTENTA (El primer intento fallará, el segundo tendrá éxito en el reintento)
solicitud_reintento = SolicitudPEPSPay(
    contratoID="BODEGA_C_INV_003", 
    url_metadatos_acceso="https://api.verificacion-mock.com/status/12345_OK", 
    datos_eticos=DatosEticos()
)
# Creamos un contrato que fallará la primera vez
contrato_fallido_primero = ContratoPEPSPay_Mock(simulacion_falla_red=True) 
ejecutarVerificacionYPago(solicitud_reintento, contrato_fallido_primero)