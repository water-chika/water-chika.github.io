---
title: Enable HDR for PRAGMATA on Steam Linux
---

# Enable HDR for PRAGMATA on Steam Linux

PRAGMATA needs a complete HDR path. Wine must report a 10-bit Advanced Color display, Gamescope must expose HDR Vulkan formats, and Gamescope must drive the physical display in HDR.

This procedure was verified with:

- official Proton 11 or Proton Experimental;
- Proton's default X11/Xwayland path;
- standalone DRM Gamescope on another virtual terminal;
- an HDR-capable display with HDR enabled.

> **Keep Proton on Xwayland.** Do not set `PROTON_ENABLE_WAYLAND=1` for this procedure. Valve's X11 driver propagates the HDR monitor state PRAGMATA checks; native Wine Wayland does not currently provide the equivalent path.

## 1. Prepare Steam and the display

1. Enable HDR in the monitor's own controls.
2. Install current Steam, Gamescope, Mesa/Vulkan drivers, and Vulkan tools.
3. Open **Steam → PRAGMATA → Properties → Compatibility**.
4. Select official Proton Experimental or Proton 11.
5. Close any Steam client already running on the desktop before starting the standalone session.

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

## 4. Launch PRAGMATA

Launch PRAGMATA from the Steam interface running inside Gamescope. This ensures the game inherits the HDR environment and Gamescope socket.

Open the game's display settings and enable HDR.

When finished, exit PRAGMATA and Steam. Gamescope should return to the terminal. Switch back to the desktop VT with **Ctrl+Alt+F1**, or the VT used by the desktop session.

## Ray tracing and path tracing

PRAGMATA uses DirectX 12 through VKD3D-Proton. On a supported GPU, the Vulkan driver must expose:

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

A verified RX 9070 XT/RADV run exposed all three extensions and feature bits. The `config.ini` beside the active Steam App ID 3357650 installation also recorded:

```ini
Capability=DirectX12
RayTracing=ON
PathTracing=ON
```

Check the file from the same Steam library and installation that launched the running process; another library or an old copy may contain stale settings.

If the game's UI still says ray tracing cannot be enabled while the active configuration records it as on, the remaining possibilities include stale UI capability state or an engine fallback after startup. A configuration value, visual difference, or performance change can support a diagnosis but does not prove that rays are being traced. Use an authoritative runtime log or API/GPU capture to confirm effective ray or path tracing.

Do not add `PROTON_ENABLE_NVAPI` on an AMD GPU. The baseline requirement is DirectX 12, a recent official Proton/VKD3D-Proton build, and a Vulkan driver exposing the RT extensions.

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
2. configure a display/session launcher that enters through PAM/logind;
3. if HDR support permits it, keep Gamescope in the existing desktop session where PipeWire already owns the devices.

For a Bluetooth headset, use **A2DP** for game playback. Opening Steam Voice Settings may request microphone capture and make WirePlumber switch the headset to the lower-quality HFP/HSP profile. Disable automatic headset-profile switching if that behavior is unwanted, and use a separate microphone for voice capture.

## Verify the HDR path

A brighter image alone does not prove that the game created an HDR swapchain. Check each layer.

### Display

The monitor should enter its HDR mode. This confirms the output signal, but does not by itself prove that PRAGMATA requested HDR.

### Gamescope

The terminal should identify the intended connector and print:

```text
HDR output enabled
```

There should be no DRM-master, seat, or output-fallback error.

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

Confirm the game is using DirectX 12 through VKD3D-Proton and that the Vulkan device selected by the actual process exposes the acceleration-structure, ray-query, and ray-tracing-pipeline extensions and feature bits. If the active installation's `config.ini` says `RayTracing=ON` or `PathTracing=ON`, use an authoritative runtime log or API/GPU capture to verify effective rendering rather than relying on the setting, image, or performance alone.

## Upstream references

- [Valve Gamescope](https://github.com/ValveSoftware/gamescope)
- [Gamescope WSI HDR implementation](https://github.com/ValveSoftware/gamescope/blob/master/layer/VkLayer_FROG_gamescope_wsi.cpp)
- [Valve Wine X11 HDR propagation](https://github.com/ValveSoftware/wine/commit/d33f47c489fcfb7d55c10cc53c0f4ed00b72ae49)
- [Official Proton Experimental 11](https://github.com/ValveSoftware/Proton/tree/experimental_11.0)
- [Wine Advanced Color query](https://github.com/ValveSoftware/wine/blob/5b557605b4e51f0853ec8e0e4f0eb536c669fae3/dlls/win32u/sysparams.c#L8079-L8115)
