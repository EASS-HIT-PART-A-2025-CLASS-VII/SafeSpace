# SafeSpace Frontend

React + TypeScript frontend for the SafeSpace mental health companion app.

## 🚀 Features

- **Modern React**: Built with React 18, TypeScript, and Vite
- **Beautiful UI**: Tailwind CSS with custom animations and gradients
- **Responsive Design**: Mobile-first approach with smooth interactions
- **AI Integration**: Seamless connection to backend AI services
- **Local Storage**: Persistent data for mood history and journal entries
- **Accessibility**: WCAG compliant with proper ARIA labels

## 🏗️ Architecture

### Component Structure
```
frontend/
├── components/
│   ├── MoodSelector.tsx      # Initial mood selection
│   ├── MoodContent.tsx       # Activity suggestions
│   ├── MusicPlayer.tsx       # AI-powered music player
│   ├── AffirmationsPlayer.tsx # AI affirmations
│   ├── BreathingExercise.tsx # Guided breathing
│   ├── JournalingSpace.tsx   # Therapeutic writing
│   ├── GroundingGame.tsx     # Anxiety relief games
│   ├── JoyJar.tsx           # Happy moments collection
│   └── AudioPlayer.tsx       # Ambient soundscapes
├── hooks/
│   └── useLocalStorage.ts    # Persistent storage hook
├── types/
│   └── index.ts             # TypeScript definitions
├── utils/
│   └── moodContent.ts       # Mood-based content logic
└── App.tsx                  # Main application router
```

### State Management
- **Local State**: React hooks for component state
- **Persistent Storage**: Custom hook for localStorage
- **No External State**: Simple, lightweight approach

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Animations**: Smooth transitions and micro-interactions
- **Mood-Based Colors**: Dynamic gradients based on emotional state
- **Mobile-First**: Responsive design for all screen sizes

## 🎨 Design System

### Color Palette
- **Happy**: Yellow to orange gradients
- **Sad**: Blue to indigo gradients  
- **Anxious**: Purple to pink gradients
- **Angry**: Red to orange gradients
- **Tired**: Indigo to purple gradients
- **Neutral**: Gray to blue gradients
- **Mixed**: Green to teal gradients

### Typography
- **Primary Font**: System fonts for optimal performance
- **Font Weights**: Light (300), Medium (500), Semibold (600), Bold (700)
- **Line Heights**: 150% for body text, 120% for headings

### Spacing
- **8px Grid System**: Consistent spacing throughout
- **Component Padding**: 16px (p-4) to 32px (p-8)
- **Margins**: 12px (mb-3) to 24px (mb-6)

## 🔧 Development

### Getting Started
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables
```bash
VITE_API_URL=http://localhost:8000  # Backend API URL
```

### Code Quality
- **ESLint**: Code linting with React hooks rules
- **TypeScript**: Strict type checking
- **Prettier**: Code formatting (recommended)

## 🧩 Key Components

### MoodSelector
- Initial mood selection interface
- Intensity slider (1-10)
- Smooth animations and transitions
- Validates input before proceeding

### MusicPlayer
- AI-generated playlist display
- Simulated audio controls
- Track navigation and progress
- Volume control and muting

### AffirmationsPlayer
- AI-generated personalized affirmations
- Auto-play functionality
- Breathing instructions for specific moods
- Navigation between affirmations

### BreathingExercise
- Multiple breathing patterns (4-7-8, box breathing, etc.)
- Visual breathing guide with animated circle
- Timer and progress tracking
- Mood-specific pattern selection

### JournalingSpace
- Rich text input for therapeutic writing
- AI-powered writing prompts
- Entry history and persistence
- Character count and save functionality

## 🎯 User Experience

### Navigation Flow
1. **Mood Selection** → User selects current mood and intensity
2. **Activity Menu** → AI suggests appropriate activities
3. **Activity Experience** → Immersive, focused activity interface
4. **Return Navigation** → Easy back navigation to previous screens

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Color Contrast**: WCAG AA compliant color ratios
- **Focus Management**: Clear focus indicators

### Performance
- **Lazy Loading**: Components loaded on demand
- **Optimized Images**: Proper image optimization
- **Bundle Splitting**: Efficient code splitting
- **Local Storage**: Minimal API calls for better performance

## 🔌 API Integration

### Backend Communication
```typescript
// Example API call
const response = await fetch('/api/music/playlist', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    mood_type: mood,
    intensity: intensity,
    duration_minutes: 30
  })
});
```

### Error Handling
- **Graceful Degradation**: Fallback content when APIs fail
- **Loading States**: Clear loading indicators
- **Error Messages**: User-friendly error communication
- **Retry Mechanisms**: Automatic retry for failed requests

## 📱 Mobile Experience

### Responsive Design
- **Mobile-First**: Designed for mobile, enhanced for desktop
- **Touch Interactions**: Optimized for touch interfaces
- **Viewport Meta**: Proper mobile viewport configuration
- **Safe Areas**: Respect for device safe areas

### Performance on Mobile
- **Lightweight**: Minimal bundle size
- **Fast Loading**: Optimized for slower connections
- **Smooth Animations**: 60fps animations on mobile devices
- **Battery Efficient**: Minimal background processing

---

Built with modern React best practices for a smooth, accessible, and beautiful user experience.