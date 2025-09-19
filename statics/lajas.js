let estadoNivelActual = null;

const labelMappings = {
  'ultimo7': { campo: 'nivel', texto: 'Nivel: ' },
  'ultimo8': { campo: 'entrada', texto: 'Q= Entrada: ' },
  'ultimo10': { campo: 'salida', texto: 'Q= Salida: ' }
};

const MAX_CYLINDER_HEIGHT = 5;
const MIN_CYLINDER_HEIGHT = 0;
const API_BASE_URL = window.location.origin;





let ultimoEstado = null;

// Cargar datos desde el servidor
async function fetchAPIData() {
    try {
        const response = await fetch("/datos-resumidos/tanquelajas");
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error al obtener datos:", error);
        return null;
    }
}

// Actualizar etiquetas e interfaz
async function updateLabels() {
    try {
        const data = await fetchAPIData();
        if (!data) return;

        const currentEstado = JSON.stringify(data);

        if (currentEstado !== ultimoEstado) {
            ultimoEstado = currentEstado;

            Object.entries(labelMappings).forEach(([id, config]) => {
                const label = document.getElementById(id);
                if (!label) return;

                if (config.campo === 'nivel') {
                    ajustarCilindro(parseFloat(data.nivel));
                }

                label.innerText = config.texto + (data[config.campo] ?? 'N/A');
            });

            const fechaElemento = document.getElementById('fechaDatos');
            if (fechaElemento && data.timestamp) {
                fechaElemento.innerText = `Última lectura: ${new Date(data.timestamp).toLocaleString()}`;
            }

            mostrarNotificacion("✅ Datos actualizados");
        }

    } catch (error) {
        console.error("Error al actualizar manualmente:", error);
        document.getElementById("ultimo8").textContent = "⚠️ Error al cargar entrada";
        document.getElementById("ultimo10").textContent = "⚠️ Error al cargar salida";
    }
}

// Notificación temporal
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

// Ejecutar al inicio y actualizar cada 30 segundos
updateLabels();
setInterval(updateLabels, 30000);


// Mostrar notificación temporal
function mostrarNotificacion(mensaje) {
  let notif = document.getElementById("notif");
  if (!notif) {
    notif = document.createElement("div");
    notif.id = "notif";
    notif.style.position = "fixed";
    notif.style.bottom = "390px";
    notif.style.right = "620px";
    notif.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
    notif.style.color = "yellow";
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


// Ajusta el cilindro visual según el nivel del tanque
function ajustarCilindro(nivel) {
    const MAX_NIVEL = 5;
    const cilindro = document.getElementById("cilindroNivel");
    const alerta = document.getElementById("alertaNivel");
    const textoAlerta = document.getElementById("textoAlerta");

    if (!cilindro) return;

    // Calcular altura proporcional
    const alturaMaxima = 46; // vh
    const nuevaAltura = (nivel / MAX_NIVEL) * alturaMaxima;
    cilindro.style.height = `${nuevaAltura}vh`;
    cilindro.style.backgroundColor = 'rgba(81, 255, 0, 0.84)';

    // Alertas visuales si hay nivel fuera de rango
    if (nivel < 2 && alerta && textoAlerta) {
        alerta.style.display = 'block';
        textoAlerta.textContent = '⚠️ Nivel Bajo';
        cilindro.style.backgroundColor = 'rgba(255, 17, 0, 0.6)';
    } else if (nivel > 4.5 && alerta && textoAlerta) {
        alerta.style.display = 'block';
        textoAlerta.textContent = '⚠️ Nivel Alto';
        cilindro.style.backgroundColor = 'rgba(255, 0, 0, 0.6)';
    } else if (alerta) {
        alerta.style.display = 'none';
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
    const response = await fetch(`${API_BASE_URL}/historial/tanquelajas`);
    if (!response.ok) throw new Error('Error al obtener historial');
    const json = await response.json();
    return json.historial || [];
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