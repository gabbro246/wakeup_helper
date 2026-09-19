const CARD_TAG = "wakeup-helper-card";

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

const isVerticalLayout = (config) =>
  Boolean(config) &&
  (!Object.prototype.hasOwnProperty.call(config, "vertical") ||
    config.vertical === true);

const defaultGridSize = (vertical) => ({
  columns: vertical ? 6 : 12,
  rows: vertical ? 3 : 1,
});

class WakeupHelperCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  static getConfigElement() {
    return document.createElement("wakeup-helper-card-editor");
  }

  static getStubConfig() {
    return {
      vertical: false,
      grid_options: defaultGridSize(false),
    };
  }

  setConfig(config) {
    this._config = { ...config };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  connectedCallback() {
    if (!this._timer) {
      this._timer = setInterval(() => this._updateCountdown(), 1000);
    }
  }

  disconnectedCallback() {
    clearInterval(this._timer);
    this._timer = undefined;
  }

  _layout() {
    return isVerticalLayout(this._config) ? "vertical" : "horizontal";
  }

  getCardSize() {
    return this._layout() === "vertical" ? 3 : 1;
  }

  getGridOptions() {
    const vertical = this._layout() === "vertical";
    if (vertical) {
      return {
        ...defaultGridSize(true),
        min_columns: 4,
        min_rows: 3,
      };
    }
    return {
      ...defaultGridSize(false),
      min_columns: 8,
      min_rows: 1,
      max_rows: 1,
    };
  }

  _base() {
    return this._config?.entity?.split(".")[1] || "";
  }

  _entity(configKey, domain, suffix) {
    if (this._config?.[configKey]) return this._config[configKey];
    const key = suffix === "fade_in_duration" ? "fade_duration" : suffix;
    const linked =
      this._hass?.states[this._config?.entity]?.attributes
        ?.wakeup_helper_entities?.[key];
    if (linked) return linked;

    const base = this._base();
    return base ? domain + "." + base + (suffix ? "_" + suffix : "") : "";
  }

  _entities() {
    const alarmTime = this._entity("alarm_time_entity", "time", "alarm_time");
    const wakeup =
      this._config?.routine === "wakeup" ||
      (this._config?.routine !== "nap" && Boolean(this._hass?.states[alarmTime]));
    return wakeup
      ? {
          type: "wakeup",
          primary: this._config?.entity || "",
          status: this._entity("status_entity", "sensor", "status"),
          end: this._entity("end_entity", "sensor", "next_alarm"),
          remaining: this._entity("remaining_entity", "sensor", "remaining"),
          alarmTime,
          duration: this._entity("duration_entity", "number", "fade_in_duration"),
        }
      : {
          type: "nap",
          primary: this._config?.entity || "",
          status: this._entity("status_entity", "sensor", "status"),
          end: this._entity("end_entity", "sensor", "ends"),
          remaining: this._entity("remaining_entity", "sensor", "remaining"),
          duration: this._entity("duration_entity", "number", "duration"),
        };
  }

  _state(entityId) {
    return entityId ? this._hass?.states[entityId] : undefined;
  }

  _secondaryText() {
    const entities = this._entities();
    const primary = this._state(entities.primary);
    const status = this._state(entities.status)?.state;
    if (!primary) return "Unavailable";
    if (primary.state !== "on") return "off";
    if (status === "alarm") return "Alarm! 🚨";

    const endState = this._state(entities.end)?.state;
    const end = endState ? new Date(endState) : undefined;
    if (end && !Number.isNaN(end.getTime())) {
      const seconds = Math.max(
        0,
        Math.ceil((end.getTime() - Date.now()) / 1000),
      );
      if (entities.type === "nap") {
        return "nap ends " + this._formatTime(end);
      }
      return this._wakeupText(seconds, entities);
    }
    const seconds = Number(this._state(entities.remaining)?.state);
    if (!Number.isFinite(seconds)) return "scheduled";
    return entities.type === "nap"
      ? "nap ends in " + this._formatDuration(seconds)
      : this._wakeupText(seconds, entities);
  }

  _wakeupText(seconds, entities) {
    const minutes = Math.max(0, Math.ceil(seconds / 60));
    const fadeDuration = Number(this._state(entities.duration)?.state ?? 0);
    if (minutes >= 720) {
      const alarm = this._state(entities.alarmTime)?.state?.slice(0, 5);
      return alarm ? "alarm at " + alarm : "scheduled";
    }
    if (minutes > fadeDuration) {
      return (
        "alarm in " +
        Math.floor(minutes / 60) +
        ":" +
        String(minutes % 60).padStart(2, "0")
      );
    }
    return String(minutes).padStart(2, " ") + " min. left";
  }

  _formatTime(date) {
    return (
      String(date.getHours()).padStart(2, "0") +
      ":" +
      String(date.getMinutes()).padStart(2, "0") +
      ":" +
      String(date.getSeconds()).padStart(2, "0")
    );
  }

  _formatDuration(totalSeconds) {
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    if (days) {
      return (
        days +
        "d " +
        String(hours).padStart(2, "0") +
        ":" +
        String(minutes).padStart(2, "0")
      );
    }
    if (hours) {
      return (
        hours +
        ":" +
        String(minutes).padStart(2, "0") +
        ":" +
        String(seconds).padStart(2, "0")
      );
    }
    return minutes + ":" + String(seconds).padStart(2, "0");
  }

  _updateCountdown() {
    const value = this.shadowRoot?.querySelector(".state");
    if (value) value.textContent = this._secondaryText();
  }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;
    if (!this._timer && this.isConnected) this.connectedCallback();

    if (!this._config.entity) {
      this.shadowRoot.innerHTML =
        "<style>" +
        this._styles() +
        "</style>" +
        '<ha-card class="setup-preview wakeup ' +
        this._layout() +
        '" aria-label="Wakeup Helper card preview">' +
        '<div class="preview-mark" aria-hidden="true"><div class="preview-icon"><ha-icon icon="mdi:weather-sunset-up"></ha-icon></div>' +
        '<div class="preview-feature"><span>−</span><strong>07:00</strong><span>+</span></div></div>' +
        "</ha-card>";
      return;
    }

    const entities = this._entities();
    const primary = this._state(entities.primary);
    if (!primary) {
      this.shadowRoot.innerHTML =
        "<style>" +
        this._styles() +
        "</style>" +
        '<ha-card class="error-card ' +
        this._layout() +
        '"><div class="empty">Entity not found: ' +
        escapeHtml(this._config.entity) +
        "</div></ha-card>";
      return;
    }

    const active = primary.state === "on";
    const title =
      this._config.name ||
      primary.attributes.friendly_name ||
      (entities.type === "wakeup" ? "Wake-up light" : "Nap mode");
    const icon =
      this._config.icon ||
      (entities.type === "wakeup" ? "mdi:alarm" : "mdi:sleep");
    const feature =
      entities.type === "wakeup"
        ? this._timeFeature(entities.alarmTime)
        : this._stepperFeature("duration", entities.duration);
    this.shadowRoot.innerHTML =
      "<style>" +
      this._styles() +
      "</style>" +
      '<ha-card class="' +
      (active ? "active " : "") +
      entities.type +
      " " +
      this._layout() +
      '">' +
      '<div class="tile-main" role="button" tabindex="0" aria-label="Open device"><button class="icon-button" aria-label="Toggle routine">' +
      '<ha-icon icon="' +
      escapeHtml(icon) +
      '"></ha-icon></button><div class="title">' +
      escapeHtml(title) +
      '</div><div class="state">' +
      escapeHtml(this._secondaryText()) +
      '</div></div><div class="features">' +
      feature +
      "</div></ha-card>";

    this.shadowRoot
      .querySelector(".icon-button")
      ?.addEventListener("click", (event) => {
        event.stopPropagation();
        this._toggle(entities.primary);
      });
    this.shadowRoot
      .querySelector("ha-card")
      ?.addEventListener("click", () => this._openDevice(entities.primary));
    const main = this.shadowRoot.querySelector(".tile-main");
    main?.addEventListener("keydown", (event) => {
      if (
        event.target === main &&
        (event.key === "Enter" || event.key === " ")
      ) {
        event.preventDefault();
        this._openDevice(entities.primary);
      }
    });
    this._wireTimeStepper(entities.alarmTime);
    this._wireNumber("duration", entities.duration);
  }

  _timeFeature(entityId) {
    const state = this._state(entityId);
    const value = state?.state?.slice(0, 5) || "Unavailable";
    return (
      '<div class="feature time-feature"><button data-time-direction="-1" aria-label="Earlier alarm"' +
      (state ? "" : " disabled") +
      '>−</button><strong>' +
      escapeHtml(value) +
      '</strong><button data-time-direction="1" aria-label="Later alarm"' +
      (state ? "" : " disabled") +
      ">+</button></div>"
    );
  }

  _stepperFeature(kind, entityId) {
    const state = this._state(entityId);
    if (!state) return '<div class="feature missing">Unavailable</div>';
    const value = Number(state.state);
    const unit = state.attributes.unit_of_measurement || "";
    return (
      '<div class="feature"><button data-number="' +
      kind +
      '" data-direction="-1" aria-label="Decrease">−</button><strong>' +
      escapeHtml(value) +
      " " +
      escapeHtml(unit) +
      '</strong><button data-number="' +
      kind +
      '" data-direction="1" aria-label="Increase">+</button></div>'
    );
  }

  _wireTimeStepper(entityId) {
    if (!entityId) return;
    this.shadowRoot.querySelectorAll("[data-time-direction]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        const state = this._state(entityId);
        if (!state) return;
        const parts = state.state.split(":").map(Number);
        const currentMinutes = parts[0] * 60 + parts[1];
        const direction = Number(button.dataset.timeDirection);
        const minutes = (currentMinutes + direction * 15 + 1440) % 1440;
        const value =
          String(Math.floor(minutes / 60)).padStart(2, "0") +
          ":" +
          String(minutes % 60).padStart(2, "0") +
          ":00";
        this._hass.callService("time", "set_value", {
          entity_id: entityId,
          time: value,
        });
      });
    });
  }

  _wireNumber(kind, entityId) {
    if (!entityId) return;
    this.shadowRoot
      .querySelectorAll('[data-number="' + kind + '"]')
      .forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          const state = this._state(entityId);
          if (!state) return;
          const step = Number(state.attributes.step ?? 1);
          const min = Number(state.attributes.min ?? 0);
          const max = Number(state.attributes.max ?? 100);
          const value = Math.min(
            max,
            Math.max(
              min,
              Number(state.state) + Number(button.dataset.direction) * step,
            ),
          );
          this._setNumber(entityId, value);
        });
      });

  }

  _setNumber(entityId, value) {
    this._hass.callService("number", "set_value", { entity_id: entityId, value });
  }

  _toggle(entityId) {
    const state = this._state(entityId);
    if (!state) return;
    this._hass.callService(
      "switch",
      state.state === "on" ? "turn_off" : "turn_on",
      { entity_id: entityId },
    );
  }

  _openDevice(entityId) {
    const state = this._state(entityId);
    const deviceId = state?.attributes?.wakeup_helper_device_id;
    if (!deviceId) {
      this._moreInfo(entityId);
      return;
    }
    window.history.pushState(
      null,
      "",
      "/config/devices/device/" + encodeURIComponent(deviceId),
    );
    window.dispatchEvent(new CustomEvent("location-changed"));
  }

  _moreInfo(entityId) {
    if (!entityId) return;
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        detail: { entityId },
        bubbles: true,
        composed: true,
      }),
    );
  }

  _styles() {
    return [
      ":host{display:block;height:100%;--wakeup-helper-nap-color:var(--primary-color);--wakeup-helper-wakeup-color:var(--accent-color,var(--primary-color));--wakeup-helper-control-surface:var(--ha-color-fill-neutral-quiet-resting,var(--secondary-background-color));--wakeup-helper-focus:var(--ha-color-focus,var(--primary-color));--wakeup-helper-feature-radius:var(--feature-border-radius,var(--ha-card-features-border-radius,var(--ha-border-radius-lg,18px)));--wakeup-helper-content-radius:var(--ha-border-radius-lg,12px)}",
      "ha-card{height:100%;min-height:120px;padding:10px;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column;gap:6px;cursor:pointer}",
      ".nap{--routine-color:var(--wakeup-helper-nap-color)}.wakeup{--routine-color:var(--wakeup-helper-wakeup-color)}",
      ".tile-main{min-height:56px;min-width:0;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:var(--wakeup-helper-content-radius);cursor:pointer;outline:none;transition:background-color .18s ease,box-shadow .18s ease}",
      ".tile-main:focus-visible,.icon-button:focus-visible,.feature button:focus-visible{box-shadow:inset 0 0 0 2px var(--wakeup-helper-focus);outline:none}",
      ".icon-button{width:42px;height:42px;border:0;border-radius:var(--ha-border-radius-circle,50%);display:grid;place-items:center;background:var(--wakeup-helper-control-surface);color:var(--ha-color-text-secondary,var(--secondary-text-color));cursor:pointer;transition:background-color .18s ease,color .18s ease,box-shadow .18s ease}",
      ".active .icon-button{background:color-mix(in srgb,var(--routine-color) 18%,var(--wakeup-helper-control-surface));color:var(--routine-color)}",
      ".title{max-width:100%;margin-top:7px;font-size:14px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
      ".state{max-width:100%;margin-top:2px;font-size:12px;color:var(--ha-color-text-secondary,var(--secondary-text-color));white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-variant-numeric:tabular-nums}",
      ".features{display:grid;gap:6px}.feature{height:36px;border-radius:var(--wakeup-helper-feature-radius);background:var(--wakeup-helper-control-surface);display:grid;grid-template-columns:36px minmax(0,1fr) 36px;align-items:center;text-align:center;overflow:hidden;transition:background-color .18s ease}",
      ".active .feature{background:color-mix(in srgb,var(--routine-color) 18%,var(--wakeup-helper-control-surface))}",
      ".feature button{height:36px;border:0;background:transparent;color:var(--primary-text-color);font-size:20px;cursor:pointer;transition:background-color .18s ease,box-shadow .18s ease}",
      ".feature button:disabled{color:var(--ha-color-text-disabled,var(--disabled-text-color));cursor:not-allowed}",
      ".feature strong{font-size:14px;font-weight:500;font-variant-numeric:tabular-nums}",
      "ha-card.horizontal{min-height:0;padding:7px 10px;flex-direction:row;align-items:center;gap:10px}",
      "ha-card.horizontal .tile-main{width:0;min-height:42px;display:grid;grid-template-columns:42px minmax(0,1fr);grid-template-rows:auto auto;column-gap:10px;align-content:center;align-items:center;justify-items:start;text-align:start}",
      "ha-card.horizontal .icon-button{grid-column:1;grid-row:1/3}",
      "ha-card.horizontal .title{grid-column:2;grid-row:1;width:100%;margin-top:0}",
      "ha-card.horizontal .state{grid-column:2;grid-row:2;width:100%;margin-top:1px}",
      "ha-card.horizontal .features{width:min(42%,180px);min-width:120px;flex:0 1 180px}",
      "ha-card.horizontal.setup-preview{justify-content:center}",
      "ha-card.horizontal .preview-mark{width:min(100%,250px);display:grid;grid-template-columns:42px minmax(120px,180px);align-items:center;justify-content:center;gap:12px}",
      "ha-card.horizontal .preview-icon{width:42px;height:42px}ha-card.horizontal.setup-preview .preview-feature{min-width:0}",
      ".missing,.empty{padding:16px;color:var(--ha-color-text-secondary,var(--secondary-text-color))}",
      ".setup-preview,.error-card{cursor:default}.setup-preview{justify-content:center;background:var(--ha-card-background,var(--card-background-color))}.preview-mark{width:min(100%,180px);margin:auto;display:grid;justify-items:center;gap:14px}.preview-icon{width:64px;height:64px;border-radius:var(--ha-border-radius-circle,50%);display:grid;place-items:center;background:color-mix(in srgb,var(--routine-color) 18%,var(--wakeup-helper-control-surface));color:var(--routine-color);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--routine-color) 22%,transparent)}.preview-icon ha-icon{--mdc-icon-size:34px}.preview-feature{width:100%;height:36px;border-radius:var(--wakeup-helper-feature-radius);display:grid;grid-template-columns:36px 1fr 36px;align-items:center;text-align:center;background:color-mix(in srgb,var(--routine-color) 12%,var(--wakeup-helper-control-surface));color:var(--primary-text-color)}.preview-feature span{font-size:20px;color:var(--routine-color)}.preview-feature strong{font-size:14px;font-variant-numeric:tabular-nums}",
      "@media(prefers-reduced-motion:reduce){.tile-main,.icon-button,.feature,.feature button{transition:none}}",
      "@media(max-width:220px){ha-card{padding:8px}}",
    ].join("");
  }
}

class WakeupHelperCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    if (this._picker) {
      this._picker.hass = hass;
      this._syncPickerEntities();
    } else {
      this._render();
    }
  }

  setConfig(config) {
    this._config = { ...config };
    if (this._picker) {
      this._syncValues();
    } else {
      this._render();
    }
  }

  _render() {
    if (!this.shadowRoot || !this._hass || !this._config) return;
    this.shadowRoot.innerHTML =
      "<style>.editor{display:grid;gap:16px;padding:8px 0}.field{display:grid;gap:6px}.field input,.field select{box-sizing:border-box;width:100%;padding:12px;border:1px solid var(--ha-color-border-neutral-normal,var(--divider-color));border-radius:var(--ha-border-radius-md,8px);background:var(--ha-color-form-background,var(--card-background-color));color:var(--primary-text-color);font:inherit;transition:border-color .18s ease}.field input:focus-visible,.field select:focus-visible{border-color:var(--ha-color-focus,var(--primary-color));outline:2px solid var(--ha-color-focus,var(--primary-color));outline-offset:1px}@media(prefers-reduced-motion:reduce){.field input,.field select{transition:none}}</style>" +
      '<div class="editor"><ha-entity-picker></ha-entity-picker><label class="field">Content layout<select class="layout"><option value="horizontal">Horizontal</option><option value="vertical">Vertical</option></select></label><label class="field">Custom name (optional)<input class="name" value="' +
      escapeHtml(this._config.name || "") +
      '"></label></div>';

    this._picker = this.shadowRoot.querySelector("ha-entity-picker");
    this._nameInput = this.shadowRoot.querySelector(".name");
    this._layoutInput = this.shadowRoot.querySelector(".layout");
    this._picker.label = "Wakeup Helper routine";
    this._picker.includeDomains = ["switch"];
    this._syncPickerEntities();
    this._picker.addEventListener("value-changed", (event) =>
      this._change({ entity: event.detail.value }),
    );
    this._layoutInput.addEventListener("change", (event) => {
      const vertical = event.target.value === "vertical";
      this._change({
        vertical,
        grid_options: defaultGridSize(vertical),
      });
    });
    this._nameInput.addEventListener("input", (event) =>
      this._change({ name: event.target.value || undefined }),
    );
    this._syncValues();
  }

  _syncValues() {
    if (!this._picker || !this._nameInput || !this._layoutInput) return;
    this._picker.hass = this._hass;
    this._syncPickerEntities();
    const entity = this._config.entity || "";
    if (this._picker.value !== entity) this._picker.value = entity;
    const layout = isVerticalLayout(this._config) ? "vertical" : "horizontal";
    if (this._layoutInput.value !== layout) this._layoutInput.value = layout;

    const name = this._config.name || "";
    if (
      this.shadowRoot.activeElement !== this._nameInput &&
      this._nameInput.value !== name
    ) {
      this._nameInput.value = name;
    }
  }

  _syncPickerEntities() {
    if (!this._picker || !this._hass) return;
    const entities = Object.entries(this._hass?.states || {})
      .filter(
        ([entityId, state]) =>
          entityId.startsWith("switch.") &&
          Boolean(state?.attributes?.wakeup_helper_entities),
      )
      .map(([entityId]) => entityId);
    const current = this._picker.includeEntities;
    if (
      Array.isArray(current) &&
      current.length === entities.length &&
      current.every((entityId, index) => entityId === entities[index])
    ) {
      return;
    }
    this._picker.includeEntities = entities;
  }

  _change(changes) {
    this._config = { ...this._config, ...changes };
    Object.keys(this._config).forEach((key) => {
      if (this._config[key] === undefined) delete this._config[key];
    });
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this._config },
        bubbles: true,
        composed: true,
      }),
    );
  }
}

if (!customElements.get(CARD_TAG)) {
  customElements.define(CARD_TAG, WakeupHelperCard);
}
if (!customElements.get("wakeup-helper-card-editor")) {
  customElements.define("wakeup-helper-card-editor", WakeupHelperCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === CARD_TAG)) {
  window.customCards.push({
    type: CARD_TAG,
    name: "Wakeup Helper",
    description: "A tile-style card for Wakeup Helper routines.",
    preview: true,
    getEntitySuggestion: (hass, entityId) => {
      const entity = hass.states[entityId];
      if (
        entityId.split(".")[0] !== "switch" ||
        !entity?.attributes?.wakeup_helper_entities
      ) {
        return null;
      }
      return {
        config: {
          type: "custom:wakeup-helper-card",
          entity: entityId,
          vertical: false,
          grid_options: defaultGridSize(false),
        },
      };
    },
  });
}
