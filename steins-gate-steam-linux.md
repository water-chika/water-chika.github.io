---
title: Fix STEINS;GATE Not Launching on Steam Linux
---

# Fix STEINS;GATE Not Launching on Steam Linux

Last verified: **2026-11-19**.

This guide covers the original **STEINS;GATE**, Steam App ID **412830**, running through Proton on an AMD GPU.

## Symptom

Steam briefly shows STEINS;GATE as running, but no game window appears. The process exits after a few seconds. Reinstalling the game or recreating the Proton prefix does not fix it.

STEINS;GATE launches `Launcher.exe` first. If the launcher cannot initialize Direct3D, it exits before starting `Game.exe`.

## Root cause

Both executables are 32-bit Windows programs:

```text
Launcher.exe: PE32, Intel i386
Game.exe:     PE32, Intel i386
```

The launcher imports `d3d9.dll`, and the Proton log confirmed that DXVK loaded its Direct3D 9 path for `Launcher.exe`. DXVK therefore needs a **32-bit Vulkan driver**, even on a 64-bit Linux installation.

On the affected AMD system, the 64-bit RADV driver and 32-bit Vulkan loader were installed, but the actual 32-bit RADV driver was missing:

```text
vulkan-radeon            installed
lib32-vulkan-icd-loader  installed
lib32-vulkan-radeon      missing
```

The Proton log showed the exact failure:

```text
Game: Launcher.exe
DXVK: v3.1.1
Failed to enumerate physical devices, res -3
DxvkInstance::createInstance: Failed to create Vulkan instance
```

Without a 32-bit Vulkan physical device, DXVK cannot initialize for the launcher. The executable contains an `Initialization of DirectX has been failed.` error path, and the observed process closed immediately after the Vulkan initialization failure.

## Fix on Arch Linux

Install the 32-bit AMD Vulkan driver from the multilib repository as part of a normal full-system upgrade:

```sh
sudo pacman -Syu lib32-vulkan-radeon
```

Arch Linux does not support partial upgrades. If repository and installed Mesa versions differ, update the system rather than manually downgrading one driver package. Verify the resulting packages:

```sh
pacman -Q vulkan-radeon lib32-vulkan-radeon lib32-vulkan-icd-loader
```

A working installation includes the 32-bit driver library:

```sh
ls -l /usr/lib32/libvulkan_radeon.so
```

For other GPUs, install the corresponding 32-bit Vulkan implementation supplied by the distribution rather than `lib32-vulkan-radeon`.

## Launch the game

Select an official recent Proton release or Proton Experimental in:

**Steam → STEINS;GATE → Properties → Compatibility**

Then launch the game normally. The first attempt after a reinstall or prefix reset may only perform prerequisite setup. On the verified run, Steam's install-script evaluator populated the prefix with legacy DirectX helper libraries and XAudio/XACT components before it attempted the launcher. Wait for that installer to complete and launch the game again.

A successful sequence is:

1. Steam completes `ProcessingInstallScript`.
2. `Launcher.exe` starts and remains open.
3. Select the desired resolution and options in the launcher.
4. Press **Launch Game** to start `Game.exe`.

## Verify the fix

Find the launcher process:

```sh
pgrep -a Launcher.exe
```

Confirm that it mapped the 32-bit RADV driver:

```sh
pid=$(pgrep -n -x Launcher.exe) || {
  echo "Launcher.exe is not running" >&2
  exit 1
}
grep libvulkan_radeon "/proc/$pid/maps"
```

The working process should reference a 32-bit library path such as:

```text
/run/host/usr/lib32/libvulkan_radeon.so
```

This mapping proves that the 32-bit ICD was loaded. Confirm successful Vulkan initialization separately with a fresh Proton log. Temporarily set this Steam launch option:

```text
PROTON_LOG=1 %command%
```

Launch and exit the game once, then inspect the newly written `steam-412830.log` in your home directory. Remove the temporary logging option afterward.

The fresh log should no longer contain:

```text
Failed to enumerate physical devices
Failed to create Vulkan instance
```

## Troubleshooting

### Steam remains on ProcessingInstallScript

After a fresh prefix is created, Steam's install-script evaluator installs legacy DirectX helper libraries and XAudio/XACT components for STEINS;GATE. Let the tracked prerequisite installer finish before launching again.

### Launcher opens but Game.exe does not

Use the launcher's **Launch Game** button. Steam starts `Launcher.exe` by design; the launcher is responsible for starting `Game.exe` after saving its settings.

Check the game-specific Proton prefix and saves under Steam App ID 412830. Do not delete the prefix until cloud or local saves are accounted for.

### The same Vulkan error remains

Confirm all of the following:

- the game is using the expected GPU;
- the distribution's 32-bit Vulkan driver is installed, not only the loader;
- the driver architecture matches the 32-bit game;
- Steam's pressure-vessel container can see the host 32-bit driver;
- the 32-bit and 64-bit Mesa packages are compatible versions.

### NVIDIA or Intel systems

Install the distribution's matching 32-bit Vulkan driver for that vendor. The package name and multilib setup differ from AMD/Arch Linux.

## Summary

A 64-bit Vulkan setup can run modern 64-bit games while silently failing older 32-bit DXVK titles. For STEINS;GATE on an AMD Arch Linux system, the required fix was:

```sh
sudo pacman -Syu lib32-vulkan-radeon
```

After installation, `Launcher.exe` initialized DXVK, loaded the 32-bit RADV driver, and remained running normally.
