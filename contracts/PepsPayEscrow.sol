// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PepsPayEscrow
 * @dev Contrato de Escrow Condicional para la red ARC (simulando USDC o stablecoins).
 * Solo permite la liquidación o el reembolso si es llamado por el Agente Autorizado.
 */
contract PepsPayEscrow {
    // La dirección del dueño del contrato (Quien lo desplegó)
    address payable public pagador;
    
    // La dirección del proveedor del servicio (Quien debe recibir el pago)
    address payable public proveedor;
    
    // La dirección del Agente PEPS-Pay que tiene permiso de Liquidar/Reembolsar.
    address public agenteAutorizado;
    
    // El monto total del Escrow
    uint256 public monto;

    // Estado del contrato: 0=Activo, 1=Liquidado, 2=Reembolsado
    uint8 public estado;

    // Eventos para el monitoreo del Agente Off-Chain
    event EscrowCreado(address indexed _pagador, address indexed _proveedor, uint256 _monto);
    event LiquidacionExitosa(uint256 _monto);
    event ReembolsoEmitido(uint256 _monto);

    modifier soloAgente() {
        require(msg.sender == agenteAutorizado, "Acceso denegado: Solo el Agente Autorizado puede llamar esta funcion.");
        require(estado == 0, "Accion denegada: El contrato no esta Activo.");
        _;
    }

    constructor(address _proveedor, address _agenteAutorizado) payable {
        // Establece el pagador como la persona que desplega el contrato
        pagador = payable(msg.sender);
        proveedor = payable(_proveedor);
        agenteAutorizado = _agenteAutorizado;
        monto = msg.value; // El valor enviado al crear el contrato es el monto
        estado = 0; // Se inicializa como Activo
        
        emit EscrowCreado(pagador, proveedor, monto);
    }

    /**
     * @dev Funcion llamada por el Agente PEPS-Pay para liquidar el pago.
     * Esto ocurre si el Oraculo Humano da OK.
     */
    function liquidar() external soloAgente {
        estado = 1; // Cambia el estado a Liquidado

        // Transfiere el monto total del Escrow al proveedor
        (bool success, ) = proveedor.call{value: monto}("");
        require(success, "Error en la transferencia de liquidacion.");

        emit LiquidacionExitosa(monto);
    }

    /**
     * @dev Funcion llamada por el Agente PEPS-Pay para reembolsar el pago.
     * Esto ocurre si el usuario pulsa el boton de Cancelar.
     */
    function reembolsar() external soloAgente {
        estado = 2; // Cambia el estado a Reembolsado

        // Transfiere el monto total del Escrow de vuelta al pagador
        (bool success, ) = pagador.call{value: monto}("");
        require(success, "Error en la transferencia de reembolso.");

        emit ReembolsoEmitido(monto);
    }

    // Funcion de fallback para evitar que se envien fondos despues de la creacion
    receive() external payable {
        revert("Fondos no permitidos despues de la creacion del Escrow.");
    }
}
