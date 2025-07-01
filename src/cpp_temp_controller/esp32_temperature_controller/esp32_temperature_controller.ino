/*
 * ESP32 Professional Temperature Controller
 * High-temperature monitoring and control system (60-120°C)
 *
 * Features:
 * - Real-time temperature monitoring with charts
 * - Automatic relay control (60-70°C range)
 * - Modern responsive web dashboard
 * - Configuration management via web interface
 * - Data logging and history
 * - REST API for external integration
 *
 * Hardware Setup:
 * - DS18B20 sensor connected to GPIO4 (with 4.7kΩ pull-up resistor)
 * - Relay connected to GPIO5
 * - ESP32 creates WiFi access point for configuration
 *
 * Temperature Specifications:
 * - Max temperature: 120°C
 * - Relay activation: 60°C
 * - Relay deactivation: 70°C
 * - Reading interval: 2 seconds
 */

#include <ArduinoJson.h>
#include <AsyncTCP.h>
#include <DallasTemperature.h>
#include <ESPAsyncWebServer.h>
#include <OneWire.h>
#include <SPIFFS.h>
#include <WiFi.h>

// Configuration
const char *WIFI_SSID = "TempController";
const char *WIFI_PASSWORD = "temp123456";
const int WIFI_CHANNEL = 1;

// Hardware pins
const int DS18B20_PIN = 4;
const int RELAY_PIN = 5;

// Default temperature settings
const float DEFAULT_TEMP_LOW = 60.0;  // Relay activation temperature
const float DEFAULT_TEMP_HIGH = 70.0; // Relay deactivation temperature
const int DEFAULT_CHECK_INTERVAL = 2; // Reading interval in seconds
const float MAX_TEMP = 80.0;          // Maximum safe temperature
const float MIN_TEMP = 0.0;           // Minimum temperature

// Configuration file
const char *CONFIG_FILE = "/config.json";

// Data logging
const int MAX_DATA_POINTS = 100; // Number of data points to keep in memory
const char *DATA_FILE = "/temperature_data.json";

// Global variables
AsyncWebServer server(80);
OneWire oneWire(DS18B20_PIN);
DallasTemperature sensors(&oneWire);

// Configuration variables
float tempLow = DEFAULT_TEMP_LOW;
float tempHigh = DEFAULT_TEMP_HIGH;
int checkInterval = DEFAULT_CHECK_INTERVAL;

// Status variables
bool relayActive = false;
bool running = true;
float currentTemp = 0.0;
unsigned long lastReadingTime = 0;
unsigned long lastControlTime = 0;

// Data logging
struct DataPoint {
  unsigned long timestamp;
  float temperature;
  bool relayActive;
};

DataPoint dataHistory[MAX_DATA_POINTS];
int dataIndex = 0;
int dataCount = 0;

// System status
struct SystemStatus {
  bool sensorConnected = false;
  bool relayWorking = false;
  unsigned long uptime = 0;
  unsigned long totalReadings = 0;
  unsigned long errors = 0;
} systemStatus;

void setup() {
  Serial.begin(115200);
  Serial.println("=== ESP32 Professional Temperature Controller ===");
  Serial.println("Starting up...");

  // Setup hardware
  setupHardware();

  // Load configuration
  loadConfig();

  // Initialize data logging
  initializeDataLogging();

  // Setup WiFi access point
  setupWiFi();

  // Wait for WiFi to be ready
  delay(1000);

  // Setup web server
  setupWebServer();

  // Start control loop
  startControlLoop();

  Serial.println("ESP32 Temperature Controller initialized");
  Serial.printf("  - Temperature Low (activate relay): %.1f°C\n", tempLow);
  Serial.printf("  - Temperature High (deactivate relay): %.1f°C\n", tempHigh);
  Serial.printf("  - Check interval: %d seconds\n", checkInterval);
  Serial.printf("  - Max temperature: %.1f°C\n", MAX_TEMP);
  Serial.printf("  - WiFi SSID: %s\n", WIFI_SSID);
  Serial.printf("  - WiFi Password: %s\n", WIFI_PASSWORD);
}

