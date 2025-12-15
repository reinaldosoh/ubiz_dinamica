# 🎨 Design System - NETCOM CRM

## 📐 1. Cores

```css
/* Primary Colors */
--primary-green: #4ECDC4;
--primary-green-dark: #3DB8AF;
--primary-green-light: #6FD9D1;

/* Background Colors */
--bg-primary: #1A1D23;
--bg-secondary: #252930;
--bg-tertiary: #2D3139;
--bg-card: #1E2128;
--bg-modal: #1C1F26;

/* Text Colors */
--text-primary: #FFFFFF;
--text-secondary: #9CA3AF;
--text-tertiary: #6B7280;
--text-placeholder: #4B5563;

/* Status Colors */
--status-enviada: #F59E0B;
--status-success: #4ECDC4;
--status-error: #EF4444;
--status-warning: #F59E0B;

/* Border Colors */
--border-primary: #374151;
--border-secondary: #2D3139;
--border-active: #4ECDC4;

/* Overlay */
--overlay: rgba(0, 0, 0, 0.7);
```

---

## 🔤 2. Tipografia

```css
/* Font Family */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

---

## 📏 3. Espaçamento

```css
/* Spacing Scale */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

---

## 🔘 4. Componentes

### Buttons

```css
/* Primary Button */
.btn-primary {
  background: var(--primary-green);
  color: var(--bg-primary);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--primary-green-dark);
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  border: 1px solid var(--border-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  border-color: var(--primary-green);
  color: var(--primary-green);
}

/* Icon Button */
.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--bg-secondary);
}
```

### Cards

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-secondary);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
}

.card:hover {
  border-color: var(--border-active);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.card-body {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-secondary);
}
```

### Inputs

```css
.input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 14px;
  width: 100%;
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
}

.input::placeholder {
  color: var(--text-placeholder);
  font-style: italic;
}

.input-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.input-group {
  margin-bottom: 20px;
}

.input-error {
  border-color: var(--status-error);
}

.input-error-message {
  color: var(--status-error);
  font-size: 12px;
  margin-top: 4px;
}
```

### Select / Dropdown

```css
.select {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 14px;
  width: 100%;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%239CA3AF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 40px;
}

.select:focus {
  outline: none;
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
}
```

### Modal

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  animation: fadeIn 0.2s ease;
}

.modal {
  background: var(--bg-modal);
  border: 1px solid var(--border-primary);
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-body {
  margin-bottom: 24px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
```

### Badges/Tags

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-enviada {
  background: rgba(245, 158, 11, 0.2);
  color: var(--status-enviada);
}

.badge-success {
  background: rgba(78, 205, 196, 0.2);
  color: var(--status-success);
}

.badge-error {
  background: rgba(239, 68, 68, 0.2);
  color: var(--status-error);
}

.badge-neutral {
  background: rgba(156, 163, 175, 0.2);
  color: var(--text-secondary);
}
```

### Step Indicators

```css
.steps-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.step:hover {
  border-color: var(--border-active);
}

.step.active {
  border-color: var(--primary-green);
  background: rgba(78, 205, 196, 0.05);
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  flex-shrink: 0;
}

.step.active .step-icon {
  background: var(--primary-green);
  color: var(--bg-primary);
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 2px;
}
```

### Tabs

```css
.tabs {
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--border-secondary);
  margin-bottom: 24px;
}

.tab {
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.tab:hover {
  color: var(--text-primary);
}

.tab.active {
  color: var(--primary-green);
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary-green);
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  font-size: 12px;
  font-weight: 600;
  margin-left: 8px;
}

.tab.active .tab-badge {
  background: rgba(78, 205, 196, 0.2);
  color: var(--primary-green);
}
```

### Avatar

```css
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-sm {
  width: 32px;
  height: 32px;
}

.avatar-lg {
  width: 56px;
  height: 56px;
}

.avatar-group {
  display: flex;
  align-items: center;
}

.avatar-group .avatar {
  margin-left: -8px;
  border: 2px solid var(--bg-primary);
}

