document.addEventListener("DOMContentLoaded", function () {
    // 1) Inyectar título dinámico
    const urlParams = new URLSearchParams(window.location.search);
    const sitio = urlParams.get('sitio') || 'p263';
    const titleEl = document.createElement('div');
    titleEl.id = 'pozo-title';
    titleEl.textContent = `Pozo ${sitio.toUpperCase()}`;
    Object.assign(titleEl.style, {
        position: 'absolute',
        top: '30px',
        left: '50%',
        transform: 'translateX(-50%)',
        color: 'black',
        fontSize: '2.5rem',
        fontWeight: 'bold',
        pointerEvents: 'none',
        zIndex: '1000'
    });
    const container = document.getElementById('diagram-container');
    if (container && container.parentNode) container.parentNode.insertBefore(titleEl, container);
    else document.body.insertBefore(titleEl, document.body.firstChild);

    // Elementos de la tarjeta de promedios
    const gastoEl = document.getElementById("gastoValue");
    const presionEl = document.getElementById("presionValue");
    const nivelEl = document.getElementById("nivelValue");
    const fechaHoraEl = document.getElementById("fechaHoraValue");

    // Cargar CSV histórico
    async function loadCSV(filePath) {
        try {
            const res = await fetch(filePath);
            if (!res.ok) throw new Error(res.statusText);
            return await res.text();
        } catch (err) {
            console.error("Error al cargar CSV:", err);
            return null;
        }
    }

    function average(arr) {
        if (!arr.length) return "--";
        return (arr.reduce((a,b)=>a+b,0)/arr.length).toFixed(2);
    }

    function processCSV(csvData) {
        if (!csvData) return;
        const lines = csvData.split("\n").filter(l => l.trim() !== "");
        const headers = lines[0].split(",");

        const idxHora = headers.indexOf("hora");
        const idxGasto = headers.indexOf("Gasto_Instantaneo");
        const idxPresion = headers.indexOf("Presion_Instantanea");
        const idxNivel = headers.indexOf("Nivel_1");

        let gastoDiurno=[], presionDiurno=[], nivelDiurno=[];
        let gastoNocturno=[], presionNocturno=[], nivelNocturno=[];

        for(let i=1; i<lines.length; i++){
            const cols = lines[i].split(",");
            if(cols.length<headers.length) continue;
            const hora = parseInt(cols[idxHora].split(":")[0]);
            const gasto = parseFloat(cols[idxGasto]);
            const presion = parseFloat(cols[idxPresion]);
            const nivel = parseFloat(cols[idxNivel]);

            if(hora>=6 && hora<18){ // Diurno
                gastoDiurno.push(gasto);
                presionDiurno.push(presion);
                nivelDiurno.push(nivel);
            } else { // Nocturno
                gastoNocturno.push(gasto);
                presionNocturno.push(presion);
                nivelNocturno.push(nivel);
            }
        }

        // Mostrar promedios en la tarjeta
        if(gastoEl) gastoEl.innerHTML = `Diurno: ${average(gastoDiurno)} | Nocturno: ${average(gastoNocturno)}`;
        if(presionEl) presionEl.innerHTML = `Diurno: ${average(presionDiurno)} | Nocturno: ${average(presionNocturno)}`;
        if(nivelEl) nivelEl.innerHTML = `Diurno: ${average(nivelDiurno)} | Nocturno: ${average(nivelNocturno)}`;
        if(fechaHoraEl) fechaHoraEl.innerHTML = "Promedios Diurno / Nocturno";
    }

    (async function(){
        const csvData = await loadCSV(`/templates/datos_new/${sitio}_promedios_horarios.csv`);

        processCSV(csvData);
    })();

    // ------------------------------------------------------
    // Función original para datos en tiempo real y animaciones
    function fetchRealData() {
        const significado = {
            "0": "Pozo en prueba",
            "1": "Pozo apagado",
            "2": "Falla de Comunicación",
            "3": "Alarma",
            "4": "Comunicación en local",
            "5": "Señal en remoto"
        };
        const dataUrl = `http://192.168.100.13:10000/datos-resumidos-detallados-new/${sitio}`;
        fetch(dataUrl)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => updateUI(data, significado))
            .catch(() => updateUI(null, null, true));
    }

    function updateUI(data, significado = {}, isError = false) {
        const setText = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };

        if (isError || !data) {
            setText('label1', 'Q = N/A');
            setText('label2', 'N/A');
            setText('label3', 'Actualización: --');
            setText('label4', 'Estatus: Sin conexión');
            ['img4', 'img5', 'img6', 'img7'].forEach(id => {
                const el = document.getElementById(id);
                if(el) el.src = '/static/img/cerrado.gif';
            });
            const motorImage = document.getElementById('motorImage');
            if(motorImage) {
                motorImage.src = '/static/img/cerrado.gif';
                motorImage.style.display = 'inline-block';
            }
            const gastoWarn = document.getElementById('gastoWarningIcon');
            if(gastoWarn) gastoWarn.style.display = 'none';
            return;
        }

        const gasto = parseFloat(data.Gasto_Instantaneo);
        const presion = parseFloat(data.Presion_Instantanea);
        const nivel = parseFloat(data.Nivel_1);
        const estadoMotor = parseFloat(data.estado_motor);
        const fecha = data.ult_dato || 'N/A';
        let codigo = (isNaN(gasto) && isNaN(nivel)) ? "2" : ((gasto === 0 && nivel === 0) ? "1" : "0");
        const texto = significado[codigo] || 'Estado desconocido';

        setText('label1', `Q = ${!isNaN(gasto) ? gasto.toFixed(2) : 'N/A'}`);
        setText('label2', `${!isNaN(presion) ? presion.toFixed(2) : 'N/A'}`);
        setText('label3', `Actualización: ${fecha}`);
        setText('label4', `Estatus: ${texto}`);

        const img4 = document.getElementById('img4');
        if(img4) img4.src = presion ? '/static/img/luz.gif' : '/static/img/cerrado.gif';
        const img5 = document.getElementById('img5');
        const img6 = document.getElementById('img6');
        const img7 = document.getElementById('img7');
        const orbital = document.getElementById('orbital');
        const motorImage = document.getElementById('motorImage');
        const gastoWarn = document.getElementById('gastoWarningIcon');

        if (estadoMotor === 1) {
            if(img5) img5.src = '/static/img/reload.gif';
            if(orbital) orbital.style.display = 'block';
            if(motorImage) motorImage.style.display = 'none';
        } else {
            if(orbital) orbital.style.display = 'none';
            if(motorImage) {
                Object.assign(motorImage.style, {
                    display: 'inline-block',
                    width: '20px',
                    height: '20px',
                    position: 'absolute',
                    top: '28%',
                    left: '72%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: '1000'
                });
            }
        }

        if (sitio === 'p25' && motorImage) motorImage.src = (!isNaN(gasto) && gasto>0) ? '/static/img/luz.gif' : '/static/img/cerrado.gif';
        if (sitio === 'p25' && img5) img5.src = (!isNaN(gasto) && gasto>0) ? '/static/img/reload.gif' : '/static/img/cerrado.gif';
        if (sitio === 'p254' && motorImage) motorImage.src = (!isNaN(gasto) && gasto>0) ? '/static/img/luz.gif' : '/static/img/cerrado.gif';
        if (sitio === 'p85' && motorImage) motorImage.src = (!isNaN(gasto) && gasto>0) ? '/static/img/luz.gif' : '/static/img/cerrado.gif';
        if (sitio === 'p85' && img5) img5.src = (!isNaN(gasto) && gasto>0) ? '/static/img/reload.gif' : '/static/img/cerrado.gif';


        let mostrarAnimacion = (sitio==='p263') ? (estadoMotor===1) : (!isNaN(gasto) && gasto>0 && !isNaN(presion) && presion>0);

        if (mostrarAnimacion) {
            if(img6) img6.src = '/static/img/flujo_izq.gif';
            if(img7) img7.src = '/static/img/flujo_izq.gif';
            if(gastoWarn) gastoWarn.style.display = 'none';
        } else {
            if(img6) img6.src = '/static/img/cerrado.gif';
            if(img7) img7.src = '/static/img/cerrado.gif';
            if(gastoWarn) gastoWarn.style.display = 'block';
        }
    }

    // Inicializar polling
    fetchRealData();
    setInterval(fetchRealData, 30000);
});
