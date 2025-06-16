function cargarTabla(nombre) {
    fetch(`/api/tabla-${nombre}`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("tablaContainer");
            if (data.length === 0) {
                container.innerHTML = "<p>No hay datos disponibles.</p>";
                return;
            }

            const columnas = Object.keys(data[0]);
            let html = "<table class='table table-bordered table-striped'>";
            html += "<thead><tr>" + columnas.map(col => `<th>${col}</th>`).join("") + "</tr></thead>";
            html += "<tbody>";
            data.forEach(row => {
                html += "<tr>" + columnas.map(col => `<td>${row[col]}</td>`).join("") + "</tr>";
            });
            html += "</tbody></table>";
            container.innerHTML = html;
        });
}

// Manejador de pestañas
document.querySelectorAll("#tablaTabs .nav-link").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll("#tablaTabs .nav-link").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        cargarTabla(btn.dataset.tab);
    });
});


cargarTabla("estudiantes");
const anioSelect = document.getElementById("selectAnio");

function cargarAnios() {
    fetch("/api/anios-disponibles")
        .then(res => res.json())
        .then(anios => {
            anioSelect.innerHTML = ""; // limpiar opciones anteriores
            anios.forEach(anio => {
                const option = document.createElement("option");
                option.value = anio;
                option.textContent = anio;
                anioSelect.appendChild(option);
            });

            // Usar el primer año como valor por defecto
            const anioInicial = anios[0];
            anioSelect.value = anioInicial;
            cargarTodosLosGraficos(anioInicial);
        })
        .catch(err => {
            console.error("❌ Error al cargar los años disponibles:", err);
        });
}

anioSelect.addEventListener("change", () => {
    const anio = anioSelect.value;
    cargarTodosLosGraficos(anio);
});

document.addEventListener("DOMContentLoaded", () => {
    cargarAnios();
});

document.addEventListener("DOMContentLoaded", () => {
    
    fetch("/api/estudiante-top")
        .then(res => res.json())
        .then(data => {
            const texto = `${data.nombre} - Nota más alta: ${data.nota}`;
            document.getElementById("mejorEstudiante").textContent = texto;
        })
        .catch(err => console.error("Error en estudiante-top:", err));

    fetch("/api/estudiante-mas-joven")
        .then(res => res.json())
        .then(data => {
            const fecha = new Date(data.fechaNacimiento).toLocaleDateString();
            const texto = `${data.nombre} - Nacido el ${fecha}`;
            document.getElementById("estudianteJoven").textContent = texto;
        })
        .catch(err => console.error("Error en estudiante-mas-joven:", err));


    fetch("/api/estudiantes-carrera")
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('graficoCarreras').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.carreras,
                    datasets: [{
                        label: 'Estudiantes por Carrera',
                        data: data.totales,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)'
                    }]
                }
            });
        });

fetch("/api/promedio-notas-curso")
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al obtener datos del servidor");
        }
        return response.json();
    })
    .then(data => {
        const ctx = document.getElementById('graficoPromedios').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.cursos,
                datasets: [{
                    label: 'Promedio de Notas',
                    data: data.promedios,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)'
                }]
            }
        });
    })
    .catch(error => {
        console.error("❌ Error al cargar el gráfico de promedios:", error);
        alert("Ocurrió un error al cargar el gráfico de promedios. Revisa la consola para más detalles.");
    });

    fetch("/api/salario-promedio-carrera")
    .then(response => {
        if (!response.ok) throw new Error("Error al obtener datos del servidor");
        return response.json();
    })
    .then(data => {
        const ctx = document.getElementById('graficoSalarioCarrera').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.carreras,
                datasets: [{
                    label: 'Salario Promedio (por carrera)',
                    data: data.salarios,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)'
                }]
            }
        });
    })
    .catch(err => {
        console.error("❌ Error al cargar el gráfico de salarios:", err);
    });

    fetch("/api/profesores-por-carrera")
    .then(response => {
        if (!response.ok) throw new Error("Error al obtener datos del servidor");
        return response.json();
    })
    .then(data => {
        const ctx = document.getElementById('graficoProfesoresCarrera').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.carreras,
                datasets: [{
                    label: 'Profesores por Carrera',
                    data: data.profesores,
                    backgroundColor: 'rgba(255, 206, 86, 0.6)'
                }]
            }
        });
    })
    .catch(err => {
        console.error("❌ Error al cargar el gráfico de profesores:", err);
    });

});

document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("modoToggle");
    const body = document.body;

    toggleBtn.addEventListener("click", () => {
        body.classList.toggle("modo-oscuro");

        const esOscuro = body.classList.contains("modo-oscuro");
        toggleBtn.innerHTML = esOscuro ? "☀️ Modo Claro" : "🌙 Modo Oscuro";
    });
});

