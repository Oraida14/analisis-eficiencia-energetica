const labelMappings = {
  'ultimo3': { campo: 'Presion_Instantanea', sitio: 'p263', texto: '', unidad: 'psi', circulo: 'circle-263' },
  'ultimo4': { campo: 'Gasto_Instantaneo', sitio: 'p263', texto: 'Q= ', unidad: 'L/s', circulo: 'circle-263' },
  'ultimo7': { campo: 'Nivel_1', sitio: 'tanque3cantos', texto: 'Nivel: ', unidad: 'm' },
  'ultimo8': { campo: 'Gasto_Instantaneo', sitio: 'tanque3cantos', texto: 'Q= Entrada: ', unidad: 'L/s' },
  'ultimo10': { campo: 'Gasto_Instantaneo', sitio: 'tanque3cantos', texto: 'Q= Salida: ', unidad: 'L/s' },
  'ultimo11': { campo: 'Presion_Instantanea', sitio: 'reb62', texto: '', unidad: 'psi', circulo: 'circle-reb_62' },
  'ultimo12': { campo: 'Gasto_Instantaneo', sitio: 'reb62', texto: 'Q= ', unidad: 'L/s', circulo: 'circle-reb_62' },
  'ultimo13': { campo: 'Presion_Instantanea', sitio: 'p25', texto: '', unidad: 'psi', circulo: 'circle-25-R' },
  'ultimo14': { campo: 'Gasto_Instantaneo', sitio: 'p25', texto: 'Q= ', unidad: 'L/s', circulo: 'circle-25-R' },
  'ultimo15': { campo: 'Presion_Instantanea', sitio: 'reb62a', texto: '', unidad: 'psi', circulo: 'circle-reb_62A' },
  'ultimo16': { campo: 'Gasto_Instantaneo', sitio: 'reb62a', texto: 'Q= ', unidad: 'L/s', circulo: 'circle-reb_62A' },
  'ultimo17': { texto: 'Gasto de Entrada', soloTexto: true },
  'ultimo18': { texto: 'Gasto de Salida', soloTexto: true }
};

const sitiosUnicos = [...new Set(Object.values(labelMappings).filter(e => e.sitio).map(e => e.sitio))];

async function fetchCSVData(sitio) {
    try {
        const response = await fetch(`/datos-individuales/${sitio}.csv`);
        if (!response.ok) throw new Error("Archivo no disponible");
        
        const text = await response.text();
        return parseCSV(text, sitio);
    } catch (error) {
        console.warn(`⚠️ No se pudo leer ${sitio}:`, error.message);
        return { sitio };
    }
}

function parseCSV(csvText, sitio) {
  const rows = csvText.trim().split('\n');
  const headers = rows[0].split(',');
  const lastRow = rows[1].split(',');

  const data = { sitio };
  headers.forEach((header, i) => {
    data[header.trim()] = lastRow[i]?.trim();
  });

  return data;
}

async function getAllData() {
  return await Promise.all(sitiosUnicos.map(sitio => fetchCSVData(sitio)));
}

async function updateLabels() {
  const data = await getAllData();
  let gastoEntrada = 0, gastoSalida = 0;

  data.forEach(d => {
    const sitio = (d.sitio || '').toLowerCase();
    const gasto = parseFloat(d.Gasto_Instantaneo);
    const presion = parseFloat(d.Presion_Instantanea);

    if (!isNaN(gasto)) {
      if (["p263", "p25"].includes(sitio)) gastoEntrada += gasto;
      if (["reb62", "reb62a"].includes(sitio)) gastoSalida += gasto;
    }

    for (const [id, config] of Object.entries(labelMappings)) {
      if (config.sitio === sitio) {
        const label = document.getElementById(id);
        if (label) {
          let valor = d[config.campo] ?? 'N/A';
          if (!isNaN(parseFloat(valor))) valor = parseFloat(valor).toFixed(2);
          label.innerText = `${config.texto}${valor} ${config.unidad || ''}`.trim();
        }
      }
    }
  });

  const le = document.getElementById('ultimo8');
  const ls = document.getElementById('ultimo10');
  if (le) le.innerText = ` ${gastoEntrada.toFixed(2)} L/s`;
  if (ls) ls.innerText = ` ${gastoSalida.toFixed(2)} L/s`;

  data.forEach(d => {
    const sitio = (d.sitio || '').toLowerCase();
    const map = { 'p263':'circle-263','p25':'circle-25-R','reb62':'circle-reb_62','reb62a':'circle-reb_62A' };
    const circle = document.getElementById(map[sitio]);
    if (!circle) return;
    const gasto = parseFloat(d.Gasto_Instantaneo);
    const presion = parseFloat(d.Presion_Instantanea);
    const u = {
      'p263':{gasto_min:30,gasto_max:52,presion_min:5,presion_max:15},
      'p25':{gasto_min:15,gasto_max:30,presion_min:6,presion_max:18},
      'reb62':{gasto_min:0,gasto_max:45,presion_min:10,presion_max:40},
      'reb62a':{gasto_min:0,gasto_max:45,presion_min:10,presion_max:40}
    }[sitio];

    if (!u || isNaN(gasto) || isNaN(presion) ||
    gasto < u.gasto_min || gasto > u.gasto_max ||
    presion < u.presion_min || presion > u.presion_max ||
    gasto === 0)
     {
      circle.classList.remove('green');
      circle.classList.add('red', 'blink');
    } else {
      circle.classList.remove('red','blink');
      circle.classList.add('green');
    }
  });
}

// Ejecutar al inicio y actualizar cada 30 segundos
updateLabels();  // Primera ejecución inmediata
setInterval(updateLabels, 30000);  // Actualización automática