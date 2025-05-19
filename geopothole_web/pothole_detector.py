import os
import time
import json
import requests
import argparse
from datetime import datetime

# You can replace this with your actual GPS module interface
# This is a simple simulation for testing
class GPSModule:
    def __init__(self, port=None):
        self.port = port
        self.connected = False
        self.latitude = 12.9716  # Default coordinates (Bangalore)
        self.longitude = 77.5946
        
    def connect(self):
        print(f"Connecting to GPS module on port {self.port}")
        # Actual code would initialize serial connection to GPS module
        self.connected = True
        return self.connected
        
    def get_coordinates(self):
        if not self.connected:
            print("GPS module not connected")
            return None, None
            
        # In a real implementation, this would read from the GPS module
        # For simulation, we'll add small random variations
        import random
        lat_variation = random.uniform(-0.001, 0.001)
        lng_variation = random.uniform(-0.001, 0.001)
        
        return self.latitude + lat_variation, self.longitude + lng_variation

# Class to handle pothole detections and reporting to the web app        
class PotholeReporter:
    def __init__(self, api_url, gps_module=None):
        self.api_url = api_url
        self.gps = gps_module if gps_module else GPSModule()
        
    def report_pothole(self, confidence):
        lat, lng = self.gps.get_coordinates()
        if lat is None or lng is None:
            print("Cannot report pothole: GPS coordinates unavailable")
            return False
            
        # Prepare data for the API
        data = {
            "lat": lat,
            "lng": lng,
            "confidence": confidence,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            # Send data to web application API
            response = requests.post(
                f"{self.api_url}/api/report-pothole",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"Pothole reported successfully at {lat}, {lng} with {confidence}% confidence")
                return True
            else:
                print(f"Failed to report pothole: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error reporting pothole: {str(e)}")
            return False

# Example of how this would integrate with your YOLO model
def integrate_with_yolo(yolo_output_file, reporter):
    """
    This function would be called by your YOLO model when a pothole is detected.
    It should read the detection results and report them.
    
    Args:
        yolo_output_file: Path to the file where YOLO saves detection results
        reporter: PotholeReporter instance
    """
    try:
        # Read YOLO detection results
        # This is just an example - adapt to your actual YOLO output format
        with open(yolo_output_file, 'r') as f:
            detections = json.load(f)
            
        # Process each detection
        for detection in detections:
            if detection["class"] == "pothole" and detection["confidence"] > 50:  # Only report if confidence > 50%
                reporter.report_pothole(detection["confidence"])
                
    except Exception as e:
        print(f"Error processing YOLO output: {str(e)}")

def simulate_detections(reporter, count=5, interval=3):
    """
    Simulate pothole detections for testing without the YOLO model
    """
    import random
    
    print(f"Simulating {count} pothole detections...")
    for i in range(count):
        confidence = random.uniform(75, 98)
        reporter.report_pothole(round(confidence, 2))
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Pothole detection reporter")
    parser.add_argument("--api-url", default="http://localhost:5000", help="Web application API URL")
    parser.add_argument("--gps-port", default="/dev/ttyUSB0", help="GPS module serial port")
    parser.add_argument("--simulate", type=int, default=0, help="Simulate N detections for testing")
    args = parser.parse_args()
    
    # Initialize GPS module
    gps = GPSModule(port=args.gps_port)
    gps.connect()
    
    # Initialize reporter
    reporter = PotholeReporter(api_url=args.api_url, gps_module=gps)
    
    if args.simulate > 0:
        simulate_detections(reporter, count=args.simulate)
    else:
        print("Ready to report pothole detections from YOLO model.")
        print("To integrate with your YOLO model, call the 'report_pothole' method")
        print("when a pothole is detected with the confidence score.")

if __name__ == "__main__":
    main()