.avatar-group .avatar:first-child {
  margin-left: 0;
}
```

### Divider

```css
.divider {
  height: 1px;
  background: var(--border-secondary);
  margin: 24px 0;
}

.divider-vertical {
  width: 1px;
  height: 100%;
  background: var(--border-secondary);
  margin: 0 16px;
}
```

### Tooltip

```css
.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip-content {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-primary);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 100;
}

.tooltip:hover .tooltip-content {
  opacity: 1;
}

.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: var(--border-primary);
}
```

### Search Input

```css
.search-input-wrapper {
  position: relative;
}

.search-input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  padding: 12px 16px 12px 44px;
  color: var(--text-primary);
  font-size: 14px;
  width: 100%;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-placeholder);
  pointer-events: none;
}
```

### Checkbox

```css
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-primary);
  border-radius: 4px;
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox:checked {
  background: var(--primary-green);
  border-color: var(--primary-green);
}

.checkbox:checked::after {
  content: '✓';
  color: var(--bg-primary);
  font-size: 14px;
  font-weight: bold;
}

.checkbox-label {
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
}
```

### Reward Badges

```css
.reward-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  position: relative;
}

.reward-badge-green {
  background: var(--primary-green);
  color: var(--bg-primary);
}

.reward-badge-orange {
  background: var(--status-enviada);
  color: var(--bg-primary);
}

.reward-badge::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid currentColor;
  opacity: 0.3;
}
```

---

## 🎯 5. Ícones & Ilustrações

### Success Icon

```css
.icon-success {
  width: 80px;
  height: 80px;
  background: var(--primary-green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin: 0 auto;
}

.icon-success::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px dashed var(--primary-green);
  animation: rotate 20s linear infinite;
}

.icon-success svg {
  width: 40px;
  height: 40px;
  color: white;
  z-index: 1;
}
```

### Icon Sizes

```css
.icon-xs { width: 16px; height: 16px; }
.icon-sm { width: 20px; height: 20px; }
.icon-md { width: 24px; height: 24px; }
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 40px; height: 40px; }
```

---

## 📱 6. Responsividade

```css
/* Breakpoints */
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;

/* Mobile First Approach */
@media (max-width: 640px) {
  .modal {
    padding: 20px;
    width: 95%;
    border-radius: 12px;
  }

  .btn-primary, .btn-secondary {
    width: 100%;
  }

  .card {
    padding: 16px;
  }

  .steps-container {
    gap: 8px;
  }

  .step {
    padding: 12px;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .modal-footer .btn-primary,
  .modal-footer .btn-secondary {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .tab {
    white-space: nowrap;
  }
}

/* Container */
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 16px;
}

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}
```

---

## ⚡ 7. Animações

```css
/* Transitions */
--transition-fast: 0.15s ease;
--transition-base: 0.2s ease;
--transition-slow: 0.3s ease;

/* Hover Effects */
.hover-lift {
  transition: transform var(--transition-base);
}

.hover-lift:hover {
  transform: translateY(-2px);
}

.hover-scale {
  transition: transform var(--transition-base);
}

.hover-scale:hover {
  transform: scale(1.05);
}

/* Fade In */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

/* Slide Up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-up {
  animation: slideUp 0.3s ease;
}

/* Slide Down */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-down {
  animation: slideDown 0.3s ease;
}

/* Rotate */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.rotate {
  animation: rotate 20s linear infinite;
}

/* Pulse */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Bounce */
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.bounce {
  animation: bounce 1s infinite;
}

/* Spin */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin 1s linear infinite;
}
```

---

## 🎨 8. Layout Utilities

```css
/* Display */
.flex { display: flex; }
.inline-flex { display: inline-flex; }
.grid { display: grid; }
.hidden { display: none; }
.block { display: block; }
.inline-block { display: inline-block; }

/* Flex Direction */
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }

/* Flex Wrap */
.flex-wrap { flex-wrap: wrap; }
.flex-nowrap { flex-wrap: nowrap; }

/* Justify Content */
.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }

