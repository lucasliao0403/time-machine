# TimeMachine UI Style Guide

## Overview

This document defines the standardized design system for the TimeMachine Web UI. The design emphasizes ultra-dark minimalism with consistent glass morphism effects, restrained animations, and professional aesthetics optimized for AI/ML development workflows.

## Design Philosophy

### Core Principles
- **Ultra-Dark Minimalism**: Pure grayscale theme eliminating visual distractions
- **Consistent Glass Morphism**: Unified `apple-glass-card` treatment across all components
- **Restrained Animations**: Minimal, purposeful interactions that enhance rather than distract
- **Standardized Typography**: Consistent text hierarchy using `text-gray-*` nomenclature
- **Professional Aesthetics**: Clean, modern interface with consistent interaction patterns

### Visual Language
- **Pure Grayscale Palette**: Complete elimination of color distractions
- **Unified Glass Effects**: Single glass card style (`apple-glass-card`) used throughout
- **Consistent Borders**: Standardized `border-gray-300/20` for all glass elements
- **Restrained Motion**: Simple transitions focusing on essential feedback only
- **Standardized Text Colors**: Clear hierarchy using `text-gray-100/200/300/400`

## Color System

### Text Color Hierarchy
```css
text-gray-100    /* Primary headings and important text */
text-gray-200    /* Secondary headings and button text */
text-gray-300    /* Body text and descriptions */
text-gray-400    /* Muted text, icons, and help text */
```

### Border System
```css
border-gray-300/20    /* Standard border for all glass elements */
border-gray-300/30    /* Focus states and active elements */
border-gray-300/40    /* Enhanced focus for form inputs */
```

### Background System
```css
apple-glass-card              /* Primary glass morphism effect */
hover:bg-gray-300/10         /* Standard hover state */
focus:ring-gray-300/30       /* Focus ring for form elements */
```

## Glass Morphism System

### Primary Glass Card
```css
.apple-glass-card {
  background: rgba(156, 163, 175, 0.12);
  backdrop-filter: blur(60px);
  border: 1px solid rgba(156, 163, 175, 0.20);
  /* Additional shadow and styling layers */
}
```

**Usage Guidelines:**
- Use `apple-glass-card` for ALL cards, panels, and containers
- Add `border border-gray-300/20` for consistent edge definition
- Apply `hover:bg-gray-300/10` for interactive elements

### Prohibited Variations
- ❌ No `frosted-card`, `glass-card`, or other glass variants
- ❌ No custom background opacities or blur values
- ❌ No colored borders or backgrounds

## Typography Standards

### Font System
```css
font-family: 'Inter', sans-serif;           /* Primary UI font */
font-family: 'JetBrains Mono', monospace;   /* Code/data display */
```

### Font Weight Standards
```css
font-medium     /* Minimum weight for body text (500) */
font-semibold   /* Headings and emphasis (600) */
```

### Text Scale Hierarchy
```css
text-xs     /* 12px - Helper text, metadata */
text-sm     /* 14px - Body text, descriptions */
text-base   /* 16px - Standard content */
text-lg     /* 18px - Subheadings */
text-xl     /* 20px - Section headings */
text-2xl    /* 24px - Page titles */
text-3xl    /* 30px - Large metrics/stats */
```

## Button Standards

### Primary Button Pattern
```tsx
<button className="inline-flex items-center px-4 py-2 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10">
  <Icon className="h-4 w-4 mr-2" />
  Button Text
</button>
```

### Button Specifications
- **Background**: Always `apple-glass-card`
- **Border**: Always `border border-gray-300/20`
- **Text**: Always `text-gray-200`
- **Radius**: Always `rounded-2xl`
- **Hover**: Always `hover:bg-gray-300/10`
- **Transition**: Always `transition-all`

### Disabled State
```tsx
<button 
  disabled 
  className="... disabled:opacity-50 disabled:cursor-not-allowed"
>
```

## Form Input Standards

### Input Field Pattern
```tsx
<input className="w-full px-3 py-2 apple-glass-card border border-gray-300/20 rounded-md text-gray-200 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-300/30 focus:border-gray-300/40" />
```

### Input Specifications
- **Background**: Always `apple-glass-card`
- **Border**: `border border-gray-300/20`
- **Text**: `text-gray-200`
- **Placeholder**: `placeholder:text-gray-500`
- **Focus**: `focus:ring-gray-300/30 focus:border-gray-300/40`

## Animation Standards

### Approved Animations
```css
/* Simple transitions only */
transition-all              /* Standard transition for interactive elements */
duration: 0.15s             /* Maximum transition duration */

/* Loading states */
animate-spin                /* For loading indicators only */
```

### Animation Guidelines
1. **Minimal Motion**: No scaling, movement, or rotation on hover
2. **Essential Feedback Only**: Animations serve functional purposes
3. **Fast Transitions**: Maximum 0.15s duration
4. **Static Elements**: Headers, content, and stats remain stationary

### Prohibited Animations
- ❌ `whileHover={{ scale: 1.02 }}`
- ❌ `whileHover={{ y: -2 }}`
- ❌ Spring animations
- ❌ Stagger effects
- ❌ Complex motion variants
- ❌ Bounce or elastic effects

## Component Patterns

### Empty State Pattern
```tsx
<div className="text-center py-16">
  <div className="apple-glass-card p-12 max-w-md mx-auto">
    <Icon className="h-16 w-16 text-gray-400 mx-auto mb-6" />
    <h3 className="text-xl font-semibold text-gray-100 mb-3">No Data Found</h3>
    <p className="text-gray-300 mb-6 leading-relaxed font-medium">
      Description of empty state and next steps.
    </p>
    <button className="inline-flex items-center px-6 py-3 apple-glass-card text-gray-200 rounded-2xl transition-all border border-gray-300/20 hover:bg-gray-300/10">
      <Icon className="h-5 w-5 mr-2" />
      Action Button
    </button>
  </div>
</div>
```

