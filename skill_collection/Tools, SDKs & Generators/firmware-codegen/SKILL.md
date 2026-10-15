---
name: "firmware-codegen"
description: ">"
---

# Firmware Codegen

This is stage 4 of the `attaky-firmware-builder` chain. The user has
an approved spec (typically four files in `<workspace>/spec/`,
produced by `firmware-spec`). You read the spec + the public hardware
catalog and produce a complete, buildable firmware source project at
`<workspace>/source/`.

The user is non-technical. They wanted to see results fast — so this
skill does **not** ship stubs or scaffolds-with-`TODO`-comments. It
produces a working implementation of the spec's MVP features so the
first build-and-flash actually does something on the device.

## Operating Principles (non-negotiable)

These nine rules shape every interaction.

1. **The spec is the contract.** Read `spec/parts-list.md`,
   `spec/module-combination.md`, `spec/requirements.md`, and
   `spec/dev-plan.md`. Generate code that implements them. Do not
   invent features, modules, or behaviors that aren't in the spec.

2. **Full implementation, not stubs.** Each MVP feature from
   `requirements.md §1` gets real code that runs on first build —
   not `// TODO: implement`. Edge-case handling (`requirements.md
   §5`) goes in too. The user's expectation is "I flash it, it does
   roughly what my spec said." That's the bar. Keep **pure logic**
   (parsing, state machines, geometry, formatting, timing) in files that
   don't depend on Arduino / ESP-IDF headers where practical — the
   example's `geo.cpp` is header-free C++ — so `firmware-build`'s
   host-native golden test can compile and check them off-target (the
   hardware / pure-logic seam the spec's `dev-plan.md` calls out).
   Reserve the board for what only hardware reveals.

3. **Catalog is authoritative for hardware facts.** Chip names, pin
   assignments, I²C addresses, peripheral configs, library names —
   all come from `../../shared/hardware-catalog.md`. Don't infer.
   Don't guess. If a fact isn't in the catalog, stop and ask the user
   rather than fabricating. **Tie-breaker rule**: if `module-combination.md`
   (from spec) and the catalog disagree on a pin / address / chip
   name, **the catalog wins** — `module-combination.md` is a derived view
   meant to summarize the catalog for spec readability, so divergence
   means `module-combination.md` is stale and should be flagged but not
   followed. **But if the *real hardware* disagrees with the catalog**
   (bring-up shows a pin / address / behavior the catalog got wrong — a
   catalog value can be *derived, not measured*): do NOT silently patch
   the generated code to a guessed value. Surface the discrepancy to the
   user as a catalog correction to verify against the hardware; the
   catalog is the authoritative source and is what gets fixed, not a
   one-off guess buried in the firmware.

4. **One toolchain per session.** A single run produces either an
   Arduino-CLI / PlatformIO project **or** an ESP-IDF project — not
   both. The toolchain decision happens once at the start (see §2
   below) and applies to every file you write that run.

5. **Local-first build path.** The generated `source/README.md`
   tells the user how to build locally with the chosen toolchain
   (`brew install arduino-cli` / VS Code PlatformIO extension /
   `idf.py` setup). Don't reference third-party online build
   alternatives or any unreleased hosted build service. The
   only build path the README promises today is local.

6. **Built-in logcat-like serial logs by default.** Every generated
   firmware emits structured serial output at 115200 baud,
   **regardless** of whether `requirements.md` explicitly asks for
   it. This is the device's "logcat" — used by `firmware-deploy`'s
   post-flash monitor to verify boot, and used by the user to debug
   failing features. The contract:

   - Format: `[LEVEL] [TAG] message` (e.g.
     `[INFO] [RADIO] LoRa init OK at 915 MHz`). LEVEL ∈
     `{ERROR, WARN, INFO, DEBUG}`. TAG = the module emitting the log
     (e.g. `RADIO`, `GPS`, `UI`, `POWER`).
   - **Boot banner** on first Serial init, before any module setup:
     ```
     [INFO] [APP] <firmware-name> v<version> on <build-SKU>
     [INFO] [APP] Build: <build timestamp> / toolchain: <PlatformIO|ESP-IDF>
     ```
     `firmware-name` and `build-SKU` come from `concept.md` /
     `parts-list.md`; `version` defaults to `0.1.0` for first
     codegen (user can bump later).
   - Each module's setup emits **at least one** `INFO` log on
     success ("`<TAG> init OK`") and an `ERROR` log on failure.
   - Errors during runtime are **always** logged at `ERROR` level
     before any user-visible failure indicator.
   - Toolchain-native logging mechanism: ESP-IDF uses `ESP_LOGI(tag, ...)`
     etc. from `esp_log.h` — part of the always-linked common set, so do
     **not** add an `esp_log` entry to a component's `REQUIRES` (there is no
     `esp_log` component name in IDF 5.5 — it fails the build; the component
     is `log`, and you don't list it). The boot **banner** specifically is
     emitted via `printf` in the `[INFO] [APP]` format, because `ESP_LOGx`'s
     `I (ts) TAG:` format won't match the deploy regex — see
     `references/esp-idf-template/`. Arduino uses `Serial.print`-based output
     emitting
     the `[LEVEL] [TAG] message` format directly via **a small
     `src/log.h` shared header** (LOGE/LOGW/LOGI/LOGD macros wrapping
     `Serial.printf`, included from `main.cpp` and every module
     `.cpp`) — no external logging library required, keeps
     `platformio.ini` `lib_deps` limited to libraries the catalog
     actually recommends per Operating Principle 3.
   - `firmware-deploy` reads this banner to confirm boot success;
     the format is part of the codegen ↔ deploy contract.

7. **Defensive boot init for stateful peripherals.**
   Some chips on Attaky modules **do not come up in a safe / quiet
   state at power-on**. Without explicit firmware action, they can
   drive lines on the FPC bus, fire spurious interrupts, spam shared
   buses with traffic, or burn battery — and the symptoms surface as
   "weird crash" rather than "obvious bug." Codegen must emit
   defensive boot init for every chip in the catalog known to need
   it (the list below is closed at the time of writing; new entries
   get added as the catalog grows).

   ### Two-phase flow

   Defensive init runs as a **single dedicated pass** between
   `Wire.begin()` and the first per-module setup. It is structured in
   two phases so the chip-specific decisions are uniform across the
   needs-init list:

   - **Phase A — Discovery.** Probe every needs-init I²C address
     once (`Wire.beginTransmission(addr); Wire.endTransmission() == 0`
     or equivalent). Build a "present chips" map keyed by address.
     Don't configure anything in this phase — just observe. Log
     `[DEBUG] [HW] discovery: 0x<addr> present` /
     `[DEBUG] [HW] discovery: 0x<addr> absent` per address.
   - **Phase B — Init.** For each chip in the needs-init list,
     branch on (a) is it present? + (b) does this firmware use it?
     and dispatch to the chip-specific handler below. Modules that
     own a present-and-used chip (e.g. `power.cpp` owns MAX17048)
     run their own setup later and may rely on the chip already
     being in the safe state established in Phase B.

   The needs-init list and the use-flag input come from `parts-list.md`
   (which modules are physically in the Complete Build) + `requirements.md` /
   `dev-plan.md` (which capabilities the firmware actually uses).
   Codegen materializes a small config struct (e.g.
   `HwInitConfig { firmware_uses_buttons, firmware_uses_keyboard,
   firmware_uses_gps, ... }`) and passes it into the discovery+init
   pass. Modules query a tiny presence API (e.g.
   `hw_is_present(addr)`) to decide whether to attempt their own
   begin().

   The boot-time **module verification** runs strictly between the two
   phases above — after Phase A's discovery sweep completes, before
   Phase B's init dispatch, and before any Expand module's own setup()
   (Phase A → module detection → Phase B). See §7.4 below; it is a
   required part of every idea-lane firmware, not an optional per-chip
   handler.

   ### Per-chip handlers

   #### 7.1 AW9523 (`@ 0x58` / `@ 0x59` / `@ 0x5A` / `@ 0x5B`)

   AW9523 power-on register state is not guaranteed safe — depending
   on the chip's I²C address strap, reset timing, and prior session
   state, P-pins can come up driving an output rather than as
   high-impedance inputs. An unconfigured AW9523 on the FPC bus or
   the host BTB stack can pull lines and interfere with adjacent
   modules.

   - **Present + used by this firmware** (e.g. host `@ 0x59` for
     buttons in a concept that reads buttons): configure all pins
     into a known safe state (all inputs, interrupts masked) here.
     The owning module's setup later reprograms direction / IRQ /
     output per the actual usage. Log
     `[INFO] [HW] AW9523 @ 0x<addr> present and active — pre-configured
     to safe state, owning module will reprogram`.
   - **Present + not used by this firmware** (e.g. Bottom
     Control Keyboard's `@ 0x5A` and `@ 0x5B` when the concept
     targets Mesh Pocket but the user is running on Mesh Deck
     hardware): set **all 16 P-pins to inputs (high-Z)**, mask all
     interrupts, leave LED-control pins (P15/P16/P17 on the
     keyboard halves) configured as inputs as well so they don't
     drive the LED. Log `[INFO] [HW] AW9523 @ 0x<addr> present but
     unused — configured to safe input state`.
   - **Absent**: skip silently (already logged in Phase A).
   - This handler applies **only to AW9523**. TCA9555 (Gamepad's
     chip) comes up in a defined all-input state per its datasheet
     and is not in the needs-init list.
   - **Reference for full init / read / matrix-scan / INT-driven /
     bus-recovery patterns + ready-to-paste code**:
     `../../shared/aw9523-driver-patterns.md`. Read that doc when
     generating any code that touches AW9523 — it has the canonical
     init sequence, POR default state gotcha (the strap-table that
     explains why unconfigured AW9523s drive lines), matrix scan
     pattern with proper µs-level settle (not ms-level `delay`), INT
     bit decode / clear logic, and a checklist of common bugs.

   #### 7.2 AT6558 / ATGM336H GPS (presence from spec, not from probe)

   The LoRa-GPS Expand has **no chip on the host's main I²C bus** —
   the SX1262 is on SPI, the AT6558 GPS is on a dedicated UART, and
   the AT24C32 assist EEPROM is wired internally between the GPS
   module and the Expand's local circuitry, **not exposed to the
   host's I²C bus**. It is used inside the Expand's local GPS module
   circuitry only. So the GPS handler can't tell from a host I²C probe
   whether the LoRa-GPS Expand is plugged in.

   Instead, codegen reads `parts-list.md` directly: if
   `Expand_LoRa-GPS_1.0` appears in the parts list, set the
   `HwInitConfig` field `lora_gps_expand_present = true`; otherwise
   `false`. The handler dispatches on this flag plus the existing
   `firmware_uses_gps`. (This trusts parts-list as ground truth —
   same model as Principle 7.1's AW9523 handling, except AW9523s
   *can* be runtime-probed because they sit on the host I²C bus,
   while LoRa-GPS Expand chips don't.)

   The GPS module powers up immediately into active acquisition
   mode. It (a) emits NMEA-0183 sentences on the dedicated UART at
   9600 bps continuously, regardless of whether the host's UART RX
   is open, and (b) draws **30+ mA** continuously while searching
   for a fix. Both behaviors waste battery on devices where the
   concept doesn't use GPS.

   - **`lora_gps_expand_present` + `firmware_uses_gps`** (e.g. LoRa
     Hike Buddy Locator): no-op in defensive init — `gps.cpp` setup
     later opens the host UART RX and lets the module run normally.
   - **`lora_gps_expand_present` + `!firmware_uses_gps`** (rare —
     LoRa-only concepts that don't read GPS): send the AT6558
     standby NMEA command on the GPS UART once. The CASIC family's
     standby command is `$PCAS12,<seconds>*<checksum>` where
     `<seconds>` is the standby duration (use a large value like
     `3600` to mean "long sleep until next reboot"; checksum is XOR
     of all chars between `$` and `*`, computed by codegen). For
     example `$PCAS12,3600*2B`. **Do not use PMTK protocol commands**
     (`$PMTK*`) — those are MediaTek and are silently ignored by
     CASIC-family chips like AT6558. Log
     `[INFO] [GPS] not used by this firmware — sent CASIC standby command`.
   - **`!lora_gps_expand_present`**: LoRa-GPS Expand isn't in this
     Complete Build's parts list. UART IO17/18 may belong to a different
     Expand (FM-AM-Radio or Media-IO use them as I²S). Skip silently.

   #### 7.3 MAX17048 (`@ 0x36`)

   The MAX17048 fuel gauge on `Power_Standard-Cell_1.0` latches its
   `ALRT#` pin when a low-SOC or low-voltage threshold is crossed,
   and the latch **persists across power cycles** (the chip stays
   alive on battery even when the host is off). If the previous
   session ended in a low-battery state, the next boot's `ALRT#` is
   already asserted — and any host ISR attached to the AW9523 P02
   pin (the catalog's MAX17048 ALRT routing) will fire immediately
   on boot for a stale condition.

   - **Present** (almost always — Power Standard-Cell is in every
     commercial Complete Build): call the library's alert-clear method here
     (`Adafruit_MAX17048::clearAlertFlag()` on Adafruit_MAX1704X
     with a bitmask covering all six STATUS alert bits) before any
     module setup runs. `power.cpp` setup later configures
     thresholds for the firmware's own low-battery behavior. Log
     `[INFO] [POWER] MAX17048 latched alert cleared on boot`.
   - **Absent** (extremely rare — basically only USB-only test
     rigs): no MAX17048 to interact with. `power.cpp` will see the
     same absence later and run in USB-only mode. Skip silently.

   #### 7.4 Module detection & safe boot

   Beyond per-chip defensive init, codegen **always** bakes in the
   boot-time module verification defined in
   `../../shared/module-detection-and-safe-boot.md` — read that doc in
   full before touching this section or `hw_init.cpp`'s module-
   detection code; it is the single source for probe order, the frozen
   serial line format, the verdict rule table, and the safe-mode park
   pin set. Unlike 7.1–7.3, this isn't a per-chip handler — it's a
   firmware-wide check that runs once, strictly between Phase A and
   Phase B above (after Phase A's discovery sweep completes, before
   Phase B's init dispatch) and before any Expand module's own setup():

   - **`kExpectedModules`** — the only per-run input this check needs.
     Source it from `parts-list.md §1`'s canonical module IDs (one
     entry per module physically in the Complete Build); never invent
     or infer it. Every generated firmware always expects Core.
   - **Probe order** (shared doc §2): the main I²C scan — reusing the
     same low-level probe helper Phase A uses, but across every
     module-identity address, not just the needs-init list, since an
     unexpected extra module is exactly the case this check exists to
     catch — then the dedicated FM-AM bus probe (`0x64` on
     `IO41`/`IO42`, a second I²C bus), then the passive LoRa-GPS NMEA
     listen (`IO17` configured INPUT, RX-only UART @ 9600 bps, ~1.5 s,
     looking for a `$G` sentence start — never driving
     `IO17`/`IO18`/`IO21`).
   - **Verdict + frozen line** (shared doc §3): compute MATCH/MISMATCH
     per the rule table and print the frozen
     `[INFO] [HW] modules: expected=... detected=... expand=...
     verdict=...` line byte-identically — do not rephrase or reformat
     it. This line is part of the codegen ↔ deploy contract
     (`firmware-deploy` regex-verifies it against the build manifest).
   - **Safe mode** (shared doc §4): on MISMATCH, never halt — park
     every Expand-mapped pin, log the expected-vs-detected message on
     serial (and mirror it on the TFT via `display.cpp`), and skip
     every Expand module's own setup() call this boot while Core-only
     features (buttons, D-pad, battery display, etc.) keep running.
     `hw_init.h` exposes `hw_module_verdict_mismatch()` (ESP-IDF:
     `app_module_verdict_mismatch()`) for `main.cpp` / `app_main()` to
     gate those calls on — see the safe-mode notes on `radio.cpp`,
     `gps.cpp`, and `audio.cpp` / `i2s.cpp` in §4 below.
   - **The SD rule** (shared doc §5): SD card presence is never a
     module marker for `Expand_Media-IO_1.0` — see the SD rule note on
     `audio.cpp` / `i2s.cpp` in §4 below.

   `references/arduino-template/src/hw_init.cpp` + `.h` carry a real,
   generic implementation of this check — everything in it is reused
   as-is except `kExpectedModules`, which is a `TODO(codegen)` stub.
   The ESP-IDF equivalent (`i2c_master_probe` + an RX-only UART driver
   instance) lives directly in
   `references/esp-idf-template/main/main.c`, since that toolchain has
   no separate `hw_init.c` file.

8. **Follow the cross-cutting ESP32 patterns.** Beyond per-peripheral
   init, the generated firmware must follow the shared bring-up and
   resource patterns so it stays stable on real hardware. Apply the ones
   that fit what this firmware does (the spec's `dev-plan.md` Architecture
   notes say which):
   - `../../shared/esp32-bringup-and-rtos-patterns.md` — no large buffers
     on the main/UI task stack; DMA / stack / LVGL transfer buffers in
     internal RAM; one task owns each bus; **keep blocking work off the
     loop** — on the Arduino path prefer a non-blocking state machine
     (split the operation across ticks) and fall back to a worker task
     for genuinely long work; on the ESP-IDF path put blocking work on a
     dedicated worker task by default (see the §4 "loop-starvation &
     Task WDT" note for the Arduino specifics);
     optional peripherals log-and-continue (no-brick boot).
   - `../../shared/display-and-lvgl-gotchas.md` — one rotation owner, one
     byte-swap owner, async-flush completion wait, touch in
     controller-native coords, input pumped in `lv_timer_handler` (any
     firmware with a UI).
   - `../../shared/persistence-patterns.md` — staged single-commit NVS,
     schema-versioned settings (any firmware that persists state).
   - `../../shared/imu-driver-patterns.md` — QMI8658 enable sequence
     (`ACC_EN` lives in `CTRL1`, not just `CTRL7`), the LPF on/off choice
     by use-case (off for shake/tap, on for steady tilt), and a
     self-baselined relative shake threshold (any firmware that reads the
     IMU / accelerometer).
   - `../../shared/connectivity-patterns.md` /
     `../../shared/realtime-audio-patterns.md` — BLE-HID / WiFi / audio
     firmware.

9. **Bring-up baseline before features.** Before generating the full
   firmware, offer the user the **bring-up self-test** first
   (`references/bringup-template/`): a minimal firmware that scans the I²C
   bus, points the screen with an **asymmetric** test pattern, and echoes
   button presses over serial — and nothing else. The user flashes it and
   confirms the hardware comes up on the real board (the scan lists every
   chip the Complete Build should expose; the pattern is upright — `TOP` at the
   top, red in the top-left corner; each button echoes over serial)
   **before** you generate the full firmware. This is the step every
   Attaky firmware bring-up starts from — it catches a dead bus, a wrong
   byte-order, a flipped panel, a mis-mapped button, or a board that won't
   boot in 30 seconds, instead of leaving it buried under feature code.
   This does NOT relax Operating Principle 2: the self-test is a separate,
   recommended **first step**; the full firmware is still complete, not
   stubbed. Skip only if the user explicitly declines or has already
   proven the board comes up.

   Both toolchains have a bring-up self-test at parity:
   `references/bringup-template/` (Arduino/PlatformIO) and
   `references/esp-idf-bringup-template/` (ESP-IDF) — each does banner + I²C
   scan + asymmetric display test pattern + button echo. The ESP-IDF one is
   **HW-validated** (Core ESP32-S3 rev v0.2): it confirms the exact things
   the IDF path gets wrong silently — that IDF's own bootloader boots the
   board, that the console is on UART0 (so the `printf` boot banner reaches
   the host), that the I²C bus enumerates, and that the ST7789 comes up over
   `esp_lcd` with the right orientation/colors — before any feature code.
   Use the one matching the chosen toolchain.

## Workflow

### Collaboration mode

Read the `Collaboration mode` field from the spec package (any of
`parts-list.md`, `module-combination.md`, `requirements.md`,
`dev-plan.md` — they match), else `concept.md`, else (porting lane)
`port/plan.md` / `port/survey.md`; default `autonomous` if absent
(build already treats `port/plan.md` as the port identity source). See
`../../shared/collaboration-mode.md`.

In **step-by-step**, before this stage's work, ask this stage's
functional questions (none — codegen is technical; runs silently),
show the plan, execute on OK. In **autonomous**, just do the stage and
stop only at the essential gates. Never ask the user a technical
question in either mode.

### 1. Find the spec (and optionally the UI package)

Locate the spec before anything else:

- Look in `<workspace>/spec/` (the workspace folder is the parent of
  the spec folder; this was established by `firmware-brainstorm` and
  is where the user has been working).
- Read all four files: `parts-list.md`, `module-combination.md`,
  `requirements.md`, `dev-plan.md`.
- If the spec folder is missing, ask the user **one** short question:

  > "I can't find a `spec/` folder in this workspace. Give me a path
  > to the spec, or paste the four spec files here."

  Wait for either an absolute path or pasted content. Do not proceed
  without the spec — codegen has nothing to generate without it.

> **Port-workspace fix mode exception**: when a fix-mode invocation
> (from `firmware-build` §5.3 or `firmware-deploy` §3.6) targets a
> port workspace (`<workspace>/port/plan.md` exists and there is no
> `<workspace>/spec/`), skip the spec requirement — read
> `port/plan.md` + `port/survey.md` in its place and proceed straight
> to the fix. Outside fix mode, a port workspace is not a codegen
> target at all: point the user back to `firmware-port`.

**Then look for `<workspace>/ui/`** (optional, written by the
`firmware-ui` skill). If present, read all three files (`style.md`,
`screens.md`, `sprites.md`) and use them to drive `display.cpp`
generation per §4 below. Do NOT ask the user to confirm or skip — the
package's presence IS the user's intent. If `ui/` is absent, fall back
to default rendering (functional but unpolished — solid colors from
fixed defaults, simple primitive sprites, plain layouts). Note in the
generated `source/README.md` whether UI was driven by `ui/` or by
fallback defaults so future regenerations have signal.

Also scan `<workspace>/references/` if it exists: user-dropped
material and durable findings from earlier stages (library-usage
notes, root-caused gotchas) are input context for generation.
Precedence is unchanged — hardware facts come only from the catalog
(Operating Principle 3); a reference file never overrides a catalog
pin, address, or chip fact. If generation itself produces a durable
finding (e.g. an upstream library API note the next iteration will
want), record it as `<workspace>/references/YYYY-MM-DD-<topic>.md`
with a one-line provenance header (NOT this skill's own bundled
`references/` folder). Scratch output goes to `<workspace>/tmp/`.

### 2. Decide the toolchain

`spec/dev-plan.md §1 Toolchain` either picks one explicitly (Arduino
CLI / PlatformIO **or** ESP-IDF) or says "Picked at firmware-codegen"
(the spec template's default). A porting-lane workspace has no
`spec/`; there the toolchain is whatever `port/plan.md` already pins
(`firmware-port` sets that from the upstream project's own build
system — e.g. an ESP-IDF upstream stays ESP-IDF).

- **Locked** (dev-plan picks one explicitly, or the porting lane's
  `port/plan.md` pin): use that toolchain, unchanged. Don't re-ask,
  don't re-decide.
- **Not locked**: decide silently. This is a technical decision, not
  a functional one — codegen never asks the user a technical
  question (Operating Principle 4 of `firmware-brainstorm`; the
  shared `../../shared/collaboration-mode.md` contract). Default to
  **Arduino CLI / PlatformIO**. Pick **ESP-IDF instead** only when
  `requirements.md` / `dev-plan.md` clearly call for a genuinely
  IDF-only capability — a chip whose only available driver is an IDF
  component with no Arduino-compatible library, `esp_lcd` /
  `esp_lvgl_port`-level display integration, or sdkconfig-level
  control of IDF-only subsystems (e.g. ULP coprocessor programs —
  NOT custom partition tables, which the Arduino/PlatformIO path
  also supports via `board_build.partitions`).
  FreeRTOS tasks / queues / timers are NOT a trigger — the Arduino
  path exposes FreeRTOS too (see the concurrency guidance later in
  this file). When in doubt, stay on the default (per the per-chip
  and cross-cutting guidance elsewhere in this file and in
  `../../shared/`).

  Record the decision back into `spec/dev-plan.md §1 Toolchain` —
  replace "Picked at firmware-codegen" with the chosen toolchain plus
  a one-line rationale (e.g. "Arduino CLI / PlatformIO — no IDF-only
  capability required by this spec") — so the run is reproducible and
  `firmware-build` / `firmware-deploy` see a locked value on the next
  read. Tell the user, as a statement rather than a question, in
  their language:

  > "I'll generate this as a **PlatformIO / Arduino** project — the
  > spec doesn't need anything ESP-IDF-only."

  (substitute the ESP-IDF equivalent narration when that's the pick).
  Lock the choice and use it consistently for the rest of this run.

### 3. Detect existing `source/`

If `<workspace>/source/` already exists from a prior codegen run,
warn the user **once** in their language:

> "I see `<workspace>/source/` already exists from an earlier codegen
> run. I'll regenerate it from the current spec — any manual edits
> you made in those files will be overwritten. OK to proceed?"

- If they say yes → continue.
- If they say no → stop. Do not touch `source/`. Suggest they back
  it up or move it aside before running codegen again.

If `source/` doesn't exist yet, skip this step.

> **Fix mode exception**: when `firmware-build` (build-failure
> auto-fix loop, its SKILL.md §5.3) or `firmware-deploy`
> (runtime-panic loop, its SKILL.md §3.6) invokes this skill, it
> passes the error log / panic evidence + a "fix mode" flag.
> In fix mode, **suppress the overwrite-confirmation prompt** above —
> proceed silently, regenerate the affected files in place, and let
> control return to the invoking skill for the next build / flash
> attempt. User-facing progress comes from the invoking skill in this
> loop, not from this skill. Fix mode also narrows the regeneration scope:
> rather than regenerating everything from scratch, focus on the
> files implicated by the error log (typically 1-3 source files)
> and leave the rest alone. **During a milestone-gated run**
> (`firmware-build` passes the current milestone identity), scope the
> fix to the current milestone's files and **never regenerate or mutate
> modules belonging to an already-passed milestone** — a passed
> milestone is frozen. **Port workspaces** (created by `firmware-port`:
> `<workspace>/port/plan.md` exists and there is no `<workspace>/spec/`):
> there is no spec to regenerate from. Fix mode there means minimal
> error-log-driven patches to the ported tree — respect the upstream's
> own conventions and `port/plan.md`'s change list, and never rewrite
> upstream files wholesale.

### 4. Generate the source tree

**First, the bring-up baseline (Operating Principle 9).** Unless the user
has already proven the board comes up, offer the bring-up self-test matching
the chosen toolchain before this step — `references/bringup-template/`
(Arduino) or `references/esp-idf-bringup-template/` (ESP-IDF) — and have them
build + flash it and confirm on the real board: the I²C scan, the upright
asymmetric display pattern (white bar on top, red top-left, correct colors),
and the button echo (the IDF one also proves the `printf` banner reaches
UART0). Generate the full source tree below only once the hardware is known
to come up (or the user declines the baseline).

**Milestone-staged generation (opt-in, for complex builds).** When the
spec's `dev-plan.md` lists milestones AND the build is large / the user
wants to go step by step, generate **one milestone at a time** into the
same `source/` (never a new tree per milestone): milestone 0 is the
bring-up baseline above; each later milestone adds its modules **fully**
(Operating Principle 2 — sequencing, not stubbing), extends the tick
scheduler + `main.cpp`, and stops. After each milestone, hand to
`firmware-build` + `firmware-deploy` to build + verify it **on the real
board** before you generate the next — don't run ahead. Emit a milestone
marker at boot as a **separate** log line, never inside the OP6 banner:
`[INFO] [APP] milestone: M<N> (<short name>)` — `firmware-deploy` checks
for it at the gate, and `firmware-build` records the milestone in the
manifest. If a milestone fails its gate, fix **only that milestone** (fix
mode, scoped to its files); never regenerate a milestone that already
passed. The **default** (no opt-in) stays: the bring-up baseline, then the
full firmware in one pass.

**Host-test target for the pure-logic seam.** When `dev-plan.md`'s
architecture notes flag hardware-independent modules (parsers, state
machines, geometry, formatting — the hardware / pure-logic seam),
also emit a small host-native golden test so `firmware-build` can
check them off-target before flashing (its Operating Principle 6): a
`test_host/` folder with a plain-C++ `main()` that includes those
modules directly and asserts golden cases, guarded by
`#ifdef <PROJ>_HOST_TEST` where it touches shared headers, plus a
one-line compile command in `source/README.md` (e.g.
`c++ -std=c++17 -D<PROJ>_HOST_TEST test_host/test_logic.cpp geo.cpp
-o <workspace>/tmp/host-test` — adjust the file list to the modules
emitted). This works identically for both toolchains, since the pure
files depend on no Arduino / ESP-IDF headers. Skip it when the
dev-plan flags no hardware-independent modules. (The bundled worked
example predates this instruction and ships without `test_host/` —
its absence there is historical, not licence to skip.)

The structure depends on the toolchain locked in §2.

#### Arduino CLI / PlatformIO branch

Project layout:

```
<workspace>/source/
├── platformio.ini           ← build config + library deps
├── README.md                ← build / flash instructions (local-only path)
├── src/
│   ├── main.cpp             ← setup() + loop() + scheduler
│   └── <module>.cpp / .h    ← one file per module from dev-plan §2
└── lib/                     ← empty; reserved for user's own libraries
```

**`platformio.ini`** — declare board target + library dependencies:

```ini
[env:attaky_esp32s3]
; pioarduino (arduino-esp32 3.x) — the maintained successor to the EOL
; official espressif32 platform. REQUIRED for boot: the 2.x platform's
; bootloader boot-loops rev-v0.2 silicon (verified 2026-06-29 that 2.x +
; qio also loops) — it needs the newer ESP-IDF 5.x bootloader pioarduino
; carries. Generated LEDC must use the 3.x pin-based API (ledcAttach /
; ledcWrite(pin, duty)).
platform = https://github.com/pioarduino/platform-espressif32/releases/download/55.03.38-1/platform-espressif32.zip
board = esp32-s3-devkitc-1
framework = arduino

; Flash mode left at the default (qio). Validated 2026-06-28 on a Core
; ESP32-S3 rev v0.2 (N16R8): qio boots; forcing dio boot-loops the
; second-stage bootloader (Saved PC:0x403cd9aa). Don't force dio.
board_build.flash_size = 16MB
board_build.partitions = default_16MB.csv
; OPI PSRAM is optional + not yet HW-validated under qio on this
; silicon — see arduino-template/platformio.ini for the gated block.

monitor_speed = 115200
; upload_speed is 460800 (NOT 921600) — 921600 fails reliably on real
; cables / USB hubs with "No serial data received" mid-handshake.
upload_speed = 460800

; arduino-esp32 default is gnu++11; example-codegen and many user
; sources use C++14 digit separators (e.g. 30'000) which need gnu++14+.
build_unflags =
    -std=gnu++11

build_flags =
    -std=gnu++17
    ; --- TFT_eSPI driver + Attaky Core ST7789 pin map ---
    ; (TFT_eSPI MUST get its driver + pins via -D flags; without these
    ; the library aborts with "User defined setup found but no driver
    ; selected" or silently uses wrong pins → black screen at runtime.)
    -DUSER_SETUP_LOADED=1
    -DST7789_DRIVER=1
    -DTFT_RGB_ORDER=TFT_BGR           ; this panel is BGR-wired; without it red/blue are swapped
    -DTFT_WIDTH=240
    -DTFT_HEIGHT=320
    -DTFT_MOSI=13
    -DTFT_MISO=-1                     ; ST7789 is write-only; explicit -1 prevents collision with LoRa MISO on IO7
    -DTFT_SCLK=11
    -DTFT_CS=45
    -DTFT_DC=12
    -DTFT_RST=10
    -DTFT_BL=14
    -DSPI_FREQUENCY=40000000
    -DUSE_HSPI_PORT=1                 ; HSPI (SPI2). On arduino-esp32 3.x the default/FSPI port collides with the flash/PSRAM SPI controller and HANGS tft.init(); HSPI fixes it (validated 2026-06-29). USE_FSPI_PORT is the WRONG flag — it is what hangs.
    -DLOAD_GLCD=1
    -DLOAD_FONT2=1
    ; --- Serial routing ---
    ; Attaky Core's USB connector is wired through the CH340X UART
    ; bridge to ESP32-S3 UART0, NOT the chip's native USB pins. Leave
    ; Serial as the default HardwareSerial(0); do NOT enable
    ; arduino-esp32's native-USB-CDC-on-boot flag (would make Serial
    ; output vanish — no host enumeration on Attaky Core's USB port).
    ; (Add -DBOARD_HAS_PSRAM only with the optional OPI-PSRAM block —
    ;  not yet HW-validated under qio; the example runs PSRAM-off.)

lib_deps =
    ; PlatformIO registry slugs use a SPACE between owner-prefix words
    ; for Adafruit libraries (e.g. `Adafruit AW9523`, NOT
    ; `Adafruit_AW9523`). Other vendors keep underscores in their
    ; library name verbatim (e.g. `TFT_eSPI` is correct).
    jgromes/RadioLib                        ; if LoRa-GPS in BOM
    mikalhart/TinyGPSPlus                   ; if LoRa-GPS in BOM
    adafruit/Adafruit AW9523                ; always — Core uses AW9523
    bodmer/TFT_eSPI                         ; for ST7789 TFT (needs build_flags above)
    adafruit/Adafruit MAX1704X              ; if Power_Standard-Cell in BOM
    ; FM-AM-Radio Complete Build: pu2clr/TEF668X has no PlatformIO registry entry
    ; — pull from GitHub directly.
    https://github.com/pu2clr/TEF668X.git   ; if FM-AM-Radio in BOM
    ; ...etc per the Complete Build's actual modules
```

> **Library list rule**: include only the libraries the catalog
> recommends for modules actually present in `parts-list.md`. Don't
> include libs for modules the user doesn't have.

> **TFT_eSPI rule (non-negotiable)**: when `bodmer/TFT_eSPI` is in
> `lib_deps`, the `-DUSER_SETUP_LOADED=1` + driver + pin block in
> `build_flags` above is **required**. Omitting it is a silent
> firmware bug (compiles but renders black or wrong-pin output). The
> pin numbers come from the catalog's `Core_ESP32_1.0` ST7789 row —
> if the catalog updates them, regenerate.

> **Partition table**: use the platform's built-in `default_16MB.csv`
> (`board_build.partitions = default_16MB.csv`) — the standard 16 MB
> layout (`nvs` + `otadata` + `app0`/`app1` + `spiffs`), validated-booting
> on real hardware (Core ESP32-S3 rev v0.2, 2026-06-28). No CSV
> needs to ship with the firmware. **A persistent `Saved PC:0x403cd9aa`
> ROM-stage boot-loop with no banner is NOT a partition problem** — it is
> `board_build.flash_mode = dio` forced on rev-v0.2 silicon; leave
> flash_mode at the default qio (the OTA-shaped `default_16MB.csv` boots
> fine). Emit a custom CSV only when a firmware needs a non-standard
> layout (e.g. a larger app slot or an `ffat` data partition).

**`src/main.cpp`** — boot, peripheral init, main loop, task
scheduler. Calls into the per-module files for actual feature logic.
Use `module-combination.md` (BTB stack pattern, FPC bus topology, ESP32 IO
allocation, mutual-exclusion caveats) to drive peripheral init order
and bus-handle wiring; don't infer the connectivity from `parts-list`
alone.

`main.cpp` also owns the **boot banner** per Operating Principle 6 —
on `Serial.begin(115200)` (Arduino) or `esp_log_level_set()` (IDF),
first thing emit:

```
[INFO] [APP] <firmware-name> v<version> on <build-SKU>
[INFO] [APP] Build: <build timestamp> / toolchain: <PlatformIO|ESP-IDF>
```

**Banner field sources** (so every codegen run produces an identical
format `firmware-deploy` can match):

- `firmware-name` = the concept's §1 one-liner heading (the title line
  in `concept.md`, e.g. `LoRa Hike Buddy Locator`). Title-case form,
  not the slug.
- `version` = `0.1.0` for the first codegen run; bumped only when the
  user explicitly requests a version bump in a later regeneration.
- `build-SKU` = the `Complete Build:` field from `parts-list.md §2` (e.g.
  `Mesh Pocket 1.0`); for custom builds with no SKU match, use
  `Custom build`.
- `build timestamp` = `__DATE__ ' ' __TIME__` macros on Arduino, or
  `IDF_VER` + buildtime from CMake on IDF.

before calling any module's setup. This banner is part of the
contract `firmware-deploy` watches for to confirm app boot.

**`src/<module>.cpp` / `.h`** — one pair per module from
`dev-plan.md §2 Code module breakdown`. Pin numbers / bus addresses /
interrupt routing all come from `module-combination.md` §Pin allocation +
the catalog's per-module pin maps. Real implementation, not stubs:
- `display.cpp` — TFT init, screen layouts, text rendering. Use
  `TFT_eSPI` with the catalog's pin map. **If `<workspace>/ui/` is
  present**, drive every aspect of rendering from those files:
  - `ui/style.md` palette tokens → emit `static const uint16_t
    kPaletteX = 0x...;` for each token + use those constants
    everywhere (no hard-coded `TFT_BLACK` / `TFT_WHITE` sprinkles).
  - `ui/style.md` typography slots → call `g_tft.setTextFont(N)` per
    slot before drawing each text region — **and add the matching
    `-DLOAD_FONTx=1` to `platformio.ini` `build_flags`** for any slot
    beyond the default `LOAD_GLCD` / `LOAD_FONT2`. TFT_eSPI compiles in
    only the font slots you flag; `setTextFont(N)` for an unflagged slot
    renders nothing (silent — compiles clean, draws blank). (A
    `ui/style.md` may instead specify the GLCD base font scaled via
    `g_tft.setTextSize(N)` — no `LOAD_FONTx` slot, smallest flash; this
    is what the bundled `example-codegen/display.cpp` does. Honor
    whichever the package declares; don't force `LOAD_FONTx` onto a
    `setTextSize` design.)
  - `ui/style.md` spacing scale + density → control region paddings
    and gap values in screen draw helpers.
  - `ui/screens.md` per-screen layout → one `draw_<screen>()` helper
    per section, with regions drawn in declared order using the
    palette tokens for fill / text colors. Coordinates copied
    one-to-one from the screen's region list.
  - `ui/sprites.md` Form A sprites → emit one C++ helper per sprite
    (`draw_cat_idle(cx, cy)`) that composes the primitives in z-order.
  - `ui/sprites.md` Form B sprites → emit one `static const uint16_t
    kSpriteX[]` per sprite and call `g_tft.drawBitmap` / equivalent.
  - **Dirty-bit redraw gating** (regardless of whether `ui/` is
    present): the TFT renderer should only repaint when state has
    changed (a `bool g_dirty` flag set on screen transitions, action
    events, ambient threshold crossings, etc.). Do NOT do periodic
    full-screen `clear() + redraw()` — full-screen black-then-redraw
    causes visible flicker on the panel. Default cadence: redraw on
    dirty only; no time-based unconditional redraw. The bundled
    `example-codegen/display.cpp` demonstrates this with per-region
    signature gating — each region (status bar / arrow pane / list)
    repaints only when the exact values it draws change.
  - **If `<workspace>/ui/` is absent**, fall back to functional
    defaults: a single neutral palette (~6 hard-coded RGB565 colors),
    one font slot, primitive-composition sprites for any visible
    entity. Note the fallback in `source/README.md`.
  - **Pattern to apply:** one rotation owner — pick the orientation the
    device is physically used in and call `setRotation()` once for it,
    per the catalog's 180°-mounted-panel correction: `setRotation(3)`
    for landscape, `setRotation(2)` for portrait (the bundled
    `example-codegen` is landscape `setRotation(3)`). Those numbers are
    the **TFT_eSPI** convention; on the ESP-IDF / `esp_lcd` or
    `Adafruit_ST7789` path the equivalent MADCTL / rotation for the same
    180° mount differs — verify with an **asymmetric** test pattern, never
    by assuming the value. Don't also rotate elsewhere. One byte-swap
    owner — and "single owner" means **whatever touches the panel / SPI /
    bus**, not just whatever *calls the renderer*
    (`../../shared/esp32-bringup-and-rtos-patterns.md`): a second writer
    on a different code path still races the bus. Light the backlight only
    after the first flush so the user never sees panel garbage during init
    (`../../shared/display-and-lvgl-gotchas.md` §1 / §2 / §5).
- `input.cpp` — read AW9523 buttons over I²C; debounce; expose
  events.
- `touch.cpp` / `.h` — capacitive touch input from the FT6636
  (FocalTech FT6x36 family) when the concept uses the touch panel:
  - **Init / CTP reset**: de-assert the touch controller's reset via
    the **shared `AW9523 @ 0x59` P13 handle** (`CTP_RESET`,
    active-low): drive the line low to reset, wait ~300 ms to settle,
    then release it high. **Reuse the single `0x59` expander handle**
    that `input.cpp` already owns (single-bus-owner / single-expander
    invariant) — never instantiate a second `Adafruit_AW9523` for the
    same address. Read `../../shared/aw9523-driver-patterns.md` before
    touching the `0x59` handle (per Operating Principle 7), and write
    only P13 — masked single-pin writes, never whole-byte writes that
    would re-mode the buttons sharing that expander.
  - **Probe**: the FT6636 is an I²C 7-bit slave at `0x38` (FT6x36
    family fixed address — the catalog's active / interface rows
    confirm `0x38` and supersede the older "touch model not exposed"
    note). Confirm presence with a probe before first read.
  - **Read points**: read touch coordinates via a **maintained
    FT6x36 Arduino library or named constants from the FT6x36
    datasheet** — keep raw register-address literals out of this skill's
    prose; let the library or named datasheet constants own them.
    Debounce and emit
    (x, y) press / release events, mirroring how `input.cpp` exposes
    button events.
  - **Pattern to apply (polling vs INT):** poll the touch controller
    at the UI tick as the **simpler default** for generated code —
    this mirrors how `input.cpp` polls buttons each tick and keeps the
    single-loop design uniform. The touch INT (routed via
    `AW9523 @ 0x58` P04, fanned out through the shared-ISR pub/sub
    pattern below) is a valid **first-class** option if a project
    genuinely needs interrupt-driven touch — but frame polling as the
    simpler choice, NOT as a workaround for a "broken" INT path.
  - **Raw-TFT_eSPI vs LVGL — coordinate mapping (Arduino path):**
    TFT_eSPI does **not** map an external touch IC's coordinates into
    the panel's rotation frame (it only knows about its own resistive
    XPT2046, not the FT6x36). Codegen must therefore map the FT6x36's
    **native (pre-rotation)** (x, y) into the panel's `setRotation()`
    frame **manually** — into whichever orientation the firmware uses
    (the bundled example and this device are landscape `setRotation(3)`;
    the catalog documents landscape 3 / portrait 2 for the 180°-mounted
    panel). The transferable rules from
    `../../shared/display-and-lvgl-gotchas.md` §7 are: (a) touch
    coordinates are controller-native / pre-rotation, so the mapping
    is on the firmware, not the touch IC; (b) validate the mapping
    with a **four-corner crosshair** test (tap each corner, confirm
    the reported point lands there); (c) the ~300 ms reset-settle is a
    **reliability** measure, not a fix for dead or offset input — that
    would be a mapping or pump bug. The LVGL-only bits in that doc
    (`lv_timer_handler()` pumping input, `esp_lcd_touch`
    `x_max` / `y_max` set to the controller's native resolution)
    are **IDF / LVGL-only** — they do not apply to the raw-TFT_eSPI
    Arduino path; apply them only when generating an LVGL firmware.
  - A manual native→rotated map (panel native is 240×320) for landscape
    `setRotation(3)` — the example's orientation — with portrait
    `setRotation(2)` shown as the alternative:
    ```cpp
    // FT6x36 reports native (pre-rotation) coords (240x320 native). Map
    // them into the panel's setRotation() frame. For LANDSCAPE
    // setRotation(3): swap axes for landscape, then flip per the 180 deg
    // mount. The exact axis signs/order depend on the panel MADCTL —
    // CONFIRM with the four-corner crosshair test; do not trust the
    // formula blind (the example is button-only, so this is not itself
    // HW-validated).
    void map_touch_native_to_panel(uint16_t nx, uint16_t ny,
                                   uint16_t& px, uint16_t& py) {
      constexpr uint16_t kNativeW = 240;  // FT6x36 native width
      constexpr uint16_t kNativeH = 320;  // FT6x36 native height
      // setRotation(3) landscape (320x240): swap, then flip.
      px = (kNativeH - 1) - ny;
      py = nx;
      // For portrait setRotation(2) instead, flip both native axes:
      //   px = (kNativeW - 1) - nx;  py = (kNativeH - 1) - ny;
    }
    ```
  - **Note**: the worked `example-codegen` is button-only (the Hike
    Buddy concept has no touch) — do NOT add touch to that example.
    The short native→rotated snippet above lives in this skill prose
    precisely because no example demonstrates touch mapping.
- `radio.cpp` — RadioLib SX1262 init at the right frequency
  (default 915 MHz; if `requirements.md §4 Configuration parameters`
  exposes `frequency`, read from there). Send/receive helpers.
  - **Safe-mode gate**: this module belongs to `Expand_LoRa-GPS_1.0`.
    Gate `radio_setup()` — and anything that calls into it — on
    `!hw_module_verdict_mismatch()` (ESP-IDF:
    `!app_module_verdict_mismatch()`). On a MISMATCH boot the module-
    detection check (Operating Principle 7 §7.4) has already parked the
    SX1262's SPI pins; initializing the radio anyway would drive lines
    that may belong to whatever module is actually attached
    (`../../shared/module-detection-and-safe-boot.md` §4).
- `gps.cpp` — UART NMEA parse via TinyGPSPlus. Expose the full
  accessor surface the example demonstrates, not just lat/lon/speed:
  fix presence + fix-staleness (treat a fix older than a few seconds as
  lost — see the example's `gps_has_fix()` gating on
  `location.age()`), course-over-ground (valid only above a small
  ground-speed floor, since slow-speed course is noise), and satellite
  count. **Wiring note**: the host UART RX receives the GPS module's
  TXD — do NOT swap the GPS UART TX/RX pins. Swapping them is the
  classic "no NMEA ever arrives" bug; if no sentences arrive, suspect
  wrong-pin / wiring before suspecting a no-fix condition (the example
  calls this out inline in `gps.cpp`).
  - **Pattern to apply:** drain the UART every tick so the driver
    keeps up with the continuous 9600-bps NMEA stream — a tick that
    skips reading risks UART RX-buffer overflow and dropped sentences
    (`../../shared/esp32-bringup-and-rtos-patterns.md` §6, the
    drain-the-RX-ring-every-loop rule).
  - **Safe-mode gate**: this module belongs to `Expand_LoRa-GPS_1.0`.
    Gate `gps_setup()` on `!hw_module_verdict_mismatch()` the same way
    as `radio.cpp` above. The module-detection check's own passive NMEA
    listen (Operating Principle 7 §7.4) already released `IO17`'s UART
    instance before `gps_setup()` runs, so re-opening it here is safe
    when this boot does own LoRa-GPS.
- `power.cpp` — MAX17048 init, periodic SOC poll, ALRT IRQ handling.
- `state.cpp` — app state machine. Persistent storage helpers
  (NVS / flash) for any data that needs to survive reboots.
  - **Pattern to apply:** stage all fields then commit in a single
    write (NVS has no multi-key transaction, so a mid-write crash can
    leave a half-updated record), carry a `schema_ver` field from day
    one, and read with tolerant defaults so an older or absent record
    degrades gracefully instead of bricking boot
    (`../../shared/persistence-patterns.md` §1 / §2). This is the
    highest-value weave to get right — persistence bugs are silent and
    destructive (corrupted settings, lost pairing, boot loops) and
    rarely show up until a real device has been power-cycled in the
    field.
- `wifi.cpp` / `.h` — station (and optional SoftAP) bring-up when the
  concept uses WiFi connectivity (the Core ESP32-S3 always *can* do
  WiFi; generate this module only when the spec's features need the
  network). Event-driven connect; expose a `wifi_is_up()` / RSSI
  accessor surface.
  - **Pattern to apply (citing `../../shared/connectivity-patterns.md`):**
    - **Power-save OFF while streaming** (§3): call
      `esp_wifi_set_ps(WIFI_PS_NONE)` the instant a sustained stream
      starts (restore `WIFI_PS_MIN_MODEM` on idle for battery). The
      default modem-sleep parks the radio between DTIM beacons and drops
      enough of a sustained stream to cause chronic underrun / stutter.
    - **Size the lwIP mailbox, not just the socket** (§3): for bursty
      UDP raise `CONFIG_LWIP_UDP_RECVMBOX_SIZE` (e.g. 6 → 64) **then**
      `SO_RCVBUF` on top — a bigger `SO_RCVBUF` alone doesn't help
      because packets are dropped before the socket.
    - **Unicast for anything that matters** (§3): broadcast / multicast
      UDP is lossy under load (basic rate, no link-layer ACK).
    - **Setup UX that can't lock the user out** (§4): keep the SoftAP up
      until the station associates; scan first and connect to the
      strongest BSSID; treat every disconnect identically (the driver
      can't tell wrong-password from signal loss) with a retry ladder
      (5 fast → 5/10/20 s backoff, cap 30 s) and the AP re-enabled in
      parallel.
    - **Coexistence** (§1): BLE + WiFi share one radio and coexistence is
      weak under load — on a WiFi-centric device keep BLE off by default
      and bring it up only when needed.
  - **Toolchain note**: Arduino path = `WiFi.h` +
    `esp_wifi_set_ps()`; ESP-IDF path = `esp_wifi` + the
    `CONFIG_LWIP_UDP_RECVMBOX_SIZE` sdkconfig knob.
  - **Note**: the worked `example-codegen` is LoRa-only (no WiFi) — do
    NOT add WiFi to that example; this guidance lives in §4 prose, the
    same way the `touch.cpp` mapping snippet above does.
- `audio.cpp` / `i2s.cpp` — I²S audio output when the parts list
  includes an audio-output (I²S DAC / speaker) module. I²S TX at the
  stream's sample rate; expose a feed / write surface backed by a ring
  buffer. **Audio out is I²S only** — there is no Bluetooth-Classic A2DP
  sink on this BLE-only silicon
  (`../../shared/connectivity-patterns.md` §1); never emit a
  Bluetooth-audio path.
  - **Safe-mode gate**: when the parts list's audio module is
    `Expand_Media-IO_1.0`, gate `audio_setup()` / `i2s_setup()` on
    `!hw_module_verdict_mismatch()` the same way as `radio.cpp` above —
    a MISMATCH boot never drives the amp/mic I²S lines, since the
    incident this whole check exists to prevent is exactly a live
    speaker amp rendering the wrong module's traffic as noise
    (`../../shared/module-detection-and-safe-boot.md` intro /
    `../../shared/realtime-audio-patterns.md` §6).
  - **SD rule**: `Expand_Media-IO_1.0`'s SD card slot is **never** a
    module marker — its absence never flips the boot verdict
    (`../../shared/module-detection-and-safe-boot.md` §5). Card-detect
    or mount failure degrades only the SD-dependent feature (e.g. a
    playlist reader) with a clear message; mic and speaker features
    keep working regardless of SD state.
  - **Pattern to apply (citing `../../shared/realtime-audio-patterns.md`):**
    - **Pace at the consumer, never throttle the producer** (§1): the
      I²S clock is master — drain the input ASAP, **no `vTaskDelay` in
      the receive / decode loop**; prime ~200 ms **once** before
      starting I²S, then free-run on a bounded ring with **late-drop**
      as the only back-pressure.
    - **Self-anchor on the first packet** (§2): map `local_now + cushion`
      to the first valid packet's timestamp; start the cushion at
      ~200 ms and tune it from a `late` counter.
    - **Underrun = zero-fill** (§3): write silence when the ring runs
      dry (repeating the last sample makes audible tones); on a
      rate / format change set a "needs reinit" flag and reconfigure I²S
      **at a frame boundary on the feeder task**, never mid-DMA from an
      event handler.
    - **Be liberal in what you accept** (§4): tolerate missing optional
      headers, keep-alives, and longer idle gaps — a strict parser
      stalls reconnects against real senders.
    - **Latency sizing** (§5): small DMA blocks (~64-128 sample frames ×
      2-4 buffers, < 10 ms) and run the audio task on its **own core**
      (`../../shared/esp32-bringup-and-rtos-patterns.md` §7).
  - **WiFi-fed audio = the split**: RX task → bounded ring → I²S
    consumer task, the consumer pinned to its own core — the same
    worker-task / core-split rule as Operating Principle 8 and
    `../../shared/esp32-bringup-and-rtos-patterns.md` §2 / §7.
  - **Toolchain note**: Arduino path = the I²S Arduino API; ESP-IDF
    path = `driver/i2s_std.h` (already named in the ESP-IDF component
    list below).
  - **Note**: no audio in the LoRa `example-codegen` — prose-only, per
    the `touch.cpp` precedent.
- *(...whatever else the dev-plan listed)*

> **Pattern to apply (main / all modules):** driver objects that carry
> large internal buffers (display drivers, sprites, framebuffers, LVGL
> draw buffers, packet scratch) go **file-static** (or are heap- /
> PSRAM-allocated), never declared stack-local inside `setup()` or a
> module init function. The main / UI task stack is small, and a fat
> object on it overflows the stack and surfaces as a "weird crash" at
> boot rather than an obvious bug
> (`../../shared/esp32-bringup-and-rtos-patterns.md` §2 / §3).

> **Loop-starvation & Task WDT (Arduino path):** arduino-esp32 runs
> `loop()` as a FreeRTOS task under a task watchdog. A single tick that
> blocks too long (hundreds of ms or more — a blocking radio
> `transmit()`, a long synchronous read, a `delay()`) starves the
> sibling modules sharing that loop (input, display, GPS drain) and can
> trip the WDT into a reset. Two sanctioned patterns:
>
> 1. **Non-blocking state machine (preferred default).** Split the
>    long operation across ticks instead of blocking inside one. For
>    example, *if the RadioLib version exposes it*, prefer
>    `startTransmit()` + poll for completion across subsequent ticks
>    over the blocking `transmit()`. The loop stays responsive and no
>    sibling starves.
> 2. **Worker task.** Move the blocking work onto its own task via
>    `xTaskCreatePinnedToCore` and hand work to it through a FreeRTOS
>    queue. Size the worker's stack for the **worst-case callee** (the
>    deepest function it can call, including library internals), not a
>    guessed round number (`../../shared/esp32-bringup-and-rtos-patterns.md`
>    §2 / §7).
>
> **The example's deliberate mitigation:** the worked `radio.cpp` uses
> the blocking `transmit()` but keeps a single-loop design safe by
> (a) broadcasting only periodically (gated on an interval, not every
> tick) and (b) returning early from `radio_tick()` right after a TX —
> skipping only that radio tick's RX path, not the rest of `loop()`
> (which continues to `gps_tick()` / `power_tick()` / etc.); see
> `radio.cpp` — the blocking `transmit()` is followed by `startReceive()`
> and an early `return`. That is the **intentional shape** for a single-loop LoRa
> design: one bounded blocking TX per interval, not blocking TX
> scattered through every tick. Preserve this shape on regeneration —
> do not spread blocking transmits across ticks or call them
> unconditionally.

> **Shared interrupts via host AW9523 expanders**: on `Core_ESP32_1.0`,
> `AW9523 @ 0x58` aggregates several physical interrupt sources
> (button presses via `AW9523 @ 0x59` chained INTN, MAX17048 `ALRT#`,
> peripheral interrupts via FPC bus, etc.) onto a single ESP32 IO
> (`IO4`). When multiple modules need interrupt-driven behavior on
> this expander (e.g. `input.cpp` for buttons + `power.cpp` for low
> battery alert), implement a **single ISR + pub/sub fan-out** pattern:
>
> 1. One handler attaches to `IO4` and reads the AW9523's input
>    register on each fire.
> 2. Modules register listeners with the handler at setup time
>    (e.g. `aw9523_subscribe(P02, &power_alrt_handler)`).
> 3. The handler dispatches to subscribed listeners based on which
>    P-pin actually changed state.
>
> Don't let multiple modules each attach their own ISR to `IO4` — they
> would race / replace each other.

**`src/<module>.h`** — clean public API. One header per module.

**`README.md`** — local-only build path:

```markdown
# <Concept title> firmware

Generated by `attaky-firmware-builder`.

## Build prerequisites

Install one of the supported toolchains:

- **PlatformIO (recommended)** — install via VS Code's PlatformIO
  extension (search "PlatformIO IDE" in the marketplace), or
  standalone:
  ```
  # macOS
  brew install platformio

  # Linux / Windows: see https://platformio.org/install
  ```

> **Note**: this project is structured as a PlatformIO project (`src/main.cpp`,
> not a `.ino` sketch). Use PlatformIO. Arduino CLI works directly on
> sketches, not PlatformIO projects, so it isn't a supported build path
> for this generated source. (`firmware-build` from this plugin chain
> drives the build for you — recommended over manual.)

## Build

```
pio run
```

The first build downloads ~50 MB of libraries via PlatformIO's
package manager. Subsequent builds use the local cache.

## Flash

```
pio run --target upload
```

(or use `firmware-deploy` from this plugin chain.)
```

#### ESP-IDF branch

Project layout:

```
<workspace>/source/
├── CMakeLists.txt           ← root build config
├── README.md                ← build / flash instructions (local-only)
├── sdkconfig.defaults       ← partition + PSRAM + flash size defaults
├── main/
│   ├── CMakeLists.txt
│   ├── main.c               ← app_main()
│   └── <module>.c / .h
└── components/              ← managed components via idf_component.yml
    └── (per-component subdirs as needed)
```

**`CMakeLists.txt`** (root) — minimum viable IDF project file
targeting `esp32s3`.

**`sdkconfig.defaults`** — set 16 MB flash, 8 MB OctalSPI PSRAM,
default partition table, 240 MHz CPU.

**`main/idf_component.yml`** — declare component dependencies:

```yaml
dependencies:
  idf:
    version: ">=5.1"
  ## Most chips on Attaky modules rely on built-in IDF drivers
  ## (`driver/i2c_master.h`, `driver/spi_master.h`, `driver/i2s_std.h`,
  ## `esp_lcd` for ST7789, `esp_vfs_fat_sdspi` for SD). Add managed
  ## components only for chips that need them — e.g. vendor Semtech's
  ## LoRaMac-node sx126x driver into a local `components/` subdirectory
  ## for `Expand_LoRa-GPS_1.0`, since there's no first-party Espressif
  ## managed component for the SX1262 today (per the public hardware
  ## catalog Recommended Libraries section).
```

**`main/main.c`** — `app_main()` entry, init peripherals, spawn
tasks for each module.

**`main/<module>.c` / `.h`** — one pair per module from
`dev-plan §2`. Idiomatic ESP-IDF (FreeRTOS tasks, queues, ESP-IDF
peripheral drivers — `driver/i2c_master.h`, `driver/spi_master.h`,
`driver/i2s_std.h`, etc.).

**`README.md`** — local-only ESP-IDF build path:

```markdown
# <Concept title> firmware (ESP-IDF)

## Build prerequisites

Install ESP-IDF 5.1+:
- macOS / Linux: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/
- Or via the VS Code "ESP-IDF" extension.

## Build

```
idf.py set-target esp32s3
idf.py build
```

## Flash

```
idf.py flash monitor
```

(or use `firmware-deploy` from this plugin chain.)
```

### 5. Save and hand off

Once generation completes:

1. Write every file to `<workspace>/source/` (creating subdirectories
   as needed).
2. Tell the user the file count + total line count for transparency:

   > "Done. Wrote *N* files (~*M* lines) to `<workspace>/source/`."

3. Hand off, in their language:

   > "Run `firmware-build` next to compile this into a `.bin` you can
   > flash. The build will read this `source/` folder."

The folder structure after this stage:

```
<workspace>/
├── concept.md
├── references/         ← optional reference library (user + skills)
├── spec/
│   └── (4 files)
├── ui/                 ← optional (present when firmware-ui ran)
├── source/
│   └── (toolchain-specific tree)
└── tmp/                ← optional scratch space (safe to delete)
```

`firmware-build` (next stage) will produce `<workspace>/build/` next
to `source/`.

## Hardware catalog handling

The catalog at `../../shared/hardware-catalog.md` is the single
source for hardware facts the generated code depends on.

- **Catalog populated** (the normal state): pull module names, chip
  names, pin maps, I²C addresses, library recommendations directly.
  Do not infer or guess.
- **Catalog placeholder** (frontmatter present but body is TODO):
  codegen cannot produce correct firmware without chip + pin facts.
  Stop and tell the user:

  > "Heads up: the public hardware catalog hasn't been filled yet, so
  > I can't generate correct firmware (chip names, pin assignments,
  > and library picks all live in the catalog). Come back when the
  > catalog is populated, and the codegen will work."

  Don't try to generate "best-effort" code — better to stop than to
  produce code that won't compile or will run on the wrong pins.

## Forbidden behaviors

- Do not invent modules, chips, pin numbers, library names, or
  capabilities that aren't in the catalog or the spec.
- Do not produce stubs / `// TODO: implement` for any MVP feature
  listed in `requirements.md §1`. Every MVP feature gets a real
  implementation. (`Nice-to-have` features from `requirements.md §2`
  may be left as small stubs with a clear comment, since they're
  explicitly post-MVP.)
- Do not put more than one question in a single turn. The only
  front-door question this skill asks by default is (§1) "where's the
  spec?" (only if the spec folder is missing) — the toolchain (§2) is
  now decided silently, never asked. The spec-contradiction questions
  below (missing module for a required feature, POWER_BTN misuse,
  uncalibrated-IMU precision ask) are conditional exceptions that
  surface only when triggered, and each still stays to one question.
- Do not generate code for both Arduino and ESP-IDF in the same run.
  One toolchain per session.
- Do not include third-party online build services, simulators, or
  unreleased hosted services in `source/README.md`. The README
  promises only the local build path with the chosen toolchain.
- Do not silently skip MVP features the user said matter. If a
  feature in `requirements.md §1` references a module that's not in
  `parts-list.md`, surface that contradiction back to the user before
  generating code (one question only — "Feature X needs module Y
  but your parts list doesn't have it. Add module Y, drop feature X,
  or do something else?").
- Do not wire POWER_BTN long-press to any firmware handler on
  Core_ESP32_1.0. POWER_BTN long-press (≥ ~2 s) is a hardware-fixed
  power toggle (off when on, on when off) handled by the PMIC; the
  firmware callback never fires in either direction. If the spec asks
  for POWER long-press as a UI gesture, treat it as a spec
  contradiction (same flow as the missing-module case above) and
  surface it back before code generation. Short-press handlers on
  POWER_BTN are fine; long-press handlers on any other button
  (SELECT / BTN_L1 / BTN_R2 / D-pad) are fine. See the
  `../../shared/hardware-catalog.md` Core_ESP32_1.0 POWER_BTN note.
- Do not emit IMU code that assumes calibrated absolute readings on
  cold-start units (e.g. "tilt > 0.5 °" thresholds, motion-energy
  integration, gesture matching against a reference template) unless
  `requirements.md` explicitly schedules per-unit IMU calibration
  (a six-face tumble routine writing offset/scale to NVS) as a setup
  feature. Default IMU code should treat readings as ship-level
  baseline only — orientation-class detection, fall detection, step
  count, ±5 ° tilt UX. If the spec demands sub-degree precision
  without the calibration step, surface the contradiction back same
  flow as above. See `../../shared/hardware-catalog.md` QMI8658A
  "Calibration policy".

## Tone

The user trusted you with a spec and is expecting a project that
builds and runs. Be confident, decisive, and concrete. Sound like a
senior firmware engineer who's read the catalog, picked the right
libraries, and is briefing the user on what's about to land in
`source/`. Avoid jargon and corporate softness in equal measure.

## Reference files

- `references/arduino-template/` — *(if present)* a worked PlatformIO
  project skeleton matching the layout in §4 Arduino branch. Use it
  to seed your generation rather than building file structure from
  scratch. If absent, fall back to the structure described in §4.
- `references/esp-idf-template/` — *(if present)* the equivalent
  ESP-IDF skeleton.
- `references/bringup-template/` — *(if present)* the minimal Arduino
  **bring-up self-test** (Operating Principle 9): I²C scan + asymmetric
  display test pattern + button echo over serial, no features. The user
  flashes this FIRST and confirms the board comes up before you generate
  the full firmware.
- `references/esp-idf-bringup-template/` — *(if present)* the ESP-IDF
  bring-up self-test (Operating Principle 9), the counterpart of
  `bringup-template/` for the IDF path, at parity: `printf` boot banner over
  UART0 + I²C scan + `esp_lcd` ST7789 asymmetric test pattern + AW9523 raw
  port-0 button echo. **HW-validated** (Core ESP32-S3 rev v0.2) — it proves
  IDF's bootloader boots the board, the console is on UART0, the bus
  enumerates, and the ST7789 comes up over `esp_lcd` upright with correct
  colors. Use it when the toolchain is ESP-IDF.
- `references/example-codegen/` — *(if present)* a complete worked
  example paired with the brainstorm + spec examples (LoRa Hike Buddy
  Locator). All ten modules are implemented in full — this is the
  fidelity bar for "real implementation, not stubs" (Operating
  Principle 2). Read it for tone, depth, structure, and what a full
  codegen output looks like end to end.
- `../../shared/aw9523-driver-patterns.md` — I/O-expander init / read /
  matrix-scan / INT / bus-recovery patterns (Operating Principle 7).
- `../../shared/module-detection-and-safe-boot.md` — the boot-time
  module verification contract (Operating Principle 7 §7.4): probe
  order, the frozen `[INFO] [HW] modules: ...` serial line, the
  verdict rule table, the safe-mode park pin set, and the SD rule.
  **Required reading before touching `hw_init.cpp`'s module-detection
  section, the ESP-IDF template's equivalent in `main.c`, or any
  Expand module's safe-mode gating** — this check is baked into every
  idea-lane firmware, not optional per-firmware guidance.
- Cross-cutting engineering patterns under `../../shared/` (Operating
  Principle 8): `esp32-bringup-and-rtos-patterns.md`,
  `display-and-lvgl-gotchas.md`, `connectivity-patterns.md`,
  `persistence-patterns.md`, `realtime-audio-patterns.md`. Read the ones
  that apply to the firmware you're generating.
