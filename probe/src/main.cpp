/*********
  Rui Santos
  Complete instructions at https://RandomNerdTutorials.com/esp8266-nodemcu-websocket-server-sensor/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.
  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*********/

/* Adapted to use a different IMU by Joey Reback at Colorado State University
 * Using code from randomNerdTutorials and Adafruit's LSM9DS1 Tutorial
 * 
 * Purpose:    Demonstrate the functionality of the Adafruit LSM9DS1 IMU
 * Parts used: Adafruit Huzzah ESP8266, LSM9DS1, Adafruit LiPo Battery and LiPo Charger
 * IDE used:   VSCode with PlatformIO plugin
 * TODO:       Threejs integration.
*/


#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"
#include <Wire.h>
#include <SPI.h>
#include <MPU6050.h>
#include <Arduino_JSON.h>

//pin definitions
#define LSM9DS1_SCK A5
#define LSM9DS1_MISO 12
#define LSM9DS1_MOSI A4
#define LSM9DS1_XGCS 6
#define LSM9DS1_MCS 5

//Network Credentials
const char* ssid     = "TP-Link_AF39";
const char* password = "65105474";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

// Create a WebSocket object
AsyncWebSocket ws("/ws");

// Json Variable to Hold Sensor Readings
JSONVar readings;

// Timer variables
unsigned long lastTime = 0;  
unsigned long timerDelay = 50;

double rotationXabs = 0;
double rotationYabs = 0;
double rotationZabs = 0;
double heading;

MPU6050 mpu;

// Init IMU
void setupSensor(){
  mpu.initialize();
  mpu.CalibrateGyro();
}

// Get Sensor Readings and return JSON object
String getSensorReadings(){
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
  /* Get a new sensor event */ 
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  readings["accelx"] = String(ax);
  readings["accely"] =  String(ay);
  readings["accelz"] = String(az);

  readings["gyrox"] = String(gx);
  readings["gyroy"] =  String(gy);
  readings["gyroz"] = String(gz); 

  if (gx > 0.5 || gx < -0.5) rotationXabs += gx; 
  if (gy > 0.5 || gy < -0.5) rotationYabs += gy;
  if (gz > 0.5 || gz < -0.5) rotationZabs += gz; 

  readings["absX"] = String(rotationXabs);
  readings["absY"] = String(rotationYabs);
  readings["absZ"] = String(rotationZabs);
  

  String jsonString = JSON.stringify(readings);
  return jsonString;
}

// Initialize LittleFS
void initFS() {
  if (!LittleFS.begin()) {
    Serial.println("An error has occurred while mounting LittleFS");
  }
  else{
   Serial.println("LittleFS mounted successfully");
  }
}

// Initialize WiFi
void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println(WiFi.localIP());
}

void notifyClients(String sensorReadings) {
  ws.textAll(sensorReadings);
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    //data[len] = 0;
    //String message = (char*)data;
    // Check if the message is "getReadings"
    //if (strcmp((char*)data, "getReadings") == 0) {
      //if it is, send current sensor readings
      String sensorReadings = getSensorReadings();
      Serial.print(sensorReadings);
      notifyClients(sensorReadings);
    //}
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

void initIMU(){
  Serial.println("BEGIN IMU SETUP");
  setupSensor();
}

void setup() {
  Serial.begin(9600);
  Serial.println("IMU Demo V2");
  initWiFi();
  Serial.println("PASSED WIFI TEST");
  initFS();
  initWebSocket();

  // Web Server Root URL
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(LittleFS, "/index.html", "text/html");
  });

  server.serveStatic("/", LittleFS, "/");

  // Start server
  server.begin();
  initIMU();
}

void loop() {
  if ((millis() - lastTime) > timerDelay) {
    String sensorReadings = getSensorReadings();
    //Serial.print(sensorReadings);
    notifyClients(sensorReadings);

  lastTime = millis();

  }

  ws.cleanupClients();
}
