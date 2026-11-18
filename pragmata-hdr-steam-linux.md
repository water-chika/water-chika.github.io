---
title: Enable HDR for PRAGMATA on Steam Linux
---

# Enable HDR for PRAGMATA on Steam Linux

PRAGMATA needs a complete HDR path. Wine must report a 10-bit Advanced Color display, Gamescope must expose HDR Vulkan formats, and Gamescope must drive the physical display in HDR.

Last verified: **2026-11-19**.

Verified test configuration:

- PRAGMATA Steam App ID 3357650, build 24543093;
- official Proton Experimental;
- Proton's default X11/Xwayland path;
- Gamescope 3.17.0 in standalone DRM mode on another virtual terminal;
- Mesa RADV 26.2.7 on an AMD Radeon RX 9070 XT;
- an HDR-capable display with HDR enabled.

The game build, GPU, connector, resolution, refresh rate, audio device, and keyboard layout are machine-specific. Discover and substitute the values for your system.

> **Keep Proton on Xwayland.** Do not set `PROTON_ENABLE_WAYLAND=1` for this procedure. Valve's X11 driver propagates the HDR monitor state PRAGMATA checks; native Wine Wayland does not currently provide the equivalent path.

## 1. Prepare Steam and the display

1. Enable HDR in the monitor's own controls.
2. Install current Steam, Gamescope, Mesa/Vulkan drivers, and Vulkan tools.
3. Open **Steam → PRAGMATA → Properties → Compatibility**.
4. Select official Proton Experimental or Proton 11.
5. Shut down Steam before starting the standalone session:

   ```sh
   steam -shutdown
   ```

6. Verify that no Steam client or helper processes remain. Otherwise `steam -gamepadui` inside Gamescope can forward to the existing desktop singleton and exit, causing Gamescope to report `Primary child shut down!`.

Start with an official Proton build. Custom builds add another variable when diagnosing display behavior.

## 2. Find the connected DRM output

Connector names differ by GPU, port, and machine. Read the live DRM state instead of copying a connector name such as `DP-1`:

```sh
for status in /sys/class/drm/card*-*/status; do
  printf '%s: %s\n' "$status" "$(cat "$status")"
done
```

Use the connected connector and a resolution and refresh rate supported by the display. Start at a conservative refresh rate if the maximum mode causes link loss.

## 3. Start standalone HDR Gamescope

Save your work, switch to another virtual terminal such as **Ctrl+Alt+F2**, and log in. Substitute the connector and mode found above:

```sh
DXVK_HDR=1 \
ENABLE_HDR_WSI=1 \
ENABLE_GAMESCOPE_WSI=1 \
GAMESCOPE_ZENITY_DISABLE=1 \
XDG_CURRENT_DESKTOP=gamescope \
DISABLE_VK_LAYER_LUNARG_override=1 \
gamescope \
  --backend drm \
  --prefer-output <connector> \
  -W <width> -H <height> \
  -r <refresh> \
  -f -e --hdr-enabled \
  -- steam -gamepadui
```

Example for `DP-1` at 3840×2160 and 120 Hz:

```sh
DXVK_HDR=1 ENABLE_HDR_WSI=1 ENABLE_GAMESCOPE_WSI=1 \
GAMESCOPE_ZENITY_DISABLE=1 XDG_CURRENT_DESKTOP=gamescope \
DISABLE_VK_LAYER_LUNARG_override=1 \
gamescope --backend drm --prefer-output DP-1 \
  -W 3840 -H 2160 -r 120 -f -e --hdr-enabled \
  -- steam -gamepadui
```

Each switch controls a different part of the path:

| Setting | Purpose |
| --- | --- |
| `DXVK_HDR=1` | On Proton's Xwayland path, lets Wine report the synthetic Windows monitor as HDR-capable. PRAGMATA's Advanced Color query can then report HDR support, HDR enabled, and 10 bits per channel. |
| `ENABLE_GAMESCOPE_WSI=1` | Activates the Gamescope WSI layer, which exposes HDR10/ST.2084 Vulkan surface formats and forwards HDR metadata. |
| `--hdr-enabled` | Tells Gamescope to drive the selected DRM output in HDR. Without it, an HDR client may be tone-mapped to SDR. |
| `ENABLE_HDR_WSI=1` | Retained for compatibility with Proton/Gamescope HDR launch conventions used by current installations. |
| `GAMESCOPE_ZENITY_DISABLE=1` and `XDG_CURRENT_DESKTOP=gamescope` | Disable Gamescope message-box helpers and select Steam's Gamescope-specific error-dialog behavior. This prevents a Zenity/WSI recursion that can create thousands of processes and exhaust system memory. |
| `DISABLE_VK_LAYER_LUNARG_override=1` | Prevent a per-user vkconfig override from injecting Vulkan validation into Gamescope. Validation noise is unnecessary for normal play and incompatible layer combinations can crash Gamescope. |

