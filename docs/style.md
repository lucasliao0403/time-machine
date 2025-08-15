# TimeMachine UI Style Guide

## Overview

This document outlines the design system and style conventions for the TimeMachine Web UI. The design emphasizes an ultra-dark, minimalist theme with enhanced glass morphism effects, subtle animations, and professional aesthetics suitable for AI/ML development tools.

## Design Philosophy

### Core Principles
- **Ultra-Dark Minimalism**: A sophisticated pure grayscale theme that eliminates visual distractions
- **Enhanced Glass Morphism**: Prominent translucent elements with strong backdrop blur effects for maximum visual depth
- **Restrained Animations**: Minimal, purposeful micro-interactions that don't distract from content
- **Professional Aesthetics**: Clean, modern interface with Apple-inspired frosted glass elements
- **High Readability**: Enhanced text contrast with medium/semibold font weights

### Visual Language
- **Pure Grayscale**: Elimination of all color distractions for focused workflow
- **Prominent Glass Effects**: Ultra-strong backdrop blur (60-160px) for premium feel
- **Subtle Gradient Flow**: Diagonal background gradient flowing toward bottom-right
- **Minimal Motion**: Reduced animations focusing only on essential feedback
- **Enhanced Contrast**: Lighter text weights for improved readability

## Color Palette

### Primary Grayscale System
```css
glass: {
  50: '#9ca3af',    /* Lightest allowed text color */
  100: '#6b7280',   /* Light gray */
  200: '#4b5563',   /* Medium-light gray */
  300: '#374151',   /* Medium gray */
  400: '#1f2937',   /* Medium-dark gray */
  500: '#111827',   /* Dark gray */
  600: '#0f172a',   /* Very dark gray */
  700: '#0d1421',   /* Deeper gray */
  800: '#0a0e1a',   /* Very near black */
  850: '#080b14',   /* Almost black */
  900: '#050711',   /* Deepest black */
  950: '#030409',   /* Pure dark background */
}
```

### Accent Colors (Grayscale Only)
```css
accent: {
  400: '#6b7280',   /* Medium light gray */
  500: '#4b5563',   /* Medium gray */
  600: '#374151',   /* Dark gray */
  700: '#1f2937',   /* Darker gray */
  800: '#111827',   /* Very dark gray */
  900: '#0f172a',   /* Extra dark gray */
}
```

### Semantic Colors (Desaturated Grayscale)
```css
success: '#6b7280',  /* Gray success states */
warning: '#9ca3af',  /* Gray warning states */
error: '#6b7280',    /* Gray error states */
info: '#6b7280',     /* Gray info states */
```

### Text Color System
```css
--text-primary: 209 213 219;   /* Ultra-light for maximum readability */
--text-secondary: 156 163 175; /* Light gray */
--text-muted: 107 114 128;     /* Medium gray */
```

## Background System

### Universal Gradient
```css
/* Main diagonal gradient (top-left to bottom-right) */
background: linear-gradient(135deg, rgba(15,23,42,1), rgba(3,4,9,1));

/* Subtle ambient overlays */
radial-gradient(ellipse_at_top_left, rgba(107,114,128,0.04), transparent 60%)
radial-gradient(ellipse_at_bottom_right, rgba(107,114,128,0.03), transparent 70%)
```

### Glass Background Variables
```css
--glass-bg: rgba(156, 163, 175, 0.12);
--glass-border: rgba(156, 163, 175, 0.20);
--frosted-bg: rgba(156, 163, 175, 0.18);
--frosted-border: rgba(156, 163, 175, 0.25);
--ultra-glass-bg: rgba(156, 163, 175, 0.25);
--ultra-glass-border: rgba(156, 163, 175, 0.35);
```

## Glass Morphism System

### Standard Glass Classes

#### `.glass`
- **Background**: 12% gray transparency
- **Backdrop Blur**: 40px
- **Border**: 20% gray transparency
- **Use Case**: Basic glass elements

