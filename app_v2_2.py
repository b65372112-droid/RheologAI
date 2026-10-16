from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import gemelo_bitumen_pkg  # <-- Nueva librería compilada

app = Flask(__name__)
CORS(app)

print("⏳ Inicializando motor ReologIA (Paquete Compilado)...")
# Inicializamos la librería compilada de MATLAB
gemelo = gemelo_bitumen_pkg.initialize()
print("🚀 Motor ReologIA cargado y listo para peticiones.")

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'Web_argon_v3.html')

@app.route('/predecir', methods=['POST'])
def predecir():
    data = request.json
    
    pct_ce = float(data.get('ce', 0))
    pct_fr = float(data.get('fr', 0))
    pct_caco3 = float(data.get('caco3', 0))
    pct_rese = float(data.get('rese', 0))
    pct_ad4 = float(data.get('ad4', 0))
    pct_bo = float(data.get('bo', 0))
    temp_c = float(data.get('temp', 25))
    freq_hz = float(data.get('freq', 10))
    estado = str(data.get('estado', 'Original'))

    try:
        # Llamada directa al paquete (retorna las 7 variables)
        res_dsr, res_mscr_jnr, res_mscr_r, mscr_valido, res_las_nf50, res_las_nf25, las_valido = gemelo.predecir_web_v2(
            pct_ce, pct_fr, pct_caco3, pct_rese, pct_ad4, pct_bo, temp_c, freq_hz, estado, nargout=7
        )
        
        return jsonify({
            'exito': True,
            'dsr': {'valor': float(res_dsr), 'unidad': 'kPa'},
            'mscr': {
                'valido': bool(mscr_valido),
                'jnr': float(res_mscr_jnr) if mscr_valido else None,
                'r': float(res_mscr_r) if mscr_valido else None,
                'mensaje': '' if mscr_valido else '⚠️ No disponible: modelos MSCR entrenados únicamente entre 30°C y 80°C'
            },
            'las': {
                'valido': bool(las_valido),
                'nf50': float(res_las_nf50) if las_valido else None,
                'nf25': float(res_las_nf25) if las_valido else None,
                'mensaje': '' if las_valido else '⚠️ No disponible: modelos LAS entrenados únicamente entre 20°C y 25°C'
            }
        })

    except Exception as e:
        return jsonify({'exito': False, 'error': 'Error en la ejecución del modelo', 'detalle': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)