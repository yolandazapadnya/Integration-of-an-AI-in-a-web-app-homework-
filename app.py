from dotenv import load_dotenv
import os
import requests  # Import the requests library for making HTTP requests
from flask import Flask, render_template, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Retrieve the GROQ API key from the environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Use GROQ API key

print("Loaded API Key:", GROQ_API_KEY)

# Check if the API key is loaded correctly
if not GROQ_API_KEY:
    print("API Key not found. Make sure your .env file is set correctly.")
else:
    print("API Key loaded successfully.")

# Set the GROQ API URL (endpoint)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Replace with correct endpoint

# Niveles de actividad
niveles_actividad_options = [
    ('sedentario', 'Sedentario (Poco o ningún ejercicio)'),
    ('poco_activo', 'Poco Activo (1-3 días/semana)'),
    ('moderadamente_activo', 'Moderadamente Activo (3-5 días/semana)'),
    ('muy_activo', 'Muy Activo (6-7 días/semana)'),
    ('super_activo', 'Super Activo (Atleta profesional/2x entrenamientos)')
]

comidas_favoritas = {
    'leite': 'leite',
    'verduras': 'verduras',
    'fastfood': 'fastfood'
}

# Initialize Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', niveles_actividad=niveles_actividad_options)

@app.route('/recommend', methods=['POST'])
def recommend():
    # Get form data
    edad = request.form.get('edad')
    niveles_actividad = request.form.get('niveles_actividad')
    comidas_favoritas = request.form.get('comidas_favoritas')
    restricciones_dietéticas_o_alergias = request.form.get('restricciones_dietéticas_o_alergias')


    if not restricciones_dietéticas_o_alergias:
        restricciones_dietéticas_o_alergias = "Ninguna"

    # Construct the prompt
    prompt = f"""Como nutricionista profesional, crea un plano de nutrición personalizado para alguien con el siguiente perfil:

    Edad: {edad} años
    Nivel de Actividad: {niveles_actividad}
    Comidas Favoritas: {comidas_favoritas}
    Restricciones Dietéticas/Alergias: {restricciones_dietéticas_o_alergias}

    Por favor, proporciona:
    1. Estimación de necesidades calóricas diarias
    2. Distribución recomendada de macronutrientes
    3. Un plan de comidas diario de ejemplo incorporando sus comidas favoritas cuando sea posible
    4. Consideraciones nutricionales específicas para su grupo de edad
    5. Recomendaciones basadas en su nivel de actividad
    6. Alternativas seguras para cualquier alimento restringido
    7. 2-3 sugerencias de snacks saludables
    Formatea la respuesta claramente con encabezados y puntos para facilitar la lectura.
    Ten en cuenta la salud y la seguridad, especialmente con respecto a las restricciones mencionadas."""

    print("Prompt que vamos a enviar a GROQ:")
    print("-----------------------------")
    print(prompt)
    print("-----------------------------")

    # Prepare the data for the request
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mixtral-8x7b-32768",  # Use a supported GROQ model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        # Make the POST request to the GROQ API
        response = requests.post(GROQ_API_URL, json=data, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            recommendation = response_data['choices'][0]['message']['content']

            # Return the response in JSON format
            return jsonify({'success': True, 'recommendation': recommendation})
        else:
            # If the response status code isn't 200, return an error
            return jsonify({'success': False, 'error': f"API Error: {response.status_code} - {response.text}"})

    except Exception as e:
        # If any error occurs, return the error message
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
