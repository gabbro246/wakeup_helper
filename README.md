# Wakeup Helper

<p align="center">
  <img src="custom_components/wakeup_helper/brand/icon.png" alt="Wakeup Helper icon" width="160">
</p>

Wakeup Helper uses your Home Assistant devices to make sure you get the rest you need and wake up on time.

## What it does

Create separate routines for different rooms or people, all controlled through Home Assistant.

### WakeupLight

Set a daily alarm and wake up gradually as your selected lights slowly brighten before your chosen wake-up time. You can adjust how long the lights take to reach your desired brightness. When the alarm goes off, Wakeup Helper can also open your covers and run a Home Assistant script, for example to play music or make an announcement.

### NapMode

Start a timed nap that turns off your lights and closes your covers. When the nap ends, Wakeup Helper can open the covers, turn on a separate set of lights, and run a Home Assistant script to wake you up. You can choose how long you want to rest, stop a nap early, and enable or disable individual actions.

### Dashboard card

The included dashboard card lets you control your routines, adjust alarm times or nap durations, and see when you'll wake up. It offers three different layout options.


## Install with HACS

Make sure you have [HACS](https://hacs.xyz/) installed in Home Assistant.

[![Open Wakeup Helper in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=gabbro246&repository=wakeup_helper&category=integration)

1. Click the button above to open Wakeup Helper and confirm adding the repository if prompted.
2. In HACS, download **Wakeup Helper**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services**, choose **Add integration**, and search for **Wakeup Helper**.

If the button doesn't work, add https://github.com/gabbro246/wakeup_helper through HACS → Custom repositories, selecting Integration as the repository type. Then follow steps 2–4.

## Set up a routine and add it to your dashboard

Choose WakeupLight or NapMode, give your routine a name, and follow the setup steps to select your devices and configure the timing. You can create multiple routines for different rooms or people.

Once created, you can adjust times, durations, and brightness from the routine's device page. To change the selected devices or scripts, find your routine under Settings → Devices & services → Wakeup Helper and select Configure.

To add a routine to your dashboard, enter edit mode, add a Wakeup Helper card, and select your routine. The card is included with the integration and requires no additional installation.

## Additional information

Found a bug or have a suggestion? Feel free to [open an issue](https://github.com/gabbro246/wakeup_helper/issues).

Wakeup Helper is based on my earlier, now deprecated projects [WakeupLight](https://github.com/gabbro246/wakeuplight) and [NapMode](https://github.com/gabbro246/napmode).

Licensed under the [MIT License](LICENSE).