/* Align Items */
.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }
.items-stretch { align-items: stretch; }

/* Gap */
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-6 { gap: var(--space-6); }
.gap-8 { gap: var(--space-8); }

/* Padding */
.p-0 { padding: 0; }
.p-2 { padding: var(--space-2); }
.p-4 { padding: var(--space-4); }
.p-6 { padding: var(--space-6); }
.p-8 { padding: var(--space-8); }

/* Margin */
.m-0 { margin: 0; }
.m-2 { margin: var(--space-2); }
.m-4 { margin: var(--space-4); }
.m-6 { margin: var(--space-6); }
.m-8 { margin: var(--space-8); }

/* Margin Auto */
.mx-auto { margin-left: auto; margin-right: auto; }
.my-auto { margin-top: auto; margin-bottom: auto; }

/* Width */
.w-full { width: 100%; }
.w-auto { width: auto; }
.w-fit { width: fit-content; }

/* Height */
.h-full { height: 100%; }
.h-auto { height: auto; }
.h-screen { height: 100vh; }

/* Text Align */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

/* Font Weight */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* Text Transform */
.uppercase { text-transform: uppercase; }
.lowercase { text-transform: lowercase; }
.capitalize { text-transform: capitalize; }

/* Overflow */
.overflow-hidden { overflow: hidden; }
.overflow-auto { overflow: auto; }
.overflow-scroll { overflow: scroll; }

/* Position */
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }

/* Z-Index */
.z-0 { z-index: 0; }
.z-10 { z-index: 10; }
.z-20 { z-index: 20; }
.z-30 { z-index: 30; }
.z-40 { z-index: 40; }
.z-50 { z-index: 50; }

/* Cursor */
.cursor-pointer { cursor: pointer; }
.cursor-not-allowed { cursor: not-allowed; }
.cursor-default { cursor: default; }

/* Border Radius */
.rounded-none { border-radius: 0; }
.rounded-sm { border-radius: 4px; }
.rounded { border-radius: 8px; }
.rounded-lg { border-radius: 12px; }
.rounded-xl { border-radius: 16px; }
.rounded-full { border-radius: 9999px; }

