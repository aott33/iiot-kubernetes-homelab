# IIoT Kubernetes Homelab - Architecture

**Last Updated:** November 11, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Network Architecture](#network-architecture)
3. [Kubernetes Architecture](#kubernetes-architecture)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Platform Integration](#platform-integration)
6. [Security Architecture](#security-architecture)

---

## System Overview

This homelab implements a production-grade Industrial IoT architecture with clear separation between Operational Technology (OT) and Information Technology (IT) networks, following industrial cybersecurity best practices.

### Design Principles

1. **OT/IT Segmentation:** Physical and logical separation between factory floor (OT) and enterprise (IT) networks
2. **Defense in Depth:** Multiple layers of security (firewall, VLANs, air-gapping, VPN)
3. **Cloud-Native Infrastructure:** Kubernetes-based platform for scalability and resilience
4. **Protocol Translation:** EdgeX Foundry bridges industrial protocols to modern APIs
5. **Data Pipeline:** Structured flow from sensors → edge → cloud-native data platform

---

## Network Architecture

### Three-VLAN Design

```mermaid
graph TB
    Internet((Internet))

    OPN[OPNsense Firewall<br/>Fitlet 3]
    Switch[Cisco CBS220<br/>Managed Switch]

    subgraph VLAN10["VLAN 10 - OT Network<br/>(192.168.10.0/24)<br/>AIR-GAPPED"]
        spacer10[ ]
        EdgeX[EdgeX Gateway<br/>FR201]
        PiWorkers[Pi Workers<br/>Edge Nodes]
        ModbusDevices[Modbus Devices<br/>Sensors]
    end

    subgraph VLAN20["VLAN 20 - IT Network<br/>(192.168.20.0/24)<br/>INTERNET ACCESS"]
        spacer20[ ]
        K3sControl[K3s Control Plane<br/>Gaming PC]
        K3sWorkerIT[K3s Worker<br/>Work PC]
        WiFiClients[WiFi Clients<br/>Orbi Mesh]
    end

    subgraph VLAN99["VLAN 99 - Management<br/>(192.168.99.0/24)<br/>ADMIN ONLY"]
        spacer99[ ]
        SwitchMgmt[Switch Management]
    end

    Internet --> OPN
    OPN --> Switch

    Switch -.-> VLAN10
    Switch -.-> VLAN20
    Switch -.-> VLAN99

    style Internet fill:#ffeb3b,stroke:#333,stroke-width:2px
    style OPN fill:#f44336,color:#fff,stroke:#333,stroke-width:2px
    style Switch fill:#f44336,color:#fff,stroke:#333,stroke-width:2px
    style VLAN10 fill:#ffcdd2,stroke:#333,stroke-width:2px,color:#000
    style VLAN20 fill:#c5e1a5,stroke:#333,stroke-width:2px,color:#000
    style VLAN99 fill:#e0e0e0,stroke:#333,stroke-width:2px,color:#000
    style spacer10 fill:none,stroke:none
    style spacer20 fill:none,stroke:none
    style spacer99 fill:none,stroke:none
```

### VLAN Details

| VLAN | Purpose | Internet | Cross-VLAN | Use Case |
|------|---------|----------|-----------|----------|
| **10 (OT)** | Factory floor devices | Denied | → IT only | EdgeX, sensors, Pi edge workers |
| **20 (IT)** | Enterprise network | Allowed | → All | K3s cluster, workstations, WiFi |
| **99 (Mgmt)** | Infrastructure | Allowed | ← IT only | Switch management, UPS |

---

## Kubernetes Architecture

### Cluster Topology

```mermaid
graph TB

   subgraph ControlPlane["`**Control Plane**
                         Gaming PC - IT VLAN
                         192.168.20.10
                         Tainted: NoSchedule`"]
      spacer1[ ]
      etcd[etcd]
      APIServer[API Server]
      Scheduler[Scheduler]
   end

   ControlPlane --> Worker1
   ControlPlane --> Worker2
   ControlPlane --> Worker3

   Worker1["`**Worker 1**
            (Work PC)
            IT VLAN: .20.11
            x86-64
            32GB RAM
            Heavy Workloads`"]
   Worker2["`**Worker 2**
            (Pi 1)
            OT VLAN: .10.21
            ARM64
            4GB RAM
            Lightweight`"]
   Worker3["`**Worker 3**
            (Pi 2)
            OT VLAN: .10.22
            ARM64
            4GB RAM
            Lightweight`"]

   style ControlPlane fill:#bbdefb,stroke:#333,stroke-width:2px,color:#000
   style Worker1 fill:#c8e6c9,stroke:#333,stroke-width:2px,color:#000
   style Worker2 fill:#ffcdd2,stroke:#333,stroke-width:2px,color:#000
   style Worker3 fill:#ffcdd2,stroke:#333,stroke-width:2px,color:#000
   style spacer1 fill:none,stroke:none
```

### Workload Distribution

| Node | VLAN | Resources | Workloads | Notes |
|------|------|-----------|-----------|-------|
| **Gaming PC** | IT | 16GB RAM, 6 cores | Control plane only | Tainted NoSchedule |
| **Work PC** | IT | 32GB RAM, 6 cores | UMH, Ignition, heavy pods | Resource limits: 10GB for K8s |
| **Pi 1** | OT | 4GB RAM, 4 cores | EdgeX (Docker), lightweight | ARM64 workloads |
| **Pi 2** | OT | 4GB RAM, 4 cores | Edge services, monitoring | ARM64 workloads |

### Cross-VLAN Networking

**Challenge:** K3s cluster spans IT and OT VLANs

**Solution:** Firewall rules allow Kubernetes control traffic:

| Port | Protocol | Direction | Purpose |
|------|----------|-----------|---------|
| 6443 | TCP | OT → IT | Kubernetes API server |
| 10250 | TCP | Bidirectional | Kubelet API |
| 8472 | UDP | Bidirectional | Flannel VXLAN overlay |

---

## Data Flow Architecture

### Platform Testing Strategy

This homelab is designed to test **three independent IIoT platforms** end-to-end:

1. **EdgeX Foundry** - Edge computing framework
2. **United Manufacturing Hub (UMH)** - Cloud-native IIoT data platform
3. **Ignition SCADA** - Traditional SCADA/HMI platform

**Data Source:** All platforms will connect to the **Pump Station Sim** (Docker container running in IT VLAN) using **Tentacle PLC** with **Sparkplug B** MQTT protocol. All PLC variables are available via MQTT Sparkplug B by default.

**Note:** Detailed platform architectures and integration patterns will be confirmed during development phases.

### EdgeX Foundry Pipeline (Simplified)

```mermaid
graph LR
    PumpSim["`**Pump Station Sim**
             Tentacle PLC
             IT VLAN
             MQTT Sparkplug B`"]
    EdgeX["`**EdgeX Foundry**`"]

    PumpSim -->|Sparkplug B| EdgeX

    style PumpSim fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000
    style EdgeX fill:#b3e5fc,stroke:#333,stroke-width:2px,color:#000
```

**Goal:** Test EdgeX integration with Sparkplug B protocol and build custom visualizations.

### United Manufacturing Hub Pipeline (Simplified)

```mermaid
graph LR
    PumpSim["`**Pump Station Sim**
             Tentacle PLC
             IT VLAN
             MQTT Sparkplug B`"]
    UMH["`**United Manufacturing Hub**`"]

    PumpSim -->|Sparkplug B| UMH

    style PumpSim fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000
    style UMH fill:#b3e5fc,stroke:#333,stroke-width:2px,color:#000
```

**Goal:** Test UMH integration with Sparkplug B and build data pipeline with Grafana dashboards.

### Ignition SCADA Pipeline (Simplified)

```mermaid
graph LR
    PumpSim["`**Pump Station Sim**
             Tentacle PLC
             IT VLAN
             MQTT Sparkplug B`"]
    Ignition["`**Ignition SCADA**`"]

    PumpSim -->|Sparkplug B| Ignition

    style PumpSim fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000
    style Ignition fill:#d1c4e9,stroke:#333,stroke-width:2px,color:#000
```

**Goal:** Test Ignition Sparkplug module and build ISA 101 compliant HMI screens.

### Integration Approach

**Current Phase:** Independent platform evaluation with shared Pump Station Sim

- Single Pump Station Sim (Docker container, IT VLAN)
- Tentacle PLC provides MQTT Sparkplug B interface
- Each platform subscribes to Sparkplug topics
- Platform-specific integration and visualization development

**Future Phase:** Potential cross-platform integration if beneficial

---

## Platform Integration

### Current Architecture: Shared Data Source

All platforms connect to a single Pump Station Sim via Sparkplug B:

```mermaid
graph TB
    subgraph IT["`**IT VLAN - Kubernetes**`"]
        PumpSim["`**Pump Station Sim**
                 Tentacle PLC
                 Docker Container
                 MQTT Sparkplug B Publisher`"]
    end

    subgraph Platforms[ ]
        EdgeX["`**EdgeX Foundry**`"]
        UMH["`**UMH Stack**`"]
        Ignition["`**Ignition SCADA**`"]
    end

    PumpSim -->|Sparkplug B<br/>Subscribe| EdgeX
    PumpSim -->|Sparkplug B<br/>Subscribe| UMH
    PumpSim -->|Sparkplug B<br/>Subscribe| Ignition

    style IT fill:#c8e6c9,stroke:#333,stroke-width:2px,color:#000
    style PumpSim fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000
    style Platforms fill:none,stroke:#333,stroke-width:2px,color:#000
    style EdgeX fill:#b3e5fc,stroke:#333,stroke-width:2px,color:#000
    style UMH fill:#b3e5fc,stroke:#333,stroke-width:2px,color:#000
    style Ignition fill:#d1c4e9,stroke:#333,stroke-width:2px,color:#000
```

### Technology Stack (Per Platform)

**Pump Station Sim (Shared):**
| Component | Technology | Purpose |
|-----------|-----------|---------|
| PLC Runtime | Tentacle PLC | Soft PLC with Modbus device integration |
| MQTT Publisher | Sparkplug B | Publishes all PLC variables to MQTT broker |
| Deployment | Docker | Container in IT VLAN (K8s or standalone) |

**EdgeX Foundry:**
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Sparkplug Subscriber | EdgeX Device Service | Consumes Sparkplug B topics |
| Visualization | TBD | Custom dashboards (architecture to be confirmed) |

**United Manufacturing Hub:**
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Sparkplug Subscriber | UMH MQTT Broker | Native Sparkplug B support |
| Data Pipeline | Kafka → TimescaleDB | Event streaming and storage |
| Visualization | Grafana | Time-series dashboards |

**Ignition SCADA:**
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Sparkplug Module | Ignition Engine | Native Sparkplug B client |
| Tag Provider | Ignition Tags | Maps Sparkplug metrics to tags |
| Visualization | Perspective HMI | ISA 101 compliant screens |

**Note:** Detailed architectures for each platform will be designed during their respective development phases.

---

## Security Architecture

### Defense in Depth

```mermaid
graph TB
    Layer1["`**Layer 1: Network Segmentation**
            • VLANs (OT/IT/Management)
            • OPNsense firewall
            • Explicit allow rules`"]
    Layer2["`**Layer 2: Air-Gapped OT Network**
            • No internet for OT VLAN
            • One-way data flow (OT → IT)
            • MQTT only cross-VLAN`"]
    Layer3["`**Layer 3: Application Security**
            • Kubernetes RBAC
            • Network Policies (future)
            • Secrets management`"]
    Layer4["`**Layer 4: Remote Access**
            • Tailscale VPN (zero-trust)
            • Tailscale ACLs
            • No port forwarding`"]

    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer3 --> Layer4

    style Layer1 fill:#ffcdd2,stroke:#333,stroke-width:2px,color:#000
    style Layer2 fill:#fff9c4,stroke:#333,stroke-width:2px,color:#000
    style Layer3 fill:#c8e6c9,stroke:#333,stroke-width:2px,color:#000
    style Layer4 fill:#b3e5fc,stroke:#333,stroke-width:2px,color:#000
```

### Firewall Rules Summary

**OPNsense LAN Rules (high-level):**

```
[IT VLAN → Internet]     ALLOW ALL
[IT VLAN → OT VLAN]      ALLOW ALL (management access)
[OT VLAN → IT VLAN]      ALLOW MQTT (1883), OPC UA (4840), K3s (6443, 10250, 8472)
[OT VLAN → Internet]     DENY (air-gapped)
[Management → Internet]  ALLOW (firmware updates)
[IT → Management]        ALLOW (admin access)
[OT → Management]        DENY
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Network** | OPNsense, Cisco CBS220, VLANs | Segmentation, routing, firewall |
| **Orchestration** | K3s (Kubernetes) | Container orchestration |
| **Storage** | Longhorn | Distributed persistent storage |
| **Load Balancing** | MetalLB | External service IPs |
| **Data Source** | Pump Station Sim + Tentacle PLC | Soft PLC with Sparkplug B MQTT publisher |
| **Edge Gateway** | EdgeX Foundry | Sparkplug B integration, edge processing |
| **Data Platform** | United Manufacturing Hub | MQTT, Kafka, TimescaleDB, Grafana |
| **SCADA** | Ignition 8.3 | Sparkplug B client, ISA 101 HMI |
| **VPN** | Tailscale | Secure remote access |
| **Backend** | Go microservices | Custom development |

---

## Future Architecture Enhancements

### Planned Additions

1. **High Availability:**
   - Multi-master K3s control plane
   - Database replication (TimescaleDB HA)

2. **Observability:**
   - Prometheus + Grafana for infrastructure metrics
   - Distributed tracing (Jaeger/Tempo)
   - Centralized logging (Loki)

3. **Network Policies:**
   - Kubernetes Network Policies (Calico or Cilium)
   - Micro-segmentation within cluster

4. **GitOps:**
   - ArgoCD for declarative deployments
   - FluxCD alternative

5. **Additional Protocols:**
   - OPC UA server/client
   - Ethernet/IP integration
   - Profinet (if hardware supports)

---

## Related Documentation

- [Network Topology Details](../hardware/network-topology.md)
- [Hardware Specifications](../hardware/hardware-list.md)
- [Main README](../README.md)
