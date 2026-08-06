# Style library

The industry profiles name a style ("Glassmorphism + Flat Design"); this file
says what that actually means, and — more usefully — where it breaks.

**Read the "Do not use for" line before the "Best for" line.** A style applied
to the case it explicitly fails at is worse than a plain default, and the
failures here are specific: glassmorphism over a low-contrast background,
neumorphism where accessibility is a requirement, brutalism on a conversion
funnel. The light/dark and performance columns are the other common trap — a
style that only holds up in one theme will fall apart the first time someone
toggles the other.

## Name variants used in the industry profiles

The profiles abbreviate several style names. These are the same styles — look
them up under the canonical name on the right:

| Written in a profile as | Entry in this file |
| --- | --- |
| Claymorphism (for patients) | Claymorphism |
| Dark Mode | Dark Mode (OLED) |
| Data-Dense | Data-Dense Dashboard |
| Feature-Rich | Feature-Rich Showcase |
| Gen Z Chaos | Gen Z Chaos / Maximalism |
| Heat Map & Heatmap | Heat Map & Heatmap Style |
| Hero-Centric | Hero-Centric Design |
| Holographic / HUD | HUD / Sci-Fi FUI |
| Minimal | Minimal & Direct |
| Minimalism, Minimalism (Frame) | Minimalism & Swiss Style |
| Parallax | Parallax Storytelling |
| Real-Time Monitor | Real-Time Monitoring |
| Spatial UI | Spatial UI (VisionOS) |
| Storytelling | Storytelling-Driven |
| Swiss Modernism | Swiss Modernism 2.0 |
| Vibrant & Block | Vibrant & Block-based |

Three labels appear in profiles with **no entry here** — `Clean Science`,
`High Imagery`, and `Masonry Grid`. They are descriptive shorthand rather than
defined styles (the last is a layout). Treat them as a hint about direction and
take the actual style from the profile's other named style; do not go looking
for a definition that does not exist.

## Minimalism & Swiss Style

