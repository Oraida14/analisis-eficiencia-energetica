let estadoNivelActual = null;

const labelMappings = {
  'ultimo7': { campo: 'nivel', texto: 'Nivel: ' },
  'ultimo8': { campo: 'entrada', texto: 'Q= Entrada: ' },
  'ultimo10': { campo: 'salida', texto: 'Q= Salida: ' }
};

const MAX_CYLINDER_HEIGHT = 5;
const MIN_CYLINDER_HEIGHT = 0;
const API_BASE_URL = 'https://render-fastapi-app.onrender.com';



async function fetchAPIData() {
  try {
    const response = await fetch(`${API_BASE_URL}/datos-resumidos/tanque3cantos`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const json = await response.json();
    return json;
  } catch (error) {
    console.error("Error al obtener datos de la API:", error);
    return null;
  }
}

updateLabels
// Función para actualizar desde botón manual
async function actualizarDatosManualmente() {
  const boton = document.getElementById("btnActualizarManual");
  boton.disabled = true;
  boton.innerText = "🔄 Actualizando...";

  try {
    const data = await fetchAPIData();
    if (!data) {
      alert("Error al obtener datos desde el servidor.");
      return;
    }

    // Actualiza solo si hay datos nuevos
    const currentEstado = JSON.stringify(data);
    if (currentEstado !== ultimoEstado) {
      ultimoEstado = currentEstado;

      Object.entries(labelMappings).forEach(([id, config]) => {
        const label = document.getElementById(id);
        if (!label) return;
        if (config.campo === 'nivel') {
          ajustarCilindro(parseFloat(data.nivel));
        } else {
          label.innerText = config.texto + (data[config.campo] ?? 'N/A');
        }
      });

      const fechaElemento = document.getElementById('fechaDatos');
      if (fechaElemento && data.timestamp) {
        fechaElemento.innerText = `Última lectura: ${new Date(data.timestamp).toLocaleString()}`;
      }

      mostrarNotificacion("✅ Datos actualizados manualmente");
    } else {
      mostrarNotificacion("ℹ️ No hubo cambios en los datos");
    }

  } catch (error) {
    console.error("Error al actualizar manualmente:", error);
    alert("Hubo un error al actualizar los datos.");
  } finally {
    boton.disabled = false;
    boton.innerText = "🔁 Actualizar Datos Manualmente";
  }
}

// Mostrar notificación temporal
function mostrarNotificacion(mensaje) {
  let notif = document.getElementById("notif");
  if (!notif) {
    notif = document.createElement("div");
    notif.id = "notif";
    notif.style.position = "fixed";
    notif.style.bottom = "80px";
    notif.style.right = "20px";
    notif.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
    notif.style.color = "white";
    notif.style.padding = "10px 20px";
    notif.style.borderRadius = "5px";
    notif.style.opacity = "0";
    notif.style.transition = "opacity 0.5s ease, transform 0.3s ease";
    notif.style.zIndex = "1000";
    document.body.appendChild(notif);
  }

  notif.innerText = mensaje;
  notif.style.opacity = "1";
  notif.style.transform = "translateY(0)";

  setTimeout(() => {
    notif.style.opacity = "0";
    notif.style.transform = "translateY(-20px)";
  }, 3000);
}


function ajustarCilindro(nivel) {
  const cilindro = document.getElementById('cilindroNivel');
  const alerta = document.getElementById('alertaNivel');
  const flechaNivel = document.getElementById('flechaNivel');
  const textoAlerta = document.getElementById('textoAlerta');

  const maxAltura = 46; // vh
  const nuevoNivel = Math.min(Math.max(nivel, MIN_CYLINDER_HEIGHT), MAX_CYLINDER_HEIGHT);
  const nuevaAltura = (nuevoNivel / MAX_CYLINDER_HEIGHT) * maxAltura;
  const nuevaAlturaStr = `${nuevaAltura}vh`;

  if (cilindro && cilindro.style.height !== nuevaAlturaStr) {
    cilindro.style.height = nuevaAlturaStr;
  }

  if (flechaNivel) {
    flechaNivel.style.bottom = nuevaAlturaStr;
    flechaNivel.innerText = `Nivel: ${nivel.toFixed(2)} m`;
  }

  let nuevoEstado = '';
  if (nuevoNivel < 1.30) {
    nuevoEstado = 'bajo';
  } else if (nuevoNivel > 3.70) {
    nuevoEstado = 'alto';
  } else {
    nuevoEstado = 'normal';
  }

  if (nuevoEstado !== estadoNivelActual) {
    estadoNivelActual = nuevoEstado;
    switch (nuevoEstado) {
      case 'bajo':
        if (cilindro) cilindro.style.backgroundColor = 'rgba(255, 17, 0, 0.6)';
        if (alerta) alerta.style.display = 'block';
        if (textoAlerta) textoAlerta.innerText = 'Nivel Bajo';
        break;
      case 'alto':
        if (cilindro) cilindro.style.backgroundColor = 'rgba(255, 0, 0, 0.6)';
        if (alerta) alerta.style.display = 'block';
        if (textoAlerta) textoAlerta.innerText = 'Nivel Alto';
        break;
      case 'normal':
        if (cilindro) cilindro.style.backgroundColor = 'rgba(81, 255, 0, 0.84)';
        if (alerta) alerta.style.display = 'none';
        break;
    }
  }
}

async function graficarHistorialNivel() {
  const historial = await obtenerHistorial();
  if (!historial.length) return;

  const labels = historial.map(item => {
    const fecha = new Date(item.fecha_hora);
    return fecha.getHours().toString().padStart(2, '0') + ':' + fecha.getMinutes().toString().padStart(2, '0');
  });

  const nivelData = historial.map(item => item.Nivel_1);

  const ctx = document.getElementById('graficaNivel').getContext('2d');
  if (window.graficaNivel) window.graficaNivel.destroy();

  window.graficaNivel = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Nivel (m)',
        data: nivelData,
        borderColor: 'rgba(0, 110, 255, 1)',
        backgroundColor: 'rgba(0, 110, 255, 0.3)',
        fill: true,
        tension: 0.3,
      }]
    },
    options: {
      responsive: false,
      scales: {
        x: {
          ticks: {
            maxTicksLimit: 10,
            color: '#006eff',
            maxRotation: 45,
            minRotation: 45,
          },
          grid: { color: 'rgba(0, 110, 255, 0.2)' }
        },
        y: {
          ticks: { color: '#006eff' },
          grid: { color: 'rgba(0, 110, 255, 0.2)' },
          beginAtZero: true,
        }
      },
      plugins: {
        legend: {
          labels: { color: '#006eff' }
        }
      }
    }
  });
}

async function obtenerHistorial() {
  try {
    const response = await fetch(`${API_BASE_URL}/historial/tanque3cantos`);
    if (!response.ok) throw new Error('Error al obtener historial');
    return await response.json();
  } catch (error) {
    console.error("Error al obtener historial de niveles:", error);
    return [];
  }
}


graficarHistorialNivel();
updateLabels();
setInterval(updateLabels, 3000);

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btnActualizarManual");
  if (btn) {
    btn.addEventListener("click", actualizarDatosManualmente);
  }
});