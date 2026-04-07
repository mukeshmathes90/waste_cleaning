# Design Document

## Overview

This design outlines the specific UI changes needed to update the Smart Waste Monitoring Dashboard. The changes are minimal and focused on improving user experience by providing clearer camera identification and accurate system status information.

## Architecture

The changes affect only the frontend presentation layer of the Flask web application:
- **Template Layer**: HTML template modifications in `templates/dashboard.html`
- **No Backend Changes**: No modifications to Flask routes, database, or business logic required
- **Static Content**: Changes are purely presentational and do not affect functionality

## Components and Interfaces

### Live YOLO View Component
**Location**: `templates/dashboard.html` - Live YOLO View card section
**Current Implementation**: 
- Displays hint text with ESP upload reference and optional stream URL
- Shows technical details that may confuse operators

**Updated Implementation**:
- Simplified hint text referencing "Cam 1" for clear identification
- Removal of optional stream URL display to reduce clutter
- Maintains refresh functionality and live image display

### Active Cameras Status Card
**Location**: `templates/dashboard.html` - Status cards row, third card
**Current Implementation**: 
- Hardcoded value of "3" active cameras
- Uses Bootstrap info styling with video icon

**Updated Implementation**:
- Updated hardcoded value to "1" to reflect actual system configuration
- Preserves all styling, icon, and card structure

## Data Models

No data model changes required. All modifications are presentational only.

## Error Handling

No new error handling required as changes are static content updates. Existing error handling for:
- Image loading failures
- Live feed unavailability
- Template rendering errors
remains unchanged.

## Testing Strategy

### Manual Testing
1. **Visual Verification**: Load dashboard and verify text changes are displayed correctly
2. **Functionality Testing**: Ensure live view refresh and image modal still work
3. **Responsive Testing**: Verify changes display properly on different screen sizes
4. **Cross-browser Testing**: Test in major browsers to ensure compatibility

### Regression Testing
1. Verify all existing dashboard functionality remains intact
2. Test live YOLO image refresh mechanism
3. Confirm detection history table displays correctly
4. Validate image viewing modal functionality

## Implementation Notes

- Changes are isolated to specific HTML elements
- No JavaScript modifications required
- No CSS changes needed as existing Bootstrap classes are maintained
- Changes are backward compatible and non-breaking