void loop() {
  // Temperature control logic runs in main loop
  unsigned long currentTime = millis();
  if (currentTime - lastControlTime >= checkInterval * 1000) {
    controlTemperature();
    lastControlTime = currentTime;
  }

  // Update system status
  systemStatus.uptime = currentTime;

  delay(100); // Small delay to prevent watchdog issues
}

void setupHardware() {
  // Setup DS18B20 sensor
  sensors.begin();

  // Find DS18B20 devices
  int deviceCount = sensors.getDeviceCount();
  if (deviceCount == 0) {
    Serial.println("No DS18B20 sensor found!");
    systemStatus.sensorConnected = false;
    return;
  }
  Serial.printf("DS18B20 sensor found: %d devices\n", deviceCount);
  systemStatus.sensorConnected = true;

  // Setup relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Start with relay off
  Serial.println("Relay initialized");
  systemStatus.relayWorking = true;
}

void setupWiFi() {
  // Configure WiFi access point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);

  Serial.println("WiFi Access Point started");
  Serial.printf("  SSID: %s\n", WIFI_SSID);
  Serial.printf("  Password: %s\n", WIFI_PASSWORD);
  Serial.printf("  IP Address: %s\n", WiFi.softAPIP().toString().c_str());
}

void setupWebServer() {
  // Root endpoint that serves inline interface
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial.println("Root endpoint called");
    Serial.println("Serving inline interface");

    // Create a simple but functional interface
    String html = "<!DOCTYPE html><html><head><title>ESP32 Temperature "
                  "Controller</title>";
    html += "<style>";
    html += "body{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}";
    html += ".container{max-width:800px;margin:0 "
            "auto;background:white;padding:20px;border-radius:10px}";
    html += ".header{text-align:center;margin-bottom:30px}";
    html += ".status-grid{display:grid;grid-template-columns:repeat(auto-fit,"
            "minmax(200px,1fr));gap:20px;margin-bottom:30px}";
    html += ".status-card{background:#f8f9fa;padding:20px;border-radius:8px;"
            "text-align:center}";
    html += ".temp-display{font-size:2.5em;font-weight:bold;color:#007bff}";
    html += ".relay-on{color:#28a745;font-weight:bold}";
    html += ".relay-off{color:#dc3545;font-weight:bold}";
    html += ".config-section{background:#f8f9fa;padding:20px;border-radius:8px;"
            "margin-bottom:20px}";
    html += ".form-group{margin-bottom:15px}";
    html +=
        ".form-group label{display:block;margin-bottom:5px;font-weight:bold}";
    html += ".form-group input{width:100%;padding:8px;border:1px solid "
            "#ddd;border-radius:4px;box-sizing:border-box}";
    html +=
        ".btn{background:#007bff;color:white;padding:10px "
        "20px;border:none;border-radius:4px;cursor:pointer;margin-right:10px}";
    html += ".btn-danger{background:#dc3545}";
    html += ".btn-success{background:#28a745}";
    html += ".control-buttons{margin-top:20px}";
    html += "</style></head><body>";
    html += "<div class='container'>";
    html += "<div class='header'><h1>🌡️ ESP32 Temperature "
            "Controller</h1><p>Professional High-Temperature Monitoring "
            "System</p></div>";
    html += "<div class='status-grid'>";
    html += "<div class='status-card'><h3>Current Temperature</h3><div "
            "class='temp-display' id='currentTemp'>--</div></div>";
    html += "<div class='status-card'><h3>Relay Status</h3><div "
            "id='relayStatus'>--</div></div>";
    html += "<div class='status-card'><h3>Controller</h3><div "
            "id='controllerStatus'>--</div></div>";
    html += "<div class='status-card'><h3>Sensor</h3><div "
            "id='sensorStatus'>--</div></div>";
    html += "</div>";
    html += "<div class='config-section'>";
    html += "<h2>Configuration</h2>";
    html += "<form id='configForm'>";
    html += "<div class='form-group'><label for='tempLow'>Temperature Low "
            "(Activate Relay) °C:</label><input type='number' id='tempLow' "
            "step='0.1' min='0' max='120' required></div>";
    html += "<div class='form-group'><label for='tempHigh'>Temperature High "
            "(Deactivate Relay) °C:</label><input type='number' id='tempHigh' "
            "step='0.1' min='0' max='120' required></div>";
    html += "<div class='form-group'><label for='checkInterval'>Reading "
            "Interval (seconds):</label><input type='number' "
            "id='checkInterval' min='1' max='60' required></div>";
    html += "<button type='submit' class='btn'>Save Configuration</button>";
    html += "<button type='button' class='btn' onclick='loadConfig()'>Load "
            "Current</button>";
    html += "</form></div>";
    html += "<div class='control-buttons'>";
    html += "<button class='btn btn-success' "
            "onclick='controlAction(\"start\")'>Start Controller</button>";
    html += "<button class='btn btn-danger' "
            "onclick='controlAction(\"stop\")'>Stop Controller</button>";
    html += "<button class='btn' onclick='controlAction(\"relay_on\")'>Relay "
            "ON</button>";
    html += "<button class='btn' onclick='controlAction(\"relay_off\")'>Relay "
            "OFF</button>";
    html += "</div></div>";
    html += "<script>";
    html += "loadStatus();loadConfig();setInterval(loadStatus,5000);";
    html += "function "
            "loadStatus(){fetch('/api/status').then(r=>r.json()).then(d=>{";
    html += "document.getElementById('currentTemp').textContent=d.temperature+'"
            "°C';";
    html += "document.getElementById('relayStatus').textContent=d.relay_active?"
            "'ON':'OFF';";
    html += "document.getElementById('relayStatus').className=d.relay_active?'"
            "relay-on':'relay-off';";
    html += "document.getElementById('controllerStatus').textContent=d.running?"
            "'Running':'Stopped';";
    html += "document.getElementById('sensorStatus').textContent=d.sensor_"
            "connected?'Connected':'Disconnected';";
    html += "}).catch(e=>console.error('Error:',e));}";
    html += "function "
            "loadConfig(){fetch('/api/config').then(r=>r.json()).then(d=>{";
    html += "document.getElementById('tempLow').value=d.temp_low;";
    html += "document.getElementById('tempHigh').value=d.temp_high;";
    html += "document.getElementById('checkInterval').value=d.check_interval;";
    html += "}).catch(e=>console.error('Error:',e));}";
    html += "document.getElementById('configForm').addEventListener('submit',"
            "function(e){";
    html += "e.preventDefault();const fd=new FormData();";
    html += "fd.append('temp_low',document.getElementById('tempLow').value);";
    html += "fd.append('temp_high',document.getElementById('tempHigh').value);";
    html += "fd.append('check_interval',document.getElementById('checkInterval'"
            ").value);";
    html += "fetch('/api/"
            "config',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{";
    html += "alert('Configuration "
            "saved!');loadStatus();}).catch(e=>alert('Error:'+e.message));});";
    html += "function controlAction(action){const fd=new "
            "FormData();fd.append('action',action);";
    html += "fetch('/api/"
            "control',{method:'POST',body:fd}).then(r=>r.json()).then(d=>{";
    html += "alert('Action "
            "executed!');loadStatus();}).catch(e=>alert('Error:'+e.message));}";
    html += "</script></body></html>";

    Serial.printf("Sending inline interface, length: %d bytes\n",
                  html.length());
    request->send(200, "text/html; charset=utf-8", html);
  });

  // API endpoints
  server.on("/api/status", HTTP_GET, handleApiStatus);
  server.on("/api/config", HTTP_GET, handleApiConfig);
  server.on("/api/config", HTTP_POST, handleApiConfigPost);
  server.on("/api/data", HTTP_GET, handleApiData);
  server.on("/api/control", HTTP_POST, handleApiControl);

  // Handle 404
  server.onNotFound([](AsyncWebServerRequest *request) {
    Serial.printf("404: %s\n", request->url().c_str());
    request->send(404, "text/plain", "File not found");
  });

  // Start server
  server.begin();
  Serial.println("Web server started on port 80");
}

