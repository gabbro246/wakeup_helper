# Changelog

## 0.4.5
- Added optional scripts that run when a NapMode nap ends.
- Made setup and later configuration show the appropriate settings.
- Simplified readme

## 0.4.4
- Added an option for WakeupLight to turn off its lights after an alarm.

## 0.4.3
- Added the option to open selected covers when a WakeupLight alarm starts.
- Added a device switch for turning the cover action on or off.

## 0.4.2
- Clarified what to select for NapMode and WakeupLight actions.
- Added concise guidance for alarm time, fade duration, brightness, and scripts.

## 0.4.1
- Combined room and individual light or cover choices into one optional selector.
- Added switches for turning off lights and closing covers when a nap starts.
- Hid unused action switches and fixed the divider between the main controls.

## 0.4.0
- Added whole-room selection alongside individual lights and covers.
- Added separate nap-end lights and switches for opening covers or turning on lights.
- Removed the divider between each routine toggle and its time control.

## 0.3.15
- Replaced the routine type dropdown with separate NapMode and WakeupLight choices.

## 0.3.14
- Fixed dashboard cards sometimes showing a configuration error after a restart.
- Cards now load reliably without repeated restarts or forced browser refreshes.

## 0.3.13
- Updated the integration icon with a clearer sunrise and transparent background.

## 0.3.12
- Added a Features card layout with the icon and details above its controls.
- Made card controls the same height as Home Assistant tile-card controls.

## 0.3.11
- Made the custom name field match Home Assistant's standard controls.

## 0.3.10
- Made the card editor dropdown match Home Assistant's standard controls.

## 0.3.9
- Fixed new horizontal cards to start at 12 × 1 while keeping 8 columns as the minimum.

## 0.3.8
- Added update notes in HACS so you can see what changed before installing an update.

## 0.3.7
- Kept existing dashboard cards in their previous vertical layout.
- Fixed old card files continuing to load after updates.

## 0.3.6
- Rewrote the README.

## 0.3.5
- Added selectable horizontal and vertical card layouts with matching resize limits.
- Moved nap duration and alarm time into the main device controls.

## 0.3.4
- Added a compact side-by-side layout when a card is resized to 12 × 1.
- Removed extra hover highlights and fixed inconsistent loading after updates.

## 0.3.3
- Made dashboard cards adapt more consistently to themes and interaction states.
- Added a clear visual preview before a routine is selected.
- Limited the card editor to Wakeup Helper routine switches.

## 0.3.2
- Fixed the card editor dropdown and custom name field losing focus.

## 0.3.1
- Added a Wakeup Helper icon for Home Assistant and the repository.

## 0.3.0
- Redesigned both dashboard cards to closely match the original vertical tiles.
- Added nap-duration and alarm-time controls while keeping advanced settings on the device page.
- Restored the original nap, countdown, fade-in, and alarm messages.
- Tapping outside a control now opens that routine's device settings.

## 0.2.0
- Added a built-in dashboard card with inline controls and a live countdown.
- Added remaining-time sensors for NapMode naps and WakeupLight alarms.
- Removed the need for a separate dashboard card from HACS.
- Wakeup Helper is now shown as a device integration.

## 0.1.0
- Added separate NapMode and WakeupLight devices for each room.
- Added setup and editing through the Home Assistant interface.
- Removed the need to create helpers or dashboard card dependencies.
- Added optional scripts and events at WakeupLight alarm time.
