---
layout: hardware-spec
title: Hardware Compatibility Specification | RDK9
nav: hardware
footer: true
hero:
    eyebrow: PLATFORM REQUIREMENTS
    title: Hardware Compatibility Specification
    description: Specifications that outline the minimal hardware configurations to run Core RDK
    status: Submitted to RTAB, RDKDEV-1741 open
---

This Hardware Compatibility Specification defines the minimum hardware configuration required to build, deploy, and reliably operate Core RDK on IP-based RDK-V Set-Top Boxes (STBs). It establishes baseline requirements for SoC and CPU capability, graphics, video and audio decode, content protection, system memory, flash storage, connectivity, peripherals, and power.

### Deployment Profiles

| Tier | Profile | Description |
|------|---------|-------------|
| Tier1 | FHD | Cost-optimized 1080p Core RDK device for standard OTT services |
| Tier2 | 4K Premium | 4K UHD device supporting HDR, premium video, and enhanced application workloads |

### System Overview

The STB is a media-streaming and application host device that connects to a television through HDMI and to the home network through Wi-Fi or Ethernet. All hardware compatibility requirements defined in this specification are aligned to the Tier 1 (FHD) and Tier 2 (4K Premium) deployment profiles.

!!! note "Note"
    Requirements are expressed as capability and performance classes rather than specific vendor components. Any SoC and platform meeting the stated capabilities, driver support, and RDK HAL/API behavior qualifies. Named CPU cores, GPUs, and chipsets are provided as informative examples only.

---

### Hardware Compatibility Baseline Specification Matrix

!!! info "Info"
    The compatibility matrix is intended for quick platform assessment. Meeting numeric hardware minimums alone does not guarantee compatibility. A compatible platform must satisfy the required capabilities, peripherals, driver support, firmware, and RDK HAL/API behavior defined in the referenced sections.