void handleApiStatus(AsyncWebServerRequest *request) {
  DynamicJsonDocument doc(1024);
  doc["temperature"] = currentTemp;
  doc["relay_active"] = relayActive;
  doc["temp_low"] = tempLow;
  doc["temp_high"] = tempHigh;
  doc["check_interval"] = checkInterval;
  doc["running"] = running;
  doc["last_reading"] = lastReadingTime;
  doc["sensor_connected"] = systemStatus.sensorConnected;
  doc["relay_working"] = systemStatus.relayWorking;
  doc["uptime"] = systemStatus.uptime;
  doc["total_readings"] = systemStatus.totalReadings;
  doc["errors"] = systemStatus.errors;

  String response;
  serializeJson(doc, response);
  request->send(200, "application/json", response);
}

void handleApiConfig(AsyncWebServerRequest *request) {
  DynamicJsonDocument doc(256);
  doc["temp_low"] = tempLow;
  doc["temp_high"] = tempHigh;
  doc["check_interval"] = checkInterval;

  String response;
  serializeJson(doc, response);
  request->send(200, "application/json", response);
}

void handleApiConfigPost(AsyncWebServerRequest *request) {
  if (request->hasParam("temp_low", true) &&
      request->hasParam("temp_high", true) &&
      request->hasParam("check_interval", true)) {

    float newTempLow = request->getParam("temp_low", true)->value().toFloat();
    float newTempHigh = request->getParam("temp_high", true)->value().toFloat();
    int newCheckInterval =
        request->getParam("check_interval", true)->value().toInt();

    // Validate configuration
    if (newTempLow < newTempHigh && newTempLow >= MIN_TEMP &&
        newTempHigh <= MAX_TEMP && newCheckInterval >= 1 &&
        newCheckInterval <= 60) {

      tempLow = newTempLow;
      tempHigh = newTempHigh;
      checkInterval = newCheckInterval;

      saveConfig();
      Serial.println("Configuration updated via API");

      request->send(200, "application/json", "{\"status\":\"success\"}");
    } else {
      request->send(400, "application/json",
                    "{\"status\":\"error\",\"message\":\"Invalid configuration "
                    "values\"}");
    }
  } else {
    request->send(400, "application/json",
                  "{\"status\":\"error\",\"message\":\"Missing parameters\"}");
  }
}

