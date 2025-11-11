# Hardware Inventory

**Total Project Cost:** ~$900 CAD

---

## Network Infrastructure

### 1. Fitlet 3 - OPNsense Router/Firewall

**Role:** Network router, firewall, VPN endpoint

**Specifications:**
- **CPU:** Intel Atom x6425E (4-core, 2.0 GHz base, 3.0 GHz boost)
- **RAM:** 8 GB DDR4
- **Storage:** 500GB Kingston NV3 NVMe M.2 2280 (PCIe Gen4, up to 5,000 MB/s read)
- **Network:** 2x Gigabit Ethernet (Intel i211 controllers)
- **Special Features:**
  - GPIO pins for industrial I/O
  - RS-232/RS-485 serial ports
  - TPM 2.0 security
  - Fanless design (passive cooling)
  - Industrial temperature range support
- **Operating System:** OPNsense CE (latest)
- **Power:** 12V DC, low power consumption (~10W idle)

**Approximate Cost:** $400 CAD

**Network Configuration:**
- **WAN Interface (em0):** ISP connection via DHCP
- **LAN Interface (em1):** 192.168.20.1/24 (IT VLAN gateway)
- **VLAN 10 (OT):** 192.168.10.1/24
- **VLAN 99 (Management):** 192.168.99.1/24

---

### 2. Cisco CBS220-16T-2G - Managed Switch

**Role:** VLAN switching, network segmentation

**Specifications:**
- **Ports:** 16x Gigabit Ethernet (10/100/1000 Mbps) + 2x Gigabit SFP
- **Switching Capacity:** 36 Gbps
- **Forwarding Rate:** 26.8 Mpps
- **VLAN Support:** 256 VLANs (802.1Q tagging)
- **Layer 2 Features:**
  - VLAN trunking and access ports
  - Spanning Tree Protocol (STP, RSTP, MSTP)
  - Link Aggregation (LACP, static)
  - Port mirroring
  - QoS (Quality of Service)
- **Management:**
  - Web GUI
  - CLI (console/SSH)
  - Mobile app
  - SNMP v1/v2/v3
- **Power:** AC 100-240V, fanless

**Cost:** $171 CAD

**VLAN Configuration:**
- **VLAN 10 (OT):** Ports 1-6
- **VLAN 20 (IT):** Ports 7-12
- **VLAN 99 (Management):** Port 13
- **Trunk Port:** Port 16 (to OPNsense)

---

### 3. Netgear Orbi RBK13 - Mesh WiFi System

**Role:** WiFi access points (AP mode), mesh coverage

**Specifications:**
- **System:** RBR10 (main router) + 2x RBS10 (satellites)
- **WiFi Standard:** 802.11ac (WiFi 5), dual-band
- **Speed:** AC1200 (300 Mbps @ 2.4GHz + 866 Mbps @ 5GHz)
- **Mesh Technology:** Tri-band backhaul (dedicated 5GHz band between nodes)
- **Coverage:** ~4,000 sq ft (with 3 units)
- **Ethernet Ports:** 2x Gigabit per unit
- **Security:** WPA2-PSK, WPA3 (on newer firmware)
- **Mode:** Access Point (AP) mode (not router mode)

**Approximate Cost:** $150 CAD (used/refurbished)

**Network Configuration:**
- **Mode:** AP Mode (bridged to OPNsense LAN)
- **Main Router IP:** 192.168.20.3 (static)
- **Satellite 1 IP:** 192.168.20.4 (static)
- **Satellite 2 IP:** 192.168.20.5 (static)
- **SSID:** Single SSID for all VLANs (segmented via OPNsense DHCP)

**Note:** Planning to upgrade to Grandstream GWN7660E Wi-Fi 6 AP (~$150 CAD) for full gigabit WiFi speeds.

---

## Compute Nodes

### 4. DIY Gaming PC - Kubernetes Control Plane

**Role:** K3s control plane (master node), dedicated to cluster management

**Specifications:**
- **CPU:** AMD Ryzen 5 3600X (6-core, 12-thread, 3.8 GHz base, 4.4 GHz boost)
- **RAM:** 16 GB DDR4-3200 (2x 8GB)
- **Storage:** 1TB Sabrent Rocket Q NVMe (PCIe Gen3 x4, up to 3,200 MB/s read)
- **GPU:** ASUS TUF GTX 1660 SUPER 6GB (not used for Kubernetes)
- **Motherboard:** ASUS ROG Strix B450-I Gaming (Mini ITX)
- **Cooling:** Corsair H55 AIO Liquid Cooler (120mm radiator)
- **PSU:** Corsair SF450 Platinum (450W SFX, 80+ Platinum)
- **Case:** Silverstone SG13 Mini ITX (compact)
- **Operating System:** Ubuntu Server 24.04 LTS
- **Network:** Gigabit Ethernet (onboard)

**Cost:** Already owned

**Role in Cluster:**
- K3s server (control plane only, taints prevent workload scheduling)
- etcd datastore
- Kubernetes API server
- Scheduler and controller manager
- Static IP: 192.168.20.10

---

### 5. MSI Work PC - Kubernetes Worker Node + Daily Driver

**Role:** K3s worker node + daily-use development workstation (dual-purpose)

**Specifications:**
- **CPU:** AMD Ryzen 5 5600G (6-core, 12-thread, 3.9 GHz base, 4.4 GHz boost)
- **RAM:** 32 GB DDR4-3200 (2x 16GB Crucial SO-DIMM)
- **Storage:** 250GB PCIe SSD
- **GPU:** Integrated AMD Radeon Graphics (Vega 7)
- **Operating System:** Omarchy Linux (Arch-based)
- **Network:** Gigabit Ethernet (onboard)