### Error State Pattern
```tsx
<div className="apple-glass-card border border-gray-300/20 rounded-lg p-4">
  <div className="flex items-center">
    <AlertCircle className="h-5 w-5 text-gray-400" />
    <span className="ml-2 text-gray-100">{error}</span>
  </div>
  <button className="mt-2 apple-glass-card text-sm text-gray-200 border border-gray-300/20 hover:bg-gray-300/10 transition-all px-3 py-1 rounded-xl">
    Try again
  </button>
</div>
```

### Loading State Pattern
```tsx
<div className="flex items-center justify-center py-16">
  <div className="apple-glass-card px-8 py-6 text-center">
    <RefreshCw className="h-8 w-8 animate-spin text-gray-200 mx-auto mb-3" />
    <span className="text-gray-100 font-medium">Loading...</span>
  </div>
</div>
```

### Card Content Pattern
```tsx
<div className="apple-glass-card p-6">
  <h3 className="text-lg font-semibold text-gray-100 mb-4">Card Title</h3>
  <p className="text-gray-300 font-medium">Card content...</p>
</div>
```

## Layout Standards

### Container System
```css
max-w-7xl mx-auto          /* Main content container */
px-4 sm:px-6 lg:px-8      /* Responsive padding */
space-y-6                 /* Standard vertical spacing */
gap-6                     /* Standard grid gap */
```

### Grid System
```css
grid-cols-1               /* Mobile default */
md:grid-cols-2           /* Tablet */
lg:grid-cols-3           /* Desktop */
xl:grid-cols-4           /* Large desktop */
```

### Spacing Scale
```css
space-y-3    /* Tight spacing - list items */
space-y-4    /* Standard spacing - related elements */
space-y-6    /* Comfortable spacing - sections */
space-y-8    /* Loose spacing - major sections */
```

## Interaction States

### Hover States
- **Background Change Only**: `hover:bg-gray-300/10`
- **No Scaling**: Elements maintain fixed size
- **No Movement**: Elements stay in position
- **Fast Transitions**: 0.15s maximum

### Focus States
- **Rings**: `focus:ring-2 focus:ring-gray-300/30`
- **Border Enhancement**: `focus:border-gray-300/40`
- **Outline**: `focus:outline-none` (replaced by ring)

### Active/Selected States
- **Background**: Subtle background enhancement
- **Border**: Enhanced border opacity
- **Text**: Maintain color hierarchy

## Icon Standards

### Icon Usage
```tsx
<Icon className="h-4 w-4 text-gray-300" />     /* Small icons */
<Icon className="h-5 w-5 text-gray-400" />     /* Medium icons */
<Icon className="h-6 w-6 text-gray-300" />     /* Large icons */
<Icon className="h-16 w-16 text-gray-400" />   /* Empty state icons */
```

### Icon Color Guidelines
- **Functional Icons**: `text-gray-300` (medium contrast)
- **Decorative Icons**: `text-gray-400` (lower contrast)
- **Interactive Icons**: `text-gray-300` (in buttons)

## Responsive Design

### Breakpoint Strategy
```css
sm: 640px    /* Small tablets */
md: 768px    /* Tablets and small laptops */
lg: 1024px   /* Laptops and desktops */
xl: 1280px   /* Large desktops */
```

### Mobile-First Approach
- Start with single-column layouts
- Progressive enhancement for larger screens
- Maintain glass effects across all devices
- Ensure touch-friendly interactive elements

## Accessibility Standards

### Color Contrast
- Minimum WCAG AA compliance
- `text-gray-100` for highest contrast needs
- `text-gray-200` for standard readability
- `text-gray-300` for secondary information
- `text-gray-400` for muted content only

### Interactive Elements
- Minimum 44px touch targets
- Clear focus indicators
- Semantic HTML structure
- Proper ARIA labels where needed

## Implementation Guidelines

### CSS Organization
```css
/* Class order priority */
1. Layout (display, position, grid, flex)
2. Sizing (width, height, padding, margin)
3. Background (apple-glass-card)
4. Border (border-gray-300/20)
5. Typography (text-gray-*, font-*)
6. Effects (transition-all, hover:)
```

### Component Consistency Checklist
- ✅ Uses `apple-glass-card` for containers
- ✅ Uses `text-gray-*` color hierarchy
- ✅ Uses standardized borders (`border-gray-300/20`)
- ✅ Uses minimal transitions only (`transition-all`)
- ✅ Follows button pattern for interactive elements
- ✅ Uses `font-medium` minimum for text weight
- ✅ Implements consistent spacing (`space-y-*`, `gap-*`)

### Quality Assurance
1. **Visual Consistency**: All cards look identical
2. **Interactive Consistency**: All buttons behave identically
3. **Text Hierarchy**: Clear distinction between text levels
4. **Animation Restraint**: No distracting motion
5. **Color Compliance**: Only approved gray scale values

## Maintenance Guidelines

### Adding New Components
1. Start with `apple-glass-card` container
2. Apply standard text color hierarchy
3. Use approved button patterns
4. Implement minimal transitions only
5. Test across all breakpoints

### Updating Existing Components
1. Replace custom glass styles with `apple-glass-card`
2. Standardize text colors to `text-gray-*`
3. Remove complex animations
4. Update buttons to standard pattern
5. Verify consistency with other components

### Design System Evolution
- New patterns require documentation updates
- Color additions must fit grayscale theme
- Animation additions must serve functional purposes
- All changes should enhance, not complicate, the system

---

*This style guide enforces consistent, professional aesthetics across the entire TimeMachine interface. All components should follow these patterns for optimal user experience and maintainability.*