void handleApiData(AsyncWebServerRequest *request) {
  DynamicJsonDocument doc(4096);
  JsonArray dataArray = doc.createNestedArray("data");

  for (int i = 0; i < dataCount; i++) {
    JsonObject point = dataArray.createNestedObject();
    point["timestamp"] = dataHistory[i].timestamp;
    point["temperature"] = dataHistory[i].temperature;
    point["relay_active"] = dataHistory[i].relayActive;
  }

  String response;
  serializeJson(doc, response);
  request->send(200, "application/json", response);
}

void handleApiControl(AsyncWebServerRequest *request) {
  if (request->hasParam("action", true)) {
    String action = request->getParam("action", true)->value();

    if (action == "start") {
      running = true;
      Serial.println("Controller started via API");
    } else if (action == "stop") {
      running = false;
      setRelay(false);
      Serial.println("Controller stopped via API");
    } else if (action == "relay_on") {
      setRelay(true);
      Serial.println("Relay activated via API");
    } else if (action == "relay_off") {
      setRelay(false);
      Serial.println("Relay deactivated via API");
    } else {
      request->send(400, "application/json",
                    "{\"status\":\"error\",\"message\":\"Invalid action\"}");
      return;
    }

    request->send(200, "application/json", "{\"status\":\"success\"}");
  } else {
    request->send(
        400, "application/json",
        "{\"status\":\"error\",\"message\":\"Missing action parameter\"}");
  }
}