If validation is still injected, also try:

```sh
export VK_LOADER_LAYERS_DISABLE=VK_LAYER_LUNARG_override,VK_LAYER_KHRONOS_validation
```

Alternatively, prefix the Gamescope command with the assignment or add it as a systemd `Environment=` value.

For a reusable launcher, place it in a constrained systemd unit or scope. A practical upper bound is `TasksMax=512`, with `MemoryMax`, `MemorySwapMax`, `OOMPolicy=kill`, and `KillMode=control-group` chosen for the machine. These limits contain a launcher or dialog recursion instead of allowing a system-wide OOM.

## 4. Launch PRAGMATA

Launch PRAGMATA from the Steam interface running inside Gamescope. This ensures the game inherits the HDR environment and Gamescope socket.

Open the game's display settings and enable HDR.

When finished, exit PRAGMATA and Steam. Gamescope should return to the terminal. Switch back to the desktop VT with **Ctrl+Alt+F1**, or the VT used by the desktop session.

## Ray tracing and path tracing

PRAGMATA deliberately hides its ordinary ray-tracing option when it detects Wine. Add this Steam launch option to bypass that game-specific gate:

```text
%command% /WineDetectionEnabled:False
```

When launching by Steam App ID, the equivalent argument is:

```sh
steam -applaunch 3357650 /WineDetectionEnabled:False
```

This only exposes the option; the renderer still needs DirectX 12 through VKD3D-Proton and a Vulkan RT-capable device. On a supported GPU, the Vulkan driver must expose:

- `VK_KHR_acceleration_structure`;
- `VK_KHR_ray_query`;
- `VK_KHR_ray_tracing_pipeline`.

As a preliminary host check, inspect the complete `vulkaninfo` output without stripping its physical-device headings:

```sh
vulkaninfo --summary
vulkaninfo | less
```

For the GPU you intend to use, confirm all three extension names and the corresponding feature booleans: `accelerationStructure = true`, `rayQuery = true`, and `rayTracingPipeline = true`. On a multi-GPU system, a bare grep can mix results from different devices.

This host check is not proof of the device or ICD selected inside Steam's pressure-vessel container. Confirm the GPU used by the actual PRAGMATA process through a VKD3D/Proton runtime log or an API/GPU capture. If Gamescope composes on the wrong GPU, its `--prefer-vk-device` option can select the compositor device, but the game's own device selection must be verified separately.

A verified RX 9070 XT/RADV run exposed all three extensions and feature bits, reported D3D feature level 12_2, Shader Model 6.8, and DXR 1.1, and retained `RayTracing=ON` in the active installation's `config.ini`.

### Path tracing is experimental

Do not treat `PathTracing=ON` as a supported AMD setup. In a normal run, PRAGMATA rewrote a forced `PathTracing=ON` value back to `PathTracing=OFF` while leaving ordinary ray tracing enabled.

`VKD3D_CONFIG=enable_experimental_features` exposed Work Graphs Tier 1.0 in a controlled probe and allowed `PathTracing=ON` to persist in one A/B run. It did not prove that PRAGMATA dispatched or rendered its path-tracing pipeline. Shader Execution Reordering was unavailable in the tested stack, and `VKD3D_CONFIG=dxr12` did not change the result.

Treat path tracing through this experimental flag as an investigation, not a recommended launch recipe. Check the configuration from the same Steam library and installation that launched the process, then use an authoritative runtime log or API/GPU capture to prove effective rendering. A configuration value, image difference, or performance change is supporting evidence only.

Do not add `PROTON_ENABLE_NVAPI` on an AMD GPU. The baseline requirement for ordinary RT is the Wine-detection bypass, DirectX 12, a recent official Proton/VKD3D-Proton build, and a Vulkan driver exposing the RT extensions.