/* Shadow */
.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.shadow {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

---

## 📦 9. Arquivo CSS Completo (Base)

```css
/* ========================================
   NETCOM CRM - Design System
   ======================================== */

:root {
  /* Colors */
  --primary-green: #4ECDC4;
  --primary-green-dark: #3DB8AF;
  --primary-green-light: #6FD9D1;

  --bg-primary: #1A1D23;
  --bg-secondary: #252930;
  --bg-tertiary: #2D3139;
  --bg-card: #1E2128;
  --bg-modal: #1C1F26;

  --text-primary: #FFFFFF;
  --text-secondary: #9CA3AF;
  --text-tertiary: #6B7280;
  --text-placeholder: #4B5563;

  --status-enviada: #F59E0B;
  --status-success: #4ECDC4;
  --status-error: #EF4444;
  --status-warning: #F59E0B;

  --border-primary: #374151;
  --border-secondary: #2D3139;
  --border-active: #4ECDC4;

  --overlay: rgba(0, 0, 0, 0.7);

  /* Typography */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;

  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}

/* Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Base Styles */
body {
  font-family: var(--font-primary);
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: var(--leading-normal);
  font-size: var(--text-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--border-primary);
}

/* Selection */
::selection {
  background: var(--primary-green);
  color: var(--bg-primary);
}

/* Focus Visible */
:focus-visible {
  outline: 2px solid var(--primary-green);
  outline-offset: 2px;
}

/* Links */
a {
  color: var(--primary-green);
  text-decoration: none;
  transition: color var(--transition-base);
}

a:hover {
  color: var(--primary-green-light);
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  color: var(--text-primary);
}

h1 { font-size: var(--text-3xl); }
h2 { font-size: var(--text-2xl); }
h3 { font-size: var(--text-xl); }
h4 { font-size: var(--text-lg); }
h5 { font-size: var(--text-base); }
h6 { font-size: var(--text-sm); }

/* Paragraphs */
p {
  margin-bottom: var(--space-4);
  color: var(--text-secondary);
}

/* Lists */
ul, ol {
  padding-left: var(--space-6);
  margin-bottom: var(--space-4);
}

li {
  margin-bottom: var(--space-2);
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

/* Buttons Reset */
button {
  font-family: inherit;
  font-size: inherit;
}
```

---

## 🚀 10. Exemplos de Uso

### Exemplo: Card de Fatura

```html
<div class="card">
  <div class="card-header">
    <div>
      <span class="badge badge-enviada">FATURA</span>
      <h3 class="card-title">Padaria Bom Vivant</h3>
      <p class="card-subtitle">ID 28063</p>
    </div>
  </div>

  <div class="card-body">
    <div class="flex items-center gap-2">
      <img src="avatar.jpg" alt="Junior Costa" class="avatar avatar-sm">
      <span class="text-sm">Junior Costa</span>
    </div>
  </div>

  <div class="card-footer">
    <span class="text-sm text-secondary">R$22.000,00</span>
  </div>
</div>
```

### Exemplo: Modal de Sucesso

```html
<div class="modal-overlay">
  <div class="modal">
    <div class="icon-success">
      <svg><!-- checkmark icon --></svg>
    </div>

    <h2 class="modal-title text-center">Solicitação realizada com sucesso!</h2>

    <p class="text-center text-secondary">
      A solicitação passará por aprovação e assim que confirmada, a
      quantia definida irá para uma conta com CPF do colaborador.
    </p>

    <button class="btn-primary w-full">Fechar</button>
  </div>
</div>
```

### Exemplo: Formulário com Steps

```html
<div class="modal">
  <div class="modal-header">
    <h2 class="modal-title">Criar nova missão</h2>
    <button class="modal-close">×</button>
  </div>

  <div class="modal-body">
    <div class="steps-container">
      <div class="step active">
        <div class="step-icon">⚙️</div>
        <div class="step-content">
          <div class="step-title">Etapa 1</div>
          <div class="step-description">Informações básicas</div>
        </div>
      </div>

      <div class="step">
        <div class="step-icon">📋</div>
        <div class="step-content">
          <div class="step-title">Etapa 2</div>
          <div class="step-description">Tarefas a fazer</div>
        </div>
      </div>
    </div>

    <div class="input-group">
      <label class="input-label">Título da missão</label>
      <input type="text" class="input" placeholder="Ex: Ligar para atendente">
    </div>
  </div>

  <div class="modal-footer">
    <button class="btn-secondary">Voltar</button>
    <button class="btn-primary">Avançar</button>
  </div>
</div>
```

---

## 📝 11. Notas de Implementação

### Fontes
Adicione no `<head>` do HTML:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Ícones
Recomendado usar uma biblioteca de ícones como:
- [Lucide Icons](https://lucide.dev/)
- [Heroicons](https://heroicons.com/)
- [Phosphor Icons](https://phosphoricons.com/)

### Acessibilidade
- Sempre use labels em inputs
- Adicione `aria-label` em botões de ícone
- Use `role` apropriado em elementos interativos
- Mantenha contraste adequado (WCAG AA)
- Suporte navegação por teclado

### Performance
- Use `will-change` com moderação
- Prefira `transform` e `opacity` para animações
- Lazy load de imagens quando possível
- Minimize uso de `box-shadow` em elementos animados

---

## 🎯 12. Checklist de Implementação

- [ ] Importar fonte Inter
- [ ] Configurar variáveis CSS
- [ ] Implementar reset/base styles
- [ ] Criar componentes de botões
- [ ] Criar componentes de inputs
- [ ] Criar componentes de cards
- [ ] Criar componentes de modais
- [ ] Implementar sistema de cores
- [ ] Implementar sistema de espaçamento
- [ ] Adicionar animações
- [ ] Testar responsividade
- [ ] Validar acessibilidade
- [ ] Otimizar performance

---

**Design System criado para NETCOM CRM**  
Versão 1.0 | 2024
