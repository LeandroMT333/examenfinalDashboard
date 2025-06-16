from flask import Flask, render_template, jsonify
from pymongo import MongoClient
import certifi
from bson.decimal128 import Decimal128

# Inicializar Flask
app = Flask(__name__)

# Conexión a MongoDB
usuario = "LeandroMT369"
password = "Nikitinh0369"  
cluster = "cluster0.9ivhqes.mongodb.net"
dbname = "examenfinal"

uri = f"mongodb+srv://{usuario}:{password}@{cluster}/?retryWrites=true&w=majority"
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client[dbname]

# Ruta principal que carga el HTML
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint de prueba para asegurar conexión
@app.route("/api/ping")
def ping():
    return jsonify({"status": "ok", "mensaje": "Conexión exitosa a MongoDB"})

##
@app.route("/api/anios-disponibles")
def obtener_anios():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$substrBytes": ["$semestre", 0, 4]
                    }
                }
            },
            {"$sort": {"_id": 1}}
        ]
        resultados = list(db.curso.aggregate(pipeline))
        anios = [r["_id"] for r in resultados]
        return jsonify(anios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
##

##

@app.route("/api/tabla-estudiantes")
def tabla_estudiantes():
    datos = list(db.estudiantes.find({}, {"_id": 0}))
    return jsonify(datos)

@app.route("/api/tabla-profesores")
def tabla_profesores():
    profesores = list(db.profesor.find({}, {"_id": 0}))
    for p in profesores:
        if isinstance(p.get("salario"), Decimal128):
            p["salario"] = float(p["salario"].to_decimal())
    return jsonify(profesores)

@app.route("/api/tabla-cursos")
def tabla_cursos():
    datos = list(db.curso.find({}, {"_id": 0}))
    return jsonify(datos)

@app.route("/api/tabla-inscripciones")
def tabla_inscripciones():
    inscripciones = list(db.inscripcion.find({}, {"_id": 0}))
    for i in inscripciones:
        if isinstance(i.get("nota"), Decimal128):
            i["nota"] = float(i["nota"].to_decimal())
    return jsonify(inscripciones)


###
@app.route("/api/estudiante-top")
def estudiante_top():
    try:
        pipeline = [
            {"$sort": {"nota": -1}},
            {"$limit": 1},
            {
                "$lookup": {
                    "from": "estudiantes",
                    "localField": "idEstudiante",
                    "foreignField": "idEstudiante",
                    "as": "info_estudiante"
                }
            },
            {"$unwind": "$info_estudiante"},
            {
                "$project": {
                    "_id": 0,
                    "nombre": "$info_estudiante.nombre",
                    "nota": 1
                }
            }
        ]
        resultado = next(db.inscripcion.aggregate(pipeline))
        nota = resultado["nota"]
        
        if isinstance(nota, Decimal128):
            nota = float(nota.to_decimal())
        else:
            nota = float(nota)

        return jsonify({
            "nombre": resultado["nombre"],
            "nota": round(nota, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/estudiante-mas-joven")
def estudiante_mas_joven():
    try:
        estudiante = db.estudiantes.find_one(
            sort=[("fechaNacimiento", -1)],
            projection={"_id": 0, "nombre": 1, "fechaNacimiento": 1}
        )
        return jsonify(estudiante)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/estudiantes-carrera")
def estudiantes_por_carrera():
    pipeline = [
        {"$group": {"_id": "$carrera", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]
    resultados = list(db.estudiantes.aggregate(pipeline))
    datos = {
        "carreras": [r["_id"] for r in resultados],
        "totales": [r["total"] for r in resultados]
    }
    return jsonify(datos)


@app.route("/api/promedio-notas-curso")
def promedio_notas_curso():

        pipeline = [
            {
                "$lookup": {
                    "from": "curso",
                    "localField": "idCurso",
                    "foreignField": "idCurso",
                    "as": "curso_info"
                }
            },
            {"$unwind": "$curso_info"},
            {
                "$group": {
                    "_id": "$curso_info.nombre",
                    "promedio": {"$avg": "$nota"}
                }
            },
            {"$sort": {"promedio": -1}}
        ]
        resultados = list(db.inscripcion.aggregate(pipeline))
        
        cursos = []
        promedios = []

        for r in resultados:
            cursos.append(r["_id"])
            promedio_val = r["promedio"]
            # Convierte Decimal128 o cualquier otro tipo a float de forma segura
            if isinstance(promedio_val, Decimal128):
                promedio_val = float(promedio_val.to_decimal())
            else:
                promedio_val = float(promedio_val)
            promedios.append(round(promedio_val, 2))

        return jsonify({
            "cursos": cursos,
            "promedios": promedios
        })

@app.route("/api/salario-promedio-carrera")
def salario_promedio_carrera():

        pipeline = [
            {
                "$lookup": {
                    "from": "curso",
                    "localField": "idCurso",
                    "foreignField": "idCurso",
                    "as": "curso_info"
                }
            },
            {"$unwind": "$curso_info"},
            {
                "$lookup": {
                    "from": "profesor",
                    "localField": "curso_info.idProfesor",
                    "foreignField": "idProfesor",
                    "as": "profesor_info"
                }
            },
            {"$unwind": "$profesor_info"},
            {
                "$lookup": {
                    "from": "estudiantes",
                    "localField": "idEstudiante",
                    "foreignField": "idEstudiante",
                    "as": "estudiante_info"
                }
            },
            {"$unwind": "$estudiante_info"},
            {
                "$group": {
                    "_id": "$estudiante_info.carrera",
                    "salario_promedio": {"$avg": "$profesor_info.salario"}
                }
            },
            {"$sort": {"salario_promedio": -1}}
        ]

        resultados = list(db.inscripcion.aggregate(pipeline))

        carreras = []
        salarios = []

        for r in resultados:
            carreras.append(r["_id"])
            s = r["salario_promedio"]
            if isinstance(s, Decimal128):
                s = float(s.to_decimal())
            else:
                s = float(s)
            salarios.append(round(s, 2))

        return jsonify({
            "carreras": carreras,
            "salarios": salarios
        })



@app.route("/api/profesores-por-carrera")
def profesores_por_carrera():

        pipeline = [
            {
                "$lookup": {
                    "from": "curso",
                    "localField": "idCurso",
                    "foreignField": "idCurso",
                    "as": "curso_info"
                }
            },
            {"$unwind": "$curso_info"},
            {
                "$lookup": {
                    "from": "estudiantes",
                    "localField": "idEstudiante",
                    "foreignField": "idEstudiante",
                    "as": "estudiante_info"
                }
            },
            {"$unwind": "$estudiante_info"},
            {
                "$group": {
                    "_id": {
                        "carrera": "$estudiante_info.carrera",
                        "profesor": "$curso_info.idProfesor"
                    }
                }
            },
            {
                "$group": {
                    "_id": "$_id.carrera",
                    "totalProfesores": {"$sum": 1}
                }
            },
            {"$sort": {"totalProfesores": -1}}
        ]

        resultados = list(db.inscripcion.aggregate(pipeline))
        datos = {
            "carreras": [r["_id"] for r in resultados],
            "profesores": [r["totalProfesores"] for r in resultados]
        }
        return jsonify(datos)



if __name__ == "__main__":
    app.run(debug=True)
