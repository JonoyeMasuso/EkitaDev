document.addEventListener('DOMContentLoaded', () => {
    // Referencias de elementos del DOM
    const form = document.getElementById('request-form');
    const logConsole = document.getElementById('log-console');
    const oracleToggle = document.getElementById('oracle-toggle');
    const toggleStatus = document.getElementById('toggle-status');
    const contractIdSpan = document.getElementById('contract-id');
    const failNetworkButton = document.getElementById('fail-network-button');
    const startButton = document.getElementById('start-button');
    
    // --> A G R E G A D O <--
    const cancelButton = document.getElementById('cancel-button'); 

    // Variables de estado del Agente
    let currentContractId = 0;
    let isContractActive = false;
    let isOracleVerified = false;

    // --- Funciones de Utilidad ---

    /**
     * Escribe un mensaje en la consola de logs con retardo simulado.
     * @param {string} message - El mensaje a mostrar.
     * @param {number} delay - El retardo en milisegundos.
     * @param {string} [colorClass] - Clase CSS para cambiar el color del mensaje (ej: 'success', 'error', 'warning').
     */
    function log(message, delay = 500, colorClass = '') {
        return new Promise(resolve => {
            setTimeout(() => {
                const logEntry = document.createElement('div');
                logEntry.textContent = `> [${new Date().toLocaleTimeString()}] ${message}`;
                if (colorClass) {
                    // Simulación de color más rica en la consola de terminal
                    logEntry.style.color = colorClass === 'success' ? 'lightgreen' :
                                           colorClass === 'error' ? 'salmon' :
                                           colorClass === 'warning' ? 'yellow' : '#00ff00';
                }
                logConsole.appendChild(logEntry);
                logConsole.scrollTop = logConsole.scrollHeight;
                resolve();
            }, delay);
        });
    }

    /**
     * Genera un ID de contrato simple.
     */
    function generateContractId() {
        return 'PEPS-' + Math.floor(Math.random() * 90000 + 10000);
    }

    // --- Lógica del Agente PEPS-Pay ---

    /**
     * Simula la llamada al Oráculo.
     */
    async function callOracle(attempt = 1) {
        await log(`📡 Intento ${attempt}: Llamando a Oráculo RWA (${document.getElementById('oracle-url').value})...`, 1500, 'warning');
        
        // Simulación de Fallo de Red (BODEGA_C_INV_003)
        if (failNetworkButton.classList.contains('active')) {
            await log("🛑 FALLO DE RED DETECTADO (simulado).", 1000, 'error');
            failNetworkButton.classList.remove('active'); // Desactiva la simulación de fallo después de 1 intento
            
            if (attempt < 3) { // Permite hasta 3 reintentos
                await log("⚠️ Implementando lógica de REINTENTO en 3s...", 2000, 'warning');
                return callOracle(attempt + 1); // Llamada recursiva para reintentar
            } else {
                await log("❌ Límite de reintentos alcanzado. Contrato CANCELADO.", 1000, 'error');
                isContractActive = false;
                resetState();
                return false;
            }
        }

        // Simula la espera por la verificación manual del Oráculo
        await log("⏳ Esperando respuesta del Oráculo (Verifique el switch de la SECCIÓN 2)...", 1500, 'warning');

        // Función de espera activa para el toggle
        return new Promise(resolve => {
            const checkToggle = setInterval(() => {
                if (isOracleVerified) {
                    clearInterval(checkToggle);
                    log("✅ Oráculo VERIFICADO (TRUE) por el operador.", 500, 'success').then(() => {
                        resolve(true);
                    });
                }
            }, 1000);
        });
    }

    /**
     * Ejecuta la liquidación si la verificación fue exitosa.
     */
    async function executeSettlement() {
        await log("💰 Ejecutando Liquidación de Contrato...", 1000);
        await log(`Transferencia de ${document.getElementById('monto').value} USD a ${document.getElementById('proveedor').value} iniciada...`, 1500);
        await log("⛓️ Confirmando transacción en la Capa de Liquidación...", 2000);
        await log("🎉 Liquidación COMPLETA y exitosa.", 1000, 'success');
        
        isContractActive = false;
        resetState();
    }
    
    // ----------------------------------------------------------------
    // PASO: Lógica de Cancelación y Reembolso (INSERTADA POR SOLICITUD)
    // ----------------------------------------------------------------
    async function executeCancellation(razon) {
        // La cancelación es una acción manual del operador (tú)
        await log(`🛑 Iniciando CANCELACIÓN de Contrato ID: ${currentContractId}.`, 1000, 'error');
        await log(`Razón: ${razon}. Ejecutando función 'cancelEscrow' para reembolso.`, 1500, 'error');
        
        // Simula la llamada a la función cancelEscrow del Smart Contract (on-chain)
        await log("⛓️ Transacción ON-CHAIN: Llamando a cancelEscrow...", 1500);
        await log("Transferencia de fondos de vuelta al Pagador...", 1500);

        // ESTE LOG SIMULA EL MENSAJE FINAL QUE EL AGENTE DEBE VER
        await log("🔴 ALERTA: OPERACIÓN FINALIZADA POR CANCELACIÓN MANUAL.", 1000, 'error'); 
        
        await log("🎉 Reembolso COMPLETO. Contrato terminado y liberado.", 1000, 'success');
        
        isContractActive = false;
        resetState();
    }
    // ----------------------------------------------------------------

    /**
     * Restablece la interfaz a su estado inicial.
     */
    function resetState() {
        contractIdSpan.textContent = 'N/A';
        oracleToggle.checked = false;
        toggleStatus.textContent = 'PENDIENTE';
        toggleStatus.style.backgroundColor = 'var(--color-danger)';
        isOracleVerified = false;
        isContractActive = false;
        startButton.disabled = false;
        startButton.textContent = 'INICIAR CONTRATO (Paso 1 y 2)';
        failNetworkButton.style.display = 'none';
        failNetworkButton.classList.remove('active');
        
        // --> M O D I F I C A C I Ó N <--
        cancelButton.style.display = 'none'; // Ocultar el botón de cancelación
    }

    // --- Manejadores de Eventos ---

    // 1. Maneja el envío del formulario (Paso 1: Solicitud)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (isContractActive) return;

        currentContractId = generateContractId();
        contractIdSpan.textContent = currentContractId;
        isContractActive = true;
        
        startButton.disabled = true;
        startButton.textContent = 'CONTRATO ACTIVO...';
        failNetworkButton.style.display = 'block';
        
        // --> M O D I F I C A C I Ó N <--
        cancelButton.style.display = 'block'; // Mostrar el botón de cancelación

        await log(`🚀 Solicitud recibida para Contrato ID: ${currentContractId}.`, 500, 'success');
        
        // Simulación del flujo: Solicitud -> Verificación -> Liquidación
        const isSuccessful = await callOracle(); 
        
        if (isSuccessful) {
            await executeSettlement(); // Si la verificación es TRUE, liquida
        } else if (isContractActive) {
            // El estado solo se reinicia si hubo un fallo terminal (ej: reintento agotado)
            await log("Contrato finalizado con estado INCOMPLETO.", 500, 'error');
            resetState();
        }
    });

    // 2. Maneja el cambio del toggle (Paso 2: Verificación del Oráculo)
    oracleToggle.addEventListener('change', () => {
        isOracleVerified = oracleToggle.checked;
        if (isOracleVerified) {
            toggleStatus.textContent = 'VERIFICADO';
            toggleStatus.style.backgroundColor = 'var(--color-success)';
        } else {
            toggleStatus.textContent = 'PENDIENTE';
            toggleStatus.style.backgroundColor = 'var(--color-danger)';
        }
    });

    // 3. Maneja la simulación de Fallo de Red (Lógica BODEGA_C_INV_003)
    failNetworkButton.addEventListener('click', () => {
        if (!isContractActive) {
            log("No hay contrato activo para simular un fallo.", 500, 'error');
            return;
        }
        // Activa la bandera de fallo de red para el próximo 'callOracle'
        failNetworkButton.classList.add('active'); 
        log("🚨 Bandera de FALLO DE RED activada.", 500, 'error');
    });

    // 4. Maneja el botón de Cancelación (NUEVO CONTROL)
    cancelButton.addEventListener('click', () => {
        if (!isContractActive) {
            log("No hay contrato activo para cancelar.", 500, 'error');
            return;
        }
        executeCancellation("Acción Manual del Operador/Fallo de Verificación");
    });
    
    // Inicializar estado del botón de fallo y cancelación
    failNetworkButton.style.display = 'none';
    cancelButton.style.display = 'none';
});