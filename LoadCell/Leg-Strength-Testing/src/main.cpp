#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"
#include <HX711_ADC.h>
#include <Wire.h>
#include <Arduino_JSON.h>

// Function prototypes
double readWeight();
String getSensorReadings();
void initFS();
void handleWebSocketMessage(void *arg, uint8_t *data, size_t len);
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len);
void initWebSocket();
void initWiFi();
void notifyClients(String sensorReadings);
void initLoadCell();

// Network Credentials (for Access Point)
const char* ssid = "RamBots";
const char* password = "csuece2024";

// Timer Variables
unsigned long lastTime = 0;
unsigned long timerDelay = 200;
volatile boolean newDataReady;

// Loadcell Values
const double calibrationValue = 696.0;
unsigned long t = 0;
const int HX711_dout = 25;
const int HX711_sck = 26;
double old_weight = 0.0;
HX711_ADC LoadCell(HX711_dout, HX711_sck);
const unsigned long stabilizingtime = 2000;

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

// Create a WebSocket object
AsyncWebSocket ws("/ws");

// Json Variable to Hold Sensor Readings
JSONVar readings;

double readWeight() {
  const int serialPrintInterval = 0;
  if (millis() > t + serialPrintInterval) {
      float i = LoadCell.getData();
      newDataReady = 0;
      old_weight = i;
      t = millis();
      return i;
    }
  return old_weight;
}

void dataReadyISR() {
  if (LoadCell.update()) {
    newDataReady = 1;
  }
}

String getSensorReadings() {
    double load = readWeight();
    readings["Strength"] = String(load);
    String jsonString = JSON.stringify(readings);
    return jsonString;
}

// Initialize LittleFS
void initFS() {
    if (!LittleFS.begin()) {
        Serial.println("An error has occurred while mounting LittleFS");
    } else {
        Serial.println("LittleFS mounted successfully");
    }
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
    AwsFrameInfo *info = (AwsFrameInfo*)arg;
    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
        String sensorReadings = getSensorReadings();
        Serial.print(sensorReadings);
        notifyClients(sensorReadings);
    }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
    switch (type) {
        case WS_EVT_CONNECT:
            Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
            break;
        case WS_EVT_DISCONNECT:
            Serial.printf("WebSocket client #%u disconnected\n", client->id());
            break;
        case WS_EVT_DATA:
            handleWebSocketMessage(arg, data, len);
            break;
        case WS_EVT_PONG:
        case WS_EVT_ERROR:
            break;
    }
}

void initWebSocket() {
    ws.onEvent(onEvent);
    server.addHandler(&ws);
}

// Initialize WiFi as Access Point
void initWiFi() {
    WiFi.mode(WIFI_AP);  // Set to Access Point mode
    WiFi.softAP(ssid, password);  // Start the Access Point

    IPAddress IP = WiFi.softAPIP();  // Get the IP address of the Access Point
    Serial.print("Access Point IP Address: ");
    Serial.println(IP);
}

void notifyClients(String sensorReadings) {
    ws.textAll(sensorReadings);
}

void initLoadCell() {
  LoadCell.begin();
  unsigned long stabilizingtime = 2000; // tare preciscion can be improved by adding a few seconds of stabilizing time
  boolean _tare = true; //set this to false if you don't want tare to be performed in the next step
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    Serial.println("Startup is complete");
  }

  attachInterrupt(digitalPinToInterrupt(HX711_dout), dataReadyISR, FALLING);
}

void setup() {
    Serial.begin(9600);
    Serial.println("Load Cell");
    initWiFi();  // Now initializing as AP
    Serial.println("Started Access Point");
    initFS();
    initWebSocket();

    // Web Server Root URL
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(LittleFS, "/index.html", "text/html");
    });

    server.serveStatic("/", LittleFS, "/");

    // Start server
    server.begin();
}

void loop() {
    if ((millis() - lastTime) > timerDelay) {
        String sensorReadings = getSensorReadings();
        notifyClients(sensorReadings);

        lastTime = millis();
    }

    ws.cleanupClients();
}