#### `.glass-card`
- **Background**: 12% gray transparency
- **Backdrop Blur**: 60px
- **Border**: 20% gray transparency
- **Shadows**: Multiple layered shadows with inset highlights
- **Use Case**: Content cards

#### `.frosted-card`
- **Background**: 18% gray transparency
- **Backdrop Blur**: 80px
- **Border**: 25% gray transparency
- **Shadows**: Enhanced layered shadows
- **Use Case**: Important content sections

#### `.ultra-glass-card`
- **Background**: 25% gray transparency
- **Backdrop Blur**: 100px
- **Border**: 35% gray transparency (2px width)
- **Shadows**: Maximum depth with multiple shadow layers
- **Use Case**: Premium content displays

#### `.minimal-card`
- **Background**: 3% gray transparency
- **Backdrop Blur**: 32px
- **Border**: 6% gray transparency
- **Use Case**: Subtle containers, list items

### Backdrop Blur Levels
```css
backdrop-blur-32  /* 32px - minimal */
backdrop-blur-60  /* 60px - standard */
backdrop-blur-80  /* 80px - frosted */
backdrop-blur-100 /* 100px - ultra */
backdrop-blur-120 /* 120px - navigation */
```

## Typography

### Font System
```css
font-family: 'Inter', sans-serif;           /* Primary UI font */
font-family: 'JetBrains Mono', monospace;   /* Code/monospace */
```

### Font Weights (Enhanced for Readability)
- **font-medium**: 500 - Standard body text
- **font-semibold**: 600 - Headings and emphasis
- **font-light**: 300 - Minimal use only
- **font-normal**: 400 - Deprecated, prefer font-medium

### Text Scale
```css
text-xs     /* 12px - Secondary info */
text-sm     /* 14px - Body text */
text-base   /* 16px - Standard */
text-lg     /* 18px - Emphasized */
text-xl     /* 20px - Subheadings */
text-2xl    /* 24px - Section headings */
text-3xl    /* 30px - Page titles */
```

### Text Color Usage
```css
text-gray-100    /* Primary text - highest contrast */
text-gray-200    /* Secondary text - good contrast */
text-gray-300    /* Tertiary text - medium contrast */
text-gray-400    /* Muted text - lower contrast */
text-gray-500    /* Disabled text - minimal contrast */
```

## Animation System

### Restrained Animation Philosophy
- **Minimal Hover Effects**: No scaling, growing, or movement on hover
- **Essential Feedback Only**: Animations only for meaningful state changes
- **Smooth Transitions**: Fast, linear transitions (0.15-0.2s duration)
- **Static Elements**: Headers, stats, and content remain still on hover

### Approved Animations

#### Tab Transitions
```css
transition: { type: "tween", duration: 0.2, ease: "easeOut" }
```

#### Gentle Ambient Effects
```css
/* Clock icon subtle glow - only animated element */
animate: { scale: [1, 1.1, 1], opacity: [0.2, 0.4, 0.2] }
transition: { duration: 3, repeat: Infinity, ease: "easeInOut" }
```

#### Loading States
```css
/* Fade in only */
initial: { opacity: 0 }
animate: { opacity: 1 }
transition: { duration: 0.3 }
```

### Prohibited Animations
- ❌ Hover scaling (`whileHover: { scale: 1.02 }`)
- ❌ Hover movement (`whileHover: { y: -2, x: 2 }`)
- ❌ Hover rotation (`whileHover: { rotate: 10 }`)
- ❌ Spring animations (`type: "spring"`)
- ❌ Bounce effects
- ❌ Complex micro-interactions

## Component Patterns

### Header Pattern
```tsx
<header className="sticky top-0 z-40">
  {/* No glass background - blends with universal gradient */}
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {/* Static content - no hover effects */}
  </div>
</header>
```