| Category | Tier 1 (FHD) | Tier 2 (4K Premium) | View Details |
|-----------|--------------|---------------------|-------------|
| Processor |ARMv8-A or newer 64-bit (AArch64) quad-core performance class or equivalent, ≥ 1.5 GHz sustained;   OpenGL ES 3.2 GPU; hardware TEE | ARMv8-A or newer 64-bit (AArch64) quad-core performance class or equivalent, ≥ 1.5 GHz sustained; OpenGL ES 3.2 GPU with Vulkan 1.3/1.4 recommended; hardware TEE | [View Details](#processor-soc--cpu) |
| Video Decode |Video Decode	H.264 and HEVC up to 1080p60; VP9 and AV1 recommended; 1 × FHD stream | H.264 up to 1080p60 and 4K30; HEVC Main10, VP9 Profile 2, and AV1 up to 4K60; 1 × 4K stream | [View Details](#video-decoder-capability) |
| HDR & Video Output | 1080p60; HDMI 1.4b or later; HDR optional |4K60; HDMI 2.0b or later; HDR10 and HLG required | [View Details](#video-decoder-capability) |
| Audio | AAC-LC/HE-AAC and PCM required; AC-3 and E-AC-3 require hardware or licensed software decode, plus HDMI passthrough where supported by the connected sink (Dolby license and certification cost applies, including on Tier 1); Atmos (DD+ JOC) passthrough and MPEG-H optional; 5.1 HDMI with stereo downmix; ± 40 ms A/V sync | Same as Tier 1 | [View Details](#audio-decoder-capability) |
| Security & Content Protection | Secure boot with hardware root of trust, TEE, Widevine L1, PlayReady SL3000, anti-rollback, debug lockdown, per-device keys; HDCP 1.4 minimum (2.2 recommended) | Same as Tier 1, with HDCP 2.2 minimum (2.3 recommended) | [View Details](#content-protection-and-secure-boot) |
| Memory | ≥ 1 GB provisional; DDR4, LPDDR4X, or newer at ≥ 1600 MT/s with ≥ 16-bit bus (≥ 3.2 GB/s peak); ≥ 0.6 GB for applications after reserves; optional 256 MB zRAM; RDK 9 FHD/1 GB validation required | ≥ 2 GB; LPDDR4X or newer at ≥ 3200 MT/s with ≥ 32-bit bus (≥ 12.8 GB/s peak); ≥ 1.2 GB for applications after reserves; optional 512 MB zRAM | [View Details](#memory-ram) |
| Storage (Flash) | 4 GB eMMC minimum; recovery + OTA at 4 GB; ≥ 2 GB free-space target| 4 GB eMMC minimum, 8 GB recommended; A/B recommended with 8 GB; ≥ 2 GB free-space target | [View Details](#storage-flash) |
| Network | 10/100 Ethernet; 802.11n 2.4 GHz Wi-Fi; ≥ 15 Mbps sustained application throughput; WPA2-PSK (AES) | 10/100 Ethernet (Gigabit recommended); dual-band 2.4/5 GHz Wi-Fi, ≥ 25 Mbps sustained; WPA2-PSK (AES), WPA3 where Wi-Fi 6/6E is implemented; Wi-Fi 6/6E recommended, Wi-Fi 7 future-ready | [View Details](#network-connectivity) |
| Peripheral & I/O | USB 2.0; IR receiver and IR remote; voice remote required; BLE 4.2+ transport required; reset/recovery button; status LED  | USB 2.0; IR receiver and IR remote; BLE 5.0+ voice remote required; reset/recovery button; status LED | [View Details](#peripheral-and-io-requirements) |
| Power | 5 V/2 A (10 W) minimum input; ≤ 5 W idle; ≤ 1 W standby | 5 V/2.4 A (12 W) minimum input; ≤ 5 W idle; ≤ 1 W standby | [View Details](#power-requirements) |
| Compliance | RDK, HDMI, DRM, regional regulatory, Wi-Fi, Bluetooth SIG, and OTT partner certifications  | Same as Tier 1  | [View Details](#regulatory-and-certification-requirements) |
| Application Platform | Launcher UI, sandboxed applications, OTA application and firmware updates | Same as Tier 1 | - |
| Software & Lifecycle | Core RDK support; OTA with rollback (A/B) or recovery-based failsafe update; factory recovery | Same as Tier 1 | - |
| Driver / Kernel Support |	Production-supported drivers for CPU/GPU, FHD codecs, HDMI, and radios on the target kernel	| Production-supported drivers for CPU/GPU, 4K/HDR codecs, HDMI, and radios on the target kernel | - |
| Firmware / Bootloader | Minimum bootloader and kernel versions compatible with the target Core RDK release | Same as Tier 1 | - |

---

### Processor (SoC / CPU)

The processor requirements establish the baseline computing and graphics capability required to support Core RDK software, multimedia processing, application execution, and platform services. The CPU instruction set is common to both tiers; tier differentiation is achieved through decode capability, HDR, memory, graphics features, and I/O.

<a id="processor-soc--cpu"></a>

| Parameter | Tier 1 (FHD) | Tier 2 (4K Premium) | Notes |
|------------|-------------|---------------------|-------|
| CPU performance class | ARMv8-A or newer, 64-bit, quad-core performance class or equivalent | ARMv8-A or newer, 64-bit, quad-core performance class or equivalent | Examples only: Cortex-A55 (Tier 1 and Tier 2); Cortex-A73-class cores may be used for higher Tier 2 application performance. ARMv8-A (AArch64) is the required processor architecture for compatible RDK-V deployments |
| Clock speed |	≥ 1.5 GHz sustained	| ≥ 1.5 GHz sustained| Sustained under thermal load, not burst |
| Instruction set | ARMv8-A or newer, 64-bit (AArch64) | ARMv8-A or newer, 64-bit (AArch64) | 32-bit-only SoCs are not supported |
| GPU |	OpenGL ES 3.2-capable GPU |	OpenGL ES 3.2-capable GPU; Vulkan 1.3/1.4 recommended |	OpenGL ES 3.2 is required on both tiers for UI and browser compositing (Westeros/WPE). Mali-G31 MP2 is an example only |
| Video decode (hardware) |	H.264/AVC and HEVC up to 1080p60; VP9 and AV1 recommended |	H.264/AVC up to 1080p60 and 4K30; HEVC Main10, VP9 Profile 2, and AV1 Main Profile up to 4K60 |	| 
|HDR support | Optional	 | HDR10 and HLG required |	Tied to the display pipeline and HDMI output, not the CPU alone |
| Security element | TEE (Arm TrustZone or equivalent) with hardware-backed DRM | TEE (Arm TrustZone or equivalent) with hardware-backed DRM | Widevine L1 and PlayReady SL3000 are required for secure DRM operation and protected media playback |

---

### Video Decoder Capability

The RDK-V STB shall provide hardware-accelerated decoding appropriate to its deployment tier. Tier 1 shall support FHD playback using H.264/AVC and HEVC up to 1080p60, with VP9 and AV1 recommended where required by the target application portfolio. Tier 2 shall support H.264/AVC, HEVC Main10, VP9 Profile 2, and AV1 Main Profile, with HEVC, VP9, and AV1 up to 4K60, together with secure playback and the HDR capabilities required by the target service certifications. AV1 is increasingly used by major streaming services for bandwidth-efficient premium delivery.

<a id="video-decoder-capability"></a>

| Capability | Tier 1 (FHD) | Tier 2 (4K Premium) | Notes |
|------------|-------------|---------------------|-------|
| H.264/AVC | Required up to 1080p60 | Required up to 1080p60 and 4K30 | |
| HEVC/H.265 | Main profile required up to 1080p60; Main10 recommended | Main10 required up to 4K60 | Main10 needed for HDR content |
| VP9 | Recommended, up to 1080p60 | Profile 2 (10-bit) required up to 4K60 | |
| AV1 Main Profile (8/10-bit) | Recommended, up to 1080p60 | Required up to 4K60 | Recommended for 2026+ streaming services; mandatory for the 4K Premium profile |
| HDR10 | Optional | Required | |
| HDR10+ | Optional | Optional | Tied to the display pipeline |
| HLG | Optional | Required | |
| Dolby Vision | Optional (platform/operator dependent) | Optional (platform/operator dependent) | Licensing and operator dependent |
| Secure DRM Playback | Widevine L1, PlayReady SL3000 | Widevine L1, PlayReady SL3000 | A secure video path is required for premium OTT certification programs |
| Concurrent Decode | 1× FHD stream | 1× 4K stream | Concurrent decode	1 × FHD stream	1 × 4K stream	Dual HD decode is optional and platform/operator dependent |

---

### Audio Decoder Capability

The RDK-V STB shall provide audio decoding and passthrough capabilities sufficient to support Core RDK media services and certification requirements for major OTT applications. Decoder support shall enable stereo and multichannel audio, broadcast-standard codecs, and lip-sync accuracy consistent with the video decode baseline. Audio requirements are identical for both tiers unless stated otherwise.

<a id="audio-decoder-capability"></a>

| Capability | Tier 1 | Tier 2 | Notes |
|------------|---------|---------|--------|
| AAC-LC / HE-AAC decode | Required, stereo and multichannel | Required, stereo and multichannel | Standard OTT audio codec baseline |
|Dolby Digital (AC-3) |	Required: hardware or licensed software decode, plus HDMI passthrough where supported by the connected sink | Required: hardware or licensed software decode, plus HDMI passthrough where supported by the connected sink | Decode is mandatory. HDMI passthrough is additionally required when supported by the connected sink and product output path. AC-3 and E-AC-3 decode (hardware or licensed software) typically carries Dolby license and certification cost, including on Tier 1 entry-level devices. Operators and SoC vendors should account for this cost in product planning |
|Dolby Digital Plus (E-AC-3) | Required: hardware or licensed software decode, plus HDMI passthrough where supported by the connected sink | Required: hardware or licensed software decode, plus HDMI passthrough where supported by the connected sink | 	|
| Dolby Atmos | Optional (DD+ JOC passthrough) | Optional (DD+ JOC passthrough) | Premium content; eARC on the sink improves support |
| MPEG-H 3D Audio (ISO/IEC 23008-3)	| Optional, LC Profile Level 3 | Optional, LC Profile Level 3 | LC Level 3 supports up to 12 loudspeaker channels (sufficient for 7.1.4) |
| PCM |	Required |	Required |	Baseline uncompressed audio |
| Multichannel output |	5.1 via HDMI; stereo downmix |	5.1 via HDMI; stereo downmix |	Downmix required when only a stereo sink is connected |
| Audio/video sync | ± 40 ms |	± 40 ms | Required for A/V sync certification |
| Sample rates	| 48 kHz required; 44.1 kHz supported | 48 kHz required; 44.1 kHz supported	| |

---

### Content Protection and Secure Boot

This section defines the minimum content protection, secure boot, and key management capabilities required to support DRM-protected playback and to prevent unauthorized extraction of firmware, keys, or protected content, building on the TEE baseline.

<a id="content-protection-and-secure-boot"></a>

| Capability | Tier 1 | Tier 2 | Notes |
|------------|---------|---------|--------|
| Secure boot / chain of trust | Required, hardware root of trust |	Required, hardware root of trust | Verifies bootloader, kernel, and rootfs signatures before execution |
| Trusted Execution Environment | Arm TrustZone or equivalent | Arm TrustZone or equivalent | Required for DRM key handling |
| DRM |	Widevine L1, PlayReady SL3000 |	Widevine L1, PlayReady SL3000 |	Hardware-backed key and video path protection |
| HDCP (HDMI output) |	HDCP 1.4 minimum; HDCP 2.2 recommended |HDCP 2.2 minimum; HDCP 2.3 recommended | HDCP 2.2 or later is required for protected 4K/UHD content |
| Secure key provisioning |	Per-device unique keys, provisioned in a secure facility |	Per-device unique keys, provisioned in a secure facility | Prevents key cloning across devices |
| Rollback protection |	Anti-rollback for bootloader/firmware |	Anti-rollback for bootloader/firmware | Prevents downgrade attacks that re-expose patched vulnerabilities |
| Debug interface lockdown | JTAG/UART disabled or authenticated in production | JTAG/UART disabled or authenticated in production | Prevents extraction of keys or firmware |

---

### Memory (RAM)

This section defines the minimum RAM requirements necessary to support Core RDK operation on an IP-based STB. The requirements ensure adequate memory is available for the embedded Linux operating system, RDK services, media processing, applications, and background system functions under normal and peak operating conditions.

<a id="memory-ram"></a>

| Parameter | Tier 1 (FHD) | Tier 2 (4K Premium) | Notes |
|------------|-------------|---------------------|--------|
| System RAM | ≥1 GB* | ≥2 GB | Tier 1 covers FHD-only devices; Tier 2 is required for any 4K/UHD-capable device |
| RAM Technology / data rate | DDR4, LPDDR4X, or newer; ≥ 1600 MT/s effective data rate | LPDDR4X or newer; ≥ 3200 MT/s effective data rate | LPDDR4X is the minimum LPDDR generation for new designs. The selected memory subsystem shall provide the declared capacity and sustain the tier workload under concurrent media, graphics, and application activity. New platform designs shall confirm the long-term availability and lifecycle support of the selected memory technology and supply chain for the intended product deployment and service life |
| Memory bus width / bandwidth | ≥ 16-bit data bus; ≥ 3.2 GB/s theoretical peak bandwidth |	≥ 32-bit data bus; ≥ 12.8 GB/s theoretical peak bandwidth |	Theoretical peak bandwidth = effective data rate (MT/s) × bus width (bits) ÷ 8. The SoC vendor shall declare the implemented bus width and channel configuration |
| Video / secure memory reserve	| Platform-declared (CMA/secure video path) | Platform-declared (CMA/secure video path) | Must be declared by the SoC vendor. It is excluded from, and reduces, the usable RAM figures below |
| Usable RAM after OS and reserves | ≥ 0.6 GB free for applications | ≥ 1.2 GB free for applications |	Measured post-boot with the launcher idle |
| Swap / zRAM |	Optional, 256 MB zRAM |	Optional, 512 MB zRAM | Compressed RAM-backed swap; not persistent flash storage |


> *Tier 1 memory values are provisional and derived from historical FHD platform data. The 1 GB system RAM baseline and related application-memory targets must be validated on a 1 GB FHD device running the RDK 9 baseline. The next controlled revision will incorporate the resulting measurements and any necessary baseline adjustments.*

### Reference memory measurements

- [Tier 1 (FHD device)](#reference-memory-measurements-tier1-fhd-device)
- [Tier 2 (4K Premium device)](#reference-memory-measurements-tier2-4k-premium-device)
  
---

### Storage (Flash)

This section defines the minimum flash storage requirements necessary to support Core RDK operation on an IP-based STB. The requirements ensure adequate capacity for the operating system, RDK components, applications, persistent data, diagnostic information, and OTA updates while maintaining system reliability and upgradeability.

<a id="storage-flash"></a>

| Parameter | Tier 1 | Tier 2 | Notes |
|------------|--------|--------|--------|
| Internal Flash capacity | 4 GB eMMC minimum | 4 GB minimum, 8 GB recommended | 8 GB is recommended where full A/B images and larger application footprints are required |
| Partition/ Update Scheme | Recovery + OTA partition at 4 GB; A/B (seamless) permitted where the verified budget allows | A/B (seamless) recommended with 8 GB; recovery + OTA permitted at 4 GB | Full A/B together with ≥ 2 GB free space is not achievable on 4 GB eMMC |
| Free space for app installs | ≥ 2 GB target after OS and reserved partitions | ≥ 2 GB target after OS and reserved partitions | Validate on the target device. Operators requiring ≥ 3 GB free space with full A/B should specify 8 GB or larger |
| Removable storage | microSD slot optional | microSD slot Optional | For media libraries or app expansion |
| Write endurance | Declared TBW sufficient for the target service life | Declared TBW sufficient for the target service life |	Stated as total bytes written under the operator write-workload profile (OTA, apps, logs); ≥ 3,000 P/E-cycle-class eMMC is the reference |

### Reference

 - [Reference Flash Measurements](#appendix-c-reference-flash-measurements)
 - [Example Flash layout](#appendix-d-example-flash-layout)

---

### Network Connectivity

This section defines the minimum network connectivity requirements necessary to support Core RDK operation on an IP-based STB. These requirements ensure that the platform can reliably access broadband services, communicate with cloud-based management systems, support OTT video delivery, and maintain secure device operation throughout its lifecycle.

<a id="network-connectivity"></a>

### Wi‑Fi

| Parameter | Tier 1 | Tier 2 | Notes |
|------------|--------|--------|--------|
| Standard | 802.11 b/g/n, 2.4 GHz minimum | Dual-band 2.4/5 GHz (802.11n/ac) minimum |	Wi-Fi 6/6E is recommended for Tier 2 and Wi-Fi 7 is future-ready; neither is required for baseline compatibility |
| Throughput | ≥ 15 Mbps sustained application throughput |	≥ 25 Mbps sustained application throughput | Validate sustained throughput in the target RF environment; do not rely on PHY rate alone |
| Security | WPA2-PSK (AES) minimum	| WPA2-PSK (AES) minimum; WPA3-SAE required where Wi-Fi 6/6E is implemented | WPA3 is mandatory for Wi-Fi Alliance Wi-Fi 6 certification |
| Antenna / receiver sensitivity | Internal antenna; ≤ -70 dBm while meeting the Tier 1 sustained-throughput requirement | Internal antenna; ≤ -70 dBm per band while meeting the Tier 2 sustained-throughput requirement |	Sensitivity shall be reported with the test channel, bandwidth, data rate, and modulation/MCS. More negative is better |
| Bluetooth / Voice Transport |	Required (BLE 4.2+) | Required (BLE 5.0+) |	Required to support voice remote capability. Wi-Fi/Bluetooth combo devices are commonly used |

### Ethernet

| Parameter | Tier 1 | Tier 2 |
|-----------|---------|---------|
| Standard | 10/100 Mbps Fast Ethernet minimum | 10/100 Mbps minimum; Gigabit recommended |	Gigabit is recommended for Tier 2 multi-stream or application-heavy use cases|
| Connector | RJ-45 | RJ-45 | |
| Auto Negotiation | Required | Required | Avoids crossover-cable issues |
| PHY | IEEE 802.3 compliant; no PoE requirement | IEEE 802.3 compliant; no PoE requirement | |

### Interface Selection

 - Wi-Fi and Ethernet are not required to operate simultaneously.
 - The device shall support automatic failover and preference logic, with Ethernet prioritized over Wi-Fi when both are connected, and shall allow the user to select the active interface through system settings.

---

### Peripheral and I/O Requirements

This section defines the minimum peripheral and input/output interfaces required to support Core RDK functionality on an IP-based STB, ensuring interoperability with display devices, user input devices, external peripherals, and service-provider operational workflows.

<a id="peripheral-and-io-requirements"></a>

| Parameter | Tier 1 | Tier 2 |
|------------|---------|---------|
| Video output	| HDMI 1.4b or later, 1080p60 |	HDMI 2.0b or later, 4K60 with HDR10 and HLG | HDMI 2.0a adds HDR10 static metadata and 2.0b adds HLG signaling. CEC recommended on both tiers |
| Audio output | HDMI embedded audio (stereo, 5.1 passthrough) | HDMI embedded audio (stereo, 5.1 passthrough) | |
| USB |	1 × USB 2.0	| 1 × USB 2.0 |	Storage, keyboard, debugging |
| IR receiver |	Required (38 kHz) | Required (38 kHz) | |
| Remote control |	IR remote required |IR remote required | |
| Bluetooth / BLE remote |	Required (BLE 4.2+) | Required (BLE 5.0+) |	Provides the transport path required for voice remote functionality and non-line-of-sight operation |
| Voice remote | Required | Required | Voice capability is mandatory for both tiers |
| Reset / recovery button |	Required (physical or button combination) | Required (physical or button combination) | For factory reset and recovery-mode entry |
| Status indicator | Single LED (power/network state) |	Single LED (power/network state)| |

---

### Power Requirements

This section defines the minimum power requirements needed to support Core RDK operation, ensuring adequate and stable power delivery for system functionality, reliability, and long-term operation.

<a id="power-requirements"></a>

| Parameter | Tier 1 | Tier 2 |
|------------|---------|---------|
|Input supply | 5 V DC, 2 A (10 W) minimum | 5 V DC, 2.4 A (12 W) minimum |	Tier 2 shall be measured with Wi-Fi active, 4K decode running, and the USB port under rated load |
|Idle power	| ≤ 5 W | ≤ 5 W | Measured with the network connected, HDMI output active, and the launcher idle |
| Standby power | ≤ 1 W	| ≤ 1 W | Network standby or quick-resume mode; regional regulations may impose lower limits |
|Operating temperature	| 0 °C to 40 °C ambient	| 0 °C to 40 °C ambient	| No active fan required |

---

### Regulatory and Certification Requirements

<a id="regulatory-and-certification-requirements"></a>

A compliant device is expected to obtain the following certifications:

- Wi-Fi Alliance certification for the implemented 802.11 standards.
- Bluetooth SIG qualification is mandatory for both tiers because BLE voice transport is required. 
- FCC Part 15 (US), CE/RED (EU), or applicable regional EMC and radio certification.
- HDMI compliance testing (HDMI CTS) for the declared HDMI version.
- Widevine and PlayReady certification at the security levels defined.
- RDK compliance test suite (RDK-V L1/L2 test pass) for the target RDK release.
- OTT partner certifications for the target application portfolio.

Hardware shall comply with applicable telecom, EMC/radio, safety, cybersecurity, and environmental requirements. Additional regional requirements may apply.

| Region | Regulatory Bodies / Marks | Radio & EMC | Safety, Environmental & Cybersecurity | Notes | 
| ------ | ------------------------- | ---- | ---- | ---- |
| North America (US, Canada, Mexico) | 	FCC (US); ISED (Canada); IFT / NOM (Mexico) | FCC Part 15 Subparts B and C; ISED RSS-Gen / RSS-247; IFT homologation | UL 62368-1 or applicable UL/CSA standard; California Proposition 65 where applicable | FCC ID and IC certification required before retail sale; certified module grants can often be leveraged |
| South America (Brazil, Argentina, Chile, Colombia, etc.) | ANATEL; ENACOM; SUBTEL; CRC / MinTIC |	ANATEL homologation for Wi-Fi/Bluetooth/RF modules; country type approval elsewhere |INMETRO (Brazil); local safety marks elsewhere | ANATEL certification is mandatory for retail sale in Brazil |
| Europe (EU/EEA and UK) | EU Notified Bodies (CE); UK Approved Bodies (UKCA) | Radio Equipment Directive 2014/53/EU; CE marking; UKCA for the UK |	RoHS 2011/65/EU; WEEE 2012/19/EU; REACH; Ecodesign standby and networked-standby limits (Regulation (EU) 2023/826); RED cybersecurity delegated act (EU) 2022/30 with EN 18031 standards, applicable from 1 August 2025; Cyber Resilience Act (EU) 2024/2847, with reporting obligations from 11 September 2026	| Declaration of Conformity and technical file required. CRA full product requirements apply from December 2027 |
| Asia (Japan, China, South Korea, India, etc.) | MIC; SRRC / CCC; RRA / KC; WPC / BIS | Japan Giteki; China SRRC; Korea KC; India WPC ETA | PSE (Japan), CCC (China), KC (Korea), BIS (India) | Module certificates are not always transferable; end-product re-testing may be required |
| Australia and New Zealand	| ACMA | Regulatory Compliance Mark (RCM) |	Electrical safety approval per risk class; e-waste schemes | Supplier self-declaration with a Declaration of Conformity and test reports on file |

---

### Appendix A - Reference Memory Measurements – Tier 1 (FHD) device

<a id="reference-memory-measurements-tier1-fhd-device"></a>

Tier 1 memory values are provisional and are based on historical FHD platform data. The proposed 1 GB system RAM baseline and associated application-memory targets have not yet been validated on an RDK 9 FHD configuration with 1 GB RAM and shall remain an open condition under RDKDEV-1741. This specification proceeds with the 1 GB baseline as a provisional target for planning purposes; however, it shall not be considered a final approved requirement until validation activities are completed and reviewed. The resulting measurements, together with any required baseline adjustments, shall be incorporated into a subsequent controlled revision of this specification

---

### Appendix B - Reference Memory Measurements – Tier 2 (4K Premium) device

<a id="reference-memory-measurements-tier2-4k-premium-device"></a>

The following values were measured on the RDK 4K reference device and are provided to support memory budgeting. 

| Workload | Measured on 4K Reference | Notes |
| -------- | ------- | ------ | 
| RDK boot without home UI | 230 MB | Kernel, init, and core RDK middleware/services, measured after boot and before the launcher starts |
| RDK Core with home UI | 330 MB | Launcher UI, RDK middleware services, WPEFramework/Thunder core |
| RDK Home App with voice | 365 MB | Total including the home UI baseline (approximately 35 MB voice increment) |
| RDK Home App, browser 4K playback | 950 MB | Total during 4K VOD playback, of which approximately 600 MB is attributable to playback workloads |
| Netflix | ≤ 800 MB | Idle 100 MB; 4K playback 800 MB; system total approximately 1.3 GB |
| Amazon Prime Video | ≤ 705 MB | Idle 212 MB; FHD playback 225 MB; 4K playback 705 MB; system total approximately 1.2 GB |
| YouTube | ≤ 300 MB | Idle 125 MB; FHD playback 140 MB; 4K playback 214 MB; DRM 4K playback 280 MB |
| Generic HTML5 / web app (WPE) | ≤ 300 MB | Idle 216 MB; live playback window 267 MB; full-screen VOD playback 300 MB |

Reference platform used for the Memory Measurements – Tier 2 (4K Premium) device:

| Parameter | Reference platform detail | Notes |
| --------- | ------- | ----- |
| Reference device | Broadcom 74116 Ref Board (ipstb-brcm974116sff) | Board used for the Appendix B measurements |
| SoC |	BCM974116SFF (B1) | SoC variant |
| SDK Version |	URSR 26.0 | Broadcom SDK release used for the measurements | 
| Build / image identifier | lib32-rdk-fullstack-image-ipstb-brcm974116sff-20260903071955 | Image flashed on the measured device | 
| Kernel version | ACK6.1.175 | Running kernel version |

---

### Appendix C - Reference Flash Measurements
 
<a id="appendix-c-reference-flash-measurements"></a>

The application flash requirement covers the launcher UI, sandboxed applications, application data, configuration files, caches, logs, and update packages, with sufficient headroom for reliable installation, operation, and over-the-air application updates without affecting the storage reserved for the RDK platform.
 
| Component | Measured on 4K Reference | Notes |
| -------- | ------- | ------ |
| RDK Core with home UI	| 540 MB | Launcher UI, RDK middleware binaries/libraries, WPEFramework/Thunder plugins. RDK rootfs (without UI) 437.4 MB; RefUI (base + WPE runtime + UI) 95 MB |
| Netflix | 75 MB | App package plus persistent cache/cookies |
| Amazon Prime Video | 40 MB | App package plus persistent cache/cookies |
| YouTube | 36 MB | App package plus persistent cache |
| Generic HTML5 / web app (per app) | 1 MB | Package plus local storage/cache |

---

### Appendix D - Example Flash Layout

<a id="appendix-d-example-flash-layout"></a>

This sample flash and mount-point layout was captured from a live RDK-V device with 4 GB on-board eMMC (filesystem table, df). It is provided for storage budgeting, device flashing, and mount-layout validation and is not a partitioning requirement.

| Device Node |	Filesystem | Size (Used / Available, Use %) | Mount Point | Purpose |
| ----------- | ---------- | ------------------------------ | ----------- | ------- |
| /dev/root | ext4 | 965.9M (437.4M used / 462.5M avail, 49%) |	/ | On-board eMMC root filesystem |
| /dev/root (bind mount) | ext4 | Same filesystem as above | /mnt/media/apps (+ /opt, /var/lib | On-board eMMC partition |
| /dev/mmcblk1p7 | ext4 | 119.0K (21.0K used / 90.0K avail, 19%) | /mnt/bp30 | On-board eMMC partition |
| /dev/dm-0 | erofs | 8.2M (8.2M used / 0 avail, 100%) | /tmp/mounts/com.rdkcentral.base_0.3.1/rootfs |	Read-only app runtime image (dm-verity/erofs) |
| /dev/dm-1 | erofs | 81.1M (81.1M used / 0 avail, 100%) | /tmp/mounts/com.rdkcentral.wpe_0.4.2/rootfs | Read-only app runtime image (dm-verity/erofs) |
| /dev/dm-2 | erofs | 4.9M (4.9M used / 0 avail, 100%) | /tmp/mounts/com.rdkcentral.refui_6.0.34/rootfs | Read-only app runtime image (dm-verity/erofs) |
| overlay | overlay | 3.7G (776.0K used / 3.7G avail, 0%) | /tmp/ralf/<id>/rootfs | tmpfs-backed overlay (RAM, not persistent flash) |

---
