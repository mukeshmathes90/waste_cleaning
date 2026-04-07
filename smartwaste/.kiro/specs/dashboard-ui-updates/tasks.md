# Implementation Plan

- [ ] 1. Update Live YOLO View text content
  - Modify the hint text in the Live YOLO View section to change "ESP uploads" to "Cam 1"
  - Remove the optional stream URL display from the live view hint
  - _Requirements: 1.1, 1.2_

- [ ] 2. Update Active Cameras count
  - Change the hardcoded active cameras count from "3" to "1" in the status card
  - _Requirements: 2.1_

- [ ]* 3. Verify UI changes through manual testing
  - Load dashboard and confirm text changes display correctly
  - Test live view refresh functionality still works
  - Verify responsive display on different screen sizes
  - _Requirements: 1.1, 1.2, 2.1_