### Navigation Pattern
```tsx
<nav className="sticky top-[88px] z-30">
  {/* No glass background - seamless with content */}
  <div className="flex space-x-1 py-2">
    {/* Tab buttons with minimal hover feedback */}
  </div>
</nav>
```

### Card Pattern
```tsx
<div className="minimal-card p-6">
  {/* Subtle glass effect for content separation */}
  {/* No hover animations */}
</div>
```

### List Item Pattern
```tsx
<button className="w-full text-left px-6 py-5 hover:bg-gray-300/5">
  {/* Minimal hover background change only */}
  {/* No movement or scaling */}
</button>
```

## Interaction States

### Hover States
- **Background Only**: Subtle background color changes
- **No Scaling**: Elements remain fixed size
- **No Movement**: Elements stay in position
- **Fast Transitions**: 0.15s duration maximum

### Active States
- **Tab Selection**: Frosted background with border highlight
- **Button Press**: Minimal feedback
- **Focus States**: Subtle outline or background change

### Disabled States
- **Reduced Opacity**: 50% opacity for disabled elements
- **Muted Colors**: Gray-500 text color
- **No Interactions**: cursor-not-allowed

## Layout System

### Container Widths
```css
max-w-7xl mx-auto    /* Main content container */
px-4 sm:px-6 lg:px-8 /* Responsive padding */
```

### Spacing Scale
```css
space-x-1   /* 4px - Tight spacing */
space-x-2   /* 8px - Close elements */
space-x-4   /* 16px - Standard spacing */
space-x-5   /* 20px - Comfortable spacing */
space-x-6   /* 24px - Loose spacing */
```

### Z-Index Layers
```css
z-10    /* Content layer */
z-30    /* Navigation */
z-40    /* Header */
z-50    /* Modals/overlays */
```

## Responsive Design

### Breakpoints
```css
sm: 640px   /* Small devices */
md: 768px   /* Medium devices */
lg: 1024px  /* Large devices */
xl: 1280px  /* Extra large */
2xl: 1536px /* 2X Extra large */
```

### Grid System
```css
grid-cols-1           /* Mobile default */
md:grid-cols-2        /* Tablet */
lg:grid-cols-3        /* Desktop */
xl:grid-cols-4        /* Large desktop */
```

## Best Practices

### Glass Effect Usage
1. **Layer Appropriately**: More important content gets stronger glass effects
2. **Avoid Over-Glass**: Not every element needs glass treatment
3. **Consider Performance**: Backdrop-blur is GPU intensive
4. **Test Contrast**: Ensure text remains readable over glass

### Animation Guidelines
1. **Less is More**: Minimal animations for professional feel
2. **Purposeful Motion**: Every animation should serve a function
3. **Performance First**: Avoid complex animations that impact performance
4. **Accessibility**: Respect user motion preferences

### Color Usage
1. **Grayscale Only**: No color distractions from content
2. **High Contrast**: Ensure accessibility standards
3. **Consistent Hierarchy**: Lighter colors for more important text
4. **Semantic Consistency**: Use same grays for similar functions

### Typography Rules
1. **Medium+ Weights**: Use font-medium as minimum for body text
2. **Semibold Headings**: Use font-semibold for all headings
3. **Consistent Scale**: Stick to defined text sizes
4. **Proper Hierarchy**: Clear visual distinction between text levels

## Implementation Notes

### CSS Custom Properties
All color values use CSS custom properties for consistent theming:
```css
color: rgb(var(--text-primary));
background: var(--glass-bg);
border: 1px solid var(--glass-border);
```

### Tailwind Configuration
The design system is fully integrated with Tailwind CSS for utility-first styling with custom color scales and backdrop-blur extensions.

### Performance Considerations
- Backdrop-blur effects are GPU-accelerated
- Minimal JavaScript animations
- Optimized for smooth 60fps performance
- Progressive enhancement for older browsers

---

*This style guide reflects the current ultra-dark, minimalist design system with enhanced glass morphism and restrained animations. All components should follow these guidelines for consistency and professional appearance.*