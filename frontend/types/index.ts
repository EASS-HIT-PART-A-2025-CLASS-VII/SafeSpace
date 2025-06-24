export type MoodType = 'happy' | 'neutral' | 'anxious' | 'sad' | 'angry' | 'tired' | 'mixed';

export interface MoodEntry {
  id: string;
  mood: MoodType;
  intensity: number;
  timestamp: Date;
  note?: string;
}

export interface JoyMoment {
  id: string;
  title: string;
  description: string;
  timestamp: Date;
  image?: string;
}

export interface JournalEntry {
  id: string;
  content: string;
  prompt?: string;
  mood: MoodType;
  timestamp: Date;
}

export interface ActivityContent {
  type: 'breathing' | 'audio' | 'game' | 'journal' | 'affirmation' | 'music';
  title: string;
  description: string;
  duration?: number;
}