## Audio in a standalone VT session

Proton forwards audio through PipeWire/PulseAudio into its pressure-vessel container. Diagnose the host and container sides separately:

1. On the host, check whether WirePlumber/PipeWire still lists the expected physical sink. If the host itself shows only **Dummy Output**, fix session and device ownership first.
2. If host playback works but PRAGMATA does not, inspect the `PULSE_SERVER` or PipeWire/PulseAudio socket forwarded into Steam's pressure-vessel container. A missing, stale, or inaccessible socket is a separate container-routing failure.

For the verified host-side failure, launching standalone Gamescope outside a genuine logind/PAM login caused the physical devices to disappear. Avoid constructing the session with a chain such as:

```text
openvt -> su -> dbus-run-session -> gamescope
```

That chain can put Gamescope on the VT without creating a proper logind user session. When the VT becomes active, WirePlumber may lose access to `/dev/snd`, physical devices can disappear, and PRAGMATA audio is routed to Dummy Output.

Use one of these approaches:

1. switch to a real login prompt on the target VT, log in normally, and start Gamescope there;
2. configure a transient or persistent systemd service with `User=<user>`, `PAMName=login`, `TTYPath=/dev/tty2`, TTY standard input/output/error, and a matching `UtmpIdentifier`, then switch to that VT;
3. if HDR support permits it, keep Gamescope in the existing desktop session where PipeWire already owns the devices.

The PAM/logind service approach was verified to register a `login` session on `seat0`, retain physical audio access, and keep game audio on the selected headset. Apply the task and memory limits described above to the service.

For a Bluetooth headset, use **A2DP** for game playback. Opening Steam Voice Settings may request microphone capture and make WirePlumber switch the headset to the lower-quality HFP/HSP profile. Disable automatic headset-profile switching if that behavior is unwanted, and use a separate microphone for voice capture.

A correct logind session does not reconnect a headset that was already disconnected. Before launch, use `bluetoothctl info` to confirm that it is connected and `wpctl status` to confirm that the expected A2DP sink exists instead of Dummy Output.

## Keyboard layout in Gamescope

Gamescope's physical-keyboard layout is separate from running `setxkbmap` inside Xwayland. Set the standard XKB environment before Gamescope starts:

```sh
export XKB_DEFAULT_LAYOUT=<layout-list>
export XKB_DEFAULT_VARIANT=<variant-list>
export XKB_DEFAULT_OPTIONS=<options>
```

Export these values in the shell that starts Gamescope, prefix them to the Gamescope command, or configure them as systemd `Environment=` entries.

For example, a two-layout configuration can use comma-separated layouts and variants plus a group-toggle option. Choose values that match your system rather than copying another machine's layout. A live override can be applied with `gamescopectl xkb_layout <layout>`, but restarting only PRAGMATA may not reload Gamescope's keyboard map.

## Verify the HDR path

A brighter image alone does not prove that the game created an HDR swapchain. Check each layer.

### Display

The monitor should enter its HDR mode. This confirms the output signal, but does not by itself prove that PRAGMATA requested HDR.

### Gamescope

The terminal should identify the intended connector and print:

```text
HDR output enabled
```

A single transient `drmModeAtomicCommit: Permission denied` can occur during VT/seat handoff even when Gamescope recovers. Judge the final state rather than one isolated line. Xwayland should remain running, and Gamescope's root properties should report:

```text
GAMESCOPE_DISPLAY_HDR_ENABLED=1
GAMESCOPE_HDR_OUTPUT_FEEDBACK=1
GAMESCOPE_DISPLAY_SUPPORTS_HDR=1
```

Persistent DRM-master, seat, or output-fallback errors still indicate a failed session.

### Windows API and game

PRAGMATA should offer its HDR option. A deeper Wine probe of `DISPLAYCONFIG_DEVICE_INFO_GET_ADVANCED_COLOR_INFO` should report:

```text
advancedColorSupported = 1
advancedColorEnabled   = 1
bitsPerColorChannel    = 10
```

## Troubleshooting

### PRAGMATA still says HDR is unsupported

Confirm that the game process inherited:

```text
DXVK_HDR=1
ENABLE_HDR_WSI=1
ENABLE_GAMESCOPE_WSI=1
```

