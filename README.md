# Wakeup Helper

<p align="center">
  <img src="custom_components/wakeup_helper/brand/icon.png" alt="Wakeup Helper icon" width="160">
</p>

Wakeup Helper adds nap routines and wake-up-light alarms to Home Assistant. You
can create separate routines for different rooms or people.

## What it does

### Nap mode

Starting a nap turns off the selected lights and closes the selected covers.
When the timer ends, the covers open again. You can also stop the nap early.

### Wake-up light

Set a daily alarm and the selected lights gradually brighten before the alarm
time, reaching the brightness you choose. You can also run a Home Assistant
script at alarm time, such as one that starts music, makes an announcement, or
opens covers.

Both routines can be controlled from Home Assistant and have a built-in
dashboard card that shows what is happening and how long is left. Active naps
and enabled alarms are remembered after Home Assistant restarts.

## Install with HACS

[![Open Wakeup Helper in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=gabbro246&repository=wakeup_helper&category=integration)

1. Select the button above from a device where you are signed in to Home
   Assistant, then confirm the repository in HACS.
2. In HACS, download **Wakeup Helper**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services**, choose **Add integration**, and
   search for **Wakeup Helper**.

You need [HACS](https://hacs.xyz/) installed first. If the button cannot open
your Home Assistant, add `https://github.com/gabbro246/wakeup_helper` in HACS
as an **Integration** repository instead.

## Set up a routine

When adding Wakeup Helper, choose **Nap mode** or **Wake-up light**. Give the
routine a clear name, such as “Bedroom nap” or “Mia’s wake-up light.” Add more
routines as needed.

For a nap, select the lights and covers to control, then choose the nap length.

For a wake-up light, select the lights to use, set the alarm time, choose how
long they should brighten for, and set the final brightness. Optionally choose a
Home Assistant script to run at alarm time.

After setup, open the routine's device page whenever you want to adjust the
time, duration, or brightness. To change which room devices a routine uses—or
to add or remove the morning script—open **Settings → Devices & services →
Wakeup Helper**, select the routine, and choose **Configure**.

## Add it to your dashboard

In dashboard edit mode, add a **Wakeup Helper** card and select the routine.
The card lets you turn the routine on or off and adjust the nap length or alarm
time. It also shows the next wake-up, a countdown, or the time a nap ends.

No separate dashboard download or resource setup is needed.

New cards use a horizontal layout by default. You can choose **Horizontal**,
**Features**, or **Vertical** under **Content layout** in the card editor.
Horizontal cards start at 12 × 1 grid cells and can shrink to 8 × 1. Features
cards place the icon and details above the controls; they start at 6 × 2 and
can shrink to 4 × 2. Vertical cards start at 6 × 3 and can shrink to 4 × 3.
Existing cards keep their previous vertical layout until you choose another
layout.

## License

[MIT](LICENSE)