void controlTemperature() {
  if (!running)
    return;

  // Read temperature
  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);

  if (temp != DEVICE_DISCONNECTED_C && temp >= MIN_TEMP && temp <= MAX_TEMP) {
    currentTemp = temp;
    lastReadingTime = millis();
    systemStatus.totalReadings++;

    // Log data point
    addDataPoint(temp, relayActive);

    Serial.printf("Current temperature: %.1f°C\n", temp);

    // Control logic
    if (temp <= tempLow && !relayActive) {
      Serial.printf("Temperature %.1f°C <= %.1f°C - Activating relay\n", temp,
                    tempLow);
      setRelay(true);
    } else if (temp >= tempHigh && relayActive) {
      Serial.printf("Temperature %.1f°C >= %.1f°C - Deactivating relay\n", temp,
                    tempHigh);
      setRelay(false);
    }

    // Check for dangerous temperatures
    if (temp >= MAX_TEMP) {
      Serial.printf(
          "WARNING: Temperature %.1f°C >= %.1f°C (MAX) - Emergency shutdown!\n",
          temp, MAX_TEMP);
      setRelay(false);
      running = false;
    }

  } else {
    Serial.println("Failed to read temperature");
    systemStatus.errors++;
    systemStatus.sensorConnected = false;
  }
}

void setRelay(bool active) {
  digitalWrite(RELAY_PIN, active ? HIGH : LOW);
  relayActive = active;
  systemStatus.relayWorking = true;
  Serial.printf("Relay: %s\n", active ? "ON" : "OFF");
}

void addDataPoint(float temperature, bool relayActive) {
  dataHistory[dataIndex].timestamp = millis();
  dataHistory[dataIndex].temperature = temperature;
  dataHistory[dataIndex].relayActive = relayActive;

  dataIndex = (dataIndex + 1) % MAX_DATA_POINTS;
  if (dataCount < MAX_DATA_POINTS) {
    dataCount++;
  }
}

void initializeDataLogging() {
  // Initialize data history array
  for (int i = 0; i < MAX_DATA_POINTS; i++) {
    dataHistory[i] = {0, 0.0, false};
  }
  dataIndex = 0;
  dataCount = 0;
  Serial.println("Data logging initialized");
}

void loadConfig() {
  File file = SPIFFS.open(CONFIG_FILE, "r");
  if (file) {
    DynamicJsonDocument doc(256);
    DeserializationError error = deserializeJson(doc, file);
    file.close();

    if (!error) {
      tempLow = doc["temp_low"] | DEFAULT_TEMP_LOW;
      tempHigh = doc["temp_high"] | DEFAULT_TEMP_HIGH;
      checkInterval = doc["check_interval"] | DEFAULT_CHECK_INTERVAL;
      Serial.println("Configuration loaded from file");
    } else {
      Serial.println("Error parsing configuration file");
      saveConfig(); // Create default config
    }
  } else {
    Serial.println("Using default configuration");
    saveConfig(); // Create default config
  }
}

void saveConfig() {
  File file = SPIFFS.open(CONFIG_FILE, "w");
  if (file) {
    DynamicJsonDocument doc(256);
    doc["temp_low"] = tempLow;
    doc["temp_high"] = tempHigh;
    doc["check_interval"] = checkInterval;

    serializeJson(doc, file);
    file.close();
    Serial.println("Configuration saved");
  } else {
    Serial.println("Error saving configuration");
  }
}

void startControlLoop() { Serial.println("Temperature control loop started"); }