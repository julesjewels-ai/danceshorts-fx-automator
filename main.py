import argparse
import sys
import os
import logging
from src.core.app import DanceShortsAutomator

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_dummy_inputs_if_missing():
    """Generates sample JSON files if they don't exist to make the MVP runnable immediately."""
    import json
    
    if not os.path.exists('veo_instructions.json'):
        with open('veo_instructions.json', 'w') as f:
            json.dump({
                "scenes": [
                    {"id": 1, "source": "clip1.mp4", "start": 0, "duration": 8, "speed": 1.0},
                    {"id": 2, "source": "clip2.mp4", "start": 0, "duration": 8, "speed": 1.0},
                    {"id": 3, "source": "clip3.mp4", "start": 0, "duration": 8, "speed": 1.0},
                    {"id": 4, "source": "clip4.mp4", "start": 0, "duration": 8, "speed": 1.0}
                ]
            }, f, indent=2)
        logging.info("Created dummy veo_instructions.json")

    if not os.path.exists('metadata_options.json'):
        with open('metadata_options.json', 'w') as f:
            json.dump({
              "option_1": {
                "title": "Recuerdos de nuestra tierra 💃",
                "description": "Reviviendo la esencia de nuestras raíces con amor y elegancia. El sentimiento que nunca se olvida. #amor ❤️ #recuerdos 🕰️ #españa 🇪🇸 #tradicion 🏠 #bachata 🎶",
                "tags": [
                  "bachata",
                  "amor",
                  "paso doble",
                  "nostalgia",
                  "baile tradicional",
                  "españa",
                  "andalucia"
                ],
                "emotional_hook": "Nostalgia cálida que conecta con las raíces y los recuerdos familiares.",
                "text_hook": "¿Recuerdas este sentimiento?",
                "text_overlay": [
                  "El sol de nuestra tierra",
                  "Como en los viejos tiempos",
                  "Tradición que vive en el alma"
                ]
              },
              "option_2": {
                "title": "Pasión bajo el cielo azul ☀️",
                "description": "La elegancia del paso doble se encuentra con el romance eterno. Si amas la bachata romantica, esto es para ti. #bachataromantica ❤️ #amor 😍 #pasodoble 💃 #españa ☀️ #elegancia ✨",
                "tags": [
                  "bachata romantica",
                  "amor",
                  "elegancia",
                  "pasion",
                  "paso doble",
                  "estetica",
                  "danza"
                ],
                "emotional_hook": "Inspiración y deseo a través de una estética visualmente impactante y romántica.",
                "text_hook": "La pasión que detiene el tiempo.",
                "text_overlay": [
                  "Elegancia en cada paso",
                  "Bajo el cielo de Andalucía",
                  "Un baile, un sentimiento",
                  "Pura pasión española"
                ]
              },
              "option_3": {
                "title": "Orgullo y tradición viva 🇪🇸",
                "description": "¡Que no se pierda nuestro arte! Unidos por el ritmo que nos identifica a todos. #bachatadance 💃 #comunidad 🤝 #españa 🇪🇸 #amor ❤️ #cultura 🏛️",
                "tags": [
                  "bachata dance",
                  "españa",
                  "comunidad",
                  "orgullo español",
                  "cultura",
                  "amor",
                  "baile"
                ],
                "emotional_hook": "Sentido de pertenencia y orgullo por la identidad cultural compartida.",
                "text_hook": "Lo que nos une es el arte.",
                "text_overlay": [
                  "Nuestra cultura es vida",
                  "Pasión que nos identifica",
                  "Andalucía en el corazón"
                ]
              },
              "recommended": 2,
              "reasoning": "La Opción 2 es la más fuerte estratégicamente. El contraste visual del vestido amarillo contra el cielo azul y la arquitectura andaluza crea una estética aspiracional que funciona excepcionalmente bien en YouTube Shorts. Al integrar 'bachata romantica' en un contexto de elegancia y pasión, atraemos a una audiencia más amplia interesada en el romance y el baile profesional, aumentando el potencial de viralidad global más allá del nicho folclórico."
            }, f, indent=2)
        logging.info("Created dummy metadata_options.json")

def main():
    """Entry point for the DanceShorts FX Automator CLI."""
    parser = argparse.ArgumentParser(
        description="DanceShorts FX Automator: Automate post-production for dance videos."
    )
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--dry-run', action='store_true', help="Simulate rendering without invoking heavy video processing.")
    
    args = parser.parse_args()
    
    setup_logging()
    create_dummy_inputs_if_missing()

    try:
        app = DanceShortsAutomator(
            instruction_file='veo_instructions.json',
            options_file='metadata_options.json'
        )
        
        app.load_configurations()
        app.process_pipeline(dry_run=args.dry_run)
        
    except Exception as e:
        logging.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()