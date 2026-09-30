---
name: Kinetic Horizon
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#434655'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#737687'
  outline-variant: '#c3c6d8'
  surface-tint: '#0052dc'
  primary: '#0047c1'
  on-primary: '#ffffff'
  primary-container: '#155eef'
  on-primary-container: '#e7eaff'
  inverse-primary: '#b4c5ff'
  secondary: '#4d5f7d'
  on-secondary: '#ffffff'
  secondary-container: '#c8dbfe'
  on-secondary-container: '#4e607e'
  tertiary: '#6718d8'
  on-tertiary: '#ffffff'
  tertiary-container: '#803ff1'
  on-tertiary-container: '#f2e8ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003da9'
  secondary-fixed: '#d6e3ff'
  secondary-fixed-dim: '#b5c7ea'
  on-secondary-fixed: '#071c36'
  on-secondary-fixed-variant: '#364764'
  tertiary-fixed: '#eaddff'
  tertiary-fixed-dim: '#d2bbff'
  on-tertiary-fixed: '#25005a'
  on-tertiary-fixed-variant: '#5a00c6'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.005em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 0.75rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system embodies high-trust, commercial-grade intelligent mobility. It balances the uncompromising precision of real-time transit telemetry with the conversational clarity of predictive AI assistance. Designed for daily commuters, long-distance travelers, and transit dispatch operators, the visual aesthetic projects absolute operational stability, modern velocity, and intuitive control.

The visual direction merges **Modern Functionalism** with **Contextual Precision**:
- **Operational Baseline**: Deep, commanding structural chrome establishes institutional authority, framing content with sharp, deliberate intent.
- **Dynamic Clarity**: Generous whitespace on canvas layers isolates route geometry, live vehicle telemetry, and schedule variances without cognitive overload.
- **Domain Specialization**: Standard product interactions remain firmly anchored in clean transit blues and emerald metrics, while an exclusive violet spectrum signals machine intelligence, anomaly detection, and route optimization.

## Colors

The palette enforces strict behavioral boundaries to ensure situational awareness at a glance:

- **Primary (`#155EEF` - Transit Electric Blue)**: Primary action pathways, interactive map waypoints, active bus progress corridors, and prominent CTA triggers.
- **Secondary (`#0B1F3A` - Deep Marine Navy)**: Structural chassis, persistent navigation sidebars, high-level headers, and high-emphasis data readouts.
- **Tertiary (`#7C3AED` - Neural Violet)**: Exclusively reserved for artificial intelligence features—predictive arrival times, smart transfer suggestions, dynamic pricing nudges, and conversational query controls. Paired with soft `#F5F3FF` fills.
- **Tracking Accent (`#38BDF8` - Atmosphere Sky)**: Live bus ping pulses, directional heading indicators, telemetry markers, and ambient map highlights.
- **Status Accents**:
  - **On-Time / Available (`#10B981` / `#ECFDF5`)**: Green operational health badges, available seat anchors, verified connections.
  - **Caution / Delay (`#F59E0B` / `#FFFBEB`)**: Route variance, traffic impediments, platform reassignment alerts.
  - **Critical / Canceled (`#EF4444` / `#FEF2F2`)**: Suspended trips, system outages, occupancy overload.
- **Seat Map Matrix**:
  - Available: Emerald outline and subtle wash (`#10B981` border, `#ECFDF5` fill).
  - Selected: Deep Transit Blue (`#155EEF` fill, white glyph).
  - Booked / Unavailable: Muted Slate (`#E2E8F0` fill, `#94A3B8` border).
- **Canvas & Surfaces**: Base canvas utilizes `#F8FAFC`, stepping up to pure white (`#FFFFFF`) for cards and floating overlay surfaces.

## Typography

The typographic system leverages **Plus Jakarta Sans** for display, route signifiers, and section headlines to inject energetic modernity into transit headers. **Inter** handles all body content, arrival grids, seat layouts, and dense tabular data to ensure absolute optical clarity across low-grade mobile displays and outdoor ambient light.

- **Tabular Numerals (`tnum`)**: All arrival countdowns, platform IDs, fare quotes, and occupancy percentages must activate tabular figures to prevent layout jitter during live telemetry polling.
- **Visual Weight Pairing**: Pair heavy structural titles (700/800) with muted, precise subheadings (Inter 400 in `#64748B`) to establish immediate hierarchical scanning.

## Layout & Spacing

The layout is built upon an 8pt architectural rhythm, translating to an adaptable 12-column grid on desktop/tablet views and a single-column layout on mobile viewports:

- **Desktop (1280px+)**: 12 columns, 24px gutters, fixed-width or responsive full-bleed map views with a fixed 380px floating or pinned interaction sidebar. Section margins sit at 32px (`2rem`).
- **Tablet (768px – 1279px)**: 8 columns, 16px gutters, 24px margins. Navigation collapes into an elevated bottom sheet or responsive drawer.
- **Mobile (< 768px)**: 4 columns, 12px gutters, 16px outer margins. Live map dominates background; ticketing search, bus manifests, and AI assistants operate through gesture-controlled bottom sheets with snap points (collapsed, half, full).

## Elevation & Depth

Depth is established through soft, multi-layered ambient shadows and subtle structural borders:

- **Level 0 (Base Canvas)**: `#F8FAFC`. Completely flat background for content staging and map viewport underlays.
- **Level 1 (Cards & Static Panels)**: `#FFFFFF` background with a crisp border (`1px solid #E2E8F0`) and ambient shadow: `0 1px 3px 0 rgba(11, 31, 58, 0.04), 0 1px 2px -1px rgba(11, 31, 58, 0.04)`.
- **Level 2 (Dropdowns, Route Selection, Hovered Cards)**: `#FFFFFF` elevated with `0 4px 6px -1px rgba(11, 31, 58, 0.07), 0 2px 4px -2px rgba(11, 31, 58, 0.05)`.
- **Level 3 (Floating Map Modals, Live Trackers, Bottom Sheets)**: `#FFFFFF` framed by a fine border (`1px solid rgba(226, 232, 240, 0.8)`) and high-diffusion shadow: `0 20px 25px -5px rgba(11, 31, 58, 0.1), 0 8px 10px -6px rgba(11, 31, 58, 0.06)`.
- **AI Highlight Elevation**: AI-driven surfaces utilize a distinct dual shadow: an outer soft violet aura (`0 0 0 1px rgba(124, 58, 237, 0.15), 0 8px 20px -4px rgba(124, 58, 237, 0.12)`).

## Shapes

The design system implements a refined **Level 2 (Rounded)** curvature rhythm. 

- Standard inputs, buttons, and status chips use `8px` (`0.5rem`).
- Primary content modules, schedule blocks, and route summary cards utilize `16px` (`1rem`).
- Floating utility drawers, booking modals, and seat map dialogs leverage `24px` (`1.5rem`).
- Live tracking status capsules and map node pills enforce total circular symmetry (`9999px`).

## Components

### Buttons
- **Primary**: Solid `#155EEF` background with `#FFFFFF` text. Hover shifts to `#1D4ED8`. Focus state presents a clean 3px ring (`rgba(21, 94, 239, 0.25)`).
- **Secondary / Ghost**: White background with `#E2E8F0` border and `#0B1F3A` typography. Hover shifts to `#F1F5F9`.
- **AI Assist Action**: Solid `#7C3AED` or dynamic gradient (`#7C3AED` to `#6D28D9`), paired with a leading sparkle icon. Hover intensifies surface luminosity with subtle purple ambient glow.

### Status Pills & Badges
- Highly scannable, compact pill shapes (`rounded-full`) with uppercase or semi-bold micro-labels (`label-sm`).
- **On-Time**: Emerald background tint (`#ECFDF5`), bold emerald text (`#047857`), solid pulsing status dot (`#10B981`).
- **Delayed**: Amber background tint (`#FFFBEB`), amber text (`#B45309`), solid amber dot (`#F59E0B`).
- **Live AI Prediction**: Light violet tint (`#F5F3FF`), violet text (`#6D28D9`), accompanied by a dynamic predictive icon.

### Form Inputs & Search Matrix
- Pure white background, `1px solid #CBD5E1` border, 8px corner radius.
- Leading icons for origins (ring icon) and destinations (pin icon) tied together by a vertical connecting line.
- Focus transitions boundary to `#155EEF` with a soft blue exterior ring.

### Seat Selection Matrix
- **Available Seat**: Ergonomic chair silhouette with an emerald border (`#10B981`), transparent/white interior, interactive hover scaling (1.05x) and `#ECFDF5` fill.
- **Selected Seat**: Deep Navy Blue (`#0B1F3A`) or Transit Blue (`#155EEF`) solid fill with white checkmark overlay.
- **Unavailable / Reserved Seat**: Disabled appearance, flat `#F1F5F9` fill, `#CBD5E1` border, slash accent.
- Grouping: 2x2 or 2x1 grid structures separated by a realistic walking aisle with clear row/column identifier typography.

### Route & Tracking Cards
- Layered white cards with sharp timeline markers connecting departure, intermediate stops, and arrival times.
- Real-time bus tracker nodes animate along a progress rail styled with `#38BDF8` pulses and vehicle direction arrows.