- **Reads as**: Clean, simple, spacious, functional, white space, high contrast, geometric, sans-serif, grid-based, essential
- **Primary colors**: Monochromatic, Black #000000, White #FFFFFF
- **Secondary colors**: Neutral (Beige #F5F1E8, Grey #808080, Taupe #B38B6D), Primary accent
- **Effects**: Subtle hover (200-250ms), smooth transitions, sharp shadows if any, clear type hierarchy, fast loading
- **Best for**: Enterprise apps, dashboards, documentation sites, SaaS platforms, professional tools
- **Do NOT use for**: Creative portfolios, entertainment, playful brands, artistic experiments
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ◐ Medium
- **Frameworks**: Tailwind 10/10, Bootstrap 9/10, MUI 9/10
- **Era**: 1950s Swiss
- **Complexity**: Low

**CSS that actually produces it**

```css
display: grid, gap: 2rem, font-family: sans-serif, color: #000 or #FFF, max-width: 1200px, clean borders, no box-shadow unless necessary
```

**Token starting point**: `--spacing: 2rem, --border-radius: 0px, --font-weight: 400-700, --shadow: none, --accent-color: single primary only`

**Before calling it done**

- [ ] Grid-based layout 12-16 columns
- [ ] Typography hierarchy clear
- [ ] No unnecessary decorations
- [ ] WCAG AAA contrast verified
- [ ] Mobile responsive grid

## Neumorphism

- **Reads as**: Soft UI, embossed, debossed, convex, concave, light source, subtle depth, rounded (12-16px), monochromatic
- **Primary colors**: Light pastels: Soft Blue #C8E0F4, Soft Pink #F5E0E8, Soft Grey #E8E8E8
- **Secondary colors**: Tints/shades (±30%), gradient subtlety, color harmony
- **Effects**: Soft box-shadow (multiple: -5px -5px 15px, 5px 5px 15px), smooth press (150ms), inner subtle shadow
- **Best for**: Health/wellness apps, meditation platforms, fitness trackers, minimal interaction UIs
- **Do NOT use for**: Complex apps, critical accessibility, data-heavy dashboards, high-contrast required
- **Theme support**: light ✓ Full, dark ◐ Partial
- **Performance**: ⚡ Good
- **Accessibility**: ⚠ Low contrast
- **Mobile**: ✓ Good
- **Conversion**: ◐ Medium
- **Frameworks**: Tailwind 8/10, CSS-in-JS 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
border-radius: 12-16px, box-shadow: -5px -5px 15px rgba(0,0,0,0.1), 5px 5px 15px rgba(255,255,255,0.8), background: linear-gradient(145deg, color1, color2), transform: scale on press
```

**Token starting point**: `--border-radius: 14px, --shadow-soft-1: -5px -5px 15px, --shadow-soft-2: 5px 5px 15px, --color-light: #F5F5F5, --color-primary: single pastel`

**Before calling it done**

- [ ] Rounded corners 12-16px consistent
- [ ] Multiple shadow layers (2-3)
- [ ] Pastel color verified
- [ ] Monochromatic palette checked
- [ ] Press animation smooth 150ms

## Glassmorphism

- **Reads as**: Frosted glass, transparent, blurred background, layered, vibrant background, light source, depth, multi-layer
- **Primary colors**: Translucent white: rgba(255,255,255,0.1-0.3)
- **Secondary colors**: Vibrant: Electric Blue #0080FF, Neon Purple #8B00FF, Vivid Pink #FF1493, Teal #20B2AA
- **Effects**: Backdrop blur (10-20px), subtle border (1px solid rgba white 0.2), light reflection, Z-depth
- **Best for**: Modern SaaS, financial dashboards, high-end corporate, lifestyle apps, modal overlays, navigation
- **Do NOT use for**: Low-contrast backgrounds, critical accessibility, performance-limited, dark text on dark
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Good
- **Accessibility**: ⚠ Ensure 4.5:1
- **Mobile**: ✓ Good
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 9/10, MUI 8/10, Chakra 8/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
backdrop-filter: blur(15px), background: rgba(255, 255, 255, 0.15), border: 1px solid rgba(255,255,255,0.2), -webkit-backdrop-filter: blur(15px), z-index layering for depth
```

**Token starting point**: `--blur-amount: 15px, --glass-opacity: 0.15, --border-color: rgba(255,255,255,0.2), --background: vibrant color, --text-color: light/dark based on BG`

**Before calling it done**

- [ ] Backdrop-filter blur 10-20px
- [ ] Translucent white 15-30% opacity
- [ ] Subtle border 1px light
- [ ] Vibrant background verified
- [ ] Text contrast 4.5:1 checked

## Brutalism

- **Reads as**: Raw, unpolished, stark, high contrast, plain text, default fonts, visible borders, asymmetric, anti-design
- **Primary colors**: Primary: Red #FF0000, Blue #0000FF, Yellow #FFFF00, Black #000000, White #FFFFFF
- **Secondary colors**: Limited: Neon Green #00FF00, Hot Pink #FF00FF, minimal secondary
- **Effects**: No smooth transitions (instant), sharp corners (0px), bold typography (700+), visible grid, large blocks
- **Best for**: Design portfolios, artistic projects, counter-culture brands, editorial/media sites, tech blogs
- **Do NOT use for**: Corporate environments, conservative industries, critical accessibility, customer-facing professional
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Low
- **Frameworks**: Tailwind 10/10, Bootstrap 7/10
- **Era**: 1950s Brutalist
- **Complexity**: Low

**CSS that actually produces it**

```css
border-radius: 0px, transition: none or 0s, font-family: system-ui or monospace, font-weight: 700+, border: visible 2-4px, colors: #FF0000, #0000FF, #FFFF00, #000000, #FFFFFF
```

**Token starting point**: `--border-radius: 0px, --transition-duration: 0s, --font-weight: 700-900, --colors: primary only, --border-style: visible, --grid-visible: true`

**Before calling it done**

- [ ] No border-radius (0px)
- [ ] No transitions (instant)
- [ ] Bold typography (700+)
- [ ] Pure primary colors used
- [ ] Visible grid/borders
- [ ] Asymmetric layout intentional

## 3D & Hyperrealism

- **Reads as**: Depth, realistic textures, 3D models, spatial navigation, tactile, skeuomorphic elements, rich detail, immersive
- **Primary colors**: Deep Navy #001F3F, Forest Green #228B22, Burgundy #800020, Gold #FFD700, Silver #C0C0C0
- **Secondary colors**: Complex gradients (5-10 stops), realistic lighting, shadow variations (20-40% darker)
- **Effects**: WebGL/Three.js 3D, realistic shadows (layers), physics lighting, parallax (3-5 layers), smooth 3D (300-400ms)
- **Best for**: Gaming, product showcase, immersive experiences, high-end e-commerce, architectural viz, VR/AR
- **Do NOT use for**: Low-end mobile, performance-limited, critical accessibility, data tables/forms
- **Theme support**: light ◐ Partial, dark ◐ Partial
- **Performance**: ❌ Poor
- **Accessibility**: ⚠ Not accessible
- **Mobile**: ✗ Low
- **Conversion**: ◐ Medium
- **Frameworks**: Three.js 10/10, R3F 10/10, Babylon.js 10/10
- **Era**: 2020s Modern
- **Complexity**: High

**CSS that actually produces it**

```css
transform: translate3d, perspective: 1000px, WebGL canvas, Three.js/Babylon.js library, box-shadow: complex multi-layer, background: complex gradients, filter: drop-shadow()
```

**Token starting point**: `--perspective: 1000px, --parallax-layers: 5, --lighting-intensity: realistic, --shadow-depth: 20-40%, --animation-duration: 300-400ms`

**Before calling it done**

- [ ] WebGL/Three.js integrated
- [ ] 3D models loaded
- [ ] Parallax 3-5 layers
- [ ] Realistic lighting verified
- [ ] Complex shadows rendered
- [ ] Physics animation smooth 300-400ms

## Vibrant & Block-based

- **Reads as**: Bold, energetic, playful, block layout, geometric shapes, high color contrast, duotone, modern, energetic
- **Primary colors**: Neon Green #39FF14, Electric Purple #BF00FF, Vivid Pink #FF1493, Bright Cyan #00FFFF, Sunburst #FFAA00
- **Secondary colors**: Complementary: Orange #FF7F00, Shocking Pink #FF006E, Lime #CCFF00, triadic schemes
- **Effects**: Large sections (48px+ gaps), animated patterns, bold hover (color shift), scroll-snap, large type (32px+), 200-300ms
- **Best for**: Startups, creative agencies, gaming, social media, youth-focused, entertainment, consumer
- **Do NOT use for**: Financial institutions, healthcare, formal business, government, conservative, elderly
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ◐ Ensure WCAG
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Chakra 9/10, Styled 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
display: flex/grid with large gaps (48px+), font-size: 32px+, background: animated patterns (CSS), color: neon/vibrant colors, animation: continuous pattern movement
```

**Token starting point**: `--block-gap: 48px, --typography-size: 32px+, --color-palette: 4-6 vibrant colors, --animation: continuous pattern, --contrast-ratio: 7:1+`

**Before calling it done**

- [ ] Block layout with 48px+ gaps
- [ ] Large typography 32px+
- [ ] 4-6 vibrant colors max
- [ ] Animated patterns active
- [ ] Scroll-snap enabled
- [ ] High contrast verified (7:1+)

## Dark Mode (OLED)

- **Reads as**: Dark theme, low light, high contrast, deep black, midnight blue, eye-friendly, OLED, night mode, power efficient
- **Primary colors**: Deep Black #000000, Dark Grey #121212, Midnight Blue #0A0E27
- **Secondary colors**: Vibrant accents: Neon Green #39FF14, Electric Blue #0080FF, Gold #FFD700, Plasma Purple #BF00FF
- **Effects**: Minimal glow (text-shadow: 0 0 10px), dark-to-light transitions, low white emission, high readability, visible focus
- **Best for**: Night-mode apps, coding platforms, entertainment, eye-strain prevention, OLED devices, low-light
- **Do NOT use for**: Print-first content, high-brightness outdoor, color-accuracy-critical
- **Theme support**: light ✗ No, dark ✓ Only
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ◐ Low
- **Frameworks**: Tailwind 10/10, MUI 10/10, Chakra 10/10
- **Era**: 2020s Modern
- **Complexity**: Low

**CSS that actually produces it**

```css
background: #000000 or #121212, color: #FFFFFF or #E0E0E0, text-shadow: 0 0 10px neon-color (sparingly), filter: brightness(0.8) if needed, color-scheme: dark
```

**Token starting point**: `--bg-black: #000000, --bg-dark-grey: #121212, --text-primary: #FFFFFF, --accent-neon: neon colors, --glow-effect: minimal, --oled-optimized: true`

**Before calling it done**

- [ ] Deep black #000000 or #121212
- [ ] Vibrant neon accents used
- [ ] Text contrast 7:1+
- [ ] Minimal glow effects
- [ ] OLED power optimization
- [ ] No white (#FFFFFF) background

## Accessible & Ethical

- **Reads as**: High contrast, large text (16px+), keyboard navigation, screen reader friendly, WCAG compliant, focus state, semantic
- **Primary colors**: WCAG AA/AAA (4.5:1 min), simple primary, clear secondary, high luminosity (7:1+)
- **Secondary colors**: Symbol-based colors (not color-only), supporting patterns, inclusive combinations
- **Effects**: Clear focus rings (3-4px), ARIA labels, skip links, responsive design, reduced motion, 44x44px touch targets
- **Best for**: Government, healthcare, education, inclusive products, large audience, legal compliance, public
- **Do NOT use for**: None - accessibility universal
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: All frameworks 10/10
- **Era**: Universal
- **Complexity**: Low

**CSS that actually produces it**

```css
color-contrast: 7:1+, font-size: 16px+, outline: 3-4px on :focus-visible, aria-label, role attributes, @media (prefers-reduced-motion), touch-target: 44x44px, cursor: pointer
```

**Token starting point**: `--contrast-ratio: 7:1, --font-size-min: 16px, --focus-ring: 3-4px, --touch-target: 44x44px, --wcag-level: AAA, --keyboard-accessible: true, --sr-tested: true`

**Before calling it done**

- [ ] WCAG AAA verified
- [ ] 7:1+ contrast checked
- [ ] Keyboard navigation tested
- [ ] Screen reader tested
- [ ] Focus visible 3-4px
- [ ] Semantic HTML used
- [ ] Touch targets 44x44px

## Claymorphism

- **Reads as**: Soft 3D, chunky, playful, toy-like, bubbly, thick borders (3-4px), double shadows, rounded (16-24px)
- **Primary colors**: Pastel: Soft Peach #FDBCB4, Baby Blue #ADD8E6, Mint #98FF98, Lilac #E6E6FA, light BG
- **Secondary colors**: Soft gradients (pastel-to-pastel), light/dark variations (20-30%), gradient subtle
- **Effects**: Inner+outer shadows (subtle, no hard lines), soft press (200ms ease-out), fluffy elements, smooth transitions
- **Best for**: Educational apps, children's apps, SaaS platforms, creative tools, fun-focused, onboarding, casual games
- **Do NOT use for**: Formal corporate, professional services, data-critical, serious/medical, legal apps, finance
- **Theme support**: light ✓ Full, dark ◐ Partial
- **Performance**: ⚡ Good
- **Accessibility**: ⚠ Ensure 4.5:1
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 9/10, CSS-in-JS 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
border-radius: 16-24px, border: 3-4px solid, box-shadow: inset -2px -2px 8px, 4px 4px 8px, background: pastel-gradient, animation: soft bounce (cubic-bezier 0.34, 1.56)
```

**Token starting point**: `--border-radius: 20px, --border-width: 3-4px, --shadow-inner: inset -2px -2px 8px, --shadow-outer: 4px 4px 8px, --color-palette: pastels, --animation: bounce`

**Before calling it done**

- [ ] Border-radius 16-24px
- [ ] Thick borders 3-4px
- [ ] Double shadows (inner+outer)
- [ ] Pastel colors used
- [ ] Soft bounce animations
- [ ] Playful interactions

## Aurora UI

- **Reads as**: Vibrant gradients, smooth blend, Northern Lights effect, mesh gradient, luminous, atmospheric, abstract
- **Primary colors**: Complementary: Blue-Orange, Purple-Yellow, Electric Blue #0080FF, Magenta #FF1493, Cyan #00FFFF
- **Secondary colors**: Smooth transitions (Blue→Purple→Pink→Teal), iridescent effects, blend modes (screen, multiply)
- **Effects**: Large flowing CSS/SVG gradients, subtle 8-12s animations, depth via color layering, smooth morph
- **Best for**: Modern SaaS, creative agencies, branding, music platforms, lifestyle, premium products, hero sections
- **Do NOT use for**: Data-heavy dashboards, critical accessibility, content-heavy where distraction issues
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Good
- **Accessibility**: ⚠ Text contrast
- **Mobile**: ✓ Good
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 9/10, CSS-in-JS 10/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
background: conic-gradient or radial-gradient with multiple stops, animation: @keyframes gradient (8-12s), background-size: 200% 200%, filter: saturate(1.2), blend-mode: screen or multiply
```

**Token starting point**: `--gradient-colors: complementary pairs, --animation-duration: 8-12s, --blend-mode: screen, --color-saturation: 1.2, --effect: iridescent, --loop-smooth: true`

**Before calling it done**

- [ ] Mesh/flowing gradients applied
- [ ] 8-12s animation loop
- [ ] Complementary colors used
- [ ] Smooth color transitions
- [ ] Iridescent effect subtle
- [ ] Text contrast verified

## Retro-Futurism

- **Reads as**: Vintage sci-fi, 80s aesthetic, neon glow, geometric patterns, CRT scanlines, pixel art, cyberpunk, synthwave
- **Primary colors**: Neon Blue #0080FF, Hot Pink #FF006E, Cyan #00FFFF, Deep Black #1A1A2E, Purple #5D34D0
- **Secondary colors**: Metallic Silver #C0C0C0, Gold #FFD700, duotone, 80s Pink #FF10F0, neon accents
- **Effects**: CRT scanlines (::before overlay), neon glow (text-shadow+box-shadow), glitch effects (skew/offset keyframes)
- **Best for**: Gaming, entertainment, music platforms, tech brands, artistic projects, nostalgic, cyberpunk
- **Do NOT use for**: Conservative industries, critical accessibility, professional/corporate, elderly, legal/finance
- **Theme support**: light ✓ Full, dark ✓ Dark focused
- **Performance**: ⚠ Moderate
- **Accessibility**: ⚠ High contrast/strain
- **Mobile**: ◐ Medium
- **Conversion**: ◐ Medium
- **Frameworks**: Tailwind 8/10, CSS-in-JS 9/10
- **Era**: 1980s Retro
- **Complexity**: Medium

**CSS that actually produces it**

```css
color: neon colors (#0080FF, #FF006E, #00FFFF), text-shadow: 0 0 10px neon, background: #000 or #1A1A2E, font-family: monospace, animation: glitch (skew+offset), filter: hue-rotate
```

**Token starting point**: `--neon-colors: #0080FF #FF006E #00FFFF, --background: #000000, --font-family: monospace, --effect: glitch+glow, --scanline-opacity: 0.3, --crt-effect: true`

**Before calling it done**

- [ ] Neon colors used
- [ ] CRT scanlines effect
- [ ] Glitch animations active
- [ ] Monospace font
- [ ] Deep black background
- [ ] Glow effects applied
- [ ] 80s patterns present

## Flat Design

- **Reads as**: 2D, minimalist, bold colors, no shadows, clean lines, simple shapes, typography-focused, modern, icon-heavy
- **Primary colors**: Solid bright: Red, Orange, Blue, Green, limited palette (4-6 max)
- **Secondary colors**: Complementary colors, muted secondaries, high saturation, clean accents
- **Effects**: No gradients/shadows, simple hover (color/opacity shift), fast loading, clean transitions (150-200ms ease), minimal icons
- **Best for**: Web apps, mobile apps, cross-platform, startup MVPs, user-friendly, SaaS, dashboards, corporate
- **Do NOT use for**: Complex 3D, premium/luxury, artistic portfolios, immersive experiences, high-detail
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Bootstrap 10/10, MUI 9/10
- **Era**: 2010s Modern
- **Complexity**: Low

**CSS that actually produces it**

```css
box-shadow: none, background: solid color, border-radius: 0-4px, color: solid (no gradients), fill: solid, stroke: 1-2px, font: bold sans-serif, icons: simplified SVG
```

**Token starting point**: `--shadow: none, --color-palette: 4-6 solid, --border-radius: 2px, --gradient: none, --icons: simplified SVG, --animation: minimal 150-200ms`

**Before calling it done**

- [ ] No shadows/gradients
- [ ] 4-6 solid colors max
- [ ] Clean lines consistent
- [ ] Simple shapes used
- [ ] Icon-heavy layout
- [ ] High saturation colors
- [ ] Fast loading verified

## Skeuomorphism

- **Reads as**: Realistic, texture, depth, 3D appearance, real-world metaphors, shadows, gradients, tactile, detailed, material
- **Primary colors**: Rich realistic: wood, leather, metal colors, detailed gradients (8-12 stops), metallic effects
- **Secondary colors**: Realistic lighting gradients, shadow variations (30-50% darker), texture overlays, material colors
- **Effects**: Realistic shadows (layers), depth (perspective), texture details (noise, grain), realistic animations (300-500ms)
- **Best for**: Legacy apps, gaming, immersive storytelling, premium products, luxury, realistic simulations, education
- **Do NOT use for**: Modern enterprise, critical accessibility, low-performance, web (use Flat/Modern)
- **Theme support**: light ◐ Partial, dark ◐ Partial
- **Performance**: ❌ Poor
- **Accessibility**: ⚠ Textures reduce readability
- **Mobile**: ✗ Low
- **Conversion**: ◐ Medium
- **Frameworks**: CSS-in-JS 7/10, Custom 8/10
- **Era**: 2007-2012 iOS
- **Complexity**: High

**CSS that actually produces it**

```css
background: complex gradient (8-12 stops), box-shadow: realistic multi-layer, background-image: texture overlay (noise, grain), filter: drop-shadow, transform: scale on press (300-500ms)
```

**Token starting point**: `--gradient-stops: 8-12, --texture-overlay: noise+grain, --shadow-layers: 3+, --animation-duration: 300-500ms, --depth-effect: pronounced, --tactile: true`

**Before calling it done**

- [ ] Realistic textures applied
- [ ] Complex gradients 8-12 stops
- [ ] Multi-layer shadows
- [ ] Texture overlays present
- [ ] Tactile animations smooth
- [ ] Depth effect pronounced

## Liquid Glass

- **Reads as**: Flowing glass, morphing, smooth transitions, fluid effects, translucent, animated blur, iridescent, chromatic aberration
- **Primary colors**: Vibrant iridescent (rainbow spectrum), translucent base with opacity shifts, gradient fluidity
- **Secondary colors**: Chromatic aberration (Red-Cyan), iridescent oil-spill, fluid gradient blends, holographic effects
- **Effects**: Morphing elements (SVG/CSS), fluid animations (400-600ms curves), dynamic blur (backdrop-filter), color transitions
- **Best for**: Premium SaaS, high-end e-commerce, creative platforms, branding experiences, luxury portfolios
- **Do NOT use for**: Performance-limited, critical accessibility, complex data, budget projects
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Moderate-Poor
- **Accessibility**: ⚠ Text contrast
- **Mobile**: ◐ Medium
- **Conversion**: ✓ High
- **Frameworks**: Framer Motion 10/10, GSAP 10/10
- **Era**: 2020s Modern
- **Complexity**: High

**CSS that actually produces it**

```css
animation: morphing SVG paths (400-600ms), backdrop-filter: blur + saturate, filter: hue-rotate + brightness, blend-mode: screen, background: iridescent gradient
```

**Token starting point**: `--morph-duration: 400-600ms, --blur-amount: 15px, --chromatic-aberration: true, --iridescent: true, --blend-mode: screen, --smooth-transitions: true`

**Before calling it done**

- [ ] Morphing animations 400-600ms
- [ ] Chromatic aberration applied
- [ ] Dynamic blur active
- [ ] Iridescent gradients
- [ ] Smooth color transitions
- [ ] Premium feel achieved

## Motion-Driven

- **Reads as**: Animation-heavy, microinteractions, smooth transitions, scroll effects, parallax, entrance anim, page transitions
- **Primary colors**: Bold colors emphasize movement, high contrast animated, dynamic gradients, accent action colors
- **Secondary colors**: Transitional states, success (Green #22C55E), error (Red #EF4444), neutral feedback
- **Effects**: Scroll anim (Intersection Observer), hover (300-400ms), entrance, parallax (3-5 layers), page transitions
- **Best for**: Portfolio sites, storytelling platforms, interactive experiences, entertainment apps, creative, SaaS
- **Do NOT use for**: Data dashboards, critical accessibility, low-power devices, content-heavy, motion-sensitive
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Good
- **Accessibility**: ⚠ Prefers-reduced-motion
- **Mobile**: ✓ Good
- **Conversion**: ✓ High
- **Frameworks**: GSAP 10/10, Framer Motion 10/10
- **Era**: 2020s Modern
- **Complexity**: High

**CSS that actually produces it**

```css
animation: @keyframes scroll-reveal, transform: translateY/X, Intersection Observer API, will-change: transform, scroll-behavior: smooth, animation-duration: 300-400ms
```

**Token starting point**: `--animation-duration: 300-400ms, --parallax-layers: 5, --scroll-behavior: smooth, --gpu-accelerated: true, --entrance-animation: true, --page-transition: smooth`

**Before calling it done**

- [ ] Scroll animations active
- [ ] Parallax 3-5 layers
- [ ] Entrance animations smooth
- [ ] Page transitions fluid
- [ ] GPU accelerated
- [ ] Prefers-reduced-motion respected

## Micro-interactions

- **Reads as**: Small animations, gesture-based, tactile feedback, subtle animations, contextual interactions, responsive
- **Primary colors**: Subtle color shifts (10-20%), feedback: Green #22C55E, Red #EF4444, Amber #F59E0B
- **Secondary colors**: Accent feedback, neutral supporting, clear action indicators
- **Effects**: Small hover (50-100ms), loading spinners, success/error state anim, gesture-triggered (swipe/pinch), haptic
- **Best for**: Mobile apps, touchscreen UIs, productivity tools, user-friendly, consumer apps, interactive components
- **Do NOT use for**: Desktop-only, critical performance, accessibility-first (alternatives needed)
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ Good
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Framer Motion 10/10, React Spring 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
animation: short 50-100ms, transition: hover states, @media (hover: hover) for desktop, :active for press, haptic-feedback CSS/API, loading animation smooth loop
```

**Token starting point**: `--micro-animation-duration: 50-100ms, --gesture-responsive: true, --haptic-feedback: true, --loading-animation: smooth, --state-feedback: success+error`

**Before calling it done**

- [ ] Micro-animations 50-100ms
- [ ] Gesture-responsive
- [ ] Tactile feedback visual/haptic
- [ ] Loading spinners smooth
- [ ] Success/error states clear
- [ ] Hover effects subtle

## Inclusive Design

- **Reads as**: Accessible, color-blind friendly, high contrast, haptic feedback, voice interaction, screen reader, WCAG AAA, universal
- **Primary colors**: WCAG AAA (7:1+ contrast), avoid red-green only, symbol-based indicators, high contrast primary
- **Secondary colors**: Supporting patterns (stripes, dots, hatch), symbols, combinations, clear non-color indicators
- **Effects**: Haptic feedback (vibration), voice guidance, focus indicators (4px+ ring), motion options, alt content, semantic
- **Best for**: Public services, education, healthcare, finance, government, accessible consumer, inclusive
- **Do NOT use for**: None - accessibility universal
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: All frameworks 10/10
- **Era**: Universal
- **Complexity**: Low

**CSS that actually produces it**

```css
aria-* attributes complete, role attributes semantic, focus-visible: 3-4px ring, color-contrast: 7:1+, @media (prefers-reduced-motion), alt text on all images, form labels properly associated
```

**Token starting point**: `--contrast-ratio: 7:1, --font-size: 16px+, --keyboard-accessible: true, --sr-compatible: true, --wcag-level: AAA, --color-symbols: true, --haptic: enabled`

**Before calling it done**

- [ ] WCAG AAA verified
- [ ] 7:1+ contrast all text
- [ ] Keyboard accessible (Tab/Enter)
- [ ] Screen reader tested
- [ ] Focus visible 3-4px
- [ ] No color-only indicators
- [ ] Haptic fallback

## Zero Interface

- **Reads as**: Minimal visible UI, voice-first, gesture-based, AI-driven, invisible controls, predictive, context-aware, ambient
- **Primary colors**: Neutral backgrounds: Soft white #FAFAFA, light grey #F0F0F0, warm off-white #F5F1E8
- **Secondary colors**: Subtle feedback: light green, light red, minimal UI elements, soft accents
- **Effects**: Voice recognition UI, gesture detection, AI predictions (smooth reveal), progressive disclosure, smart suggestions
- **Best for**: Voice assistants, AI platforms, future-forward UX, smart home, contextual computing, ambient experiences
- **Do NOT use for**: Complex workflows, data-entry heavy, traditional systems, legacy support, explicit control
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ Excellent
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Custom 10/10
- **Era**: 2020s AI-Era
- **Complexity**: Low

**CSS that actually produces it**

```css
voice-commands: Web Speech API, gesture-detection: touch events, AI-predictions: hidden by default (reveal on hover), progressive-disclosure: show on demand, minimal UI visible
```

**Token starting point**: `--voice-ui: enabled, --gesture-detection: active, --ai-predictions: smart, --progressive-disclosure: true, --visible-ui: minimal, --context-aware: true`

**Before calling it done**

- [ ] Voice commands responsive
- [ ] Gesture detection active
- [ ] AI predictions hidden/revealed
- [ ] Progressive disclosure working
- [ ] Minimal visible UI
- [ ] Smart suggestions contextual

## Soft UI Evolution

- **Reads as**: Evolved soft UI, better contrast, modern aesthetics, subtle depth, accessibility-focused, improved shadows, hybrid
- **Primary colors**: Improved contrast pastels: Soft Blue #87CEEB, Soft Pink #FFB6C1, Soft Green #90EE90, better hierarchy
- **Secondary colors**: Better combinations, accessible secondary, supporting with improved contrast, modern accents
- **Effects**: Improved shadows (softer than flat, clearer than neumorphism), modern (200-300ms), focus visible, WCAG AA/AAA
- **Best for**: Modern enterprise apps, SaaS platforms, health/wellness, modern business tools, professional, hybrid
- **Do NOT use for**: Extreme minimalism, critical performance, systems without modern OS
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA+
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 9/10, MUI 9/10, Chakra 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

**CSS that actually produces it**

```css
box-shadow: softer multi-layer (0 2px 4px), background: improved contrast pastels, border-radius: 8-12px, animation: 200-300ms smooth, outline: 2-3px on focus, contrast: 4.5:1+
```

**Token starting point**: `--shadow-soft: modern blend, --border-radius: 10px, --animation-duration: 200-300ms, --contrast-ratio: 4.5:1+, --color-hierarchy: improved, --wcag-level: AA+`

**Before calling it done**

- [ ] Improved contrast AA/AAA
- [ ] Soft shadows modern
- [ ] Border-radius 8-12px
- [ ] Animations 200-300ms
- [ ] Focus states visible
- [ ] Color hierarchy clear

## Hero-Centric Design

- **Reads as**: Large hero section, compelling headline, high-contrast CTA, product showcase, value proposition, hero image/video, dramatic visual
- **Primary colors**: Brand primary color, white/light backgrounds for contrast, accent color for CTA
- **Secondary colors**: Supporting colors for secondary CTAs, accent highlights, trust elements (testimonials, logos)
- **Effects**: Smooth scroll reveal, fade-in animations on hero, subtle background parallax, CTA glow/pulse effect
- **Best for**: SaaS landing pages, product launches, service landing pages, B2B platforms, tech companies
- **Do NOT use for**: Complex navigation, multi-page experiences, data-heavy applications
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Full
- **Conversion**: ✓ Very High
- **Frameworks**: Tailwind 10/10, Bootstrap 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

## Conversion-Optimized

- **Reads as**: Form-focused, minimalist design, single CTA focus, high contrast, urgency elements, trust signals, social proof, clear value
- **Primary colors**: Primary brand color, high-contrast white/light backgrounds, warning/urgency colors for time-limited offers
- **Secondary colors**: Secondary CTA color (muted), trust element colors (testimonial highlights), accent for key benefits
- **Effects**: Hover states on CTA (color shift, slight scale), form field focus animations, loading spinner, success feedback
- **Best for**: E-commerce product pages, free trial signups, lead generation, SaaS pricing pages, limited-time offers
- **Do NOT use for**: Complex feature explanations, multi-product showcases, technical documentation
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Full (mobile-optimized)
- **Conversion**: ✓ Very High

## Feature-Rich Showcase

- **Reads as**: Multiple feature sections, grid layout, benefit cards, visual feature demonstrations, interactive elements, problem-solution pairs
- **Primary colors**: Primary brand, bright secondary colors for feature cards, contrasting accent for CTAs
- **Secondary colors**: Supporting colors for: benefits (green), problems (red/orange), features (blue/purple), social proof (neutral)
- **Effects**: Card hover effects (lift/scale), icon animations on scroll, feature toggle animations, smooth section transitions
- **Best for**: Enterprise SaaS, software tools landing pages, platform services, complex product explanations, B2B products
- **Do NOT use for**: Simple product pages, early-stage startups with few features, entertainment landing pages
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Good
- **Conversion**: ✓ High

## Minimal & Direct

- **Reads as**: Minimal text, white space heavy, single column layout, direct messaging, clean typography, visual-centric, fast-loading
- **Primary colors**: Monochromatic primary, white background, single accent color for CTA, black/dark grey text
- **Secondary colors**: Minimal secondary colors, reserved for critical CTAs only, neutral supporting elements
- **Effects**: Very subtle hover effects, minimal animations, fast page load (no heavy animations), smooth scroll
- **Best for**: Simple service landing pages, indie products, consulting services, micro SaaS, freelancer portfolios
- **Do NOT use for**: Feature-heavy products, complex explanations, multi-product showcases
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ Full
- **Conversion**: ✓ High

## Social Proof-Focused

- **Reads as**: Testimonials prominent, client logos displayed, case studies sections, reviews/ratings, user avatars, success metrics, credibility markers
- **Primary colors**: Primary brand, trust colors (blue), success/growth colors (green), neutral backgrounds
- **Secondary colors**: Testimonial highlight colors, logo grid backgrounds (light grey), badge/achievement colors
- **Effects**: Testimonial carousel animations, logo grid fade-in, stat counter animations (number count-up), review star ratings
- **Best for**: B2B SaaS, professional services, premium products, e-commerce conversion pages, established brands
- **Do NOT use for**: Startup MVPs, products without users, niche/experimental products
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Full
- **Conversion**: ✓ High

## Interactive Product Demo

- **Reads as**: Embedded product mockup/video, interactive elements, product walkthrough, step-by-step guides, hover-to-reveal features, embedded demos
- **Primary colors**: Primary brand, interface colors matching product, demo highlight colors for interactive elements
- **Secondary colors**: Product UI colors, tutorial step colors (numbered progression), hover state indicators
- **Effects**: Product animation playback, step progression animations, hover reveal effects, smooth zoom on interaction
- **Best for**: SaaS platforms, tool/software products, productivity apps landing pages, developer tools, productivity software
- **Do NOT use for**: Simple services, consulting, non-digital products, complexity-averse audiences
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Good (video/interactive)
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Good
- **Conversion**: ✓ Very High

## Trust & Authority

- **Reads as**: Certificates/badges displayed, expert credentials, case studies with metrics, before/after comparisons, industry recognition, security badges
- **Primary colors**: Professional colors (blue/grey), trust colors, certification badge colors (gold/silver accents)
- **Secondary colors**: Certificate highlight colors, metric showcase colors, comparison highlight (success green)
- **Effects**: Badge hover effects, metric pulse animations, certificate carousel, smooth stat reveal
- **Best for**: Healthcare/medical landing pages, financial services, enterprise software, premium/luxury products, legal services
- **Do NOT use for**: Casual products, entertainment, viral/social-first products
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ Full
- **Conversion**: ✓ High

## Storytelling-Driven

- **Reads as**: Narrative flow, visual story progression, section transitions, consistent character/brand voice, emotional messaging, journey visualization
- **Primary colors**: Brand primary, warm/emotional colors, varied accent colors per story section, high visual variety
- **Secondary colors**: Story section color coding, emotional state colors (calm, excitement, success), transitional gradients
- **Effects**: Section-to-section animations, scroll-triggered reveals, character/icon animations, morphing transitions, parallax narrative
- **Best for**: Brand/startup stories, mission-driven products, premium/lifestyle brands, documentary-style products, educational
- **Do NOT use for**: Technical/complex products (unless narrative-driven), traditional enterprise software
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Moderate (animations)
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Good
- **Conversion**: ✓ High

## Data-Dense Dashboard

- **Reads as**: Multiple charts/widgets, data tables, KPI cards, minimal padding, grid layout, space-efficient, maximum data visibility
- **Primary colors**: Neutral primary (light grey/white #F5F5F5), data colors (blue/green/red), dark text #333333
- **Secondary colors**: Chart colors: success (green #22C55E), warning (amber #F59E0B), alert (red #EF4444), neutral (grey)
- **Effects**: Hover tooltips, chart zoom on click, row highlighting on hover, smooth filter animations, data loading spinners
- **Best for**: Business intelligence dashboards, financial analytics, enterprise reporting, operational dashboards, data warehousing
- **Do NOT use for**: Marketing dashboards, consumer-facing analytics, simple reporting
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable

## Heat Map & Heatmap Style

- **Reads as**: Color-coded grid/matrix, data intensity visualization, geographical heat maps, correlation matrices, cell-based representation, gradient coloring
- **Primary colors**: Gradient scale: Cool (blue #0080FF) to hot (red #FF0000), neutral middle (white/yellow)
- **Secondary colors**: Support gradients: Light (cool blue) to dark (warm red), divergent for positive/negative data, monochromatic options
- **Effects**: Color gradient transitions on data change, cell highlighting on hover, tooltip reveal on click, smooth color animation
- **Best for**: Geographical analysis, performance matrices, correlation analysis, user behavior heatmaps, temperature/intensity data
- **Do NOT use for**: Linear data representation, categorical comparisons (use bar charts), small datasets
- **Theme support**: light ✓ Full, dark ✓ Full (with adjustments)
- **Performance**: ⚡ Excellent
- **Accessibility**: ⚠ Colorblind considerations
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable

## Executive Dashboard

- **Reads as**: High-level KPIs, large key metrics, minimal detail, summary view, trend indicators, at-a-glance insights, executive summary
- **Primary colors**: Brand colors, professional palette (blue/grey/white), accent for KPIs, red for alerts/concerns
- **Secondary colors**: KPI highlight colors: positive (green), negative (red), neutral (grey), trend arrow colors
- **Effects**: KPI value animations (count-up), trend arrow direction animations, metric card hover lift, alert pulse effect
- **Best for**: C-suite dashboards, business summary reports, decision-maker dashboards, strategic planning views
- **Do NOT use for**: Detailed analyst dashboards, technical deep-dives, operational monitoring
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✗ Low (not mobile-optimized)
- **Conversion**: ✗ Not applicable

## Real-Time Monitoring

- **Reads as**: Live data updates, status indicators, alert notifications, streaming data visualization, active monitoring, streaming charts
- **Primary colors**: Alert colors: critical (red #FF0000), warning (orange #FFA500), normal (green #22C55E), updating (blue animation)
- **Secondary colors**: Status indicator colors, chart line colors varying by metric, streaming data highlight colors
- **Effects**: Real-time chart animations, alert pulse/glow, status indicator blink animation, smooth data stream updates, loading effect
- **Best for**: System monitoring dashboards, DevOps dashboards, real-time analytics, stock market dashboards, live event tracking
- **Do NOT use for**: Historical analysis, long-term trend reports, archived data dashboards
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good (real-time load)
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable

## Drill-Down Analytics

- **Reads as**: Hierarchical data exploration, expandable sections, interactive drill-down paths, summary-to-detail flow, context preservation
- **Primary colors**: Primary brand, breadcrumb colors, drill-level indicator colors, hierarchy depth colors
- **Secondary colors**: Drill-down path indicator colors, level-specific colors, highlight colors for selected level, transition colors
- **Effects**: Drill-down expand animations, breadcrumb click transitions, smooth detail reveal, level change smooth, data reload animation
- **Best for**: Sales analytics, product analytics, funnel analysis, multi-dimensional data exploration, business intelligence
- **Do NOT use for**: Simple linear data, single-metric dashboards, streaming real-time dashboards
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable

## Comparative Analysis Dashboard

- **Reads as**: Side-by-side comparisons, period-over-period metrics, A/B test results, regional comparisons, performance benchmarks
- **Primary colors**: Comparison colors: primary (blue), comparison (orange/purple), delta indicator (green/red)
- **Secondary colors**: Winning metric color (green), losing metric color (red), neutral comparison (grey), benchmark colors
- **Effects**: Comparison bar animations (grow to value), delta indicator animations (direction arrows), highlight on compare
- **Best for**: Period-over-period reporting, A/B test dashboards, market comparison, competitive analysis, regional performance
- **Do NOT use for**: Single metric dashboards, future projections (use forecasting), real-time only (no historical)
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable

## Predictive Analytics

- **Reads as**: Forecast lines, confidence intervals, trend projections, scenario modeling, AI-driven insights, anomaly detection visualization
- **Primary colors**: Forecast line color (distinct from actual), confidence interval shading, anomaly highlight (red alert), trend colors
- **Secondary colors**: High confidence (dark color), low confidence (light color), anomaly colors (red/orange), normal trend (green/blue)
- **Effects**: Forecast line animation on draw, confidence band fade-in, anomaly pulse alert, smoothing function animations
- **Best for**: Forecasting dashboards, anomaly detection systems, trend prediction dashboards, AI-powered analytics, budget planning
- **Do NOT use for**: Historical-only dashboards, simple reporting, real-time operational dashboards
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Good (computation)
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable

## User Behavior Analytics

- **Reads as**: Funnel visualization, user flow diagrams, conversion tracking, engagement metrics, user journey mapping, cohort analysis
- **Primary colors**: Funnel stage colors: high engagement (green), drop-off (red), conversion (blue), user flow arrows (grey)
- **Secondary colors**: Stage completion colors (success), abandonment colors (warning), engagement levels (gradient), cohort colors
- **Effects**: Funnel animation (fill-down), flow diagram animations (connection draw), conversion pulse, engagement bar fill
- **Best for**: Conversion funnel analysis, user journey tracking, engagement analytics, cohort analysis, retention tracking
- **Do NOT use for**: Real-time operational metrics, technical system monitoring, financial transactions
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ Good
- **Conversion**: ✗ Not applicable

## Financial Dashboard

- **Reads as**: Revenue metrics, profit/loss visualization, budget tracking, financial ratios, portfolio performance, cash flow, audit trail
- **Primary colors**: Financial colors: profit (green #22C55E), loss (red #EF4444), neutral (grey), trust (dark blue #003366)
- **Secondary colors**: Revenue highlight (green), expenses (red), budget variance (orange/red), balance (grey), accuracy (blue)
- **Effects**: Number animations (count-up), trend direction indicators, percentage change animations, profit/loss color transitions
- **Best for**: Financial reporting, accounting dashboards, portfolio tracking, budget monitoring, banking analytics
- **Do NOT use for**: Simple business dashboards, entertainment/social metrics, non-financial data
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✗ Low
- **Conversion**: ✗ Not applicable

## Sales Intelligence Dashboard

- **Reads as**: Deal pipeline, sales metrics, territory performance, sales rep leaderboard, win-loss analysis, quota tracking, forecast accuracy
- **Primary colors**: Sales colors: won (green), lost (red), in-progress (blue), blocked (orange), quota met (gold), quota missed (grey)
- **Secondary colors**: Pipeline stage colors, rep performance colors, quota achievement colors, forecast accuracy colors
- **Effects**: Deal movement animations, metric updates, leaderboard ranking changes, gauge needle movements, status change highlights
- **Best for**: CRM dashboards, sales management, opportunity tracking, performance management, quota planning
- **Do NOT use for**: Marketing analytics, customer support metrics, HR dashboards
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Good
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Not applicable
- **Frameworks**: Recharts 9/10, Chart.js 9/10
- **Era**: 2020s Modern
- **Complexity**: Medium

## Neubrutalism

- **Reads as**: Bold borders, black outlines, primary colors, thick shadows, no gradients, flat colors, 45° shadows, playful, Gen Z
- **Primary colors**: #FFEB3B (Yellow), #FF5252 (Red), #2196F3 (Blue), #000000 (Black borders)
- **Secondary colors**: Limited accent colors, high contrast combinations, no gradients allowed
- **Effects**: box-shadow: 4px 4px 0 #000, border: 3px solid #000, no gradients, sharp corners (0px), bold typography
- **Best for**: Gen Z brands, startups, creative agencies, Figma-style apps, Notion-style interfaces, tech blogs
- **Do NOT use for**: Luxury brands, finance, healthcare, conservative industries (too playful)
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Bootstrap 8/10
- **Era**: 2020s Modern
- **Complexity**: Low

**CSS that actually produces it**

```css
border: 3px solid black, box-shadow: 5px 5px 0px black, colors: #FFDB58 #FF6B6B #4ECDC4, font-weight: 700, no gradients
```

**Token starting point**: `--border-width: 3px, --shadow-offset: 4px, --shadow-color: #000, --colors: high saturation, --font: bold sans`

**Before calling it done**

- [ ] Hard borders (2-4px)
- [ ] Hard offset shadows
- [ ] High saturation colors
- [ ] Bold typography
- [ ] No blurs/gradients
- [ ] Distinctive 'ugly-cute' look

## Bento Box Grid

- **Reads as**: Modular cards, asymmetric grid, varied sizes, Apple-style, dashboard tiles, negative space, clean hierarchy, cards
- **Primary colors**: Neutral base + brand accent, #FFFFFF, #F5F5F5, brand primary
- **Secondary colors**: Subtle gradients, shadow variations, accent highlights for interactive cards
- **Effects**: grid-template with varied spans, rounded-xl (16px), subtle shadows, hover scale (1.02), smooth transitions
- **Best for**: Dashboards, product pages, portfolios, Apple-style marketing, feature showcases, SaaS
- **Do NOT use for**: Dense data tables, text-heavy content, real-time monitoring
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, CSS Grid 10/10
- **Era**: 2020s Apple
- **Complexity**: Low

## Y2K Aesthetic

- **Reads as**: Neon pink, chrome, metallic, bubblegum, iridescent, glossy, retro-futurism, 2000s, futuristic nostalgia
- **Primary colors**: #FF69B4 (Hot Pink), #00FFFF (Cyan), #C0C0C0 (Silver), #9400D3 (Purple)
- **Secondary colors**: Metallic gradients, glossy overlays, iridescent effects, chrome textures
- **Effects**: linear-gradient metallic, glossy buttons, 3D chrome effects, glow animations, bubble shapes
- **Best for**: Fashion brands, music platforms, Gen Z brands, nostalgia marketing, entertainment, youth-focused
- **Do NOT use for**: B2B enterprise, healthcare, finance, conservative industries, elderly users
- **Theme support**: light ✓ Full, dark ◐ Partial
- **Performance**: ⚠ Good
- **Accessibility**: ⚠ Check contrast
- **Mobile**: ✓ Good
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 8/10, CSS-in-JS 9/10
- **Era**: Y2K 2000s
- **Complexity**: Medium

## Cyberpunk UI

- **Reads as**: Neon, dark mode, terminal, HUD, sci-fi, glitch, dystopian, futuristic, matrix, tech noir
- **Primary colors**: #00FF00 (Matrix Green), #FF00FF (Magenta), #00FFFF (Cyan), #0D0D0D (Dark)
- **Secondary colors**: Neon gradients, scanline overlays, glitch colors, terminal green accents
- **Effects**: Neon glow (text-shadow), glitch animations (skew/offset), scanlines (::before overlay), terminal fonts
- **Best for**: Gaming platforms, tech products, crypto apps, sci-fi applications, developer tools, entertainment
- **Do NOT use for**: Corporate enterprise, healthcare, family apps, conservative brands, elderly users
- **Theme support**: light ✗ No, dark ✓ Only
- **Performance**: ⚠ Moderate
- **Accessibility**: ⚠ Limited (dark+neon)
- **Mobile**: ◐ Medium
- **Conversion**: ◐ Medium
- **Frameworks**: Tailwind 8/10, Custom CSS 10/10
- **Era**: 2020s Cyberpunk
- **Complexity**: Medium

## Organic Biophilic

- **Reads as**: Nature, organic shapes, green, sustainable, rounded, flowing, wellness, earthy, natural textures
- **Primary colors**: #228B22 (Forest Green), #8B4513 (Earth Brown), #87CEEB (Sky Blue), #F5F5DC (Beige)
- **Secondary colors**: Natural gradients, earth tones, sky blues, organic textures, wood/stone colors
- **Effects**: Rounded corners (16-24px), organic curves (border-radius variations), natural shadows, flowing SVG shapes
- **Best for**: Wellness apps, sustainability brands, eco products, health apps, meditation, organic food brands
- **Do NOT use for**: Tech-focused products, gaming, industrial, urban brands
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, CSS 10/10
- **Era**: 2020s Sustainable
- **Complexity**: Low

## AI-Native UI

- **Reads as**: Chatbot, conversational, voice, assistant, agentic, ambient, minimal chrome, streaming text, AI interactions
- **Primary colors**: Neutral + single accent, #6366F1 (AI Purple), #10B981 (Success), #F5F5F5 (Background)
- **Secondary colors**: Status indicators, streaming highlights, context card colors, subtle accent variations
- **Effects**: Typing indicators (3-dot pulse), streaming text animations, pulse animations, context cards, smooth reveals
- **Best for**: AI products, chatbots, voice assistants, copilots, AI-powered tools, conversational interfaces
- **Do NOT use for**: Traditional forms, data-heavy dashboards, print-first content
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, React 10/10
- **Era**: 2020s AI-Era
- **Complexity**: Low

## Memphis Design

- **Reads as**: 80s, geometric, playful, postmodern, shapes, patterns, squiggles, triangles, neon, abstract, bold
- **Primary colors**: #FF71CE (Hot Pink), #FFCE5C (Yellow), #86CCCA (Teal), #6A7BB4 (Blue Purple)
- **Secondary colors**: Complementary geometric colors, pattern fills, contrasting accent shapes
- **Effects**: transform: rotate(), clip-path: polygon(), mix-blend-mode, repeating patterns, bold shapes
- **Best for**: Creative agencies, music sites, youth brands, event promotion, artistic portfolios, entertainment
- **Do NOT use for**: Corporate finance, healthcare, legal, elderly users, conservative brands
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ⚠ Check contrast
- **Mobile**: ✓ Good
- **Conversion**: ◐ Medium
- **Frameworks**: Tailwind 9/10, CSS 10/10
- **Era**: 1980s Postmodern
- **Complexity**: Medium

## Vaporwave

- **Reads as**: Synthwave, retro-futuristic, 80s-90s, neon, glitch, nostalgic, sunset gradient, dreamy, aesthetic
- **Primary colors**: #FF71CE (Pink), #01CDFE (Cyan), #05FFA1 (Mint), #B967FF (Purple)
- **Secondary colors**: Sunset gradients, glitch overlays, VHS effects, neon accents, pastel variations
- **Effects**: text-shadow glow, linear-gradient, filter: hue-rotate(), glitch animations, retro scan lines
- **Best for**: Music platforms, gaming, creative portfolios, tech startups, entertainment, artistic projects
- **Do NOT use for**: Business apps, e-commerce, education, healthcare, enterprise software
- **Theme support**: light ✓ Full, dark ✓ Dark focused
- **Performance**: ⚠ Moderate
- **Accessibility**: ⚠ Poor (motion)
- **Mobile**: ◐ Medium
- **Conversion**: ◐ Medium
- **Frameworks**: Tailwind 8/10, CSS-in-JS 9/10
- **Era**: 1980s-90s Retro
- **Complexity**: Medium

## Dimensional Layering

- **Reads as**: Depth, overlapping, z-index, layers, 3D, shadows, elevation, floating, cards, spatial hierarchy
- **Primary colors**: Neutral base (#FFFFFF, #F5F5F5, #E0E0E0) + brand accent for elevated elements
- **Secondary colors**: Shadow variations (sm/md/lg/xl), elevation colors, highlight colors for top layers
- **Effects**: z-index stacking, box-shadow elevation (4 levels), transform: translateZ(), backdrop-filter, parallax
- **Best for**: Dashboards, card layouts, modals, navigation, product showcases, SaaS interfaces
- **Do NOT use for**: Print-style layouts, simple blogs, low-end devices, flat design requirements
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Good
- **Accessibility**: ⚠ Moderate (SR issues)
- **Mobile**: ✓ Good
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, MUI 10/10, Chakra 10/10
- **Era**: 2020s Modern
- **Complexity**: Medium

## Exaggerated Minimalism

- **Reads as**: Bold minimalism, oversized typography, high contrast, negative space, loud minimal, statement design
- **Primary colors**: #000000 (Black), #FFFFFF (White), single vibrant accent only
- **Secondary colors**: Minimal - single accent color, no secondary colors, extreme restraint
- **Effects**: font-size: clamp(3rem 10vw 12rem), font-weight: 900, letter-spacing: -0.05em, massive whitespace
- **Best for**: Fashion, architecture, portfolios, agency landing pages, luxury brands, editorial
- **Do NOT use for**: E-commerce catalogs, dashboards, forms, data-heavy, elderly users, complex apps
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Typography.js 10/10
- **Era**: 2020s Modern
- **Complexity**: Low

## Kinetic Typography

- **Reads as**: Motion text, animated type, moving letters, dynamic, typing effect, morphing, scroll-triggered text
- **Primary colors**: Flexible - high contrast recommended, bold colors for emphasis, animation-friendly palette
- **Secondary colors**: Accent colors for emphasis, transition colors, gradient text fills
- **Effects**: @keyframes text animation, typing effect, background-clip: text, GSAP ScrollTrigger, split text
- **Best for**: Hero sections, marketing sites, video platforms, storytelling, creative portfolios, landing pages
- **Do NOT use for**: Long-form content, accessibility-critical, data interfaces, forms, elderly users
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Moderate
- **Accessibility**: ❌ Poor (motion)
- **Mobile**: ✓ Good
- **Conversion**: ✓ Very High
- **Frameworks**: GSAP 10/10, Framer Motion 10/10
- **Era**: 2020s Modern
- **Complexity**: High

## Parallax Storytelling

- **Reads as**: Scroll-driven, narrative, layered scrolling, immersive, progressive disclosure, cinematic, scroll-triggered
- **Primary colors**: Story-dependent, often gradients and natural colors, section-specific palettes
- **Secondary colors**: Section transition colors, depth layer colors, narrative mood colors
- **Effects**: transform: translateY(scroll), position: fixed/sticky, perspective: 1px, scroll-triggered animations
- **Best for**: Brand storytelling, product launches, case studies, portfolios, annual reports, marketing campaigns
- **Do NOT use for**: E-commerce, dashboards, mobile-first, SEO-critical, accessibility-required
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ❌ Poor
- **Accessibility**: ❌ Poor (motion)
- **Mobile**: ✗ Low
- **Conversion**: ✓ High
- **Frameworks**: GSAP ScrollTrigger 10/10, Locomotive Scroll 10/10
- **Era**: 2020s Modern
- **Complexity**: High

## Swiss Modernism 2.0

- **Reads as**: Grid system, Helvetica, modular, asymmetric, international style, rational, clean, mathematical spacing
- **Primary colors**: #000000, #FFFFFF, #F5F5F5, single vibrant accent only
- **Secondary colors**: Minimal secondary, accent for emphasis only, no gradients
- **Effects**: display: grid, grid-template-columns: repeat(12 1fr), gap: 1rem, mathematical ratios, clear hierarchy
- **Best for**: Corporate sites, architecture, editorial, SaaS, museums, professional services, documentation
- **Do NOT use for**: Playful brands, children's sites, entertainment, gaming, emotional storytelling
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Bootstrap 9/10, Foundation 10/10
- **Era**: 1950s Swiss + 2020s
- **Complexity**: Low

## HUD / Sci-Fi FUI

- **Reads as**: Futuristic, technical, wireframe, neon, data, transparency, iron man, sci-fi, interface
- **Primary colors**: Neon Cyan #00FFFF, Holographic Blue #0080FF, Alert Red #FF0000
- **Secondary colors**: Transparent Black, Grid Lines #333333
- **Effects**: Glow effects, scanning animations, ticker text, blinking markers, fine line drawing
- **Best for**: Sci-fi games, space tech, cybersecurity, movie props, immersive dashboards
- **Do NOT use for**: Standard corporate, reading heavy content, accessible public services
- **Theme support**: light ✓ Low, dark ✓ Full
- **Performance**: ⚠ Moderate (renders)
- **Accessibility**: ⚠ Poor (thin lines)
- **Mobile**: ◐ Medium
- **Conversion**: ✗ Low
- **Frameworks**: React 9/10, Canvas 10/10
- **Era**: 2010s Sci-Fi
- **Complexity**: High

**CSS that actually produces it**

```css
border: 1px solid rgba(0,255,255,0.5), color: #00FFFF, background: transparent or rgba(0,0,0,0.8), font-family: monospace, text-shadow: 0 0 5px cyan
```

**Token starting point**: `--hud-color: #00FFFF, --bg-color: rgba(0,10,20,0.9), --line-width: 1px, --glow: 0 0 5px, --font: monospace`

**Before calling it done**

- [ ] Fine lines 1px
- [ ] Neon glow text/borders
- [ ] Monospaced font
- [ ] Dark/Transparent BG
- [ ] Decorative tech markers
- [ ] Holographic feel

## Pixel Art

- **Reads as**: Retro, 8-bit, 16-bit, gaming, blocky, nostalgic, pixelated, arcade
- **Primary colors**: Primary colors (NES Palette), brights, limited palette
- **Secondary colors**: Black outlines, shading via dithering or block colors
- **Effects**: Frame-by-frame sprite animation, blinking cursor, instant transitions, marquee text
- **Best for**: Indie games, retro tools, creative portfolios, nostalgia marketing, Web3/NFT
- **Do NOT use for**: Professional corporate, modern SaaS, high-res photography sites
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ Good (if contrast ok)
- **Mobile**: ✓ High
- **Conversion**: ◐ Medium
- **Frameworks**: CSS (box-shadow) 8/10, Canvas 10/10
- **Era**: 1980s Arcade
- **Complexity**: Medium

**CSS that actually produces it**

```css
font-family: 'Press Start 2P', image-rendering: pixelated, box-shadow: 4px 0 0 #000 (pixel border), no anti-aliasing
```

**Token starting point**: `--pixel-size: 4px, --font: pixel font, --border-style: pixel-shadow, --anti-alias: none`

**Before calling it done**

- [ ] Pixelated fonts loaded
- [ ] Images sharp (no blur)
- [ ] CSS box-shadow for pixel borders
- [ ] Retro palette
- [ ] Blocky layout

## Bento Grids

- **Reads as**: Apple-style, modular, cards, organized, clean, hierarchy, grid, rounded, soft
- **Primary colors**: Off-white #F5F5F7, Clean White #FFFFFF, Text #1D1D1F
- **Secondary colors**: Subtle accents, soft shadows, blurred backdrops
- **Effects**: Hover scale (1.02), soft shadow expansion, smooth layout shifts, content reveal
- **Best for**: Product features, dashboards, personal sites, marketing summaries, galleries
- **Do NOT use for**: Long-form reading, data tables, complex forms
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: CSS Grid 10/10, Tailwind 10/10
- **Era**: 2020s Apple/Linear
- **Complexity**: Low

**CSS that actually produces it**

```css
display: grid, grid-template-columns: repeat(auto-fit, minmax(...)), gap: 1rem, border-radius: 20px, background: #FFF, box-shadow: subtle
```

**Token starting point**: `--grid-gap: 20px, --card-radius: 24px, --card-bg: #FFFFFF, --page-bg: #F5F5F7, --shadow: soft`

**Before calling it done**

- [ ] Grid layout (CSS Grid)
- [ ] Rounded corners 16-24px
- [ ] Varied card spans
- [ ] Content fits card size
- [ ] Responsive re-flow
- [ ] Apple-like aesthetic

## Neubrutalism

- **Reads as**: Bold, ugly-cute, raw, high contrast, flat, hard shadows, distinct, playful, loud
- **Primary colors**: Pop Yellow #FFDE59, Bright Red #FF5757, Black #000000
- **Secondary colors**: Lavender #CBA6F7, Mint #76E0C2
- **Effects**: Hard hover shifts (4px), marquee scrolling, jitter animations, bold borders
- **Best for**: Design tools, creative agencies, Gen Z brands, personal blogs, gumroad-style
- **Do NOT use for**: Banking, legal, healthcare, serious enterprise, elderly users
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ High
- **Frameworks**: Tailwind 10/10, Plain CSS 10/10
- **Era**: 2020s Modern Retro
- **Complexity**: Low

**CSS that actually produces it**

```css
border: 3px solid black, box-shadow: 5px 5px 0px black, colors: #FFDB58 #FF6B6B #4ECDC4, font-weight: 700, no gradients
```

**Token starting point**: `--border-width: 3px, --shadow-offset: 4px, --shadow-color: #000, --colors: high saturation, --font: bold sans`

**Before calling it done**

- [ ] Hard borders (2-4px)
- [ ] Hard offset shadows
- [ ] High saturation colors
- [ ] Bold typography
- [ ] No blurs/gradients
- [ ] Distinctive 'ugly-cute' look

## Spatial UI (VisionOS)

- **Reads as**: Glass, depth, immersion, spatial, translucent, gaze, gesture, apple, vision-pro
- **Primary colors**: Frosted Glass #FFFFFF (15-30% opacity), System White
- **Secondary colors**: Vibrant system colors for active states, deep shadows for depth
- **Effects**: Parallax depth, dynamic lighting response, gaze-hover effects, smooth scale on focus
- **Best for**: Spatial computing apps, VR/AR interfaces, immersive media, futuristic dashboards
- **Do NOT use for**: Text-heavy documents, high-contrast requirements, non-3D capable devices
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Moderate (blur cost)
- **Accessibility**: ⚠ Contrast risks
- **Mobile**: ✓ High (if adapted)
- **Conversion**: ✓ High
- **Frameworks**: SwiftUI, React (Three.js/Fiber)
- **Era**: 2024 Spatial Era
- **Complexity**: High

## E-Ink / Paper

- **Reads as**: Paper-like, matte, high contrast, texture, reading, calm, slow tech, monochrome
- **Primary colors**: Off-White #FDFBF7, Paper White #F5F5F5, Ink Black #1A1A1A
- **Secondary colors**: Pencil Grey #4A4A4A, Highlighter Yellow #FFFF00 (accent)
- **Effects**: No motion blur, distinct page turns, grain/noise texture, sharp transitions (no fade)
- **Best for**: Reading apps, digital newspapers, minimal journals, distraction-free writing, slow-living brands
- **Do NOT use for**: Gaming, video platforms, high-energy marketing, dark mode dependent apps
- **Theme support**: light ✓ Full, dark ✗ Low (inverted only)
- **Performance**: ⚡ Excellent
- **Accessibility**: ✓ WCAG AAA
- **Mobile**: ✓ High
- **Conversion**: ✓ Medium
- **Frameworks**: Tailwind 10/10, CSS 10/10
- **Era**: 2020s Digital Well-being
- **Complexity**: Low

## Gen Z Chaos / Maximalism

- **Reads as**: Chaos, clutter, stickers, raw, collage, mixed media, loud, internet culture, ironic
- **Primary colors**: Clashing Brights: #FF00FF, #00FF00, #FFFF00, #0000FF
- **Secondary colors**: Gradients, rainbow, glitch, noise, heavily saturated mix
- **Effects**: Marquee scrolls, jitter, sticker layering, GIF overload, random placement, drag-and-drop
- **Best for**: Gen Z lifestyle brands, music artists, creative portfolios, viral marketing, fashion
- **Do NOT use for**: Corporate, government, healthcare, banking, serious tools
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Poor (heavy assets)
- **Accessibility**: ❌ Poor
- **Mobile**: ◐ Medium
- **Conversion**: ✓ High (Viral)
- **Frameworks**: CSS-in-JS 8/10
- **Era**: 2023+ Internet Core
- **Complexity**: High

## Biomimetic / Organic 2.0

- **Reads as**: Nature-inspired, cellular, fluid, breathing, generative, algorithms, life-like
- **Primary colors**: Cellular Pink #FF9999, Chlorophyll Green #00FF41, Bioluminescent Blue
- **Secondary colors**: Deep Ocean #001E3C, Coral #FF7F50, Organic gradients
- **Effects**: Breathing animations, fluid morphing, generative growth, physics-based movement
- **Best for**: Sustainability tech, biotech, advanced health, meditation, generative art platforms
- **Do NOT use for**: Standard SaaS, data grids, strict corporate, accounting
- **Theme support**: light ✓ Full, dark ✓ Full
- **Performance**: ⚠ Moderate
- **Accessibility**: ✓ Good
- **Mobile**: ✓ Good
- **Conversion**: ✓ High
- **Frameworks**: Canvas 10/10, WebGL 10/10
- **Era**: 2024+ Generative
- **Complexity**: High