Use official Proton 11 or Experimental, remove `PROTON_ENABLE_WAYLAND`, and launch the game from the Steam instance inside Gamescope.

### Gamescope cannot acquire the seat or DRM master

Run Gamescope from a real local VT with an active login session. Ensure another compositor does not still own the target output. Verify that the distribution's logind or seatd configuration grants access to DRM and input devices.

### Black screen or connector not found

Rediscover the connector and test a lower refresh rate such as 60 or 120 Hz. Check whether the requested resolution, refresh rate, bit depth, cable, and port fit within the link bandwidth.

### HDR looks washed out

Confirm that PRAGMATA enabled HDR rather than presenting SDR inside an HDR output. Check full/limited range and the monitor's tone-mapping settings.

Do not use `--hdr-debug-force-support` as proof of working HDR. Gamescope can advertise support while the final output remains SDR.

### The game opens on the normal desktop

The wrong Steam process handled the launch. Exit desktop Steam, start Steam inside standalone Gamescope, and then launch PRAGMATA from that instance.

### Audio uses Dummy Output

First check the host. If WirePlumber no longer sees physical sinks, verify the active login session and access to `/dev/snd`. If the session was started with `openvt` and `su`, exit it and log in normally on the VT through PAM/logind before starting Gamescope again.

If normal host applications can use the expected sink, check the audio server/socket visible to the Steam pressure-vessel container and PRAGMATA process. Host session ownership and container socket forwarding are separate failure points.

### A Bluetooth headset switches to low-quality audio

Steam or another application probably opened microphone capture and triggered HFP/HSP. Return the headset to A2DP for playback, prevent automatic profile switching if appropriate for the desktop, and select a separate microphone for capture.

### Ray tracing is unavailable or has no visible effect

Confirm that `/WineDetectionEnabled:False` reaches PRAGMATA, that the game is using DirectX 12 through VKD3D-Proton, and that the Vulkan device selected by the actual process exposes the acceleration-structure, ray-query, and ray-tracing-pipeline extensions and feature bits. If the active installation's `config.ini` says `RayTracing=ON`, use an authoritative runtime log or API/GPU capture to verify effective rendering rather than relying on the setting, image, or performance alone.

Do not present a forced `PathTracing=ON` value as working path tracing. The default AMD/Proton path resets it to off, and the experimental VKD3D feature path remains unverified.

### Steam or Gamescope suddenly spawns many dialogs or processes

Stop the session before it exhausts memory. Confirm `GAMESCOPE_ZENITY_DISABLE=1` and `XDG_CURRENT_DESKTOP=gamescope` reached Steam. Do not rely on an empty `STEAM_ZENITY`; current Steam startup code can overwrite it. Use a systemd task/memory limit so a future recursion is contained.

### Gamescope prints Vulkan validation errors or crashes in a validation layer

Disable the vkconfig override with `DISABLE_VK_LAYER_LUNARG_override=1`. If needed, set `VK_LOADER_LAYERS_DISABLE=VK_LAYER_LUNARG_override,VK_LAYER_KHRONOS_validation`. Do not disable the Gamescope WSI layer required for HDR.

## Upstream references

- [Valve Gamescope](https://github.com/ValveSoftware/gamescope)
- [Gamescope WSI HDR implementation](https://github.com/ValveSoftware/gamescope/blob/master/layer/VkLayer_FROG_gamescope_wsi.cpp)
- [Valve Wine X11 HDR propagation](https://github.com/ValveSoftware/wine/commit/d33f47c489fcfb7d55c10cc53c0f4ed00b72ae49)
- [Official Proton Experimental 11](https://github.com/ValveSoftware/Proton/tree/experimental_11.0)
- [Wine Advanced Color query](https://github.com/ValveSoftware/wine/blob/5b557605b4e51f0853ec8e0e4f0eb536c669fae3/dlls/win32u/sysparams.c#L8079-L8115)
- [PRAGMATA Wine-detection RT workaround](https://steamcommunity.com/app/3357650/discussions/0/796715497279450892/)
- [VKD3D-Proton configuration reference](https://github.com/HansKristian-Work/vkd3d-proton#environment-variables)
- [PRAGMATA path-tracing crash tracking](https://github.com/HansKristian-Work/vkd3d-proton/issues/2949)
