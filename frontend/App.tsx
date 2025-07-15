import { useState } from 'react';
import AuthPage from './components/AuthPage';
import MoodSelector from './components/MoodSelector';
import MoodContent from './components/MoodContent';
import BreathingExercise from './components/BreathingExercise';
import JournalingSpace from './components/JournalingSpace';
import GroundingGame from './components/GroundingGame';
import JoyJar from './components/JoyJar';
import AudioPlayer from './components/AudioPlayer';
import MusicPlayer from './components/MusicPlayer';
import AffirmationsPlayer from './components/AffirmationsPlayer';
import { MoodType, MoodEntry, ActivityContent } from './types';
import { useLocalStorage } from './hooks/useLocalStorage';

interface User {
  id: string;
  email: string;
  name: string;
}

type AppState =
  | { stage: 'mood-selection' }
  | { stage: 'mood-content'; mood: MoodType; intensity: number }
  | { stage: 'breathing'; mood: MoodType; duration: number }
  | { stage: 'journal'; mood: MoodType; prompt?: string }
  | { stage: 'game'; mood: MoodType }
  | { stage: 'joy-jar' }
  | { stage: 'audio'; mood: MoodType }
  | { stage: 'music'; mood: MoodType; intensity: number }
  | { stage: 'affirmations'; mood: MoodType; intensity: number };

function App() {
  const [appState, setAppState] = useState<AppState>({ stage: 'mood-selection' });
  const [user, setUser] = useState<User | null>(() => {
    const userData = localStorage.getItem('user_data');
    const token = localStorage.getItem('auth_token');
    return userData && token ? JSON.parse(userData) : null;
  });
  const [moodHistory, setMoodHistory] = useLocalStorage<MoodEntry[]>('mood-history', []);

  const handleLogin = (userData: User) => {
    setUser(userData);
  };
  const handleMoodSelect = (mood: MoodType, intensity: number) => {
    // Save mood entry
    const moodEntry: MoodEntry = {
      id: Date.now().toString(),
      mood,
      intensity,
      timestamp: new Date()
    };
    setMoodHistory(prev => [moodEntry, ...prev.slice(0, 29)]); // Keep last 30 entries

    setAppState({ stage: 'mood-content', mood, intensity });
  };

  const handleActivitySelect = (activity: ActivityContent) => {
    if (appState.stage !== 'mood-content') return;

    const { mood, intensity } = appState;

    switch (activity.type) {
      case 'breathing':
        setAppState({
          stage: 'breathing',
          mood,
          duration: activity.duration || 300
        });
        break;
      case 'journal':
        setAppState({
          stage: 'journal',
          mood,
          prompt: activity.title === 'Joy Jar Entry' ? 'What made you happy today?' : undefined
        });
        break;
      case 'game':
        setAppState({ stage: 'game', mood });
        break;
      case 'audio':
        setAppState({ stage: 'audio', mood });
        break;
      case 'music':
        setAppState({ stage: 'music', mood, intensity });
        break;
      case 'affirmation':
        setAppState({ stage: 'affirmations', mood, intensity });
        break;
    }
  };

  const handleBack = () => {
    if (appState.stage === 'mood-selection') return;

    if (appState.stage === 'mood-content') {
      setAppState({ stage: 'mood-selection' });
    } else {
      // Go back to mood content with the current mood
      const mood = 'mood' in appState ? appState.mood : 'neutral';
      const lastMoodEntry = moodHistory[0];
      const intensity = lastMoodEntry?.intensity || 5;
      setAppState({ stage: 'mood-content', mood, intensity });
    }
  };
// Show auth page if user is not logged in
  if (!user) {
    return <AuthPage onLogin={handleLogin} />;
  }

  switch (appState.stage) {
    case 'mood-selection':
      return <MoodSelector onMoodSelect={handleMoodSelect} />;
    
    case 'mood-content':
      return (
        <MoodContent
          mood={appState.mood}
          intensity={appState.intensity}
          onBack={handleBack}
          onActivitySelect={handleActivitySelect}
        />
      );
    
    case 'breathing':
      return (
        <BreathingExercise
          mood={appState.mood}
          duration={appState.duration}
          onBack={handleBack}
        />
      );
    
    case 'journal':
      return (
        <JournalingSpace
          mood={appState.mood}
          prompt={appState.prompt}
          onBack={handleBack}
        />
      );
    
    case 'game':
      return (
        <GroundingGame
          mood={appState.mood}
          onBack={handleBack}
        />
      );
    
    case 'joy-jar':
      return <JoyJar onBack={handleBack} />;
    
    case 'audio':
      return (
        <AudioPlayer
          mood={appState.mood}
          onBack={handleBack}
        />
      );
    
    case 'music':
      return (
        <MusicPlayer
          mood={appState.mood}
          intensity={appState.intensity}
          onBack={handleBack}
        />
      );
    
    case 'affirmations':
      return (
        <AffirmationsPlayer
          mood={appState.mood}
          intensity={appState.intensity}
          onBack={handleBack}
        />
      );
    
    default:
      return <MoodSelector onMoodSelect={handleMoodSelect} />;
  }
}

export default App;