**Cost:** Already owned

**Role in Cluster:**
- K3s agent (worker node with resource limits)
- Runs heavy IIoT workloads (UMH, Ignition)
- Kubelet reserves 2 CPU cores + 10GB RAM for K8s
- Leaves 4 cores + 22GB RAM for daily use
- Static IP: 192.168.20.11

**Resource Management:**
- Target: <70% memory utilization during normal use
- Kubernetes workloads throttled to prevent UI lag
- Tested with daily workload stress tests

---

### 6. OnLogic FR201 - EdgeX Gateway (Industrial Grade)

**Role:** EdgeX Foundry gateway, edge data processing (OT VLAN)

**Specifications:**
- **SoM:** Raspberry Pi CM4 (4GB RAM, no eMMC - uses SATA)
- **Storage:** 128GB SATA SSD (industrial-grade)
- **CPU:** Broadcom BCM2711 (quad-core Cortex-A72, 1.5 GHz)
- **Operating Temperature:** -20°C to +75°C (industrial fanless design)
- **Network:** Gigabit Ethernet
- **Operating System:** Ubuntu Desktop 22.04 64-bit (ARM64)
- **Power:** 12V DC industrial power supply
- **Enclosure:** Rugged industrial enclosure with DIN rail mount

**Cost:** Already owned

**Role in Network:**
- EdgeX Foundry deployment (Docker Compose)
- Modbus device service (connects to Pump Station Simulator)
- MQTT bridge to UMH (cross-VLAN: OT → IT)
- Static IP: 192.168.10.20 (OT VLAN)

---

### 7. Raspberry Pi Cluster (2x) - K3s Edge Workers

**Role:** K3s worker nodes in OT VLAN, edge computing simulation

**Specifications (per unit):**
- **Model:** Raspberry Pi 4 Model B
- **RAM:** 4GB LPDDR4
- **CPU:** Broadcom BCM2711 (quad-core Cortex-A72, 1.5 GHz)
- **Storage:** 64GB microSD card (SanDisk Extreme A2)
- **Network:** Gigabit Ethernet
- **Power:** USB-C power supply (5V 3A, official)
- **Operating System:** Raspberry Pi OS Lite 64-bit (or Ubuntu Server 22.04 ARM)
- **Cooling:** GeeekPi 1U Rack Mount Kit with active cooling fans

**Cost:** ~$230 CAD
- 2x Raspberry Pi 4B (4GB): ~$180 CAD
- 2x USB-C power supplies: ~$30 CAD
- GeeekPi 1U Rack Mount Kit: ~$20 CAD (from Amazon.ca)

**Role in Cluster:**
- K3s agent (worker nodes in OT VLAN)
- Lightweight IIoT workloads
- Multi-architecture support (ARM64 + x86-64)
- Static IPs: 192.168.10.21, 192.168.10.22

---

## Additional Hardware

### 8. Server Rack

**Specifications:**
- **Size:** 12U open-frame rack with wheels
- **Brand:** PrimeCables
- **Features:** Adjustable depth, cable management arms

**Cost:** $140 CAD

---

### 9. Networking Cables

**Cable Inventory:**
- **CAT6A Patch Cables (1ft):** 10x - Rack cable management
- **CAT6A Patch Cables (0.5ft):** 10x - Short connections

**Cost:** $43 CAD

---

## Total Hardware Investment

| Category | Cost (CAD) |
|----------|------------|
| **Network Infrastructure** | $764 |
| - Fitlet3 (OPNsense) | $400 |
| - Cisco CBS220 Switch | $171 |
| - Netgear Orbi Mesh WiFi | $150 |
| - Cables | $43 |
| **Compute Nodes** | $230 |
| - Raspberry Pi Cluster (2x) | $230 |
| - Gaming PC | Owned |
| - Work PC | Owned |
| - OnLogic FR201 | Owned |
| **Rack & Accessories** | $140 |
| - Server Rack | $140 |
| **Total** | **~$1,134** |

**Note:** Total exceeds $900 estimate due to including all hardware. Core new purchases for this project were ~$900 CAD.

---

## Future Upgrades (Optional)

### Planned
- **Grandstream GWN7660E Wi-Fi 6 AP** (~$150 CAD) - Full gigabit WiFi
- **PoE Injector for AP** (~$20 CAD) - If not using PoE switch

### Potential
- **UPS (CyberPower CP1500PFCRM2U)** (~$440 CAD) - Rack-mount UPS
- **Additional Raspberry Pi 4B** (~$115 CAD) - Expand K3s cluster
- **USB 3.0 External HDD (2TB)** (~$60 CAD) - K8s etcd backups

---

## Power Consumption Estimate

| Device | Idle Power | Peak Power | 24/7 Cost/Month (CAD)* |
|--------|-----------|------------|-------------------------|
| Fitlet3 | 10W | 15W | ~$1.50 |
| Cisco Switch | 8W | 12W | ~$1.20 |
| Orbi System (3 units) | 20W | 30W | ~$3.00 |
| Gaming PC | 50W | 150W | ~$7.50 |
| Work PC | 30W | 120W | ~$4.50 |
| OnLogic FR201 | 5W | 10W | ~$0.75 |
| 2x Raspberry Pi 4B | 10W | 20W | ~$1.50 |
| **Total** | **~133W** | **~357W** | **~$20/month** |

*Assumes $0.15/kWh electricity rate, 24/7 operation

---

## See Also

- [Network Topology Diagram](network-topology.md)
- [Architecture Overview](../docs/architecture.md)
