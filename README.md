# Wakeup Helper

Wakeup Helper is a Home Assistant custom integration that combines a nap mode
and a wake-up light. Every routine is its own Home Assistant device, so you can
create separate routines for different people or rooms without manually making
helpers or blueprint automations.

## Features

- Create any number of nap mode and wake-up light devices.
- Configure everything in the Home Assistant interface.
- Control each routine with normal switch, time, number, and sensor entities.
- Build dashboards with built-in Home Assistant cards—no custom card required.
- Keep active naps and enabled alarms across Home Assistant restarts.
- Optionally run a script when a wake-up light reaches its alarm time.
- Fire a `wakeup_helper_wakeup` event at every alarm time for advanced automations.

### Nap mode

Starting a nap closes the selected covers and turns off the selected lights. It
automatically opens the covers and switches itself off when the configured nap
duration ends. Turning it off early ends the nap immediately.

Entities:

- Nap switch
- Duration
- Status
- Nap ends

### Wake-up light

The wake-up light gradually raises the selected lights from their minimum
brightness to the configured brightness, reaching it at the alarm time. The
alarm repeats daily while enabled.

Entities:

- Wake-up light switch
- Alarm time
- Fade-in duration
- End brightness
- Status
- Next alarm

## Installation with HACS

1. Open HACS in Home Assistant.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/gabbro246/wakeup_helper` as an **Integration**.
4. Download **Wakeup Helper** and restart Home Assistant.
5. Go to **Settings → Devices & services → Add integration** and search for
   **Wakeup Helper**.

Run the setup again for every nap mode or wake-up light you want to create.

## Configuration

When adding a routine, choose its type and give it a descriptive name such as
“Bedroom nap” or “Kids wake-up light.” Select the lights and, for a nap, covers
that belong to that room.

The duration, time, and brightness are regular entities. Change them from the
device page, a dashboard, an automation, or a voice assistant. To change target
lights, covers, or the optional alarm script later, open the integration entry
and choose **Configure**.

## Dashboard examples

The generated entity IDs depend on the name chosen during setup. Replace the
example IDs below with the entities shown on your routine's device page.

```yaml
type: entities
title: Bedroom nap
entities:
  - entity: switch.bedroom_nap
  - entity: number.bedroom_nap_duration
  - entity: sensor.bedroom_nap_status
  - entity: sensor.bedroom_nap_ends
```

```yaml
type: entities
title: Bedroom wake-up light
entities:
  - entity: switch.bedroom_wake_up_light
  - entity: time.bedroom_wake_up_light_alarm_time
  - entity: number.bedroom_wake_up_light_fade_in_duration
  - entity: number.bedroom_wake_up_light_end_brightness
  - entity: sensor.bedroom_wake_up_light_status
  - entity: sensor.bedroom_wake_up_light_next_alarm
```

More card examples are available in [`examples/dashboard.yaml`](examples/dashboard.yaml).

## Wake-up event

At the alarm time, the integration fires `wakeup_helper_wakeup` with these
fields: `config_entry_id`, `name`, and `lights`. This makes it possible to start
music, open covers, or perform any other action in a separate automation.

```yaml
triggers:
  - trigger: event
    event_type: wakeup_helper_wakeup
conditions:
  - condition: template
    value_template: "{{ trigger.event.data.name == 'Bedroom wake-up light' }}"
actions:
  - action: media_player.media_play
    target:
      entity_id: media_player.bedroom
```

## Removing a routine

Delete its entry from **Settings → Devices & services → Wakeup Helper**. The
device and its entities will be removed with it.

## Migrating from the blueprints

Create matching Wakeup Helper devices first, then disable the old blueprint
automations. Once the new devices behave as expected, the old input helpers can
be removed.

## License

MIT
