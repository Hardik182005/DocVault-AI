/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "secondary": "#65568a",
        "surface-tint": "#6434ed",
        "on-secondary": "#ffffff",
        "error-container": "#ffdad6",
        "outline-variant": "#cac3d9",
        "surface": "#fcf9f8",
        "tertiary": "#005a3e",
        "surface-container": "#f0edec",
        "on-primary-container": "#e9e1ff",
        "on-error": "#ffffff",
        "on-tertiary-fixed-variant": "#005138",
        "surface-variant": "#e5e2e1",
        "primary-fixed-dim": "#cbbeff",
        "secondary-fixed-dim": "#cfbdf9",
        "error": "#ba1a1a",
        "inverse-primary": "#cbbeff",
        "inverse-surface": "#313030",
        "surface-bright": "#fcf9f8",
        "surface-container-high": "#ebe7e7",
        "on-secondary-fixed": "#201142",
        "background": "#fcf9f8",
        "on-surface": "#1c1b1b",
        "primary": "#5317dd",
        "on-error-container": "#93000a",
        "primary-fixed": "#e7deff",
        "surface-container-low": "#f6f3f2",
        "primary-container": "#6c3ff5",
        "on-primary-fixed-variant": "#4b00d3",
        "surface-container-highest": "#e5e2e1",
        "on-secondary-container": "#5c4e81",
        "on-primary": "#ffffff",
        "secondary-container": "#d5c3ff",
        "on-tertiary-container": "#68ffc2",
        "surface-dim": "#dcd9d9",
        "tertiary-fixed": "#63fcc0",
        "tertiary-fixed-dim": "#3fdfa5",
        "on-tertiary-fixed": "#002114",
        "on-tertiary": "#ffffff",
        "on-background": "#1c1b1b",
        "secondary-fixed": "#e9ddff",
        "on-primary-fixed": "#1e0060",
        "inverse-on-surface": "#f3f0ef",
        "on-secondary-fixed-variant": "#4d3e71",
        "outline": "#797487",
        "tertiary-container": "#007552",
        "surface-container-lowest": "#ffffff",
        "on-surface-variant": "#484456",
        "charcoal": "#0D0D0D",
        "offwhite": "#FAFAFA",
        "purple-night": "#1A0A3C"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      spacing: {
        "gutter": "24px",
        "unit": "4px",
        "margin": "32px",
        "container-max": "1440px"
      },
      maxWidth: {
        "container-max": "1440px"
      },
      fontFamily: {
        "display-hero": ["DM Sans", "sans-serif"],
        "headline-lg": ["DM Sans", "sans-serif"],
        "headline-lg-mobile": ["DM Sans", "sans-serif"],
        "title-md": ["DM Sans", "sans-serif"],
        "body-md": ["DM Sans", "sans-serif"],
        "label-caps": ["DM Sans", "sans-serif"],
        "data-mono": ["JetBrains Mono", "monospace"]
      },
      fontSize: {
        "headline-lg": ["40px", { "lineHeight": "48px", "fontWeight": "700" }],
        "headline-lg-mobile": ["32px", { "lineHeight": "40px", "fontWeight": "700" }],
        "label-caps": ["12px", { "lineHeight": "16px", "letterSpacing": "0.05em", "fontWeight": "700" }],
        "title-md": ["18px", { "lineHeight": "24px", "fontWeight": "600" }],
        "title-lg": ["22px", { "lineHeight": "28px", "fontWeight": "700" }],
        "body-md": ["16px", { "lineHeight": "24px", "fontWeight": "400" }],
        "display-hero": ["72px", { "lineHeight": "80px", "letterSpacing": "-0.02em", "fontWeight": "700" }],
        "data-mono": ["14px", { "lineHeight": "20px", "letterSpacing": "-0.01em", "fontWeight": "600" }]
      },
      animation: {
        'marquee': 'marquee 25s linear infinite',
        'scanline': 'scanline 10s linear infinite',
        'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'packet-move': 'packetMove 3s linear infinite',
        'spin-slow': 'spin 3s linear infinite',
        'fade-up': 'fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'fade-up-stagger': 'fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'typewriter': 'typewriter 2s steps(20) forwards',
        'blink': 'blink 1s step-end infinite',
        'draw-line': 'drawLine 0.6s ease forwards',
        'packet-travel': 'packetTravel 2s linear infinite',
        'pulse-green': 'pulseGreen 1.2s infinite',
        'rotate-once': 'rotateOnce 2s linear forwards',
        'heartbeat-pulse': 'heartbeatPulse 3s ease-in-out infinite',
        'ring-pulse': 'ringPulse 2s infinite',
        'mask-up': 'maskUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' }
        },
        scanline: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' }
        },
        pulseGlow: {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(108, 63, 245, 0.4)' },
          '50%': { opacity: '.8', boxShadow: '0 0 0 8px rgba(108, 63, 245, 0)' },
        },
        packetMove: {
          '0%': { left: '0%' },
          '100%': { left: '100%' }
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)', filter: 'blur(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)', filter: 'blur(0)' },
        },
        typewriter: {
          '0%': { width: '0' },
          '100%': { width: '100%' }
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' }
        },
        drawLine: {
          '0%': { strokeDashoffset: '100%' },
          '100%': { strokeDashoffset: '0' }
        },
        packetTravel: {
          '0%': { offsetDistance: '0%' },
          '100%': { offsetDistance: '100%' }
        },
        pulseGreen: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' }
        },
        rotateOnce: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' }
        },
        heartbeatPulse: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' }
        },
        ringPulse: {
          '0%': { boxShadow: '0 0 0 0 rgba(0,196,140,0.4)' },
          '100%': { boxShadow: '0 0 0 8px rgba(0,196,140,0)' }
        },
        maskUp: {
          '0%': { transform: 'translateY(120%) rotate(4deg)' },
          '100%': { transform: 'translateY(0) rotate(0deg)' }
        }
      }
    },
  },
  plugins: [],
}
