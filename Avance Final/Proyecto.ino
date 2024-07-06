#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "COTE1";
const char* password = "08192905ca";
const char* serverUrl = "http://52.200.139.211:5000/api/data"; // URL del servidor Flask

#define TRIG WB_IO6
#define ECHO WB_IO4

#define DEPOSIT_HEIGHT 100 // Altura del depósito en cm

float ratio = 343.0 / 2 / 10000; // Velocidad del sonido en el aire (m/s) -> cm/us

void connectToWiFi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado a WiFi");
  } else {
    Serial.println("\nNo se pudo conectar a WiFi");
  }
}

void setup() {
  Serial.begin(115200);
  connectToWiFi();

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  Serial.println("========================");
  Serial.println("    Sensor de Llenado");
  Serial.println("========================");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  long duration, distance;
  float fillLevel;

  // Emitir pulso ultrasónico
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = duration * ratio;

  // Calcular nivel de llenado en porcentaje
  if (distance > 0 && distance <= DEPOSIT_HEIGHT) {
    fillLevel = (1.0 - (distance / (float)(DEPOSIT_HEIGHT))) * 100.0;
  } else {
    fillLevel = 0; // Manejar caso fuera de rango o error de lectura
  }

  // Enviar datos al servidor Flask
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Construir el mensaje JSON
    String payload = "{\"nivelLlenado\":" + String(fillLevel) + "}";

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

  delay(60000); // Esperar 60 segundos antes de la siguiente medición 60000
}

