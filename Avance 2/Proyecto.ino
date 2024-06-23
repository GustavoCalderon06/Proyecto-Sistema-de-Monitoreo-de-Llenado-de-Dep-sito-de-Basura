#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "COTE1";
const char* password = "08192905ca";
const char* serverUrl = "http://52.200.139.211:5000/api/data"; // URL del servidor Flask

#define TRIG WB_IO6
#define ECHO WB_IO4

#define DEPOSIT_HEIGHT 100 // Altura del depósito en cm

float ratio = 346.6 / 1000 / 2; // Velocidad del sonido en el aire (m/s)
#define SCREEN_WIDTH 128 // set OLED width,unit
#define SCREEN_HEIGHT 64 // set OLED height,unit

#define OLED_RESET -1

Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conectado a WiFi");

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  oled.begin(SSD1306_SWITCHCAPVCC, 0x3C); // Inicializar pantalla OLED
  oled.clearDisplay();
  oled.display();

  Serial.println("========================");
  Serial.println("    Sensor de Llenado");
  Serial.println("========================");
}

void loop() {
  long duration, distance;
  float fillLevel;

  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = duration * ratio;

  // Calcular nivel de llenado en porcentaje
  if (distance > 0 && distance <= DEPOSIT_HEIGHT * 10) {
    fillLevel = (1.0 - (distance / (float)(DEPOSIT_HEIGHT * 10))) * 100.0;
  } else {
    fillLevel = 0; // Manejar caso fuera de rango o error de lectura
  }

  // Enviar datos al servidor Flask
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Construir el mensaje JSON
    String payload = "{\"distancia\":" + String(distance) + ",\"nivelLlenado\":" + String(fillLevel) + "}";

    int codigoRespuesta = http.POST(payload);

    if (codigoRespuesta > 0) {
      String respuesta = http.getString();
      Serial.println("Datos enviados correctamente: " + payload);
      Serial.println("Respuesta del servidor: " + respuesta);
    } else {
      Serial.println("Error al enviar datos: " + String(codigoRespuesta));
    }

    http.end(); // Terminar la conexión
  } else {
    Serial.println("Error al conectar al WiFi");
  }

 

  delay(5000); // Esperar 1 segundo antes de la siguiente medición
}

