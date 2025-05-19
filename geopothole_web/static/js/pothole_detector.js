/**
 * Client-side code to integrate with YOLO pothole detection model
 * and send coordinates to the server.
 */

class PotholeReporter {
    constructor(apiEndpoint = '/api/report-pothole') {
        this.apiEndpoint = apiEndpoint;
        this.gpsCoordinates = null;
        
        // Initialize GPS tracking if available
        if (navigator.geolocation) {
            this.initGPS();
        } else {
            console.error("Geolocation is not supported by this browser.");
        }
    }
    
    // Initialize GPS tracking
    initGPS() {
        // Get initial position
        navigator.geolocation.getCurrentPosition(
            this.updateGPSPosition.bind(this),
            this.handleGPSError.bind(this)
        );
        
        // Set up continuous tracking (useful for moving detection systems)
        this.watchId = navigator.geolocation.watchPosition(
            this.updateGPSPosition.bind(this),
            this.handleGPSError.bind(this),
            { enableHighAccuracy: true, maximumAge: 0, timeout: 5000 }
        );
    }
    
    // Update GPS position when it changes
    updateGPSPosition(position) {
        this.gpsCoordinates = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
        };
        console.log("GPS coordinates updated:", this.gpsCoordinates);
    }
    
    // Handle GPS errors
    handleGPSError(error) {
        console.error("Error obtaining GPS coordinates:", error.message);
    }
    
    // Stop GPS tracking when no longer needed
    stopGPSTracking() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }
    
    // Get current GPS coordinates
    getGPSCoordinates() {
        return this.gpsCoordinates;
    }
    
    // Report a detected pothole with the current GPS coordinates
    async reportPothole(confidence) {
        if (!this.gpsCoordinates) {
            console.error("GPS coordinates not available");
            return { success: false, message: "GPS coordinates not available" };
        }
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    lat: this.gpsCoordinates.lat,
                    lng: this.gpsCoordinates.lng,
                    confidence: confidence,
                    accuracy: this.gpsCoordinates.accuracy
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                console.log("Pothole reported successfully");
                return { success: true, data: result };
            } else {
                console.error("Error reporting pothole:", result.message);
                return { success: false, message: result.message };
            }
        } catch (error) {
            console.error("Error reporting pothole:", error);
            return { success: false, message: error.message };
        }
    }
    
    // For external GPS modules - manually set coordinates
    setExternalGPSCoordinates(lat, lng, accuracy = 0) {
        this.gpsCoordinates = {
            lat: lat,
            lng: lng,
            accuracy: accuracy
        };
        console.log("External GPS coordinates set:", this.gpsCoordinates);
    }
}

// Example usage:
// 1. Create a reporter instance
// const reporter = new PotholeReporter();
// 
// 2. When YOLO detects a pothole with confidence score:
// reporter.reportPothole(95.7);
//
// 3. For external GPS modules (USB dongle, etc.):
// reporter.setExternalGPSCoordinates(12.9716, 77.5946);
// reporter.reportPothole(92.3);