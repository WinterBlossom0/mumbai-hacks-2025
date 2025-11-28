# CSS Architecture

The CSS has been modularized into three organized files for better maintainability:

## File Structure

```
frontend/
├── css/
│   ├── base.css          (~120 lines)
│   ├── components.css    (~350 lines)
│   └── layout.css        (~380 lines)
└── index.html
```

## Files Overview

### 1. **base.css**
Foundation styles and global configurations:
- CSS Variables (colors, spacing, shadows)
- Reset styles
- Body and global typography
- Custom cursor (eye cursor)
- Core animations (fadeIn, slideIn, pulse)

### 2. **components.css**
Reusable UI components:
- Navigation (nav-container, nav-links, logo)
- Buttons (btn, btn-primary, btn-secondary, vote-btn)
- Cards
- Verdict badges (verdict-badge, history-verdict)
- Forms (input-group, toggle-switch)
- Authentication components (auth-buttons, user-avatar)
- Reveal-on-hover effect

### 3. **layout.css**
Page-specific layouts and sections:
- Hero section (hero, hero-redesigned, hero-post-display)
- News ticker (ticker-band, ticker-item, animations)
- Public feed section
- Verify container
- History container
- Responsive design breakpoints
- Clerk UI customization

## Benefits

✅ **Better Organization**: Each file has a clear purpose
✅ **Easier Maintenance**: Find and update styles quickly
✅ **Improved Performance**: Browser can cache individual files
✅ **Team Collaboration**: Multiple developers can work on different files
✅ **Reduced Conflicts**: Smaller files = fewer merge conflicts

## Import Order

The files are imported in this specific order in `index.html`:

```html
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/components.css">
<link rel="stylesheet" href="css/layout.css">
```

This order ensures:
1. Variables and resets load first
2. Components can use base variables
3. Layouts can use both base and component styles

## Migration Notes

- Original `styles.css` (1349 lines) → Split into 3 files (~850 lines total)
- All functionality preserved
- No breaking changes
- Improved readability and maintainability
