# Requirements Document

## Introduction

This feature involves updating the Smart Waste Monitoring Dashboard UI to improve clarity and accuracy of the camera information display. The changes focus on simplifying the live view information and correcting the active camera count to reflect the actual system configuration.

## Glossary

- **Dashboard**: The main web interface for monitoring waste detection system
- **Live_YOLO_View**: The real-time camera feed display section showing YOLO-annotated frames
- **Active_Cameras_Card**: The status card displaying the count of operational cameras
- **Stream_URL_Text**: The optional stream URL information displayed in the live view

## Requirements

### Requirement 1

**User Story:** As a system operator, I want the live view to show clear camera identification without technical stream details, so that I can easily understand which camera feed I'm viewing.

#### Acceptance Criteria

1. WHEN the Live_YOLO_View displays, THE Dashboard SHALL show "Showing latest YOLO-annotated frame from Cam 1" instead of "Showing latest YOLO-annotated frame from ESP uploads"
2. WHEN the Live_YOLO_View displays, THE Dashboard SHALL NOT show the optional stream URL text
3. THE Dashboard SHALL maintain all other live view functionality unchanged

### Requirement 2

**User Story:** As a system administrator, I want the active cameras count to reflect the actual system configuration, so that I have accurate system status information.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE Active_Cameras_Card SHALL display "1" instead of "3"
2. THE Active_Cameras_Card SHALL maintain its visual styling and icon
3. THE Dashboard SHALL preserve all other status card functionality